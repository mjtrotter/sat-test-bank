# Vanguard — Architect Manifest
> Generated: 2026-03-28 | Status: PENDING REVIEW

## Scope

**MVP: Math Competition Vertical** — adaptive training for MATHCOUNTS / AMC / AIME

Post-MVP (not in this manifest): SAT/ACT/AP extraction, Writing vertical, voice clone, Apple Pencil work analysis

## Architecture Summary

- **Backend:** Python (FastAPI), PostgreSQL, runs on M3 Ultra (dev) → EPYC+MI50 (prod)
- **Frontend:** Native iOS (SwiftUI), App Store, school iPads
- **Rating Engine:** Glicko-2 + Bayesian IRT, multi-dimensional (global → domain → 528 skill nodes)
- **Content:** ~23K problems from 3 MVP sources (MATHCOUNTS PDFs, AoPS wiki, textbooks)
- **Explanations:** Pre-generated in Mark's teaching style, served via retrieval (not runtime inference)

## Hardware

All development on **M3 Ultra Mac Studio** (256GB). EPYC+MI50 server is not built yet.

---

## Task Manifest

### WAVE 1: Data Foundation (all independent — run in parallel)

---

#### Task 1.1: Backend Scaffolding + Database Schema

**Goal:** Set up the Python backend with all database tables from the specs.

**Deliverables:**
- FastAPI project structure (`src/api/`, `src/models/`, `src/services/`, `src/core/`)
- PostgreSQL schema: `problems`, `skill_nodes`, `problem_figures`, `student_ratings`, `student_domain_ratings`, `student_global_ratings`, `item_ratings`, `students` tables (from rating-system.md + extraction-pipeline.md)
- Alembic migrations
- Docker Compose (FastAPI + PostgreSQL)
- Health check endpoint, CORS config
- `.env.example` with all config vars
- Basic test harness (pytest + test DB)

**Context files:** `specs/rating-system.md`, `specs/extraction-pipeline.md`, `specs/data-model.md`, `specs/architecture.md`, `specs/constraints.md`

**Depends on:** nothing

**Executor:** Jules (multi-file scaffolding)

**Estimated size:** 2-3 days

---

#### Task 1.2: Skill Taxonomy Loader

**Goal:** Parse `taxonomy-atomic.md` into the `skill_nodes` database table with full prerequisite graph.

**Deliverables:**
- Parser that reads taxonomy-atomic.md and extracts all 528 skill nodes (ID, name, description, domain, level, prerequisites, source_mapping)
- CLI command: `python -m vanguard.cli load-taxonomy`
- Prerequisite graph validation (no cycles, no orphan references, all prerequisite IDs exist)
- Domain/level summary stats printed after load
- Tests: round-trip parse → DB → query, prerequisite graph integrity

**Context files:** `specs/taxonomy-atomic.md`, `specs/rating-system.md` (skill node schema)

**Depends on:** 1.1 (needs database schema)

**Executor:** Gemini CLI

**Estimated size:** 1 day

---

#### Task 1.3: MATHCOUNTS Extraction Pipeline

**Goal:** Extract ~9,450 problems from 315 MATHCOUNTS PDFs into the problems database.

**Deliverables:**
- PyMuPDF-based text extractor
- Metadata parser: year, level, round from filepath (`year/level/round.pdf`)
- Question segmenter: regex-based, handles Sprint (30 Qs), Target (8 Qs), Team (10 Qs), Countdown
- Answer key extractor: maps answer number → answer value
- Solution extractor (where available)
- Figure detector + cropper (rare in MATHCOUNTS but present in some Target problems)
- Output writer: inserts into `problems` table
- CLI command: `python -m vanguard.cli extract-mathcounts <pdf_dir>`
- Validation: spot-check 10 random PDFs across different years/levels, print extraction stats

**Context files:** `specs/extraction-pipeline.md` (Pipeline 1 section), `specs/architecture.md` (Verified Data Archive section)

**Input data:** `~/Downloads/MathCounts Tests/` (315 PDFs)

**Depends on:** 1.1 (needs database schema)

**Executor:** Jules (multi-file, needs file system access for PDF testing)

**Estimated size:** 2-3 days

---

#### Task 1.4: AoPS Wiki Scraper

**Goal:** Extract ~4,200 AMC 8/10/12 + AIME problems with solutions from Art of Problem Solving wiki.

**Deliverables:**
- Web scraper using `httpx` + `BeautifulSoup` (NOT Playwright — static HTML pages)
- Contest page indexer: generates URLs for all AMC 8 (2000-present), AMC 10A/B (2000-present), AMC 12A/B (2000-present), AIME I/II (1983-present)
- Problem parser: extracts problem text with LaTeX math notation preserved
- Solution parser: follows link to individual problem page, extracts all solution approaches
- AoPS difficulty rating extractor (where available)
- Figure downloader: saves inline images, links to problem
- Rate limiter: max 1 request/second, respectful User-Agent
- Output writer: inserts into `problems` table
- CLI command: `python -m vanguard.cli scrape-aops [--contest AMC10A] [--year 2020]`
- Resume capability: tracks which contests/years have been scraped, skips completed

**Context files:** `specs/extraction-pipeline.md` (Pipeline 3 section)

**Depends on:** 1.1 (needs database schema)

**Executor:** Gemini CLI

**Estimated size:** 2 days

---

### WAVE 2: Core Engine (depends on Wave 1)

---

#### Task 2.1: Glicko-2 Rating Engine

**Goal:** Implement the complete Glicko-2 rating system for students and items.

**Deliverables:**
- `src/services/glicko2.py` — core Glicko-2 algorithm:
  - `update_rating(player_rating, player_RD, player_vol, opponent_rating, opponent_RD, outcome)` → new rating, RD, volatility
  - RD decay with inactivity (increases toward ceiling after 14 days)
  - RD floor (50) and ceiling (350) enforcement
- `src/services/rating_engine.py` — multi-dimensional wrapper:
  - On student answer: update skill node rating(s), recalculate domain aggregate (1/RD weighted), recalculate global aggregate
  - Update item difficulty rating symmetrically
  - Mastery state transitions: Locked → Available → Lesson → Practicing → Proficient → Mastered
  - Prerequisite checking for node unlocks
- Comprehensive tests:
  - Known Glicko-2 test vectors (Glickman's paper examples)
  - Multi-dimensional propagation: answer a problem, verify skill/domain/global all update correctly
  - Mastery state machine: verify correct transitions
  - Edge cases: new student (high RD), returning student (RD inflation), item with no attempts

**Context files:** `specs/rating-system.md` (full spec), `specs/taxonomy-atomic.md` (prerequisite structure)

**Depends on:** 1.1, 1.2

**Executor:** Gemini CLI (algorithmic, well-specified)

**Estimated size:** 2-3 days

---

#### Task 2.2: Adaptive Problem Selection

**Goal:** Given a student's current state, select the optimal next problem.

**Deliverables:**
- `src/services/problem_selector.py`:
  - Input: student_id, optional domain filter, optional skill node filter
  - Algorithm:
    1. Get student's skill node ratings + RDs
    2. If high RD (>200): select problems near current rating (reduce uncertainty)
    3. If established RD (<200): select problems at rating+50 to rating+150 (stretch zone, 65-75% expected success)
    4. Filter: only problems whose skill nodes are Available/Practicing/Proficient for this student
    5. Prefer items with low difficulty_RD (well-calibrated)
    6. Exclude items attempted in last 7 days (spaced repetition)
    7. Mix in 20% review items from Proficient/Mastered nodes
    8. Return ranked list of N candidates
- API endpoint: `GET /api/v1/students/{id}/next-problem?domain=counting&count=5`
- Tests: mock student at various states, verify selection priorities

**Context files:** `specs/rating-system.md` (Adaptive Problem Selection section)

**Depends on:** 1.1, 1.2, 2.1

**Executor:** Gemini CLI

**Estimated size:** 1-2 days

---

#### Task 2.3: Textbook Extraction Pipeline

**Goal:** Extract problems and worked examples from the 11 math textbook PDFs.

**Deliverables:**
- Marker-based layout segmenter: headings, paragraphs, figures, equations
- Content-type classifier (LLM-assisted): LESSON / EXAMPLE / EXERCISE / SOLUTION / MIXED
- Texify integration for math OCR on equation regions
- Chapter → skill node mapping table (from taxonomy source mapping column)
- Problem segmenter within EXERCISE pages
- Worked example segmenter within EXAMPLE pages
- Solution-to-problem linker (by number, proximity, chapter)
- Figure extractor (PDFFigures2 or PyMuPDF bounding boxes)
- CLI command: `python -m vanguard.cli extract-textbook <pdf_path> --book aops_algebra_1`
- Start with Batterson (best structured, MVP core), then AoPS Algebra I
- Human review queue: low-confidence extractions flagged in DB

**Context files:** `specs/extraction-pipeline.md` (Pipeline 2 section), `specs/taxonomy-atomic.md` (source mapping column)

**Input data:** `~/Downloads/Math Texts/` (11 PDFs)

**Depends on:** 1.1, 1.2

**Executor:** Jules (multi-file, needs file system + LLM integration)

**Estimated size:** 4-5 days (most complex pipeline)

---

#### Task 2.4: Problem Skill-Tagging Service

**Goal:** Automatically tag extracted problems with atomic skill node IDs.

**Deliverables:**
- `src/services/skill_tagger.py`:
  - Phase 1: Chapter-based tagging (use source mapping from taxonomy-atomic.md — book + chapter → skill nodes)
  - Phase 2: LLM-assisted refinement (send problem text to local model, get skill node predictions)
  - Phase 3: Confidence scoring (high confidence = auto-tag, low confidence = flag for review)
- Batch tagging CLI: `python -m vanguard.cli tag-problems [--source mathcounts] [--retag]`
- API endpoint: `POST /api/v1/problems/{id}/tags` for manual tag correction
- Dashboard stats: tagged vs untagged vs flagged counts per source

**Context files:** `specs/taxonomy-atomic.md`, `specs/extraction-pipeline.md`

**Depends on:** 1.1, 1.2, 1.3, 1.4

**Executor:** Gemini CLI

**Estimated size:** 2 days

---

### WAVE 3: iOS App (depends on Waves 1-2)

---

#### Task 3.1: iOS App — Core Architecture

**Goal:** SwiftUI project with networking, data models, and navigation structure.

**Deliverables:**
- Xcode project: `VanguardApp/`
- Navigation: TabView with Practice, Skill Tree, Profile, Settings tabs
- Networking layer: `APIClient` class wrapping the FastAPI backend (async/await, Codable models)
- Data models mirroring backend: Student, Problem, SkillNode, Rating, etc.
- Local cache (SwiftData or CoreData) for offline-first
- Auth: simple student ID entry (no passwords for MVP — school iPads, single-user)
- Dark mode support
- Design tokens: colors, typography, spacing following "minimalist, modern, professional" direction

**Context files:** `specs/ux.md`, `specs/constraints.md`, `specs/architecture.md`

**Depends on:** 1.1 (needs API contract)

**Executor:** Jules (multi-file iOS project)

**Estimated size:** 3-4 days

---

#### Task 3.2: iOS App — Problem View + Explanation Display

**Goal:** The core practice loop: see problem → answer → see explanation → rate it.

**Deliverables:**
- Problem display: text + LaTeX rendering (use MathJax via WKWebView or native LaTeX renderer)
- Figure display: images loaded from server, positioned with problem
- Answer input: numeric keypad for competition math, MC selector for SAT-style
- Submit + immediate feedback (correct/incorrect)
- Explanation display: Mark-style explanation with LaTeX, step-by-step
- Explanation rating: thumbs up/down sent to backend
- Session flow: problem → answer → explanation → next problem (smooth, fast)
- Personality slider (just the UI toggle — explanation variants come in Phase 4)

**Context files:** `specs/ux.md` (Explanation Feedback, Personality Slider sections)

**Depends on:** 3.1, 2.2

**Executor:** Jules

**Estimated size:** 3 days

---

#### Task 3.3: iOS App — Skill Tree View

**Goal:** Visual representation of 528 skill nodes with mastery states.

**Deliverables:**
- Skill tree organized by domain (6 domains as sections)
- Within each domain: nodes grouped by level (L1 → L2 → L3 → L4 → L5)
- Node states visually distinct: Locked (grey), Available (outlined), Lesson (book icon), Practicing (progress ring), Proficient (filled), Mastered (gold)
- Tap on Available/Lesson node → enter lesson
- Tap on Practicing/Proficient node → enter practice
- Prerequisite lines connecting nodes (shows dependency flow)
- Domain summary: X/Y nodes proficient, Z mastered
- Overall progress: total nodes proficient/mastered across all domains

**Context files:** `specs/rating-system.md` (Skill Tree Progression section), `specs/taxonomy-atomic.md`

**Depends on:** 3.1, 2.1

**Executor:** Jules

**Estimated size:** 3-4 days

---

#### Task 3.4: Diagnostic Test Flow

**Goal:** Initial placement test that determines starting skill node states.

**Deliverables:**
- Diagnostic screen: sequential problem presentation with progress bar
- Adaptive item selection: starts at L2 difficulty across domains, adjusts based on responses
- Fast-tracking: if student answers L2+ correctly, infer L1 prerequisite proficiency
- Early termination: stop domain testing when placement is confident (RD < threshold)
- ~50-60 questions total (8 per domain × 6 domains, fewer with fast-tracking)
- Results screen: domain placement summary, skill nodes unlocked
- Writes initial ratings to all relevant student_ratings rows

**Context files:** `specs/rating-system.md` (Diagnostic Fast-Track section), `specs/taxonomy-atomic.md` (Diagnostic Coverage Guide)

**Depends on:** 3.1, 2.1, 2.2

**Executor:** Jules

**Estimated size:** 2-3 days

---

### WAVE 4: Content & Polish (depends on Waves 2-3)

---

#### Task 4.1: Mini-Model Difficulty Calibration

**Goal:** Run 10 sub-1B models against all extracted problems to seed difficulty ratings.

**Deliverables:**
- Model runner: loads 10 small models via MLX on M3 Ultra
- Candidate models: Phi-3.5-mini, Qwen2.5-0.5B, Qwen2.5-1.5B, SmolLM-1.7B, Gemma-2B, TinyLlama-1.1B, StableLM-2-1.6B, etc. (benchmark to select final 10)
- Problem formatter: converts problem text into CoT prompt
- Answer extractor: parses model output for numeric/MC answer
- Batch runner: processes all problems, tracks per-model solve rate
- Difficulty mapper: solve_rate → initial difficulty_rating (per rating-system.md table)
- Output: updates `item_ratings.difficulty_rating` and `item_ratings.mini_model_solve_rate` for all problems
- CLI: `python -m vanguard.cli calibrate-difficulty [--models all] [--source mathcounts]`

**Context files:** `specs/rating-system.md` (Mini-Model Solve Rate section)

**Depends on:** 1.3, 1.4, 2.3 (needs extracted problems)

**Executor:** Gemini CLI

**Estimated size:** 2-3 days

---

#### Task 4.2: Lesson Content Framework

**Goal:** Structure for one lesson per skill node, initially seeded from textbook content.

**Deliverables:**
- `lessons` table: skill_node_id, lesson_type (text/video/recording), content (markdown + LaTeX), worked_examples (JSONB), visual_aids (JSONB), mark_recording_url (nullable)
- Lesson template: Definition → Technique → 2-3 Worked Examples → "Try It" practice transition
- Auto-seeder: pulls worked examples from textbook extraction (Task 2.3) and maps to skill nodes
- API endpoints: `GET /api/v1/lessons/{skill_node_id}`, `PUT /api/v1/lessons/{skill_node_id}` (for Mark to edit)
- Placeholder lessons for nodes without textbook content (just the template + skill description)
- Mark can later add recordings per node — pipeline accepts Notability exports

**Context files:** `specs/rating-system.md` (Lesson Embedding section), `specs/architecture.md` (Explanation Pipeline)

**Depends on:** 1.2, 2.3

**Executor:** Gemini CLI

**Estimated size:** 2 days

---

#### Task 4.3: Mini-Games Integration (Simon Tatham)

**Goal:** Embed puzzle games as earned breaks in the practice loop.

**Deliverables:**
- Evaluate Simon Tatham C source → compile for iOS, or find/build SwiftUI equivalents for top 6:
  - Solo (Sudoku), Towers, Pattern (Nonogram), Keen (KenKen), Net, Untangle
- UI facelift: minimalist modern styling matching app aesthetic
- Break trigger system: earned after streaks (5 correct) or milestones (level up)
- 3-minute time-boxed session, progress saves between breaks
- Game selection screen: student picks preferred game
- Settings: enable/disable mini-games

**Context files:** `specs/ux.md` (Mini-Game Breaks section, Simon Tatham section)

**Depends on:** 3.1

**Executor:** Jules (iOS integration)

**Estimated size:** 3-4 days

---

#### Task 4.4: Coach Dashboard

**Goal:** Mark's view for monitoring all students.

**Deliverables:**
- Separate tab or login role in the iOS app (or web-based — TBD)
- Student list: all students with global rating, active/inactive, last session
- Per-student detail: skill tree with mastery states, domain ratings, session history
- Class heatmap: across all students, which skill nodes have lowest proficiency rates
- Assignment capability (stretch): Mark can assign specific skill nodes or problem sets
- Explanation quality monitor: low-rated explanations flagged for review
- API endpoints: `GET /api/v1/coach/students`, `GET /api/v1/coach/heatmap`, `GET /api/v1/coach/flagged-explanations`

**Context files:** `specs/ux.md` (Coach Dashboard), `specs/rating-system.md` (Coach Dashboard View)

**Depends on:** 3.1, 2.1

**Executor:** Jules

**Estimated size:** 2-3 days

---

## Wave Summary

| Wave | Tasks | Parallelizable | Total Duration (est.) |
|------|-------|---------------|----------------------|
| **Wave 1** | 1.1, 1.2, 1.3, 1.4 | 1.1 runs first (1-2d), then 1.2/1.3/1.4 in parallel | 3-4 days |
| **Wave 2** | 2.1, 2.2, 2.3, 2.4 | 2.1 + 2.3 in parallel, then 2.2 + 2.4 | 4-5 days |
| **Wave 3** | 3.1, 3.2, 3.3, 3.4 | 3.1 first, then 3.2/3.3/3.4 in parallel | 5-6 days |
| **Wave 4** | 4.1, 4.2, 4.3, 4.4 | All in parallel | 3-4 days |
| **Total** | 16 tasks | | **~15-19 days** |

## Execution Dependency Graph

```
WAVE 1 (Foundation):
  1.1 ──┬──→ 1.2
        ├──→ 1.3
        └──→ 1.4

WAVE 2 (Engine):
  1.1 + 1.2 ──→ 2.1 ──→ 2.2
  1.1 + 1.2 ──→ 2.3
  1.1 + 1.2 + 1.3 + 1.4 ──→ 2.4

WAVE 3 (iOS):
  1.1 ──→ 3.1 ──┬──→ 3.2 (needs 2.2)
                ├──→ 3.3 (needs 2.1)
                └──→ 3.4 (needs 2.1, 2.2)

WAVE 4 (Content & Polish):
  1.3 + 1.4 + 2.3 ──→ 4.1
  1.2 + 2.3 ──→ 4.2
  3.1 ──→ 4.3
  3.1 + 2.1 ──→ 4.4
```

## Post-MVP Tasks (not in this manifest)

- SAT extraction pipeline (specs/extraction-pipeline.md Pipeline 4)
- ACT extraction pipeline (specs/extraction-pipeline.md Pipeline 5)
- AP extraction pipeline (specs/extraction-pipeline.md Pipeline 6)
- Writing vertical (real-time inference, AP/SAT essay prompts)
- Explanation generation pipeline (Mark's recordings → style extraction → batch generation)
- Personality slider explanation variants
- Voice clone / TTS
- Apple Pencil work capture + analysis
- Offline sync (daily practice set download)
- Bayesian IRT recalibration batch job
- App Store submission + Kids Category compliance
