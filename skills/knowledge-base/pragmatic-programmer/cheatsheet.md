# Cheatsheet

## Decision Rules

- **When you see the same knowledge expressed in two places** (code, config, docs, schema): that's a DRY violation regardless of whether the text looks identical — diagnose which of the four "I"s caused it (imposed/inadvertent/impatient/interdeveloper) before picking a fix. (Ch2)
- **When starting a system with an unclear end-to-end path**: build a Tracer Bullet (thin, real, end-to-end slice meant to survive) rather than a throwaway Prototype (meant to be discarded) — pick based on whether you need to keep what you build. (Ch2)
- **When a condition is "impossible"**: assert it. If it's truly impossible, the assertion never fires and costs nothing; if you're wrong, you find out immediately instead of via silent corruption. (Ch4)
- **When a program hits a genuinely inconsistent state**: crash immediately rather than attempt to continue — a dead program tells no lies, but a corrupted one running onward can do real damage. (Ch4)
- **When reviewing a method call chain like `a.getB().getC().frobnicate()`**: that's a Law of Demeter violation — only talk to your direct collaborators, not objects reached transitively. (Ch5)
- **When behavior is likely to change independent of the next release**: drive it from metadata/config (metaprogramming), not a hardcoded branch — but only when that variability is real, not speculative. (Ch5)
- **When stakeholders hand you a requirements document**: treat it as a starting point for digging (Requirements Pit), not a literal spec to implement verbatim — the stated requirement is rarely the real underlying need. (Ch7)
- **When a manual process is repeated more than once**: automate it. Ubiquitous automation exists specifically to remove human memory/discipline as a dependency. (Ch8)
- **When code is hard to test**: that's a design smell (usually excess coupling), not a testing-tool problem — fix the design (Orthogonality, Law of Demeter) before reaching for more elaborate test infrastructure. (Ch2, Ch5, Ch6)
- **When choosing an algorithm before implementation**: reason about its Big-O scaling first, then verify empirically once built — don't skip either step. (Ch6)

## Decision Tree: Prototype vs. Tracer Bullet vs. Production Code

1. Is the primary goal to reduce *uncertainty* about a risky area (a new library, an unfamiliar API, a UI concept)?
   - Yes → **Prototype**. Build it fast, throw it away, keep only the lessons learned.
   - No → continue.
2. Is the goal to validate the *whole system's* architecture end-to-end, with the intent to keep and refine what you build?
   - Yes → **Tracer Bullet**. Thin slice through every layer, refined iteratively into the final system.
   - No → continue.
3. Is the requirement well-understood and the architecture already validated?
   - Yes → **Production code**, built with full DRY/Orthogonality/Design-by-Contract discipline from the start.
(Ch2)

## Trade-off Matrix: Duplication Type → Fix

| "I" of duplication | Cause | Typical fix |
|---|---|---|
| Imposed | Environment/organization forces it (e.g., a required format duplicated across systems) | Generate the duplicate copies from one authoritative source |
| Inadvertent | Developers didn't realize the same knowledge already existed elsewhere | Improve discoverability (naming, documentation, code review) |
| Impatient | Duplicating felt faster than finding/reusing existing code | Invest in making the reusable path actually faster to find and use |
| Interdeveloper | Multiple people/teams independently implement the same thing | Improve cross-team communication and shared ownership of common code |
(Ch2)

## Thresholds & Defaults

- **Estimate precision should match requested precision** — if asked for a rough estimate, answer in matching units ("about a month," not "23.2 days"); false precision misleads more than a rounded honest range. (Ch2)
- **A tracer bullet is judged by whether it reaches every layer**, not by how polished any single layer is — resist gold-plating one layer before the full path connects. (Ch2)
- **Assertions should never have side effects** — an assertion that mutates state changes behavior when assertions are disabled in production, silently reintroducing the bug they were meant to catch. (Ch4)
- **Testing should start from day one**, not as a late-project phase — code designed without testability in mind from the start is markedly more expensive to retrofit. (Ch4, Ch8)

## Tells & Smells

- **A bug you "can't explain" that seems to work by luck** → Programming by Coincidence; you don't actually understand why the code works, so you can't predict when it will stop working. (Ch6)
- **You're afraid to touch a piece of code because you don't know what else it might break** → an Orthogonality/coupling failure, not a testing gap alone. (Ch2, Ch5)
- **A requirements document reads as exhaustively complete before any code exists** → likely a Specification Trap; real requirements surface through iteration, not upfront completeness. (Ch7)
- **A generated-code "wizard" produced something nobody on the team fully understands** → an Evil Wizard; if you can't maintain what it generated, you've taken on hidden technical debt. (Ch6)
- **A once-clean codebase has accumulated small unaddressed rough edges** ("it's just a quick hack," "we'll clean it up later") → Broken Windows in progress; left unaddressed, they normalize further decay. (Ch1)
- **A project's design diagrams are ad hoc boxes-and-arrows with no consistent notation or semantics** → "Circles and Arrows" — useful for talking, not a substitute for an actual specification/model. (Ch7)
