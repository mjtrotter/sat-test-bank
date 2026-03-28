# Content Extraction Pipeline — Vanguard Adaptive Trainer
> Version: 2.0 | 2026-03-28 (Rev 2: added SAT/ACT/AP pipelines)

## Overview

Six source types, six pipelines, one unified problem database. Estimated total: **33,000-38,000 problems**.

| Source | Count | Format | Pipeline | Priority |
|--------|-------|--------|----------|----------|
| MATHCOUNTS Tests | 315 PDFs (1990-2013) | Standardized test format | Deterministic (regex + layout) | MVP (Week 1) |
| Textbooks | 11 PDFs (AoPS, Gelfand, Batterson) | Chapter-structured books | Hybrid (Marker + Math OCR + LLM) | MVP (Week 2-4) |
| AMC/AIME (AoPS Wiki) | ~4,200 problems | Structured HTML + LaTeX | Web scrape | MVP (Week 1-2) |
| SAT (College Board) | ~4,000-6,000 problems | Standardized test PDF | Deterministic + CB metadata | Phase 2 (Week 2-3) |
| ACT | ~1,500-3,000 problems | Standardized test PDF | Deterministic | Phase 2 (Week 2-3) |
| AP (Calc/Stats/English) | ~4,000-5,000 problems | Test PDF + free-response | Hybrid + multi-part parsing | Phase 3 (Week 4-5) |

## Pipeline 1: MATHCOUNTS Tests (Deterministic)

### Source Material
- 315 PDFs in `~/Downloads/MathCounts Tests/`
- Organized: year / level / round
- Years: 1990-2013
- Levels: School, Chapter, State, National
- Rounds: Sprint, Target, Team, Countdown
- Solutions available for Chapter and State levels
- Clean quality (not scanned, native PDF text)

### Strategy
These are the most regular sources. Standardized layout means deterministic extraction.

### Pipeline Steps

```
1. PDF → Text (PyMuPDF native extraction)
2. Metadata extraction (year, level, round from filename/path)
3. Question segmentation (regex: numbered items 1-30+)
4. Answer key extraction (separate page, mapped by number)
5. Solution extraction (where available, mapped by number)
6. Math notation normalization → LaTeX
7. Figure detection + cropping (if any)
8. Output: structured JSON per problem
```

### Segmentation Heuristics
- Sprint Round: 30 questions, numbered 1-30, no figures typically
- Target Round: 8 questions (4 pairs), numbered 1-8, may have figures
- Team Round: 10 questions, numbered 1-10
- Countdown Round: varies

### Output Schema (per problem)
```json
{
  "id": "MC_2010_STATE_SPRINT_17",
  "source": "mathcounts",
  "year": 2010,
  "level": "state",
  "round": "sprint",
  "number": 17,
  "problem_text": "If the sum of...",
  "problem_latex": "If the sum of $n$ consecutive...",
  "answer": "42",
  "answer_type": "numeric",
  "solution_text": null,
  "solution_latex": null,
  "figures": [],
  "skill_tags": [],
  "difficulty_band": null,
  "raw_page": 3,
  "extraction_confidence": 0.95
}
```

### Tools
- **PyMuPDF** — native text extraction (fast, accurate for non-scanned PDFs)
- **pdfplumber** — fallback for layout-sensitive pages (tables, columns)
- **Texify** — math notation OCR if any pages have image-based equations
- **regex** — question segmentation, answer key parsing

### Estimated Yield
- 315 PDFs × ~30 problems avg = ~9,450 problems
- With answer keys: ~70% have answers
- With solutions: ~40% have full solutions

---

## Pipeline 2: Textbooks (Hybrid)

### Source Material
| Book | Pages (est.) | Content Type |
|------|-------------|--------------|
| Batterson: Competition Math for Middle School | ~400 | Lessons + exercises + solutions |
| AoPS: Introduction to Algebra | ~600 | Lessons + examples + exercises |
| AoPS: Intermediate Algebra | ~700 | Lessons + examples + exercises |
| AoPS: Introduction to Geometry | ~550 | Lessons + examples + exercises + diagrams |
| AoPS: Precalculus | ~500 | Lessons + examples + exercises |
| Gelfand: Algebra | ~250 | Exposition + problems |
| Gelfand: Functions & Graphs | ~150 | Exposition + problems |
| Gelfand: Geometry | ~200 | Exposition + problems + diagrams |
| Gelfand: Method of Coordinates | ~150 | Exposition + problems |
| Gelfand: Trigonometry | ~200 | Exposition + problems |
| MATHCOUNTS Primary Text | ~300 | Lessons + practice sets |

**Total: ~4,000 pages**

### Strategy
Textbooks mix exposition, worked examples, and exercises. Need a multi-stage pipeline that classifies content type before extracting problems.

### Pipeline Steps

```
1. PDF → Page Images (PyMuPDF, 300 DPI)
2. Native text extraction (PyMuPDF — use when PDF has embedded text)
3. Layout segmentation (Marker/MinerU — headings, paragraphs, figures, equations)
4. Page-type classification (LLM classifier):
   - LESSON: exposition, definitions, theorems
   - EXAMPLE: worked example with solution
   - EXERCISE: practice problem (may or may not have solution)
   - SOLUTION: answer to a previous exercise
   - MIXED: page has multiple types (split further)
5. Math OCR on equation regions (Texify for open-source, Mathpix fallback for hard pages)
6. Problem segmentation within EXERCISE pages
7. Example segmentation within EXAMPLE pages
8. Solution-to-problem linking (by number, proximity, chapter reference)
9. Figure extraction + linking (PDFFigures2 for bounding boxes)
10. Metadata enrichment (chapter, section, book, topic from heading hierarchy)
11. Skill tagging (from chapter → taxonomy mapping + LLM classification)
12. Human review queue for low-confidence extractions
```

### Content-Type Classification Heuristics

| Type | Signals |
|------|---------|
| **Lesson** | Long paragraphs, "Definition:", "Theorem:", section headings, no problem numbering |
| **Example** | "Example N:", "Solution:", stepwise derivation, bold/callout formatting |
| **Exercise** | Sequential numbered items, instruction verbs ("Find", "Prove", "Compute", "Determine"), short items |
| **Solution** | "Solution to N:", answer-first patterns, references to problem numbers |

### Source-to-Taxonomy Mapping

Pre-built chapter → skill_node mapping (from taxonomy.md source mapping column):

```
Batterson Chapter 1.1 → [ALG_L1_EXPR_SUBST, ALG_L1_EXPR_DISTRIB, ALG_L1_WORD_TRANSLATE]
Batterson Chapter 2.7 → [COUNT_L2_COMB_BASIC, COUNT_L2_COMB_GRID, COUNT_L2_COMB_COMPLEMENT]
AoPS Algebra I ch10-11 → [ALG_L2_QUAD_FACTOR, ALG_L2_QUAD_FORMULA, ALG_L2_QUAD_COMPLETE]
...
```

This chapter-level mapping provides initial tags; LLM classification refines per-problem.

### Figure Handling (Geometry-Critical)
1. PDFFigures2 extracts bounding boxes + captions
2. Crop each figure as a separate PNG
3. Link to nearest problem by spatial proximity + numbering
4. Store figure as a problem attachment (not inline — the iOS app renders separately)
5. For geometry diagrams with labels: OCR the labels, store as structured metadata

### Output Schema (per problem)
```json
{
  "id": "AOPS_ALG1_CH10_EX_23",
  "source": "textbook",
  "book": "aops_algebra_1",
  "chapter": 10,
  "section": "10.3",
  "content_type": "exercise",
  "problem_text": "Factor completely: x^4 - 16",
  "problem_latex": "Factor completely: $x^4 - 16$",
  "answer": "(x^2+4)(x+2)(x-2)",
  "answer_latex": "$(x^2+4)(x+2)(x-2)$",
  "solution_text": null,
  "solution_latex": null,
  "figures": [],
  "skill_tags": ["ALG_L2_QUAD_FACTOR", "ALG_L3_FACTOR_DIFF_SQUARES"],
  "difficulty_band": null,
  "page": 287,
  "extraction_confidence": 0.85
}
```

### Estimated Yield
- ~4,000 pages total
- ~30% are exercise pages → ~1,200 exercise pages
- ~8 problems per exercise page → ~9,600 problems
- Plus ~3,000 worked examples (valuable as lesson material)

---

## Pipeline 3: AMC/AIME from AoPS Wiki (Web Scrape)

### Source Material
AoPS Wiki hosts complete problem + solution archives:
- **AMC 8:** 2000-present (~25 problems/year × 24 years = ~600)
- **AMC 10:** 2000-present, A and B variants (~25 problems/year × 2 × 24 = ~1,200)
- **AMC 12:** 2000-present, A and B variants (~25 problems/year × 2 × 24 = ~1,200)
- **AIME:** 1983-present, I and II (~15 problems/year × 2 × 40+ = ~1,200)

**Total: ~4,200 problems with full solutions**

### Strategy
AoPS Wiki is structured HTML with LaTeX math. This is the cleanest source by far — no OCR needed.

### Pipeline Steps

```
1. Index all contest pages (known URL pattern: artofproblemsolving.com/wiki/index.php/YYYY_AMC_NN_Problems)
2. For each contest page:
   a. Parse problem list (numbered, LaTeX in <math> tags or $...$)
   b. Extract each problem + answer
   c. Follow link to individual problem page for full solution(s)
3. Parse solution page:
   a. Often has multiple solution approaches
   b. Extract all solutions with LaTeX preserved
4. Extract metadata: contest, year, problem number, difficulty (AoPS has community difficulty ratings)
5. Figure extraction: AoPS problems with diagrams have inline images — download and link
6. Skill tagging from problem content + AoPS's own topic categorization
```

### URL Patterns
```
Problems: https://artofproblemsolving.com/wiki/index.php/{YEAR}_AMC_{8|10|12}{A|B}_Problems
Individual: https://artofproblemsolving.com/wiki/index.php/{YEAR}_AMC_{8|10|12}{A|B}_Problems/Problem_{N}
AIME: https://artofproblemsolving.com/wiki/index.php/{YEAR}_AIME_{I|II}_Problems
```

### Output Schema
```json
{
  "id": "AMC10A_2020_15",
  "source": "aops_wiki",
  "contest": "AMC 10A",
  "year": 2020,
  "number": 15,
  "problem_text": "...",
  "problem_latex": "...",
  "answer": "B",
  "answer_choices": ["A) 12", "B) 15", "C) 18", "D) 21", "E) 24"],
  "solutions": [
    {"approach": "Solution 1", "text": "...", "latex": "..."},
    {"approach": "Solution 2 (bash)", "text": "...", "latex": "..."}
  ],
  "figures": ["AMC10A_2020_15_fig1.png"],
  "skill_tags": ["GEO_L2_CIRCLE_INSCRIBED", "ALG_L1_SYSTEM_SUBST"],
  "difficulty_band": 4,
  "aops_difficulty_rating": 3.5,
  "extraction_confidence": 0.98
}
```

### Estimated Yield
- ~4,200 problems, all with answers
- ~90%+ with at least one full solution
- ~40% with multiple solution approaches
- Community difficulty ratings available for most

### Legal Note
AoPS Wiki content is community-contributed. AMC problems are copyrighted by MAA. For a non-commercial school tool used by ~30 students, this falls under fair use for educational purposes. Worth confirming if the app ever goes commercial.

---

## Pipeline 4: SAT (College Board PDFs + Bluebook)

### Source Material
- College Board released practice tests (8+ full tests, free)
- Khan Academy / College Board partnership content (structured)
- Mark's existing SAT PDFs (~3,000-5,000 problems per data-model.md)
- **College Board already assigns content strand IDs** — these map directly to skill nodes

### Strategy
SAT has a well-defined structure: Reading & Writing (54 questions, modular) and Math (44 questions, 2 modules). Questions already have College Board difficulty levels (1-3) and content domain tags.

### Pipeline Steps

```
1. PDF → Text (PyMuPDF — CB practice tests are native PDF, not scanned)
2. Section/module segmentation (Reading & Writing Module 1/2, Math Module 1/2)
3. Question extraction (numbered, MC with 4 choices or student-produced response)
4. Answer key mapping (separate answer document)
5. CB content domain → Vanguard skill node mapping
6. CB difficulty (1-3) → initial difficulty prior (mapped to internal rating scale)
7. Passage extraction for R&W questions (link passage to question)
8. Figure/graph extraction for data-interpretation questions
```

### Content Domains (College Board's own taxonomy)

**Math:**
- Algebra (linear equations, systems, functions) — ~35%
- Advanced Math (quadratics, polynomials, exponentials) — ~35%
- Problem Solving & Data Analysis (ratios, percentages, statistics) — ~15%
- Geometry & Trigonometry — ~15%

**Reading & Writing:**
- Craft and Structure
- Information and Ideas
- Standard English Conventions
- Expression of Ideas

### Output Schema
```json
{
  "id": "SAT_PRACTICE4_MATH_M1_12",
  "source": "sat",
  "test_name": "Practice Test 4",
  "section": "math",
  "module": 1,
  "number": 12,
  "problem_text": "...",
  "problem_latex": "...",
  "answer": "B",
  "answer_choices": ["A) 3", "B) 5", "C) 7", "D) 9"],
  "answer_type": "multiple_choice",
  "passage_id": null,
  "cb_content_domain": "Advanced Math",
  "cb_difficulty": 2,
  "skill_tags": ["ALG_L2_QUAD_FACT"],
  "figures": [],
  "extraction_confidence": 0.95
}
```

### Estimated Yield
- 8+ practice tests × 98 questions = ~784 official CB problems
- Mark's existing PDFs: ~3,000-5,000 additional
- Total SAT: ~4,000-6,000 problems

---

## Pipeline 5: ACT

### Source Material
- Released ACT practice tests (publicly available)
- ACT prep book PDFs (if Mark has them)
- ACT has: English (75 Qs), Math (60 Qs), Reading (40 Qs), Science (40 Qs)

### Strategy
ACT Math overlaps heavily with SAT Math + competition math. English/Reading/Science are separate verticals. Math extraction is high priority; other sections are Phase 2+.

### Pipeline Steps

```
1. PDF → Text (PyMuPDF)
2. Section segmentation (English, Math, Reading, Science)
3. Question extraction (all MC, 5 choices for Math, 4 for others)
4. Answer key mapping
5. ACT content area → Vanguard skill node mapping
6. Figure/graph extraction (especially Science section)
```

### ACT Math Content Areas
- Pre-Algebra (~20-25%)
- Elementary Algebra (~15-20%)
- Intermediate Algebra (~15-20%)
- Coordinate Geometry (~15-20%)
- Plane Geometry (~20-25%)
- Trigonometry (~5-10%)

### Output Schema
```json
{
  "id": "ACT_2023_MATH_42",
  "source": "act",
  "test_name": "ACT 2023 Released",
  "section": "math",
  "number": 42,
  "problem_text": "...",
  "problem_latex": "...",
  "answer": "K",
  "answer_choices": ["F) ...", "G) ...", "H) ...", "J) ...", "K) ..."],
  "answer_type": "multiple_choice",
  "act_content_area": "Intermediate Algebra",
  "skill_tags": ["ALG_L2_FUNC_COMP"],
  "figures": [],
  "extraction_confidence": 0.92
}
```

### Estimated Yield
- ~5-10 released tests × 60 math questions = ~300-600 math problems
- Other sections: ~500-1,000 per section if extracted
- Total ACT: ~1,500-3,000 problems (math-focused initially)

---

## Pipeline 6: AP (Advanced Placement)

### Source Material
- Released AP exams (College Board publishes free-response questions annually)
- AP prep books (Barron's, Princeton Review, etc. if Mark has PDFs)
- Primary targets: AP Calculus AB/BC, AP Statistics, AP English Language/Composition

### Strategy
AP problems are different from MC competitions — they include free-response, multi-part questions, and essay prompts. The Writing/AP vertical needs these for Phase 3 of the app.

**AP Math (Calc/Stats):** Extract MC + free-response separately. Free-response needs multi-part answer handling.

**AP English:** Extract prompts + rubrics. These feed the Writing vertical's real-time inference pipeline (different from the retrieval-based math pipeline).

### Pipeline Steps

```
1. PDF → Text (PyMuPDF or Marker for complex formatting)
2. Section segmentation (MC vs free-response)
3. MC extraction: same as SAT pipeline
4. Free-response extraction:
   a. Multi-part question parsing (parts a, b, c, d)
   b. Rubric/scoring guideline extraction (where available)
   c. Sample response extraction (where available)
5. AP topic → Vanguard skill node mapping (will need AP-specific skill nodes in taxonomy)
6. Essay prompt extraction (AP English) → stored as writing_prompts table, not problems
```

### Output Schema (MC)
```json
{
  "id": "AP_CALCBC_2022_MC_18",
  "source": "ap",
  "exam": "AP Calculus BC",
  "year": 2022,
  "section": "multiple_choice",
  "number": 18,
  "problem_text": "...",
  "problem_latex": "...",
  "answer": "C",
  "answer_choices": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
  "skill_tags": [],
  "figures": [],
  "extraction_confidence": 0.90
}
```

### Output Schema (Free Response)
```json
{
  "id": "AP_CALCBC_2022_FRQ_3",
  "source": "ap",
  "exam": "AP Calculus BC",
  "year": 2022,
  "section": "free_response",
  "number": 3,
  "problem_text": "...",
  "problem_latex": "...",
  "parts": [
    {"part": "a", "prompt": "...", "points": 2, "sample_answer": "..."},
    {"part": "b", "prompt": "...", "points": 3, "sample_answer": "..."},
    {"part": "c", "prompt": "...", "points": 4, "sample_answer": "..."}
  ],
  "rubric": "...",
  "skill_tags": [],
  "figures": [],
  "extraction_confidence": 0.85
}
```

### Estimated Yield
- AP Calc AB/BC: ~20 years × ~50 questions/year = ~1,000 problems
- AP Statistics: ~20 years × ~40 questions/year = ~800 problems
- AP English: ~20 years × 3 prompts/year = ~60 essay prompts
- Prep books: ~2,000-3,000 additional practice problems
- Total AP: ~4,000-5,000 problems + ~60 writing prompts

---

## Unified Problem Database

All six pipelines feed into one unified schema:

```sql
CREATE TABLE problems (
    id TEXT PRIMARY KEY,                -- e.g., 'MC_2010_STATE_SPRINT_17'
    source TEXT NOT NULL,               -- 'mathcounts', 'textbook', 'aops_wiki', 'sat', 'act', 'ap'

    -- Source metadata
    source_detail JSONB,                -- contest/book/chapter specifics

    -- Problem content
    problem_text TEXT NOT NULL,          -- plain text
    problem_latex TEXT,                  -- LaTeX-formatted
    problem_html TEXT,                   -- rendered HTML (for display)

    -- Answer
    answer TEXT,
    answer_latex TEXT,
    answer_type TEXT,                    -- 'numeric', 'multiple_choice', 'proof', 'expression'
    answer_choices JSONB,               -- for MC questions

    -- Solutions
    solutions JSONB,                    -- array of {approach, text, latex}

    -- Figures
    figures JSONB,                      -- array of {filename, caption, type}

    -- Classification
    primary_skill TEXT REFERENCES skill_nodes(id),
    secondary_skills TEXT[],
    domain TEXT NOT NULL,
    level INTEGER,                       -- 1-6 (maps to taxonomy levels)

    -- Difficulty (from rating-system.md)
    difficulty_rating REAL DEFAULT 1500.0,
    difficulty_RD REAL DEFAULT 300.0,
    mini_model_solve_rate REAL,
    expert_difficulty INTEGER,           -- Mark's 1-6 rating

    -- Pipeline metadata
    extraction_confidence REAL,
    extraction_pipeline TEXT,            -- 'deterministic', 'hybrid', 'web_scrape', 'sat', 'act', 'ap'
    needs_review BOOLEAN DEFAULT FALSE,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE skill_nodes (
    id TEXT PRIMARY KEY,                 -- e.g., 'COUNT_L2_COMB_GRID'
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT NOT NULL,
    level INTEGER NOT NULL,
    prerequisites TEXT[],                -- array of skill_node IDs
    source_mapping TEXT[],               -- textbook chapter references
    problem_count INTEGER DEFAULT 0      -- updated after extraction
);

CREATE TABLE problem_figures (
    id SERIAL PRIMARY KEY,
    problem_id TEXT REFERENCES problems(id),
    filename TEXT NOT NULL,
    caption TEXT,
    figure_type TEXT,                    -- 'geometry_diagram', 'graph', 'table', 'number_line'
    width INTEGER,
    height INTEGER,
    ocr_labels JSONB                    -- extracted text labels from the figure
);
```

## Execution Plan

### Phase 1: MATHCOUNTS Tests (Week 1)
- Highest volume, most standardized, lowest risk
- Build the deterministic pipeline
- Extract ~9,450 problems
- Validate on 10 sample PDFs across different years/levels

### Phase 2: AoPS Wiki Scrape (Week 1-2, parallel)
- Clean structured HTML, no OCR
- Build scraper with rate limiting (respect AoPS servers)
- Extract ~4,200 problems with solutions
- These come pre-tagged with difficulty — excellent calibration data

### Phase 3: Textbook Extraction (Week 2-4)
- Most complex pipeline
- Start with Batterson (best structured, middle school competition math = MVP content)
- Then AoPS Algebra I (most problems, well-structured)
- Then remaining books in priority order
- Iterate on classification accuracy with human review

### Phase 4: SAT/ACT Extraction (Week 2-3, parallel with textbooks)
- SAT PDFs: deterministic pipeline (similar to MATHCOUNTS — standardized format)
- ACT PDFs: same approach
- CB content strand IDs → Vanguard skill node mapping
- ACT content areas → skill node mapping

### Phase 5: AP Extraction (Week 4-5)
- AP released exams (free-response needs special handling)
- Multi-part question parsing
- Essay prompt extraction → separate `writing_prompts` table for Writing vertical
- Prep book extraction follows textbook pipeline

### Phase 6: Tagging & Difficulty Calibration (Week 4-6)
- Map all extracted problems to atomic skill nodes
- Run mini-model difficulty calibration (Phase 3 from rating-system.md)
- Mark reviews sample of ~200 problems for expert difficulty ratings
- Cross-validate: do model ratings correlate with expert ratings?

### Total Estimated Yield

| Source | Problems | With Solutions | With Figures |
|--------|----------|---------------|-------------|
| MATHCOUNTS Tests | ~9,450 | ~3,800 | ~500 |
| AoPS Wiki (AMC/AIME) | ~4,200 | ~3,800 | ~1,000 |
| Textbooks (11 PDFs) | ~9,600 | ~5,000 | ~2,000 |
| SAT (CB + Mark's PDFs) | ~4,000-6,000 | ~1,000 | ~800 |
| ACT | ~1,500-3,000 | ~500 | ~400 |
| AP (Calc/Stats/English) | ~4,000-5,000 | ~2,000 | ~500 |
| **Total** | **~33,000-38,000** | **~16,000** | **~5,200** |

Plus ~3,000 worked examples from textbooks (lesson material, not practice items).
Plus ~60 AP English essay prompts (Writing vertical).

## Hardware Assignment

All development runs on M3 Ultra Mac Studio. EPYC+MI50 server is not yet built — will be the production deployment target.

| Task | Hardware | Why |
|------|----------|-----|
| PDF text extraction (PyMuPDF) | M3 Ultra | CPU-bound, fast |
| Marker/MinerU layout segmentation | M3 Ultra | GPU-accelerated on Apple Silicon |
| Math OCR (Texify) | M3 Ultra (MLX) | Runs well on Apple Silicon |
| LLM content classification | M3 Ultra (MLX) | Local inference, batch |
| Mini-model difficulty calibration | M3 Ultra | 10 models × 256GB unified memory |
| AoPS web scraping | M3 Ultra | Network-bound |
| Bayesian IRT fitting | M3 Ultra (dev) → EPYC + MI50 (prod) | Heavy computation, periodic batch |
| Explanation generation | M3 Ultra (MLX, dev) → EPYC + MI50 (ROCm, prod) | Model TBD |
