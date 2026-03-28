# Rating System Spec — Vanguard Adaptive Trainer
> Version: 2.0 | 2026-03-28 (Rev 2: skill-tree progression replaces competition-band system)

## Architecture Decision

**Glicko-2** for online updates + **Bayesian IRT** for periodic offline recalibration.

Not plain ELO. The uncertainty parameter (rating deviation) is critical for:
- 30 students with sparse/irregular practice patterns
- 300-500+ skill nodes (most will have few observations per student)
- Cold-start on both students and items

## Scale

### Internal Model Scale
- **Center:** 1500 (new student default)
- **Range:** 400–2800
- **Rating deviation (RD):** starts at 350 (max uncertainty), decays toward 50 with activity

### Student-Facing Progression: Skill Tree (NOT competition bands)

The student does NOT see a single rating or broad band. Progression is **per-skill-node**:

Each of the 528 atomic skill nodes has a mastery state visible to the student:

| State | Internal Criteria | Visual |
|-------|------------------|--------|
| **Locked** | Prerequisites not met | Greyed out node |
| **Available** | Prerequisites met, not yet attempted | Visible, unstarted |
| **Lesson** | Node selected, lesson not completed | Lesson content shown |
| **Practicing** | Lesson done, rating uncertain (RD > 150) | Progress ring filling |
| **Proficient** | Node rating ≥ proficiency threshold AND RD < 150 | Solid fill |
| **Mastered** | Node rating ≥ mastery threshold AND RD < 100 AND 7+ day retention confirmed | Gold/complete indicator |

**Proficiency threshold per node:** `node_base_rating + 200` (i.e., rating exceeds the node's difficulty center by enough to demonstrate competence)

**Mastery threshold per node:** `node_base_rating + 350` AND confirmed via spaced review (prevents cramming without retention)

This gives students **528 individual goals** — each skill node is a lesson to learn and a challenge to master. Far more granular than 6 broad bands. Progress is visible at every session.

### Coach Dashboard View

The coach sees:
- Per-student skill tree with mastery states color-coded
- Domain-level aggregate ratings (internal Glicko-2 numbers)
- Global rating and percentile within the cohort
- Heatmap of class-wide weak spots (which nodes have lowest proficiency rates)
- Competition-readiness flags are derived but secondary: "12 students are AIME-track in algebra" is inferred from the skill tree, not displayed as a band

### Lesson Embedding

Every skill node has an associated lesson. The student's path through the skill tree is:

```
Node unlocks (prerequisites met)
  → Student watches/reads lesson for that node
  → Lesson completion flagged
  → Practice problems served at node difficulty
  → Rating converges (RD drops)
  → Proficiency reached → next nodes unlock
  → Spaced review confirms retention → Mastery
```

This means the taxonomy IS the curriculum. 528 nodes = 528 lessons = 528 progression goals.

## Multi-Dimensional Structure

Three tiers of rating, all maintained simultaneously:

```
Global Rating (1 per student)
  └── Domain Ratings (6 per student: Counting, Algebra, NT, Geometry, Arith, Logic)
       └── Skill Node Ratings (300-500+ per student, sparse — only populated after exposure)
```

### Update Rules

When a student answers a problem tagged with skills `[S1, S2]` in domain `D`:

1. **Skill node update:** Each tagged skill gets a Glicko-2 update weighted by tag strength (primary skill = 1.0, secondary = 0.5)
2. **Domain update:** Domain `D` rating updated as weighted aggregate of its child skill nodes (weighted by 1/RD — more certain nodes contribute more)
3. **Global update:** Global rating = weighted aggregate of domain ratings (same 1/RD weighting)

### Glicko-2 Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `tau` (volatility constant) | 0.5 | Controls how much volatility can change per period. Lower = more stable. |
| `initial_rating` | 1500 | All new students and items |
| `initial_RD` | 350 | Maximum uncertainty |
| `initial_volatility` | 0.06 | Standard starting volatility |
| `RD_floor` | 50 | Minimum RD (never fully certain) |
| `RD_ceiling` | 350 | Resets to this after prolonged inactivity |
| `inactivity_period` | 14 days | After this, RD starts increasing toward ceiling |
| `rating_period` | 1 day | How often Glicko-2 batch processes (can also do real-time approximation) |

### Effective K-Factor (Emergent)

Glicko-2 doesn't use a fixed K-factor — the update magnitude is driven by RD. But the effective behavior is:

| Student State | RD Range | Effective K Equivalent |
|---------------|----------|----------------------|
| Brand new | 300-350 | ~40-48 (fast convergence) |
| Few sessions | 150-300 | ~20-40 (learning quickly) |
| Established | 75-150 | ~8-20 (stable, small adjustments) |
| Very stable | 50-75 | ~4-8 (almost locked in) |
| Returning after break | 150-250 (RD increased) | ~15-30 (reopened for learning) |

## Item (Problem) Difficulty Model

Each problem also has a Glicko-2-style rating:

| Field | Description |
|-------|-------------|
| `difficulty_rating` | Internal scale, same 400-2800 range |
| `difficulty_RD` | Uncertainty — high for new/unvalidated items |
| `difficulty_volatility` | How much difficulty estimate changes |
| `solve_rate` | Empirical: fraction of attempts that are correct |
| `discrimination` | IRT `a` parameter: how well the item separates ability levels |
| `guessing` | IRT `c` parameter: probability of correct guess (0.25 for 4-choice MC) |

### Item Difficulty Calibration (Cold Start)

Three-phase bootstrapping, in order of precedence:

**Phase 1: Expert Priors (Mark)**
- Mark rates each problem 1-6 (maps to mastery bands)
- This is the initial difficulty_rating with high RD (250+)
- Fastest, most reliable at small scale

**Phase 2: Content Heuristics (Automated)**
Feature-based difficulty estimation:
- Number of concepts required (from skill tags)
- Computation steps
- Prerequisite depth (how deep in the skill tree)
- Problem length (words)
- Diagram complexity
- Solution length (if available)

These refine the expert prior, reduce RD slightly.

**Phase 3: Mini-Model Solve Rate (Empirical)**
Run 10 sub-1B parameter models against each problem:
- Candidates: Phi-3.5-mini, Qwen2.5-0.5B/1.5B, SmolLM-1.7B, Gemma-2B, TinyLlama, etc.
- Each model gets 1 attempt per problem (temperature=0, CoT prompting)
- Solve rate maps to difficulty band:

| Models Correct | Estimated Band | Approximate Rating |
|---------------|---------------|-------------------|
| 10/10 | 1 (Foundations) | 400-900 |
| 8-9/10 | 2 (Competitor) | 900-1200 |
| 5-7/10 | 3 (Contender) | 1200-1500 |
| 2-4/10 | 4 (Elite) | 1500-1800 |
| 1/10 | 5 (Master) | 1800-2100 |
| 0/10 | 6 (Grandmaster) | 2100+ |

This runs in batch on the M3 Ultra (all 10 models fit in 256GB unified memory).

**Phase 4: Live Student Data (Ongoing)**
Once students use the app, Glicko-2 updates on items converge toward true difficulty. Bayesian IRT recalibration runs weekly to re-anchor.

## Bayesian IRT Recalibration (Offline)

Weekly batch job (M3 Ultra during dev, EPYC+MI50 in production when server is built):

1. Export all student response logs
2. Fit a 3PL IRT model (difficulty, discrimination, guessing) across all items
3. Compare IRT difficulty estimates to current Glicko-2 item ratings
4. Where they diverge significantly (>200 rating points), flag for review
5. Gradually re-anchor item ratings toward IRT estimates (damped, not instant)
6. Update discrimination and guessing parameters
7. Re-estimate student ability parameters and compare to Glicko-2 student ratings

This prevents drift and catches items whose difficulty was miscalibrated at cold start.

## Skill-Tree-Gated Progression

Students unlock nodes based on **prerequisite mastery**, not domain-level rating gates:

```
To unlock skill node N:
  - ALL prerequisite nodes listed in taxonomy-atomic.md must be Proficient or Mastered
  - If node has no prerequisites, it is available immediately (L1 foundation nodes)
```

### Anti-Gaming

The RD requirement on each node prevents gaming:
- Can't reach Proficient on a node by getting lucky on 2-3 problems — need enough attempts to drive RD below 150
- Can't reach Mastered without 7+ day spaced review confirmation
- Prerequisites are hard gates — no skipping ahead without demonstrated competence

### Diagnostic Fast-Track

The initial diagnostic can fast-track students past nodes they've clearly mastered:
- If a student answers L2+ problems correctly during diagnostic, the system infers proficiency on their L1 prerequisites
- This prevents gifted students from grinding through 100+ trivial foundation nodes
- Fast-tracked nodes get Proficient status with moderate RD (~120) — they'll be spot-checked during spaced review

## Data Schema

```sql
-- Student ratings (one row per student per skill node)
CREATE TABLE student_ratings (
    student_id UUID REFERENCES students(id),
    skill_node_id TEXT NOT NULL,         -- e.g., 'COMB_GRID_PATHS'
    domain TEXT NOT NULL,                -- e.g., 'counting'
    rating REAL DEFAULT 1500.0,
    rating_deviation REAL DEFAULT 350.0,
    volatility REAL DEFAULT 0.06,
    last_updated TIMESTAMP,
    total_attempts INTEGER DEFAULT 0,
    PRIMARY KEY (student_id, skill_node_id)
);

-- Domain-level aggregated ratings
CREATE TABLE student_domain_ratings (
    student_id UUID REFERENCES students(id),
    domain TEXT NOT NULL,
    rating REAL DEFAULT 1500.0,
    rating_deviation REAL DEFAULT 350.0,
    volatility REAL DEFAULT 0.06,
    last_updated TIMESTAMP,
    PRIMARY KEY (student_id, domain)
);

-- Global student rating
CREATE TABLE student_global_ratings (
    student_id UUID REFERENCES students(id) PRIMARY KEY,
    rating REAL DEFAULT 1500.0,
    rating_deviation REAL DEFAULT 350.0,
    volatility REAL DEFAULT 0.06,
    nodes_proficient INTEGER DEFAULT 0,
    nodes_mastered INTEGER DEFAULT 0,
    last_updated TIMESTAMP
);

-- Item difficulty ratings
CREATE TABLE item_ratings (
    item_id UUID REFERENCES problems(id) PRIMARY KEY,
    difficulty_rating REAL DEFAULT 1500.0,
    difficulty_RD REAL DEFAULT 300.0,
    difficulty_volatility REAL DEFAULT 0.06,
    solve_rate REAL,
    discrimination REAL DEFAULT 1.0,     -- IRT 'a' parameter
    guessing REAL DEFAULT 0.25,          -- IRT 'c' parameter
    calibration_source TEXT,             -- 'expert', 'heuristic', 'model', 'student_data'
    mini_model_solve_rate REAL,          -- from Phase 3 calibration
    total_attempts INTEGER DEFAULT 0,
    last_calibrated TIMESTAMP
);
```

## Adaptive Problem Selection

When selecting the next problem for a student in domain D:

1. Get student's domain rating R and RD
2. **If RD > 200 (high uncertainty):** select problems near R to reduce uncertainty fast
3. **If RD < 200 (established):** select problems at R + 50 to R + 150 (slight stretch, ~60-70% expected success rate)
4. Filter to skill nodes the student hasn't mastered (node rating < gate for next level)
5. Prefer items with low difficulty_RD (well-calibrated problems)
6. Avoid items attempted in the last 7 days (spaced repetition integration)
7. Mix in 20% "review" items from mastered skills (prevent regression)

Target success rate: **65-75%** — the sweet spot for learning (challenging but not discouraging).
