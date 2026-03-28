# Data Model Spec — Gifted Adaptive Trainer
> Last verified: 2026-03-28 via discovery session

## Verified (Gold Standard)

### Problem Taxonomy (Classification Schema)

Each problem in the database is tagged with:

| Field | Description | Example |
|-------|-------------|---------|
| `contest_family` | Source competition/test | MATHCOUNTS, AMC_8, AMC_10, AMC_12, AIME, MU_ALPHA_THETA, SAT, AP_CALC, AP_LANG |
| `contest_year` | Year of the test | 2008 |
| `contest_round` | Specific round/section | Sprint, Target, Team, Countdown, Individual, etc. |
| `problem_number` | Original problem number | 24 |
| `difficulty_band` | 1-5 scale (AoPS-aligned) | 3 (= harder MATHCOUNTS National / easier AMC 10) |
| `primary_domain` | Top-level math domain | Counting/Probability |
| `secondary_skills` | Granular skill tags (array) | [casework, complementary_counting, inclusion_exclusion] |
| `problem_style` | Type of reasoning required | multi_step_reasoning, trick_insight, visualization, computation |
| `level` | Within-domain progression level | Counting Level 2 |
| `cluster_role` | Role in skill cluster | template, edge_case, practice |
| `elo_value` | Calibrated ELO difficulty | 1450 |

**Difficulty Band Mapping:**
| Band | Typical Level |
|------|--------------|
| 1 | Easy chapter MATHCOUNTS, basic AMC 8 |
| 2 | Hard AMC 8, mid MATHCOUNTS, easy AMC 10 |
| 3 | Hard MATHCOUNTS National, mid AMC 10/12, easiest AIME |
| 4 | Hard AMC 10/12, mid AIME |
| 5 | Hard AIME, olympiad-entry |

**Primary Domains:**
1. Arithmetic / Prealgebra
2. Algebra
3. Geometry
4. Number Theory
5. Counting / Probability
6. Logic / Strategy

**Granular skills (secondary_skills) need further development** — Mark emphasized that "factoring" alone is too broad. Need sub-skills like: quadratic factoring, cubic factoring, quartic factoring, factoring alternative forms, etc. This taxonomy should be built out collaboratively during the ingestion phase.

- **Source:** AoPS framework + "Mark, discovery session 2026-03-28"

### Problem Content

Each problem record contains:
- `problem_text` — The full problem statement (extracted from PDF)
- `answer` — Correct answer (numeric for competition math, multiple choice letter for SAT)
- `official_solution` — The published solution from the test maker
- `mark_explanation` — AI-generated explanation in Mark's teaching style (or direct recording transcript for seed problems)
- `mark_audio_url` — Optional: URL to Mark's recorded audio explanation (for seed problems)
- `mark_diagram_url` — Optional: URL to Mark's sketched diagram
- `visual_solution` — Optional: step-by-step visual solution build (for future phases)
- `explanation_rating` — Aggregate student rating (1-5)
- `explanation_flags` — Count of low ratings triggering review
- `personality_variants` — Pre-generated explanation variants at different roast levels

### Problem Sources and Estimated Counts

| Source | Est. Count | Format | Notes |
|--------|-----------|--------|-------|
| MATHCOUNTS 1990-2012 (chapter/state/national) | ~3,300 | PDF | Sprint (30) + Target (8) + Team (10) per level per year |
| MATHCOUNTS 2012-present (chapter/state) | ~2,100 | PDF | Plus countdown rounds (100-150 per competition) |
| MATHCOUNTS Countdown rounds | ~2,000+ | PDF | Some years only |
| AMC 8/10/12 historical | ~2,000+ | PDF | Well-documented online |
| AIME historical | ~500+ | PDF | |
| Mu Alpha Theta (Florida) | ~3,000+ | Google Drive | 6 subjects × 30 individual + 4 team × multiple events/year |
| SAT (College Board) | 3,000-5,000 | PDF | **Already has content strand IDs** |
| Problem set books (by topic) | ~2,000+ | PDF (books) | Clustered by topic with content explanations |
| AP prep books | ~1,000+ | PDF | Various subjects |
| **Total estimate** | **15,000-25,000+** | | |

- **Source:** "Mark, discovery session 2026-03-28"

### Student Data Model

| Field | Description | Sensitivity |
|-------|-------------|-------------|
| `student_id` | Internal UUID (not name/email) | Low |
| `display_name` | Initials or chosen nickname | Medium — COPPA compliant |
| `grade_level` | 6, 7, or 8 | Low |
| `overall_elo` | Global ELO rating | Low |
| `domain_elos` | ELO per primary domain | Low |
| `skill_levels` | Current level per skill cluster | Low |
| `diagnostic_results` | Baseline test performance | Low |
| `session_history` | Per-session: problems attempted, answers, time spent, ELO changes | Low |
| `explanation_ratings` | Ratings given to explanations | Low |
| `roast_preference` | Personality slider setting (0.0-1.0) | Low |
| `mini_game_preference` | Selected game type | Low |
| `mini_game_state` | Saved progress on active puzzle | Low |

**Data minimization:** No full names, email addresses, photos, voice recordings, location, or unique device identifiers stored. Student identified only by internal UUID + chosen display name.

### Explanation Pipeline Data Flow

```
[Mark's Seed Recordings]
    ↓ transcribe (MLX Whisper)
    ↓ extract pedagogical patterns
[Style Model: Mark's teaching DNA]
    +
[Official Solution per problem]
    +
[Nearest seed explanation (same skill cluster)]
    ↓ LLM generates Mark-style explanation
    ↓ generate personality variants (helpful → roast)
[Pre-generated Explanation Set]
    ↓ stored in database
    ↓ served to students at runtime (retrieval, not inference)
    ↓ student rates (1-5)
    ↓ low ratings flagged → Mark reviews → regenerate
```

## Assumed (Needs Verification)
- PostgreSQL for problem and student data storage (SQLite insufficient for concurrent iOS app + batch jobs)
- Explanation text + audio stored as files with DB references
- The "nearest seed explanation" matching uses the atomic skill node taxonomy

## Resolved (2026-03-28)
- **Rating system:** Glicko-2 replaces plain ELO. Multi-dimensional (global → domain → skill node). See `specs/rating-system.md`.
- **Skill taxonomy:** 300-500+ atomic nodes replace the coarse secondary_skills array. See `specs/taxonomy-atomic.md`.
- **Problem extraction:** 3 pipelines yield ~23K problems. See `specs/extraction-pipeline.md`.
- **Book handling:** Extract individual problems AND preserve chapter structure as lesson references.
- **Cold-start:** Glicko-2 RD=350 drives fast convergence (~15-20 problems). Item cold-start via expert priors + mini-model solve-rates.

## Open Questions
- Should the diagnostic test be a fixed set or adaptively selected?
- Exact PostgreSQL vs managed DB hosting (self-hosted EPYC or cloud?)
