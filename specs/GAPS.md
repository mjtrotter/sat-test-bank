# Gifted Adaptive Trainer — Known Unknowns

## Blocking (Must resolve before architect session)

- [x] **Granular skill taxonomy** — resolved 2026-03-28: Draft taxonomy synthesized from 11 source textbook TOCs. 6 primary domains with Level 1-3 progressions. See `specs/taxonomy.md`. **Atomic decomposition in progress** — expanding to 300-500+ ratable nodes with Level 4-5 extension for AIME/olympiad. See `specs/taxonomy-atomic.md`.
- [x] **Rating system design** — resolved 2026-03-28: Glicko-2 (not plain ELO) + Bayesian IRT recalibration. Scale 400-2800, 6 mastery bands, multi-dimensional (global → domain → skill node). Cold-start via expert priors + content heuristics + mini-model solve-rate calibration. See `specs/rating-system.md`.
- [x] **Content extraction pipeline** — resolved 2026-03-28: Three pipelines designed — deterministic for MATHCOUNTS, hybrid (Marker + Math OCR + LLM) for textbooks, web scrape for AMC/AIME from AoPS wiki. Estimated yield: ~23,250 problems. See `specs/extraction-pipeline.md`.
- [ ] **ROCm model selection** — Which LLM runs on the MI50s for explanation generation? Must fit in 64GB combined MI50 VRAM (or split across MI50 + M3 Ultra MLX). Mark is open to fine-tuning. Needs benchmarking — the style-transfer task is constrained (adapt official solution using Mark's teaching patterns), so a smaller fine-tuned model may outperform a larger general one.

## Non-Blocking (Can resolve during implementation)

- [x] **ELO K-factor calibration** — resolved 2026-03-28: Glicko-2 makes this moot — update magnitude is driven by rating deviation (RD), not a fixed K. Effective K: ~40-48 for new students, ~4-8 for established. See `specs/rating-system.md`.
- [ ] **Diagnostic test composition** — Fixed set or adaptive? Fallback: fixed 50-question diagnostic covering all domains at mixed difficulty.
- [ ] **Mini-game visual design** — Simon Tatham's puzzle collection confirmed as the game engine base (open source, MIT license, ~40 puzzle types). Needs a "massive facelift" for the UI to match the app's minimalist modern aesthetic.
- [ ] **Offline sync strategy** — "Daily practice set" concept is clear but sync conflict resolution needs design. Fallback: offline is read-only (download set, work, sync answers on reconnect).
- [x] **Problem set books handling** — resolved 2026-03-28: Both. Extract individual problems for the question bank AND preserve chapter structure as lesson references. Worked examples become lesson material, exercises become practice items. See `specs/extraction-pipeline.md`.
- [ ] **IP/fair use assessment** — Are competition problems usable in a non-commercial school tool? Likely yes for personal educational use but worth confirming.
- [ ] **Coach dashboard scope** — Passive monitoring vs. active assignment. Fallback: passive monitoring for MVP, assignment capability in v2.
- [ ] **Writing vertical specifics** — Scaffolded exercises, AP/SAT/GRE prompts, but the feedback model and exercise progression need design. Deferred to Phase 3.
- [ ] **Voice clone vs. pre-recorded vs. text-only** — The personality slider suggests AI-generated text explanations (with tone variation) for MVP, with voice as a later enhancement. Needs confirmation.
- [x] **Cold-start problem** — resolved 2026-03-28: New students start at rating 1500 with RD=350 (max uncertainty). Glicko-2's high-uncertainty state causes rapid convergence (~15-20 problems to stabilize). Diagnostic selects problems near the student's current rating to reduce RD fast. Item cold-start solved via expert priors + content heuristics + mini-model solve rates. See `specs/rating-system.md`.

## Resolved

- [x] **UI direction** — resolved 2026-03-28: Minimalist, modern, professional. "More cerebral side of games/competition — marketing to chess players, not gamers." No reference app provided but clear aesthetic direction established.
- [x] **Recording workflow tooling** — resolved 2026-03-28: Notability confirmed. Mark will record however is best for ingestion.
- [x] **Mini-game puzzle source** — resolved 2026-03-28: Simon Tatham's Portable Puzzle Collection (https://www.chiark.greenend.org.uk/~sgtatham/puzzles/). Open source, ~40 puzzle types. Games need visual redesign to match app aesthetic.
- [x] **Problem archive availability** — resolved 2026-03-28: 315 PDFs in Downloads/MathCounts Tests/ (1990-2013, organized year/level/round, clean quality). 11 PDF textbooks in Downloads/Math Texts/ (AoPS series, Gelfand series, MATHCOUNTS Primary Text). Solutions available for chapter and state levels.
- [x] **Additional compute** — resolved 2026-03-28: M3 Ultra Mac also available. Can run MLX models for supplementary inference or ingestion pipeline.
