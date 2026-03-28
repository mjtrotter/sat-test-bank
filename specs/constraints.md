# Constraints Spec — Gifted Adaptive Trainer
> Last verified: 2026-03-28 via discovery session

## Verified (Gold Standard)

### Compliance (FERPA / COPPA)
- **COPPA applies:** Students include 6th graders (age 11-12, under 13)
- **FERPA applies:** School setting, student performance data is an education record
- **Mitigations:**
  - Mark is school administrator at a private school — has authority to authorize the app
  - Data minimization: student IDs are UUIDs, display names are initials/nicknames, no PII collected
  - No full names, emails, photos, voice, location, or device identifiers stored
  - Data encrypted in transit and at rest
  - Student data used only for educational purpose — no analytics, advertising, or secondary use
  - Deletion capability: Mark can delete any student's data at any time
  - App Store: may need Kids Category compliance (parental gates, no external links, no purchase prompts)
- **Source:** "Mark, discovery session 2026-03-28" + FERPA/COPPA research

### Anti-Patterns (What This App Is NOT)
- **NOT Khan Academy** — Khan is all lessons, mastery component isn't real or deep enough. This app has real ELO-gated mastery progression.
- **NOT a pure problem bank** (like AoPS Alcumus) — Alcumus adapts problems but doesn't scaffold lessons. This app blends lessons with adaptive practice.
- **NOT a gamified distraction** — Mini-games are earned breaks, not the core experience. Time-boxed to ~3 minutes. The "reverse game kit" model: learn → play, not play → learn.
- **NOT generic AI tutoring** — The differentiator is Mark's specific teaching persona and methodology, not a generic LLM tutor
- **Source:** "Mark, discovery session 2026-03-28"

### Hard Rules
1. **Explanations must reflect Mark's teaching methodology:** anchor (what we know) → question (what we wish we knew) → pattern-seek → stress-test critical points. Visualization is core. Generic textbook solutions are unacceptable.
2. **Difficulty targeting must be real.** 40-70% predicted success range, not fake mastery badges. If a student is getting everything right, they're not being challenged enough.
3. **Personality slider is fully opt-in.** Defaults to helpful. Student explicitly moves it themselves. Nothing explicit or harmful at any setting.
4. **Student data never leaves the self-hosted server.** No cloud services, no analytics platforms, no third-party SDKs that phone home.
5. **Mini-games must be age-appropriate for gifted teens.** Not childish, not time-wasting. Puzzles that exercise adjacent cognitive skills (logic, language, spatial reasoning).
6. **Offline fallback must exist.** At minimum, one daily practice set downloadable for offline use.
- **Source:** "Mark, discovery session 2026-03-28"

### Technology Constraints
- **GPU:** AMD MI50 with ROCm — must use ROCm-compatible models and frameworks
- **Client:** iOS only (iPad, App Store) — no Android, no web app for MVP
- **PDF ingestion:** Local processing only (VL models on MI50 or MLX on Mac). No cloud OCR services.
- **Voice recording:** Mark records on whatever tool is cleanest (Notability, paper, whiteboard). Pipeline must accept multiple input formats.
- **Source:** "Mark, discovery session 2026-03-28"

### Libraries/Frameworks — Mandated
- **iOS:** SwiftUI + PencilKit (future phases)
- **Server ML:** ROCm-compatible PyTorch
- **Transcription:** MLX Whisper (local, already in use)
- **PDF extraction:** Local VL models (e.g., Qwen 2.5 VL or successor)

### Libraries/Frameworks — Off-Limits
- No cloud AI APIs for student-facing inference (OpenAI, Anthropic, Google) — all inference is self-hosted
- No student data sent to any external service
- No ad SDKs, analytics SDKs, or tracking pixels

## Assumed (Needs Verification)
- The App Store submission can avoid the Kids Category if marketed as a "teacher tool" rather than "for children" — but this is a gray area worth legal review
- The private school setting simplifies compliance vs. public school district procurement

## Open Questions
- Does the private school have any existing data governance policies that need alignment?
- Should explanations be reviewed by a second adult before students see them (especially at higher roast levels)?
- IP considerations for competition problems — are MATHCOUNTS/AMC/MAT problems fair use for a non-commercial educational tool?
