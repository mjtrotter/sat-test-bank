
import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple, Optional
import os
import json

def detect_mathcounts_format(pdf_path: str) -> Optional[Dict]:
    """
    Analyze the first page of a MATHCOUNTS PDF to determine parsing strategy.

    Returns dict with:
    - era: '1990s_early', '1990s_late', '2000s', '2010s'
    - layout: 'single_column' or 'two_column'
    - has_header: bool
    - header_end_y: float (y coordinate where problems start)
    - problem_pattern: regex string for this format
    - round_type: 'sprint', 'target', 'team', 'countdown', 'answers'
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        text = page.get_text("text")
        blocks = page.get_text("dict")["blocks"]

        year_match = re.search(r'(199\d|200\d|201\d)', text)
        year = int(year_match.group(0)) if year_match else 0

        round_type = "unknown"
        if "Answer Key" in text or "answers" in pdf_path.lower():
            round_type = "answers"
        elif "Sprint Round" in text or "sprint" in pdf_path.lower():
            round_type = "sprint"
        elif "Target Round" in text or "target" in pdf_path.lower():
            round_type = "target"
        elif "Team Round" in text or "team" in pdf_path.lower():
            round_type = "team"
        elif "Countdown Round" in text or "countdown" in pdf_path.lower():
            round_type = "countdown"

        era = ""
        layout = "single_column"
        if 1990 <= year < 1995:
            era = "1990s_early"
            layout = "single_column"
        elif 1995 <= year < 2000:
            era = "1990s_late"
            layout = "single_column"
        elif 2000 <= year < 2010:
            era = "2000s"
            if round_type == 'sprint':
                layout = 'two_column'
        elif 2010 <= year < 2014:
            era = "2010s"
            if round_type == 'sprint':
                layout = 'two_column'

        header_end_y = 0
        has_header = False
        problem_pattern = r"^\d+\."

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    span_texts = " ".join([s["text"] for s in line["spans"]])
                    if "DO NOT BEGIN" in span_texts:
                        has_header = True
                        header_end_y = block['bbox'][3]
                        break
                if header_end_y > 0:
                    break
            if header_end_y > 0:
                break

        if not has_header:
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        if any("Name" in s["text"] for s in line["spans"]):
                            has_header = True
                            header_end_y = block['bbox'][3]
                            break
                    if header_end_y > 0:
                        break
                if header_end_y > 0:
                    break

        return {
            "era": era,
            "layout": layout,
            "has_header": has_header,
            "header_end_y": header_end_y,
            "problem_pattern": problem_pattern,
            "round_type": round_type,
            "year": year
        }
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def parse_answer_key(pdf_path: str) -> Dict[int, str]:
    """
    Parse MATHCOUNTS answer key PDF using spatial layout.
    """
    answers = {}
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_width = page.rect.width
            mid_x = page_width / 2
            
            left_col_items = []
            right_col_items = []

            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if not block.get('lines'):
                    continue
                
                line_text = "".join(span["text"] for line in block["lines"] for span in line["spans"]).strip()
                bbox = block['bbox']
                
                # Problem numbers are on the left
                if re.match(r"^\d+\.\s*_{5,}", line_text):
                    if bbox[0] < mid_x:
                        left_col_items.append((bbox[1], line_text))
                # Answers are on the right (or left, need to be flexible)
                elif re.match(r"^\d+\.", line_text) and "___" not in line_text:
                     right_col_items.append((bbox[1], line_text))
                elif block['bbox'][0] > mid_x:
                    right_col_items.append((bbox[1], line_text))


            left_col_items.sort()
            right_col_items.sort()

            used_answers = set()
            if left_col_items and right_col_items:
                for y_left, text_left in left_col_items:
                    problem_num_match = re.match(r"(\d+)\.", text_left)
                    if problem_num_match:
                        num = int(problem_num_match.group(1))
                        
                        best_answer = None
                        min_dist = float('inf')

                        for i, (y_right, text_right) in enumerate(right_col_items):
                            dist = abs(y_right - y_left)
                            if dist < min_dist and i not in used_answers:
                                min_dist = dist
                                best_answer = (i, text_right)

                        if best_answer and min_dist < 20: # y-tolerance
                             used_answers.add(best_answer[0])
                             answers[num] = best_answer[1]
                             
    except Exception as e:
        print(f"Could not parse answer key {pdf_path}: {e}")
        
    return answers


def test_format_detector():
    SAMPLE_FILES = {
        "1990s_early": {
            "sprint": os.path.expanduser("~/Downloads/MathCounts Tests/1992/chapter/sprint 2024-10-28 03_04_26.pdf"),
            "answers": os.path.expanduser("~/Downloads/MathCounts Tests/1992/chapter/answers 2024-10-28 03_04_27.pdf"),
        },
        "1990s_late": {
            "sprint": os.path.expanduser("~/Downloads/MathCounts Tests/1997/chapter/sprint 2024-10-28 03_05_38.pdf"),
            "answers": os.path.expanduser("~/Downloads/MathCounts Tests/1997/chapter/answers 2024-10-28 03_05_38.pdf"),
        },
        "2000s": {
            "sprint": os.path.expanduser("~/Downloads/MathCounts Tests/2002/chapter/sprint 2024-10-28 03_06_16.pdf"),
            "answers": os.path.expanduser("~/Downloads/MathCounts Tests/2002/chapter/answers 2024-10-28 03_06_17.pdf"),
        },
        "2000s_late": {
            "sprint": os.path.expanduser("~/Downloads/MathCounts Tests/2007/chapter/sprint 2024-10-28 03_05_01.pdf"),
            "answers": os.path.expanduser("~/Downloads/MathCounts Tests/2007/chapter/answers 2024-10-28 03_05_02.pdf"),
        },
        "2010s": {
            "sprint": os.path.expanduser("~/Downloads/MathCounts Tests/2012/chapter/sprint 2024-10-28 03_03_51.pdf"),
            "answers": os.path.expanduser("~/Downloads/MathCounts Tests/2012/chapter/answers 2024-10-28 03_03_51.pdf"),
        },
    }

    report_lines = []

    for era, files in SAMPLE_FILES.items():
        print(f"--- Testing Era: {era} ---")
        report_lines.append(f"## Era: {era}")
        report_lines.append("")

        sprint_format = detect_mathcounts_format(files["sprint"])
        print(f"Detected format for {os.path.basename(files['sprint'])}: {sprint_format}")
        report_lines.append(f"### Sprint Format (`{os.path.basename(files['sprint'])}`)")
        report_lines.append("```json")
        report_lines.append(json.dumps(sprint_format, indent=2))
        report_lines.append("```")
        report_lines.append("")

        answers = parse_answer_key(files["answers"])
        print(f"Parsed answers for {os.path.basename(files['answers'])}:")
        report_lines.append(f"### Answer Key Extraction (`{os.path.basename(files['answers'])}`)")
        if answers:
            for num, ans in sorted(answers.items())[:5]:
                print(f"  {num}: {ans}")
                report_lines.append(f"- Problem {num}: {ans}")
        else:
            report_lines.append("No answers extracted.")
        report_lines.append("")

        print("-" * 20)
    
    report_path = os.path.expanduser("~/Desktop/Dev/Vanguard/research/format-detection-report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    test_format_detector()
