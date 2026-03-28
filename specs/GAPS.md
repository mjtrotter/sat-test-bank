# Gifted Adaptive Trainer — Known Unknowns

## Blocking (Must resolve before architect session)

- [x] **Granular skill taxonomy** — resolved 2026-03-28: Draft taxonomy synthesized from 11 source textbook TOCs. 6 primary domains with Level 1-3 progressions defined for Counting/Probability, Algebra, Number Theory, and Geometry. See `specs/taxonomy.md`. Will refine during ingestion as natural clustering emerges.
- [ ] **ROCm model selection** — Which LLM runs on the MI50s for explanation generation? Must fit in 64GB combined MI50 VRAM (or split across MI50 + M3 Ultra MLX). Mark is open to fine-tuning. Needs benchmarking — the style-transfer task is constrained (adapt official solution using Mark's teaching patterns), so a smaller fine-tuned model may outperform a larger general one.

## Non-Blocking (Can resolve during implementation)

- [ ] **ELO K-factor calibration** — Standard chess ELO as starting point, but K-factor for new students and educational context needs tuning. Fallback: start with K=32 for new students, K=16 for established.
- [ ] **Diagnostic test composition** — Fixed set or adaptive? Fallback: fixed 50-question diagnostic covering all domains at mixed difficulty.
- [ ] **Mini-game visual design** — Simon Tatham's puzzle collection confirmed as the game engine base (open source, MIT license, ~40 puzzle types). Needs a "massive facelift" for the UI to match the app's minimalist modern aesthetic.
- [ ] **Offline sync strategy** — "Daily practice set" concept is clear but sync conflict resolution needs design. Fallback: offline is read-only (download set, work, sync answers on reconnect).
- [ ] **Problem set books handling** — AoPS series (5 books) + Gelfand series (5 books) + Mathcounts Primary Text available. Treat as lesson material, individual problems, or both? Fallback: extract problems individually, tag book chapters as lesson references.
- [ ] **IP/fair use assessment** — Are competition problems usable in a non-commercial school tool? Likely yes for personal educational use but worth confirming.
- [ ] **Coach dashboard scope** — Passive monitoring vs. active assignment. Fallback: passive monitoring for MVP, assignment capability in v2.
- [ ] **Writing vertical specifics** — Scaffolded exercises, AP/SAT/GRE prompts, but the feedback model and exercise progression need design. Deferred to Phase 3.
- [ ] **Voice clone vs. pre-recorded vs. text-only** — The personality slider suggests AI-generated text explanations (with tone variation) for MVP, with voice as a later enhancement. Needs confirmation.
- [ ] **Cold-start problem** — New student with no data: how does the adaptive engine select initial problems before the diagnostic is complete?

## Resolved

- [x] **UI direction** — resolved 2026-03-28: Minimalist, modern, professional. "More cerebral side of games/competition — marketing to chess players, not gamers." No reference app provided but clear aesthetic direction established.
- [x] **Recording workflow tooling** — resolved 2026-03-28: Notability confirmed. Mark will record however is best for ingestion.
- [x] **Mini-game puzzle source** — resolved 2026-03-28: Simon Tatham's Portable Puzzle Collection (https://www.chiark.greenend.org.uk/~sgtatham/puzzles/). Open source, ~40 puzzle types. Games need visual redesign to match app aesthetic.
- [x] **Problem archive availability** — resolved 2026-03-28: 315 PDFs in Downloads/MathCounts Tests/ (1990-2013, organized year/level/round, clean quality). 11 PDF textbooks in Downloads/Math Texts/ (AoPS series, Gelfand series, MATHCOUNTS Primary Text). Solutions available for chapter and state levels.
- [x] **Additional compute** — resolved 2026-03-28: M3 Ultra Mac also available. Can run MLX models for supplementary inference or ingestion pipeline.
