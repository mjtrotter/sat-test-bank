import re
from typing import List, Dict, Any, Optional, Set # Added Set
from collections import defaultdict # Added defaultdict
from sqlalchemy.ext.asyncio import AsyncSession # Added AsyncSession
from src.models.tables import SkillNode

class TaxonomyLoader:
    def __init__(self, markdown_path: str):
        self.markdown_path = markdown_path
        self.skill_nodes_data: List[Dict[str, Any]] = []
        self.domains_map: Dict[str, str] = { # Mapping full domain names to short codes
            "Counting & Probability": "COUNT",
            "Algebra": "ALG",
            "Number Theory": "NT",
            "Geometry": "GEO",
            "Arithmetic / Prealgebra": "ARITH",
            "Logic & Strategy": "LOGIC",
        }
        self.levels_map: Dict[str, int] = {
            "Level 1": 1, "Level 2": 2, "Level 3": 3, "Level 4": 4, "Level 5": 5
        }

    async def parse_markdown(self) -> List[Dict[str, Any]]:
        """
        Parses the markdown file to extract skill node data using a state-machine approach.
        """
        current_domain_full_name: Optional[str] = None
        current_domain_code: Optional[str] = None
        current_level: Optional[int] = None
        
        with open(self.markdown_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1

            # Detect Domain header
            domain_match = re.match(r'^## Domain \d+: (.+)', line)
            if domain_match:
                current_domain_full_name = domain_match.group(1).strip()
                current_domain_code = self.domains_map.get(current_domain_full_name)
                current_level = None # Reset level when new domain starts
                continue

            # Detect Level header
            level_match = re.match(r'^### (Level \d+) — (.+)', line)
            if level_match:
                level_text = level_match.group(1).strip()
                current_level = self.levels_map.get(level_text)
                continue # Level header doesn't start a table itself, just sets context

            # --- Table Parsing Logic ---
            # A table header is always prefixed by '| ID | Skill Name |'
            # It must be after a domain and level have been set.
            if current_domain_code and current_level is not None and line.startswith('| ID | Skill Name |'):
                table_headers = [h.strip() for h in line.split('|') if h.strip()]
                
                # The next line MUST be the separator, e.g., "|----|-----------|"
                if i < len(lines):
                    sep_line = lines[i].strip()
                    i += 1
                    if re.match(r'^\|-+\|', sep_line):
                        # Now we are officially in a table, consume all rows
                        while i < len(lines):
                            row_line = lines[i].strip()
                            
                            # Custom splitting logic to handle pipes in description
                            # Assumes a 5-column structure: | ID | Name | Description | Prereqs | Source |
                            first_pipe_idx = row_line.find('|')
                            second_pipe_idx = row_line.find('|', first_pipe_idx + 1)
                            third_pipe_idx = row_line.find('|', second_pipe_idx + 1)

                            last_pipe_idx = row_line.rfind('|')
                            second_last_pipe_idx = row_line.rfind('|', 0, last_pipe_idx)
                            third_last_pipe_idx = row_line.rfind('|', 0, second_last_pipe_idx)

                            row_cells = []
                            if all(idx != -1 for idx in [first_pipe_idx, second_pipe_idx, third_pipe_idx,
                                                         last_pipe_idx, second_last_pipe_idx, third_last_pipe_idx]) \
                               and third_pipe_idx < third_last_pipe_idx:
                                
                                id_str = row_line[first_pipe_idx+1:second_pipe_idx].strip()
                                name_str = row_line[second_pipe_idx+1:third_pipe_idx].strip()
                                desc_str = row_line[third_pipe_idx+1:third_last_pipe_idx].strip()
                                prereq_str = row_line[third_last_pipe_idx+1:second_last_pipe_idx].strip()
                                source_str = row_line[second_last_pipe_idx+1:last_pipe_idx].strip()

                                row_cells = [id_str, name_str, desc_str, prereq_str, source_str]


                            if row_line.startswith('|') and len(row_cells) == len(table_headers):
                                # It's a data row, process it
                                skill_data_raw = dict(zip(table_headers, row_cells))
                                
                                skill_id = skill_data_raw.get('ID')
                                if not skill_id:
                                    # Skip malformed row, or row without ID
                                    i += 1 
                                    continue
                                
                                prerequisites_raw = skill_data_raw.get('Prerequisites', '').replace('—', '').strip()
                                prerequisites = [p.strip() for p in re.split(r'[;,]', prerequisites_raw) if p.strip()] if prerequisites_raw else []
                                
                                source_mapping_raw = skill_data_raw.get('Source Mapping', '').replace('—', '').strip()
                                source_mapping = [s.strip() for s in re.split(r'[;,]', source_mapping_raw) if s.strip()] if source_mapping_raw else []

                                self.skill_nodes_data.append({
                                    'id': skill_id,
                                    'name': skill_data_raw.get('Skill Name'),
                                    'description': skill_data_raw.get('Description') if skill_data_raw.get('Description') != '—' else None,
                                    'domain': current_domain_code,
                                    'level': current_level,
                                    'prerequisites': prerequisites,
                                    'source_mapping': source_mapping,
                                })
                                i += 1 # Move to the next line (next potential table row)
                            else:
                                # Not a table row, so the current table has ended
                                break
                # After a table (or if separator/header was malformed), table context is reset implicitly by loop structure
        return self.skill_nodes_data

    def validate_prerequisites(self) -> List[str]:
        """
        Validates the prerequisite graph for cycles, orphan references, and existence.
        Returns a list of error messages, or an empty list if valid.
        """
        errors: List[str] = []
        skill_ids: Set[str] = {node['id'] for node in self.skill_nodes_data}
        prereq_graph: Dict[str, List[str]] = {node['id']: node['prerequisites'] for node in self.skill_nodes_data}

        # 1. Check for existence of prerequisites (and orphan references)
        for node_id, prereqs in prereq_graph.items():
            for prereq_id in prereqs:
                if prereq_id not in skill_ids:
                    errors.append(f"Validation Error: Skill '{node_id}' has a prerequisite '{prereq_id}' which does not exist.")

        # 2. Check for cycles using DFS
        # Adjacency list for DFS (node -> its prerequisites)
        # Only build adj list with existing skills, to prevent DFS errors from non-existent prereqs
        adj: Dict[str, List[str]] = {node_id: [] for node_id in skill_ids}
        for node_id, prereqs in prereq_graph.items():
            for prereq_id in prereqs:
                if prereq_id in skill_ids: # Ensure prereq_id exists before adding to graph
                    adj[node_id].append(prereq_id)

        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def dfs_cycle_check(u: str):
            visited.add(u)
            recursion_stack.add(u)

            for v in adj.get(u, []):
                if v not in visited:
                    if dfs_cycle_check(v):
                        return True
                elif v in recursion_stack:
                    errors.append(f"Validation Error: Cycle detected involving skill '{u}' and its prerequisite '{v}'.")
                    return True # Found a cycle

            recursion_stack.remove(u)
            return False

        for node_id in skill_ids:
            if node_id not in visited:
                dfs_cycle_check(node_id)
        
        return errors

    async def load_to_db(self, session: AsyncSession) -> None:
        """
        Loads the parsed skill nodes into the database.
        """
        skill_nodes_to_add: List[SkillNode] = []
        for node_data in self.skill_nodes_data:
            skill_node = SkillNode(
                id=node_data['id'],
                name=node_data['name'],
                description=node_data['description'],
                domain=node_data['domain'],
                level=node_data['level'],
                # SQLAlchemy's JSONB type handles Python lists/dicts automatically
                prerequisites=node_data['prerequisites'],
                source_mapping=node_data['source_mapping'],
            )
            skill_nodes_to_add.append(skill_node)
        
        session.add_all(skill_nodes_to_add)
        await session.commit()
        print(f"Successfully loaded {len(skill_nodes_to_add)} skill nodes into the database.")

    def print_summary_stats(self) -> None:
        """
        Calculates and prints summary statistics for the loaded skill nodes
        by domain and level.
        """
        if not self.skill_nodes_data:
            print("No skill nodes to summarize.")
            return

        domain_level_counts: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        domain_totals: Dict[str, int] = defaultdict(int)
        level_totals: Dict[int, int] = defaultdict(int)
        
        all_levels = sorted(list(set(node['level'] for node in self.skill_nodes_data)))
        all_domains = sorted(list(set(node['domain'] for node in self.skill_nodes_data)))

        for node in self.skill_nodes_data:
            domain = node['domain']
            level = node['level']
            domain_level_counts[domain][level] += 1
            domain_totals[domain] += 1
            level_totals[level] += 1

        print("\n--- Skill Node Summary Statistics ---")
        
        # Header row for levels
        header = "{:<15}".format("Domain")
        for level in all_levels:
            header += "{:>5}".format(f"L{level}")
        header += "{:>8}".format("Total")
        print(header)
        print("-" * len(header))

        # Data rows
        for domain in all_domains:
            row = "{:<15}".format(domain)
            for level in all_levels:
                row += "{:>5}".format(domain_level_counts[domain][level] if domain_level_counts[domain][level] > 0 else '-')
            row += "{:>8}".format(domain_totals[domain])
            print(row)

        # Total row
        print("-" * len(header))
        total_row = "{:<15}".format("Total")
        for level in all_levels:
            total_row += "{:>5}".format(level_totals[level])
        total_row += "{:>8}".format(len(self.skill_nodes_data))
        print(total_row)
        print("-----------------------------------\n")


