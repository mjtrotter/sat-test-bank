
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.extraction.parser import MathCountsParser
from src.extraction.answer_parser import parse_answer_key

def get_metadata_from_path(path: Path) -> Dict[str, Any]:
    """Extracts contest metadata from the PDF's file path."""
    parts = path.parts
    # Expected structure: .../year/level/round.pdf
    try:
        year = int(parts[-3])
        level = parts[-2].lower()
        round_name = path.stem.lower()
        
        # Clean round name
        if "sprint" in round_name:
            round_type = "sprint"
        elif "target" in round_name:
            round_type = "target"
        elif "team" in round_name:
            round_type = "team"
        elif "countdown" in round_name:
            round_type = "countdown"
        else:
            round_type = "unknown"

        return {
            "contest_year": year,
            "contest_level": level,
            "contest_round": round_type,
            "contest_family": "mathcounts",
        }
    except (IndexError, ValueError) as e:
        print(f"Could not parse metadata from path: {path}. Error: {e}")
        return {}

def find_answer_key_path(problem_pdf_path: Path) -> Optional[Path]:
    """Finds the corresponding answer key PDF for a given problem PDF."""
    directory = problem_pdf_path.parent
    base_name = problem_pdf_path.stem
    
    # Common answer key naming conventions
    possible_names = [
        f"{base_name}_answers.pdf",
        f"{base_name}-answers.pdf",
        "answers.pdf",
        "answer_key.pdf",
    ]
    
    for name in possible_names:
        if (directory / name).exists():
            return directory / name
    
    # Fallback search for any file with 'answers' in the name
    for f in directory.glob("*answer*.pdf"):
        return f

    return None

def process_single_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """Processes a single problem PDF, finds its answers, and returns structured data."""
    print(f"Processing: {pdf_path.name}")
    
    metadata = get_metadata_from_path(pdf_path)
    if not metadata:
        return []

    # 1. Parse problems
    parser = MathCountsParser(str(pdf_path))
    try:
        problems = parser.parse()
    except Exception as e:
        print(f"  ERROR parsing problems from {pdf_path.name}: {e}")
        return []

    # 2. Find and parse answers
    answers = {}
    answer_key_path = find_answer_key_path(pdf_path)
    if answer_key_path:
        print(f"  Found answer key: {answer_key_path.name}")
        try:
            answers = parse_answer_key(str(answer_key_path))
        except Exception as e:
            print(f"  ERROR parsing answers from {answer_key_path.name}: {e}")
    else:
        print("  WARNING: No answer key found.")

    # 3. Combine problems and answers into the final schema
    output_data = []
    for problem in problems:
        problem_num = problem["problem_number"]
        final_problem = {
            "contest_family": metadata.get("contest_family"),
            "contest_year": metadata.get("contest_year"),
            "contest_round": metadata.get("contest_round"),
            "contest_level": metadata.get("contest_level"),
            "problem_number": problem_num,
            "problem_text": problem["problem_text"],
            "answer": answers.get(problem_num),
            "source_path": str(pdf_path),
            # Fields from the model that we don't extract yet
            "official_solution": None,
            "mark_explanation": None,
            "mark_audio_url": None,
            "mark_diagram_url": None,
            "personality_variants": None,
            "explanation_rating": None,
            "explanation_flags": 0,
            "latex_content": None,
            "difficulty_band": None,
            "primary_domain": None,
            "problem_style": None,
        }
        output_data.append(final_problem)
        
    return output_data

def run_pipeline():
    """
    Walks the input directory, processes all MATHCOUNTS PDFs, and outputs structured data.
    """
    input_dir = Path(os.path.expanduser("~/Downloads/MathCounts Tests/"))
    if not input_dir.is_dir():
        print(f"Error: Input directory not found at {input_dir}")
        return

    all_extracted_problems = []
    processed_files = 0
    errors = 0
    
    # Using a sample of 5 PDFs for testing as requested
    pdf_paths = list(input_dir.rglob("*.pdf"))
    sample_paths = [p for p in pdf_paths if 'answer' not in p.name.lower()][:5]

    print(f"Starting pipeline. Processing {len(sample_paths)} sample PDFs...")

    for pdf_path in sample_paths:
        try:
            extracted_data = process_single_pdf(pdf_path)
            if extracted_data:
                all_extracted_problems.extend(extracted_data)
                processed_files += 1
            else:
                errors +=1
        except Exception as e:
            print(f"FATAL ERROR processing {pdf_path.name}: {e}")
            errors += 1

    # Output results
    output_path = Path("/Users/mjtrotter/Desktop/Dev/Vanguard/src/extraction/extraction_results.json")
    with open(output_path, "w") as f:
        json.dump(all_extracted_problems, f, indent=2)

    # Print statistics
    print("\n" + "="*50)
    print("Extraction Pipeline Complete")
    print(f"Total PDFs processed: {processed_files}")
    print(f"Total problems extracted: {len(all_extracted_problems)}")
    print(f"Files with errors: {errors}")
    print(f"Results saved to: {output_path}")
    print("="*50)

if __name__ == "__main__":
    run_pipeline()
