# Architecture Spec — Gifted Adaptive Trainer
> Last verified: 2026-03-28 via discovery session

## Verified (Gold Standard)

### Deployment Target
- **Client:** Native iOS app (Swift/SwiftUI), distributed via App Store
- **Server:** Self-hosted on student-built server — AMD EPYC 7532 processor
- **GPU Cluster A:** 2x AMD MI50 (32GB VRAM each) — primary inference, ROCm
- **GPU Cluster B:** 2x 16GB cards (to be added later) — secondary inference
- **Additional compute:** M3 Ultra Mac — available for MLX inference, ingestion pipeline, or supplementary tasks
- Mark is open to fine-tuning a model for the style-transfer task
- **Source:** "Mark, discovery session 2026-03-28"

### The Retrieval/Inference Split (Critical Architecture Decision)
- **Math Comp / SAT / AP (retrieval at runtime):** All explanations are pre-generated in batch. At runtime, the app checks the student's answer, retrieves the pre-generated explanation, and serves it. Minimal compute required — this is a database lookup + adaptive selection algorithm.
- **Writing (real-time inference):** Student submits novel written content. The server runs real-time LLM inference to generate personalized feedback in Mark's teaching style. This is the only vertical requiring heavy runtime compute.
- **Implication:** The MI50 cluster's primary runtime load is writing feedback. Math/SAT/AP runtime is lightweight. The MI50s are heavily used during batch explanation generation and PDF ingestion, but the live math app could run on modest hardware.
- **Source:** "Mark, discovery session 2026-03-28"

### Adaptive Engine
- **Item selection:** Bayesian IRT targeting ~50% predicted success probability (zone of proximal development)
- **Mastery tracking:** Bayesian Knowledge Tracing (BKT) as supporting signal for skill progression
- **ZPD policy:** Keep most items in 40-70% predicted success range, centered at 50%. Occasional harder "stretch" items to probe transfer and prevent plateauing.
- **Progression:** Chess ELO-style rating system. Students earn ELO through adaptive practice. ELO gates progression between skill levels.
- **Source:** "Mark, discovery session 2026-03-28" (ZPD/50% target), research validation (Bayesian IRT + BKT recommendation)

### Explanation Generation Pipeline
1. **Seed recordings:** Mark records ~3 template explanations + 3-5 edge case explanations per skill cluster (voice + optional sketched diagrams)
2. **Style extraction:** Transcribe recordings, extract Mark's pedagogical patterns (anchor → question → pattern-seek → stress-test), tone, visual approach
3. **Batch generation:** For every problem in the database, AI reads (a) the official solution and (b) Mark's explanation on the nearest template/edge case → generates a "Mark-style" explanation bridging the two
4. **Quality loop:** Students rate explanations 1-5. Low-rated explanations flagged for review. Mark re-records or adjusts → regenerate.
5. **Personality slider:** Explanations can be generated at different "personality temperatures" — from purely helpful to Mark's playful roasting style. Student-controlled opt-in.
- **Source:** "Mark, discovery session 2026-03-28"

### Data Ingestion Pipeline
- **Source format:** PDFs (mostly good quality), some scanned
- **Processing:** Local VL models (MLX-compatible, e.g., Qwen 2.5 VL) for OCR/extraction with review by stronger models
- **Flow:** PDF → VL model extracts problems + solutions (separate documents) → standardized format → classification → storage
- **SAT shortcut:** College Board PDFs already include content strand IDs and standardized formatting
- **Source:** "Mark, discovery session 2026-03-28"

### Client Architecture (iOS)
- **Framework:** SwiftUI + PencilKit (for Apple Pencil work capture in future phases)
- **Distribution:** App Store (school-managed iPads)
- **Offline:** Daily practice set downloaded for offline fallback; syncs when reconnected
- **Networking:** REST API or WebSocket to self-hosted server for adaptive selection, explanation retrieval, and (writing only) real-time inference
- **Source:** "Mark, discovery session 2026-03-28"

### Verified Data Archive

**MathCounts Tests** (in `~/Downloads/MathCounts Tests/`):
- 315 PDFs, organized: `year/level/round.pdf`
- Years: 1990-2013 (24 years)
- Levels: chapter, state, national
- Rounds per level: sprint, target, team, answers, solutions
- Solutions available for chapter (14 years) and state (14 years), NOT national
- PDF quality: clean text, embedded diagrams/charts, consistent layout. VL model ingestion viable.

**Math Texts** (in `~/Downloads/Math Texts/`):
- AoPS series: Algebra I, Algebra II, Basics, Geometry, Precalculus (5 books)
- Gelfand series: Algebra, Functions & Graphs, Geometry, Method of Coordinates, Trigonometry (5 books)
- Mathcounts Primary Text (1 book)
- Total: 11 PDF textbooks — usable as lesson scaffolding material and problem sources

### Recording Workflow
- **Tool:** Notability (iPad) — screen recording captures voice + Apple Pencil ink in one file
- **Process:** Mark views problem + official solution → records voice explanation with optional sketched diagrams → output is a Notability recording (exportable as video or audio + PDF)
- **Source:** "Mark, discovery session 2026-03-28"

## Assumed (Needs Verification)
- ROCm is the right GPU compute stack for MI50s (vs. alternative AMD frameworks)
- Server runs a standard Linux distro (Ubuntu/RHEL) with ROCm drivers
- API server is Python-based (FastAPI or similar) given the ML pipeline
- Student data stored in PostgreSQL or SQLite on the server (not cloud)
- M3 Ultra runs MLX models for supplementary inference and/or ingestion pipeline
- Fine-tuning a smaller model for style-transfer may outperform prompting a larger general model

## Open Questions
- What specific VL model for PDF ingestion? Qwen 2.5 VL is mentioned but may have better options by launch
- What LLM powers the explanation generation? Needs to be ROCm-compatible and fit in 64GB combined MI50 VRAM
- WebSocket vs REST for real-time writing feedback?
- CDN or local caching strategy for pre-generated explanations on the iPad?
