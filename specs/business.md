# Business Spec — Gifted Adaptive Trainer
> Last verified: 2026-03-28 via discovery session

## Verified (Gold Standard)

### Problem Statement
- Mark coaches gifted students (grades 6-8) for math competitions (MATHCOUNTS, AMC, Mu Alpha Theta) at a private school where he is also an administrator
- In a single room he has 6th, 7th, and 8th graders with huge content gaps between them — impossible to give each student individualized attention at the right level simultaneously
- Existing tools (AoPS/Alcumus, Khan Academy, MathDash) either do adaptive problem selection without work analysis, or provide lessons without real mastery progression
- **Source:** "Mark, discovery session 2026-03-28"

### Core Value Proposition
- AI-driven adaptive training that analyzes student work and delivers feedback in Mark's teaching voice and style
- The differentiator is NOT problem selection (solved) — it's the explanation quality, teaching persona, and work analysis
- **Source:** "Mark, discovery session 2026-03-28"

### Users
- **Primary:** ~30 gifted students, grades 6-8, at Mark's private school
- **Secondary:** Mark himself (coach dashboard, progress monitoring, group rotation)
- Students access via school-managed iPads through the App Store
- **Source:** "Mark, discovery session 2026-03-28"

### Use Cases
1. **Independent practice** — Students work on their own when Mark isn't present
2. **In-class rotation** — Mark works with a group while others use the app independently
3. **Enrichment** — Students who finish regular classwork use the app for challenge problems (with teacher permission)
4. **Competition prep** — Targeted practice before chapter/state/national competitions
- **Source:** "Mark, discovery session 2026-03-28"

### Three Verticals (One App)
1. **Math Competitions** — MATHCOUNTS, AMC 8/10/12, AIME, Mu Alpha Theta (primary, deepest archive, launch vertical)
2. **SAT** — Math + Evidence-Based Reading/Writing (College Board PDFs with existing content strand IDs)
3. **Writing / AP** — AP Lang, AP Lit, SAT essay, GRE writing for advanced students (scaffolded exercises + real-time inference feedback)
- All three share the same core adaptive engine; they differ in content structure and feedback modality
- **Source:** "Mark, discovery session 2026-03-28"

### MVP Definition
- **MVP vertical:** Math Competitions (deepest archive, most urgent coaching need)
- **MVP features:** Problem ingestion, classification, ELO-gated progression with lesson scaffolding, adaptive practice, pre-generated explanations in Mark's style, student ratings on explanations
- **Deferred to later phases:** Apple Pencil work analysis, voice clone/TTS, writing vertical real-time inference, advanced mini-games
- **Source:** "Mark, discovery session 2026-03-28"

### Success Criteria
- Students can independently practice at their appropriate level without Mark's direct attention
- Explanation quality rated 4+ out of 5 by students on average
- Measurable ELO progression over a competition season
- Mark can monitor progress and assign targeted work via coach dashboard
- **Source:** inferred from discovery conversation, not explicitly stated — needs Mark's confirmation

## Assumed (Needs Verification)
- The app will not be distributed beyond Mark's school in the initial phase
- No monetization planned initially — this is a personal teaching tool
- Timeline is flexible; quality of the explanation pipeline matters more than speed to market

## Open Questions
- Does Mark want a formal coach dashboard with assignment capability, or is passive progress monitoring sufficient for MVP?
- Are there specific competition dates driving the timeline (e.g., MATHCOUNTS chapter in Nov/Dec)?
