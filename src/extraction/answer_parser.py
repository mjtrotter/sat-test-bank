
import re
from typing import Dict

import fitz  # PyMuPDF


def parse_answer_key(pdf_path: str) -> Dict[int, str]:
    """
    Parses MATHCOUNTS answer key PDFs using spatial layout analysis.
    It's designed to be robust against multi-column layouts.
    """
    answers = {}
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_width = page.rect.width
            # Blocks containing problem numbers (e.g., "1. ____")
            problem_blocks = []
            # Blocks containing potential answers
            answer_blocks = []

            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]
            for block in blocks:
                block_text = " ".join(
                    span["text"] for line in block.get("lines", []) for span in line.get("spans", [])
                ).strip()

                if not block_text:
                    continue

                # Identify blocks that look like problem number placeholders
                if re.match(r"^\d+\.", block_text) and "___" in block_text:
                    problem_blocks.append(block)
                # This is a potential answer block if it starts with a number but has no placeholder
                elif re.match(r"^\d+\.", block_text) and "___" not in block_text:
                     answer_blocks.append(block)
                # Or if it's just some text that could be an answer.
                # Avoid capturing instructions.
                elif len(block_text.split()) < 10 and not re.search(r'(?i)round|tiebreaker|note', block_text):
                     answer_blocks.append(block)


            # Associate answers with problems based on spatial proximity
            for p_block in problem_blocks:
                p_num_match = re.match(r"(\d+)\.", " ".join(span["text"] for l in p_block.get("lines",[]) for span in l.get("spans",[])))
                if not p_num_match:
                    continue
                
                problem_num = int(p_num_match.group(1))
                p_bbox = p_block['bbox']
                
                best_match = None
                min_dist = float('inf')

                # Find the closest answer block on the same vertical level
                for a_block in answer_blocks:
                    a_bbox = a_block['bbox']
                    # Check for vertical overlap/closeness and horizontal separation
                    y_dist = abs(a_bbox[1] - p_bbox[1])
                    x_dist = abs(a_bbox[0] - p_bbox[0])

                    # Heuristic: must be reasonably close vertically, but not the same block
                    if y_dist < 20 and x_dist > 50:
                        dist = (y_dist**2 + (x_dist/10)**2)**0.5 # Prioritize vertical alignment
                        if dist < min_dist:
                            min_dist = dist
                            best_match = a_block
                
                if best_match:
                    ans_text = " ".join(
                        span["text"] for line in best_match.get("lines", []) for span in line.get("spans", [])
                    ).strip()
                    
                    # Clean up the extracted answer text
                    # Remove the number if it's also present in the answer text
                    ans_text = re.sub(f"^{problem_num}\.\s*", "", ans_text).strip()
                    
                    if ans_text:
                        answers[problem_num] = ans_text
                        
    except Exception as e:
        print(f"Could not parse answer key {pdf_path}: {e}")
        
    return answers
