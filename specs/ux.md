# UX Spec — Gifted Adaptive Trainer
> Last verified: 2026-03-28 via discovery session

## Verified (Gold Standard)

### Target User Profile
- Gifted students, grades 6-8 (ages 11-14)
- Technically comfortable (school iPads, Apple Pencil)
- Competitive — respond to ELO systems, leaderboards, peer comparison
- Enjoy Mark's personality, including his playful roasting style
- **Source:** "Mark, discovery session 2026-03-28"

### Progression Model: ELO-Gated Lesson-Practice Hybrid
This is the core UX loop. Each skill domain is organized into levels:

```
Counting Level 1
├── Lesson: techniques + sample problems with Mark's explanations
├── Adaptive Practice: earn ELO by solving problems at ~50% difficulty
├── Gate: reach ELO threshold → unlock Level 2
└── Mini-game breaks: triggered by streaks or milestones

Counting Level 2
├── Lesson: advanced techniques for this level
├── Adaptive Practice: harder problems, higher ELO stakes
├── Gate: reach ELO threshold → unlock Level 3
└── Mini-game breaks
...
```

- **Lessons come first.** Before adaptive practice starts at a new level, students go through a structured lesson with sample problems demonstrating the techniques they'll need.
- **Adaptive practice follows.** Problems selected via Bayesian IRT targeting ~50% success. Students earn ELO through correct answers (weighted by difficulty).
- **ELO gates progression.** Can't advance to the next level without sufficient mastery demonstrated through ELO.
- **This is NOT Khan Academy** (lessons without real mastery) or **AoPS** (problems without scaffolded lessons). It's a deliberate hybrid.
- **Source:** "Mark, discovery session 2026-03-28"

### Baseline Diagnostic
- Every new student takes a diagnostic test covering all domains and strands
- Results establish starting ELO and place students at appropriate levels across all skill domains
- Identifies strengths and gaps to inform initial adaptive selection
- **Source:** "Mark, discovery session 2026-03-28"

### Explanation Feedback
When a student answers a problem (correctly or incorrectly), they receive:
1. Whether they got it right/wrong
2. Mark-style explanation (pre-generated, retrieved)
3. Visual component where applicable (diagrams, step-by-step visual builds)
4. Personality-adjusted tone based on their roast slider setting

Students rate each explanation (1-5 stars or thumbs up/down) to feed the quality loop.
- **Source:** "Mark, discovery session 2026-03-28"

### Personality/Roast Slider
- Student-controlled toggle: Helpful ←→ "Mr. Trotter Mode"
- At the helpful end: clear, encouraging, supportive explanations
- At the roast end: Mark's signature creative insults woven into the explanation ("you donut", "your mother was eating dryer sheets — that's why you have no wrinkles on your brain")
- Nothing explicit or harmful — playful teacher-student banter that Mark's students genuinely enjoy
- **Fully opt-in** — defaults to helpful, student moves slider themselves
- **Source:** "Mark, discovery session 2026-03-28"

### Mini-Game Breaks (Reverse Game Kit)
- Traditional "game kit" = play a game, answer questions to continue
- This app inverts it: answer questions → earn a game break
- **Trigger:** Streaks, milestones, or timed intervals during practice sessions
- **Student selects preferred game:** crosswords, boggle/word scramble, riddles, sudoku, logic puzzles
- **Time-boxed:** ~3 minutes per break, then closes. Progress saves for next break (e.g., crossword picks up where you left off)
- Games should be simple, engaging, and appropriate for gifted teens — not childish
- Open-source puzzle packs preferred
- **Source:** "Mark, discovery session 2026-03-28"

### Student Dashboard
- ELO rating (overall and per domain)
- Progress across skill levels (visual tree or map)
- Streak tracking
- Comparison with peers (leaderboard)
- Personal progress over time (ELO graph)
- **Source:** inferred from ELO discussion — needs confirmation

### Coach Dashboard (Mark's View)
- See all students' ELO ratings, progress, and activity
- Identify struggling students or skill gaps across the class
- Ability to assign specific problem sets or levels
- View explanation ratings and flagged low-quality explanations
- **Source:** inferred from coaching workflow discussion — needs confirmation

### Design Principles
- **Minimalist, modern, professional** — "more cerebral side of games/competition — marketing to chess players, not gamers"
- **Clean and focused** — problem area + work area + answer input + submit
- **Fast feedback** — explanations load instantly (pre-generated retrieval)
- **Minimal friction** — students should be able to start a session in seconds
- **Not gimmicky** — no flashy animations, no patronizing childish design. Respect the student's intelligence.
- **Source:** "Mark, discovery session 2026-03-28"

### Mini-Game Source: Simon Tatham's Portable Puzzle Collection
- **URL:** https://www.chiark.greenend.org.uk/~sgtatham/puzzles/
- **License:** MIT (open source, free to redistribute and modify)
- **~40 puzzle types** including: Bridges, Filling, Galaxies, Keen, Light Up, Loopy, Net, Pattern, Solo (Sudoku), Tents, Towers, Tracks, Undead, Unequal, Untangle, and many more
- **Current state:** Functional but visually utilitarian — needs a "massive facelift" to match the app's minimalist modern aesthetic
- Mark's examples of student-selectable games: crosswords, boggle, riddles, sudoku, logic puzzles
- Many Tatham puzzles map directly: Solo=Sudoku, Untangle=spatial, Towers=logic, Pattern=nonogram, Keen=KenKen
- **Source:** "Mark, discovery session 2026-03-28"

## Assumed (Needs Verification)
- Dark mode support (common teen preference)
- No reference screenshots provided — UI design is a gap that needs resolution before implementation
- Sound/haptics for correct/incorrect feedback
- The ELO system uses standard chess ELO math (K-factor adjustments for new students)

## Open Questions
- Does Mark want to see real-time student activity during class (who's working, who's stuck)?
- Should the app support multiple verticals simultaneously (student doing math comp AND SAT prep) with separate ELO per vertical?
- What's the visual style direction? (Reference apps, color palette, typography)
- Need reference screenshots or mockups before any UI implementation begins
