"""
MATHCOUNTS extraction pipeline.

Walks the PDF directory, classifies files, extracts questions + answers + images,
and outputs structured JSON per year/level. Focuses on 2002-2013 chapter/state
(native digital PDFs with clean text extraction).

Usage:
    python -m src.extraction [pdf_dir] [--output-dir data/extracted/]
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional

from src.extraction.answer_parser import parse_answer_key
from src.extraction.question_parser import parse_questions
from src.extraction.image_extractor import extract_images


ROUND_TYPES = ["sprint", "target", "team"]
EXPECTED_COUNTS = {"sprint": 30, "target": 8, "team": 10}

# Years with clean digital PDFs (not scanned/OCR)
CLEAN_YEARS = range(2002, 2014)
CLEAN_LEVELS = ["chapter", "state"]


def classify_files(dirpath: str) -> Dict[str, Optional[str]]:
    """
    Classify PDF files in a directory by type.
    Returns: {sprint: path, target: path, team: path, answers: path, solutions: path}
    """
    result = {k: None for k in ROUND_TYPES + ["answers", "solutions"]}
    for f in os.listdir(dirpath):
        if not f.endswith(".pdf"):
            continue
        name_lower = f.lower()
        for key in result:
            if name_lower.startswith(key):
                result[key] = os.path.join(dirpath, f)
                break
    return result


def process_level(
    year: int,
    level: str,
    dirpath: str,
    output_dir: str,
    image_dir: str,
) -> Dict:
    """
    Process all rounds for a single year/level.
    Returns stats dict.
    """
    files = classify_files(dirpath)
    stats = {
        "year": year,
        "level": level,
        "problems_extracted": 0,
        "answers_matched": 0,
        "images_extracted": 0,
        "issues": [],
    }

    # Parse answers first (from the answer key PDF)
    all_answers = {"sprint": {}, "target": {}, "team": {}}
    if files["answers"]:
        try:
            all_answers = parse_answer_key(files["answers"])
        except Exception as e:
            stats["issues"].append(f"answer key parse error: {e}")

    # Process each round type
    all_problems = []
    for rtype in ROUND_TYPES:
        if not files[rtype]:
            stats["issues"].append(f"missing {rtype} PDF")
            continue

        # Extract questions
        try:
            questions = parse_questions(files[rtype], rtype)
        except Exception as e:
            stats["issues"].append(f"{rtype} parse error: {e}")
            continue

        expected = EXPECTED_COUNTS[rtype]
        if len(questions) != expected:
            stats["issues"].append(f"{rtype}: got {len(questions)}/{expected} questions")

        # Extract images
        figures = []
        img_subdir = os.path.join(image_dir, f"{year}", f"{level}", rtype)
        try:
            # Pass problem markers for image-to-problem association
            markers = [{"num": q["problem_number"], "page": q["page"], "y": 0} for q in questions]
            figures = extract_images(files[rtype], img_subdir, markers)
            stats["images_extracted"] += len(figures)
        except Exception as e:
            stats["issues"].append(f"{rtype} image extraction error: {e}")

        # Build figure lookup
        fig_lookup = {}
        for fig in figures:
            num = fig["problem_number"]
            if num not in fig_lookup:
                fig_lookup[num] = []
            fig_lookup[num].append(fig["image_path"])

        # Merge questions with answers and figures
        answers = all_answers.get(rtype, {})
        for q in questions:
            num = q["problem_number"]
            problem = {
                "contest_family": "mathcounts",
                "contest_year": year,
                "contest_round": rtype,
                "contest_level": level,
                "problem_number": num,
                "problem_text": q["problem_text"],
                "answer": answers.get(num),
                "source_path": files[rtype],
                "figure_paths": fig_lookup.get(num, []),
            }
            all_problems.append(problem)
            stats["problems_extracted"] += 1
            if answers.get(num):
                stats["answers_matched"] += 1

    # Write output JSON
    if all_problems:
        out_path = os.path.join(output_dir, f"{year}_{level}.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(all_problems, f, indent=2)

    return stats


def run_pipeline(
    pdf_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    image_dir: Optional[str] = None,
    years: Optional[range] = None,
    levels: Optional[List[str]] = None,
):
    """
    Run the full extraction pipeline.
    """
    pdf_dir = pdf_dir or os.path.expanduser("~/Downloads/MathCounts Tests/")
    output_dir = output_dir or os.path.join(os.path.dirname(__file__), "../../data/extracted/")
    image_dir = image_dir or os.path.join(os.path.dirname(__file__), "../../data/figures/")
    years = years or CLEAN_YEARS
    levels = levels or CLEAN_LEVELS

    output_dir = os.path.abspath(output_dir)
    image_dir = os.path.abspath(image_dir)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    print(f"MATHCOUNTS Extraction Pipeline")
    print(f"  PDF source: {pdf_dir}")
    print(f"  Output: {output_dir}")
    print(f"  Years: {min(years)}-{max(years)}")
    print(f"  Levels: {', '.join(levels)}")
    print("=" * 60)

    total_stats = {
        "levels_processed": 0,
        "levels_perfect": 0,
        "total_problems": 0,
        "total_answers": 0,
        "total_images": 0,
        "all_issues": [],
    }

    all_extracted = []

    for year in years:
        for level in levels:
            dirpath = os.path.join(pdf_dir, str(year), level)
            if not os.path.isdir(dirpath):
                continue

            stats = process_level(year, level, dirpath, output_dir, image_dir)
            total_stats["levels_processed"] += 1
            total_stats["total_problems"] += stats["problems_extracted"]
            total_stats["total_answers"] += stats["answers_matched"]
            total_stats["total_images"] += stats["images_extracted"]

            is_perfect = (
                stats["problems_extracted"] == 48  # 30+8+10
                and not stats["issues"]
            )
            if is_perfect:
                total_stats["levels_perfect"] += 1

            status = "✓" if is_perfect else "~"
            answer_pct = (
                f"{stats['answers_matched']}/{stats['problems_extracted']}"
                if stats["problems_extracted"] > 0
                else "0/0"
            )
            print(f"  {status} {year}/{level}: {stats['problems_extracted']} problems, "
                  f"{answer_pct} answers, {stats['images_extracted']} images")

            if stats["issues"]:
                for iss in stats["issues"]:
                    print(f"      ⚠ {iss}")
                    total_stats["all_issues"].append(f"{year}/{level}: {iss}")

            # Load extracted problems for spot-check
            out_path = os.path.join(output_dir, f"{year}_{level}.json")
            if os.path.exists(out_path):
                with open(out_path) as f:
                    all_extracted.extend(json.load(f))

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print(f"  Levels: {total_stats['levels_perfect']}/{total_stats['levels_processed']} perfect")
    print(f"  Problems: {total_stats['total_problems']}")
    print(f"  Answers matched: {total_stats['total_answers']}")
    print(f"  Images: {total_stats['total_images']}")
    print(f"  Issues: {len(total_stats['all_issues'])}")

    # Spot-check: print 3 random problems
    if all_extracted:
        print("\n--- SPOT CHECK (3 random problems) ---")
        samples = random.sample(all_extracted, min(3, len(all_extracted)))
        for s in samples:
            print(f"\n  [{s['contest_year']} {s['contest_level']} {s['contest_round']} #{s['problem_number']}]")
            text = s["problem_text"][:150]
            print(f"  Q: {text}{'...' if len(s['problem_text']) > 150 else ''}")
            print(f"  A: {s['answer']}")
            if s.get("figure_paths"):
                print(f"  Figures: {len(s['figure_paths'])}")

    return total_stats
