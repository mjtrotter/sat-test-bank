
import re
from typing import Dict, List, Any

import fitz  # PyMuPDF

from src.extraction.format_detector import detect_mathcounts_format


def clean_text(text: str) -> str:
    """Cleans common OCR errors and formatting issues."""
    text = re.sub(r'’', "'", text)  # Replace curly apostrophes
    text = re.sub(r'“|”', '"', text)  # Replace curly quotes
    text = re.sub(r'\s+–\s+', ' - ', text) # Standardize dashes
    text = re.sub(r'\n{3,}', '\n\n', text)  # Collapse excessive newlines
    return text.strip()


class MathCountsParser:
    """
    Parses MATHCOUNTS problem PDFs, handling different eras and layouts.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.format_info = detect_mathcounts_format(pdf_path)

    def parse(self) -> List[Dict[str, Any]]:
        """
        Main parsing logic. Delegates to the correct method based on format.
        """
        if not self.format_info:
            return []

        if self.format_info["layout"] == "two_column":
            return self._parse_two_column()
        else:
            return self._parse_single_column()

    def _parse_single_column(self) -> List[Dict[str, Any]]:
        """Parses single-column layouts (common in 1990s PDFs)."""
        problems = []
        full_text = ""
        for page_num, page in enumerate(self.doc):
            # Ignore header if present
            header_end_y = self.format_info.get("header_end_y", 0) if page_num == 0 else 0
            rect = page.rect
            clip_rect = fitz.Rect(rect.x0, header_end_y, rect.x1, rect.y1)
            full_text += page.get_text(clip=clip_rect) + "\n"

        problem_matches = list(re.finditer(r"(?m)^(\d+)\.\s+", full_text))

        for i, match in enumerate(problem_matches):
            problem_num = int(match.group(1))
            start_pos = match.end()
            end_pos = problem_matches[i + 1].start() if i + 1 < len(problem_matches) else len(full_text)

            problem_text = full_text[start_pos:end_pos]
            problem_text = clean_text(problem_text)
            
            # Filter out spurious matches
            if len(problem_text) > 10:
                problems.append({
                    "problem_number": problem_num,
                    "problem_text": problem_text
                })
        return problems

    def _parse_two_column(self) -> List[Dict[str, Any]]:
        """
        Parses two-column layouts using block-level analysis.
        Common in 2000s/2010s Sprint Rounds.
        """
        problems = []
        
        for page in self.doc:
            page_width = page.rect.width
            mid_x = page_width / 2

            # 1. Get all text blocks and sort them by vertical position, then horizontal
            blocks = page.get_text("dict")["blocks"]
            sorted_blocks = sorted(blocks, key=lambda b: (b['bbox'][1], b['bbox'][0]))

            # 2. Filter and process blocks
            current_problem_num = 0
            current_problem_text = ""

            for block in sorted_blocks:
                block_text = " ".join(
                    span["text"] for line in block.get("lines", []) for span in line.get("spans", [])
                ).strip()

                if not block_text:
                    continue

                # Check if the block is a new problem number
                match = re.match(r"^(\d+)\.\s*", block_text)
                if match:
                    # If we were building a problem, save it first
                    if current_problem_num > 0 and current_problem_text:
                        problems.append({
                            "problem_number": current_problem_num,
                            "problem_text": clean_text(current_problem_text)
                        })

                    # Start new problem
                    current_problem_num = int(match.group(1))
                    # Remove the number itself from the text
                    current_problem_text = re.sub(r"^(\d+)\.\s*", "", block_text).strip()
                elif current_problem_num > 0:
                    # Append text to the current problem, ignoring answer blanks
                    if "___" not in block_text:
                        current_problem_text += " " + block_text
            
            # Add the last problem from the page
            if current_problem_num > 0 and current_problem_text:
                problems.append({
                    "problem_number": current_problem_num,
                    "problem_text": clean_text(current_problem_text)
                })

        # Post-process to merge problems that were split across columns/pages
        merged_problems = {}
        for p in sorted(problems, key=lambda x: x['problem_number']):
            num = p['problem_number']
            if num not in merged_problems:
                merged_problems[num] = {"problem_number": num, "problem_text": ""}
            merged_problems[num]['problem_text'] += " " + p['problem_text']

        final_list = [v for v in merged_problems.values()]
        for p in final_list:
            p['problem_text'] = clean_text(p['problem_text'])

        return final_list
