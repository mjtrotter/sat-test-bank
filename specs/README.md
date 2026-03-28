# Specs Index — Gifted Adaptive Trainer

> Project working name: **Gifted Adaptive Trainer** (repo: `sat-test-bank`, pending rename)
> Last verified: 2026-03-28 via discovery session (Mark Trotter, 6 batches)

## Spec Files

| File | Status | Coverage |
|------|--------|----------|
| [business.md](business.md) | **Verified** | Purpose, users, MVP, success criteria |
| [architecture.md](architecture.md) | **Verified** | Infrastructure, inference pipeline, app stack |
| [ux.md](ux.md) | **Verified** | Progression model, UI principles, gamification |
| [data-model.md](data-model.md) | **Verified** | Problem taxonomy, student data, explanation pipeline |
| [constraints.md](constraints.md) | **Verified** | Compliance, anti-patterns, hard rules |
| [GAPS.md](GAPS.md) | **Active** | Known unknowns — blocking and non-blocking |

## Discovery Session Summary

Six interrogation batches covering business purpose, data sources, teaching methodology, architecture, UX, and constraints. Mark responded via voice messages throughout. Core architecture reached saturation at Batch 5; Batch 6 confirmed and added feature-level detail.

### Key Architectural Decisions
1. **One app, three verticals** — Math Competition, SAT, Writing/AP as modes within a single app
2. **Retrieval vs inference split** — Math/SAT/AP are retrieval at runtime (pre-generated explanations); writing is real-time inference on novel student content
3. **Explanation pipeline** — Mark seeds ~8 recordings per skill cluster; AI style-transfers to entire database; student ratings close the quality loop
4. **Native iOS** — App Store distribution, PencilKit for work capture, school-managed iPads
5. **Self-hosted inference** — EPYC 7532 + MI50 cluster (ROCm), primarily for batch generation + writing feedback
