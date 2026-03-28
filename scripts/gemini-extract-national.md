# MATHCOUNTS National PDF Extraction — Gemini Prompt

Run this in terminal:
```bash
cd ~/Desktop/Dev/Vanguard && gemini -m gemini-2.5-pro < scripts/gemini-extract-national.txt
```

## The Prompt (copy to gemini-extract-national.txt)

---

You are extracting math competition problems from MATHCOUNTS National Competition PDFs. These are scanned/semi-scanned PDFs with varying layouts across years.

## Source Location

All PDFs: `~/Downloads/MathCounts Tests/{YEAR}/national/`
Each year has: sprint *.pdf, target *.pdf, team *.pdf, answers *.pdf

## Your Approach

For EACH year, do this:

### Step 1: Convert PDF pages to images
Use PyMuPDF (already installed) to render each page as a 200dpi PNG:

```python
import fitz, os
year = 2008  # change per year
base = os.path.expanduser(f"~/Downloads/MathCounts Tests/{year}/national/")
out = f"/tmp/mc_national_{year}"
os.makedirs(out, exist_ok=True)
for fname in os.listdir(base):
    if not fname.endswith('.pdf'): continue
    prefix = fname.split()[0]
    doc = fitz.open(os.path.join(base, fname))
    for pg in range(len(doc)):
        pix = doc[pg].get_pixmap(dpi=200)
        pix.save(f"{out}/{prefix}_page{pg}.png")
    doc.close()
```

### Step 2: Read each image visually
Use your multimodal vision to read:
- **Question PDFs**: Read problem text from sprint, target, team pages
- **Answer PDF**: Read correct answers from the answer key pages

### Step 3: Match and validate
- Match answers to questions by round and problem number
- **HARD VALIDATION**: Sprint = EXACTLY 30, Target = EXACTLY 8, Team = EXACTLY 10
- Every problem MUST have an answer
- If counts don't match, re-read the images — you missed something

### Step 4: Write output JSON
Write to `~/Desktop/Dev/Vanguard/data/extracted/{YEAR}_national.json`

## Output Schema

```json
[
  {
    "contest_family": "mathcounts",
    "contest_year": 2008,
    "contest_round": "sprint",
    "contest_level": "national",
    "problem_number": 1,
    "problem_text": "The solid below formed by identical cubic blocks can be represented by the accompanying numerical grid...",
    "answer": "16",
    "source_path": "~/Downloads/MathCounts Tests/2008/national/sprint *.pdf",
    "figure_paths": []
  }
]
```

## Answer Formatting Rules

- Numbers: "16", "320000", "2.5"
- Fractions: "1/36", "4/3", "14/3", "70/297" (slash notation)
- Expressions: "2pi-3", "6sqrt(7)", "sqrt(13)"
- Exponents: "5^12"
- Variables: "md/(3n)" (if the answer is algebraic)
- Strip units — just the value (no "cu feet", "ounces", etc.)
- Comma-free numbers: "320000" not "320,000"

## Known Layout Gotchas

1. **Answer keys have NO underscore blanks** in national PDFs. Answers appear inline after "N." markers in multi-column layouts.
2. **Stacked fractions**: Numerator above a line, denominator below. The text extractor will miss these — that's why you must READ THE IMAGES visually.
3. **Countdown Round** appears at the end of the answer key — IGNORE IT. Only extract Sprint, Target, Team.
4. **Cover pages**: First page of each PDF is usually a cover (instructions, honor pledge). Skip it.
5. **Two-column layouts**: Some years have questions in the left half and answer blanks in the right half. The question text is what you want, not the answer blank column.
6. **OCR artifacts**: Pre-2008 PDFs may have garbled text in the extracted text layer. Always trust what you SEE in the image, not what PyMuPDF extracts as text.

## Execution Plan

**TEST BATCH (run first, show me results):**
- Extract 2008 national only
- Print: count per round, 3 sample Q+A per round
- Wait for my review

**FULL RUN (after I approve):**
- Extract all years: 2002-2013 national
- Print summary table: year | sprint_count | target_count | team_count | total_answers
- Flag any year that doesn't hit exact counts

## Quality Checks Per Year

After extracting each year, verify:
1. Sprint has exactly 30 problems with 30 answers
2. Target has exactly 8 problems with 8 answers
3. Team has exactly 10 problems with 10 answers
4. No empty problem_text fields
5. No empty answer fields
6. Print 1 random problem per round as spot check

## Important

- 2013 national has a .txt file for team instead of .pdf — skip it or handle gracefully
- Some years may have slightly different file naming — look for files starting with "sprint", "target", "team", "answers"
- If a year is truly broken (can't extract), log it and move on — don't halt the whole run
