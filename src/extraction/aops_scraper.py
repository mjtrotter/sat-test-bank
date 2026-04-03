# src/extraction/aops_scraper.py
import httpx
from bs4 import BeautifulSoup, Tag
import time
import os
from typing import Optional, List, Dict, Any
import re
import asyncio

from src.core.database import async_session
from src.models.tables import Problem, ProblemFigure, ProblemSkillTag # Assuming ProblemSkillTag might be used later
from src.models.enums import ContestFamily, RoundType

# Base URL for AoPS Wiki
AOPS_BASE_URL = "https://artofproblemsolving.com"

# Contest definitions and their URL patterns
CONTEST_CONFIG = {
    "AMC8": {
        "years": range(2000, 2027),  # 2000 to present
        "url_pattern": "wiki/index.php/{year}_AMC_8_Problems",
        "problem_pattern": "wiki/index.php/{year}_AMC_8_Problems/Problem_{problem_number}",
        "max_problems": 25,
    },
    "AMC10A": {
        "years": range(2000, 2027),
        "url_pattern": "wiki/index.php/{year}_AMC_10A_Problems",
        "problem_pattern": "wiki/index.php/{year}_AMC_10A_Problems/Problem_{problem_number}",
        "max_problems": 25,
    },
    "AMC10B": {
        "years": range(2000, 2027),
        "url_pattern": "wiki/index.php/{year}_AMC_10B_Problems",
        "problem_pattern": "wiki/index.php/{year}_AMC_10B_Problems/Problem_{problem_number}",
        "max_problems": 25,
    },
    "AMC12A": {
        "years": range(2000, 2027),
        "url_pattern": "wiki/index.php/{year}_AMC_12A_Problems",
        "problem_pattern": "wiki/index.php/{year}_AMC_12A_Problems/Problem_{problem_number}",
        "max_problems": 25,
    },
    "AMC12B": {
        "years": range(2000, 2027),
        "url_pattern": "wiki/index.php/{year}_AMC_12B_Problems",
        "problem_pattern": "wiki/index.php/{year}_AMC_12B_Problems/Problem_{problem_number}",
        "max_problems": 25,
    },
    "AIME_I": {
        "years": range(1983, 2027),
        "url_pattern": "wiki/index.php/{year}_AIME_I_Problems",
        "problem_pattern": "wiki/index.php/{year}_AIME_I_Problems/Problem_{problem_number}",
        "max_problems": 15,
    },
    "AIME_II": {
        "years": range(1983, 2027),
        "url_pattern": "wiki/index.php/{year}_AIME_II_Problems",
        "problem_pattern": "wiki/index.php/{year}_AIME_II_Problems/Problem_{problem_number}",
        "max_problems": 15,
    },
}

# Rate limiting: 1 request per second
RATE_LIMIT_DELAY = 1.0

# Directory to save figures
FIGURES_DIR = "data/aops/figures"
os.makedirs(FIGURES_DIR, exist_ok=True)

# Placeholder for resume capability
COMPLETED_TRACKER_FILE = "data/aops/completed_contests.txt"

def load_completed_contests() -> Dict[str, List[int]]:
    """Loads a dictionary of completed contests and years from a tracker file."""
    completed = {}
    if os.path.exists(COMPLETED_TRACKER_FILE):
        with open(COMPLETED_TRACKER_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    contest, year_str = line.split(":")
                    if contest not in completed:
                        completed[contest] = []
                    completed[contest].append(int(year_str))
    return completed

def save_completed_contest(contest: str, year: int):
    """Saves a completed contest and year to the tracker file."""
    with open(COMPLETED_TRACKER_FILE, "a") as f:
        f.write(f"{contest}:{year}\n")

def get_aops_url(contest_type: str, year: int, problem_number: Optional[int] = None) -> str:
    """Constructs the full URL for a given contest page or individual problem."""
    config = CONTEST_CONFIG.get(contest_type)
    if not config:
        raise ValueError(f"Unknown contest type: {contest_type}")

    if problem_number is None:
        path = config["url_pattern"].format(year=year)
    else:
        path = config["problem_pattern"].format(year=year, problem_number=problem_number)
    return f"{AOPS_BASE_URL}/{path}"

async def fetch_page(url: str) -> Optional[BeautifulSoup]:
    """Fetches a page and returns a BeautifulSoup object, with rate limiting."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            await asyncio.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            return BeautifulSoup(response.text, "html.parser")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching {url}: {e}")
        except httpx.RequestError as e:
            print(f"Request error fetching {url}: {e}")
    return None

async def download_figure(url: str, local_path: str):
    """Downloads a figure from the given URL to the specified local path."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded figure to {local_path}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error downloading figure from {url}: {e}")
        except httpx.RequestError as e:
            print(f"Request error downloading figure from {url}: {e}")

async def save_problem_to_db(problem_data: Dict[str, Any]):
    """Saves the extracted problem data to the database."""
    async with async_session() as session:
        try:
            # Map contest type to ContestFamily enum
            contest_family_enum = None
            if problem_data["contest"].startswith("AMC8"):
                contest_family_enum = ContestFamily.AMC_8
            elif problem_data["contest"].startswith("AMC10"):
                contest_family_enum = ContestFamily.AMC_10
            elif problem_data["contest"].startswith("AMC12"):
                contest_family_enum = ContestFamily.AMC_12
            elif problem_data["contest"].startswith("AIME"):
                contest_family_enum = ContestFamily.AIME
            
            # Determine problem style
            problem_style = "multiple_choice"
            if contest_family_enum == ContestFamily.AIME:
                problem_style = "free_response"

            problem = Problem(
                contest_family=contest_family_enum.value,
                contest_year=problem_data["year"],
                contest_round=problem_data["contest"], # Store the full contest type as round for now (e.g. AMC10A)
                problem_number=problem_data["problem_number"],
                problem_text=problem_data["problem_text"],
                answer=problem_data["answer"],
                official_solution=problem_data["solutions"][0]["text"] if problem_data["solutions"] else None,
                latex_content=problem_data["problem_latex"],
                difficulty_band=problem_data["difficulty_band"],
                primary_domain=None, # Will be set by skill tagging later
                problem_style=problem_style,
                # source_path will be set by the overall scraper if needed, not per problem
                # For AoPS, we can use the URL as source_path if we want.
            )
            session.add(problem)
            await session.flush() # Flush to get problem.id

            for figure_path in problem_data["figures"]:
                problem_figure = ProblemFigure(
                    problem_id=problem.id,
                    figure_path=figure_path,
                    figure_type="diagram" # Assuming all figures are diagrams for now
                )
                session.add(problem_figure)
            
            # TODO: Handle ProblemSkillTag if we decide to extract skills from AoPS directly

            await session.commit()
            print(f"Saved Problem {problem.id} to DB: {problem_data['contest']} {problem_data['year']} Problem {problem_data['problem_number']}")
        except Exception as e:
            await session.rollback()
            print(f"Error saving problem to DB: {e}")

async def scrape_aops_problems(contest: str = None, year: int = None):
    """
    Scrapes problems from AoPS Wiki for the specified contest and year.
    If contest and year are None, it scrapes all configured contests and years.
    """
    print(f"AoPS Scraper: Initiating scrape for contest: {contest}, year: {year}")

    completed_contests = load_completed_contests()

    target_contests = [contest] if contest else CONTEST_CONFIG.keys()

    for c_type in target_contests:
        config = CONTEST_CONFIG[c_type]
        # Ensure year range is always iterable
        target_years = [year] if year else list(config["years"]) 

        for y in target_years:
            if c_type in completed_contests and y in completed_contests[c_type]:
                print(f"Skipping {c_type} {y} as already completed.")
                continue

            print(f"Scraping {c_type} {y}...")
            contest_url = get_aops_url(c_type, y)
            print(f"Fetching contest page: {contest_url}")
            soup = await fetch_page(contest_url)

            if soup:
                problems_data = await parse_contest_page(soup, c_type, y)
                for problem in problems_data:
                    problem_url = get_aops_url(c_type, y, problem["problem_number"])
                    print(f"Fetching individual problem page: {problem_url}")
                    problem_soup = await fetch_page(problem_url)
                    if problem_soup:
                        solution_data = await parse_problem_page(problem_soup)
                        problem.update(solution_data)
                        # Save problem to database
                        await save_problem_to_db(problem)
                        print(f"Scraped Problem {problem['problem_number']} from {c_type} {y}")
                save_completed_contest(c_type, y)
            else:
                print(f"Could not fetch contest page for {c_type} {y}")

async def parse_contest_page(soup: BeautifulSoup, contest_type: str, year: int) -> List[Dict[str, Any]]:
    """Parses the main contest page to get problem statements, answer choices, and links."""
    problems = []
    content_div = soup.find("div", class_="wiki-content")

    if not content_div:
        print("Warning: Could not find wiki-content div on contest page.")
        return problems

    problem_tags = content_div.find_all(lambda tag: tag.name in ['h2', 'h3'] and "Problem" in tag.get_text())

    for problem_tag in problem_tags:
        problem_number_match = re.search(r"Problem (\d+)", problem_tag.get_text())
        if not problem_number_match:
            continue
        problem_num = int(problem_number_match.group(1))

        problem_data = {
            "contest": contest_type,
            "year": year,
            "problem_number": problem_num,
            "problem_text": "",
            "problem_latex": "",
            "answer": None,
            "answer_choices": [],
            "figures": [],
            "skill_tags": [],
            "difficulty_band": None,
            "aops_difficulty_rating": None,
        }

        # Traverse siblings to get problem text, answer choices, and figures
        current_tag = problem_tag.next_sibling
        problem_text_parts = []
        
        while current_tag and not (isinstance(current_tag, Tag) and current_tag.name in ['h2', 'h3'] and "Problem" in current_tag.get_text()):
            if isinstance(current_tag, Tag):
                # Collect all content within the current problem section
                problem_text_parts.append(str(current_tag))
            current_tag = current_tag.next_sibling
        
        # Now, parse the collected HTML for text, LaTeX, and answer choices
        problem_html_content = BeautifulSoup("".join(problem_text_parts), "html.parser")
        problem_data["problem_text"] = problem_html_content.get_text(separator="\\n", strip=True)
        problem_data["problem_latex"] = extract_latex_from_html(problem_html_content)

        # Extract answer choices (A) B) C) D) E)
        for p_tag in problem_html_content.find_all('p'):
            text_content = p_tag.get_text(separator="\\n", strip=True)
            # This regex looks for (A) text, (B) text, etc., but doesn't consume the next (A)
            choice_matches = re.findall(r"\(([A-E])\)\s*(.*?)(?=\s*\([A-E]\)|\s*$)", text_content)
            if choice_matches:
                for choice_letter, choice_text in choice_matches:
                    problem_data["answer_choices"].append(f"{choice_letter}) {choice_text.strip()}")
        
        # Handle images - this should extract image URLs from problem_html_content
        for img_tag in problem_html_content.find_all('img'):
            img_src = img_tag.get('src')
            if img_src:
                # Normalize URL
                if img_src.startswith("/"):
                    img_src = AOPS_BASE_URL + img_src
                
                # Generate a unique filename for the figure
                filename = os.path.basename(img_src)
                # Append a unique identifier to prevent overwriting, if needed
                # For now, let's just use the filename
                local_figure_path = os.path.join(FIGURES_DIR, filename)
                
                # Download the figure asynchronously
                await download_figure(img_src, local_figure_path)
                problem_data["figures"].append(local_figure_path)

        problems.append(problem_data) # Append problem_data here
    return problems

async def parse_problem_page(soup: BeautifulSoup) -> Dict[str, Any]:
    """Parses an individual problem page for solutions and difficulty."""
    solutions = []
    aops_difficulty_rating = None
    problem_answer = None

    content_div = soup.find("div", class_="wiki-content")
    if not content_div:
        print("Warning: Could not find wiki-content div for problem page.")
        return {"solutions": solutions, "aops_difficulty_rating": aops_difficulty_rating, "answer": problem_answer}

    # Extract difficulty rating
    difficulty_span = content_div.find("span", class_="aops-rating")
    if difficulty_span and difficulty_span.get_text(strip=True).startswith("Difficulty:"):
        try:
            rating_text = difficulty_span.get_text(strip=True).replace("Difficulty:", "").strip()
            aops_difficulty_rating = float(rating_text)
        except ValueError:
            pass

    # Extract official answer if present
    # Looking for a <p> tag that contains "Answer: "
    for p_tag in content_div.find_all('p'):
        if "Answer:" in p_tag.get_text():
            # Extract text after "Answer:" up to the next newline or tag
            answer_match = re.search(r"Answer:\s*(.*?)(?=
|<br>|$)", p_tag.get_text())
            if answer_match:
                problem_answer = answer_match.group(1).strip()
                break # Found the answer, no need to continue

    # Find all solution sections
    solution_headers = content_div.find_all(lambda tag: tag.name in ['h2', 'h3', 'h4'] and "Solution" in tag.get_text())

    for header in solution_headers:
        current_solution_approach = header.get_text(strip=True)
        solution_content_parts = []
        
        current_tag = header.next_sibling
        while current_tag and not (isinstance(current_tag, Tag) and current_tag.name in ['h2', 'h3', 'h4'] and "Solution" in current_tag.get_text()):
            if isinstance(current_tag, Tag):
                solution_content_parts.append(str(current_tag))
            current_tag = current_tag.next_sibling
        
        solution_html_content = BeautifulSoup("".join(solution_content_parts), "html.parser")
        solutions.append({
            "approach": current_solution_approach,
            "text": solution_html_content.get_text(separator="\\n", strip=True),
            "latex": extract_latex_from_html(solution_html_content),
        })

    return {"solutions": solutions, "aops_difficulty_rating": aops_difficulty_rating, "answer": problem_answer}

def extract_latex_from_html(element: Any) -> str:
    """
    Extracts LaTeX content from a BeautifulSoup element or a string.
    AoPS uses MathJax, so LaTeX is often within specific tags like <span class="latex">
    or directly within $...$ or $$...$$ delimiters.
    """
    latex_content_parts = []

    if isinstance(element, BeautifulSoup):
        # Find elements that contain LaTeX, e.g., <span class="latex">...</span>
        for latex_span in element.find_all(class_="latex"):
            latex_content_parts.append(latex_span.get_text())
        
        # Also, check for LaTeX within the text nodes using regex for $...$ and $$...$$
        # This is for cases where MathJax might not wrap in <span class="latex">
        for text_node in element.find_all(string=True):
            text = str(text_node)
            # Find both $$...$$ and $...$
            matches = re.findall(r'\$\$(.*?)\$\$|\$(.*?)\$', text, re.DOTALL)
            for m in matches:
                # m will be a tuple like ('formula_with_double_dollars', '') or ('', 'formula_with_single_dollar')
                # We want the non-empty string
                latex_content_parts.extend([grp for grp in m if grp])

    elif isinstance(element, str):
        # Simple regex for $...$ and $$...$$
        matches = re.findall(r'\$\$(.*?)\$\$|\$(.*?)\$', element, re.DOTALL)
        for m in matches:
            latex_content_parts.extend([grp for grp in m if grp])

    return " ".join(latex_content_parts).strip()

if __name__ == "__main__":
    # Example usage for testing
    async def main_test():
        # Scrape a specific AMC10A year
        await scrape_aops_problems(contest="AMC10A", year=2020)
        
        # Scrape all AMC8
        # await scrape_aops_problems(contest="AMC8")

    asyncio.run(main_test())