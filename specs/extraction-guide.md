# MATHCOUNTS Extraction Guide — For Agent Delegation

## What's Done

The extraction pipeline at `src/extraction/` handles **2002-2013 chapter/state PDFs** (24 levels, 1,152 problems). These are native digital PDFs with clean text extraction via PyMuPDF.

## What's Left

Two categories of PDFs still need extraction:

### 1. National-Level PDFs (2002-2013)
- **Count:** 12 answer keys × (sprint + target + team) = ~576 problems
- **Problem:** These are scanned documents. PyMuPDF text extraction produces garbled OCR output.
- **Answer key format:** Answers are inline with numbered items (e.g., "14. 560 (gallons)") rather than spatial blank+value pairs.
- **Example (2012 national answer key):**
  ```
  Sprint Round Answers
  21
  11. 4 integers
  . 14.4 inches
  4
  66 degrees
  ```
- The numbers, answers, and units are interleaved with no consistent spatial structure.

### 2. Pre-2002 PDFs (1990-2001, all levels)
- **Count:** 12 years × 3 levels × 48 problems = ~1,728 problems
- **Problem:** All scanned with poor OCR quality. Text has artifacts like "MAT!-{COUNTS", "depreoiates", "($)4,32O".
- **Answer keys** use a different layout — answers are inline or in a dense grid without underscore blanks.

## How the Current Pipeline Works

### Architecture

```
src/extraction/
├── __main__.py        # CLI entry point
├── pipeline.py        # Orchestrator — walks dirs, classifies files, merges results
├── answer_parser.py   # Parses answer key PDFs using word-level spatial analysis
├── question_parser.py # Parses question PDFs by round type (sprint/target/team)
└── image_extractor.py # Extracts embedded images, associates with problems
```

### Key Design Decisions

1. **Word-level extraction** (`page.get_text("words")`) gives `(x, y, text)` for each word. This is MUCH better than block-level or full-text extraction for spatial analysis.

2. **Problem markers** are "N." words followed by underscore blanks within 80px horizontally and 5px vertically. This distinguishes actual problem numbers from "N." appearing in math text.

3. **Answer matching** finds the answer value word that sits 15-160px to the right of and 0-30px above a numbered blank. Fractions (stacked numerator/denominator at same x) are detected and joined with "/".

4. **Text collection** gathers all words in the y-range between consecutive markers, filtering out blanks, marker numbers, and boilerplate.

### PDF Directory Structure

```
~/Downloads/MathCounts Tests/
└── {year}/              # 1990-2013
    └── {level}/         # chapter, state, national
        ├── sprint *.pdf  # 30 questions
        ├── target *.pdf  # 8 questions (4 pairs)
        ├── team *.pdf    # 10 questions
        ├── answers *.pdf # Answer key (covers all rounds)
        └── solutions *.pdf  # Worked solutions (2002+ only, 28 total)
```

### Round Structure (Always Consistent)
- **Sprint:** 30 questions, 40 minutes, no calculator
- **Target:** 8 questions in 4 pairs (2 per page), 6 minutes per pair
- **Team:** 10 questions, 20 minutes, team collaboration

### What Makes National/Pre-2002 Different

| Aspect | Chapter/State 2002+ | National / Pre-2002 |
|--------|-------------------|-------------------|
| PDF type | Native digital | Scanned + OCR |
| Text quality | Clean unicode | Garbled artifacts |
| Answer format | Spatial blank + value | Inline "N. answer (unit)" |
| Blank pattern | "N. ________________" | No underscores |
| Word positions | Precise | Approximate |

## Strategy for Remaining PDFs

### Approach A: Better OCR (Recommended for Pre-2002)

Re-OCR the scanned PDFs with a modern OCR engine (Tesseract 5 or Apple's Vision framework) to get clean text, then run the existing spatial parser.

```python
# Using Apple Vision framework (macOS)
import subprocess
def reocr_pdf(input_path, output_path):
    # Convert PDF pages to images, run Vision OCR, reconstruct
    ...
```

### Approach B: Inline Answer Parser (For National-Level)

Write a parser that handles the inline format where answers appear as "N. answer_value (unit)":

```python
import re

def parse_inline_answers(text: str) -> dict:
    """
    Parse answer text in format: "N. answer_value (unit)"
    National PDFs don't use spatial blanks.
    """
    answers = {}
    # Find section headers
    sections = re.split(r'(Sprint|Target|Team)\s+Round', text, flags=re.I)

    for section in sections:
        # Match "N." followed by answer value
        for match in re.finditer(r'(\d+)\.\s*([^\n]+?)(?:\s*\([^)]+\))?\s*$', section, re.M):
            num = int(match.group(1))
            answer = match.group(2).strip()
            if answer and len(answer) < 30:
                answers[num] = answer

    return answers
```

### Approach C: Known-Answer Validation

MATHCOUNTS answers are publicly available for many years. Use a reference answer set to validate extraction:
1. Extract what you can from the OCR text
2. Cross-reference against known answers (AoPS wiki, MATHCOUNTS archives)
3. Flag mismatches for manual review

## Output Format

Each extracted problem should match this schema (from `src/models/tables.py`):

```json
{
  "contest_family": "mathcounts",
  "contest_year": 2012,
  "contest_round": "sprint",       // sprint, target, team
  "contest_level": "chapter",      // chapter, state, national
  "problem_number": 1,
  "problem_text": "Mrs. Smith teaches for 5½ hours each day...",
  "answer": "33",
  "source_path": "/path/to/pdf",
  "figure_paths": []               // list of extracted image paths
}
```

Output goes to `data/extracted/{year}_{level}.json`.

## Testing

After extraction, validate:
1. **Count check:** Sprint = 30, Target = 8, Team = 10
2. **Answer coverage:** Every question should have an answer
3. **Text quality:** No merged problems, no solutions in question text, no garbled artifacts
4. **Spot check:** Print 3 random problems and verify manually
