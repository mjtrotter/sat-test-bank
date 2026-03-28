# Specs Index — Vanguard Adaptive Trainer

> Project: **Vanguard** (repo: `Vanguard/`)
> Last verified: 2026-03-28 via discovery session (Mark Trotter, 6 batches)

## Spec Files

| File | Status | Coverage |
|------|--------|----------|
| [business.md](business.md) | **Verified** | Purpose, users, MVP, success criteria |
| [architecture.md](architecture.md) | **Verified** | Infrastructure, inference pipeline, app stack |
| [ux.md](ux.md) | **Verified** | Progression model, UI principles, gamification |
| [data-model.md](data-model.md) | **Verified** | Problem taxonomy, student data, explanation pipeline |
| [constraints.md](constraints.md) | **Verified** | Compliance, anti-patterns, hard rules |
| [taxonomy.md](taxonomy.md) | **Verified** | 6-domain, 3-level skill taxonomy skeleton (superseded by atomic) |
| [taxonomy-atomic.md](taxonomy-atomic.md) | **In Progress** | 300-500+ atomic ELO-ratable skill nodes, Levels 1-5 |
| [rating-system.md](rating-system.md) | **Verified** | Glicko-2 + Bayesian IRT, scale 400-2800, multi-dimensional |
| [extraction-pipeline.md](extraction-pipeline.md) | **Verified** | 3 pipelines (MATHCOUNTS, textbooks, AoPS wiki), ~23K problems |
| [GAPS.md](GAPS.md) | **Active** | Known unknowns — 1 blocking, 6 non-blocking remain |

## Discovery Session Summary

Six interrogation batches covering business purpose, data sources, teaching methodology, architecture, UX, and constraints. Mark responded via voice messages throughout. Core architecture reached saturation at Batch 5; Batch 6 confirmed and added feature-level detail.

### Key Architectural Decisions
1. **One app, three verticals** — Math Competition, SAT, Writing/AP as modes within a single app
2. **Retrieval vs inference split** — Math/SAT/AP are retrieval at runtime (pre-generated explanations); writing is real-time inference on novel student content
3. **Explanation pipeline** — Mark seeds ~8 recordings per skill cluster; AI style-transfers to entire database; student ratings close the quality loop
4. **Native iOS** — App Store distribution, PencilKit for work capture, school-managed iPads
5. **Self-hosted inference** — EPYC 7532 + MI50 cluster (ROCm), primarily for batch generation + writing feedback
