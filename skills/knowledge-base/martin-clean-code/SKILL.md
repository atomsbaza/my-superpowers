---
name: martin-clean-code
description: "Knowledge base from \"Clean Code\" and \"The Clean Coder\" by Robert C. Martin. Use when applying Martin's frameworks for naming, functions, testing, refactoring, code smells, TDD, professionalism, estimation, or software craftsmanship; studying either book; or referencing specific chapters/concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Clean Code & The Clean Coder
**Author**: Robert C. Martin | **Pages**: ~706 (Clean Code ~462, The Clean Coder ~244) | **Chapters**: 32 (17 + 15) | **Generated**: 2026-07-24

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `naming`, `TDD`, `estimation`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch09` or `ch22`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**Boy Scout Rule** (ch01/15/18): leave every file cleaner than you found it — one small improvement per touch (rename, extract, dedupe), not a big rewrite. "Grand Redesign in the Sky" and LeBlanc's Law ("later equals never") are the failure modes it prevents.

**Beck's/Kent Beck's Four Rules of Simple Design**, in strict priority order (ch01, ch12): (1) Runs all the tests, (2) Contains no duplication, (3) Expresses the intent/design ideas of the programmer, (4) Minimizes the number of classes/methods. Apply during every refactor pass, in this order — correctness first, dedupe before expressiveness, minimize entities last.

**Naming** (ch02): use Intention-Revealing Names — if a name needs a comment, it fails. Prefer context via enclosure (extract a class) over prefixing. Avoid disinformation and Hungarian notation.

**Functions** (ch03): Small! (then smaller). Do One Thing — all statements one level of abstraction below the function's name. One Level of Abstraction per Function. The Stepdown Rule (callers above callees, reading top-down like nested "TO" paragraphs). Command-Query Separation — a function either does something or answers something, never both. Prefer exceptions to error codes.

**Comments** (ch04): a comment is a confession of failure to express intent in code — fix the code first (rename, extract) rather than explain the mess.

**Objects vs. Data Structures** (ch06): deliberate anti-symmetry — objects hide data behind behavior (easy to add new types); data structures expose data with no behavior (easy to add new functions). Don't build hybrids. **Law of Demeter**: a method of class C may only call methods on C itself, objects it creates, objects passed as arguments, or its own instance variables — never on objects returned by those calls ("talk to friends, not strangers"; avoid train wrecks like `a.getB().getC()`).

**Error Handling** (ch07): use exceptions, not return codes; write try-catch-finally first; use the Special Case Pattern (Fowler) to eliminate special-case branches from callers.

**Boundaries** (ch08): wrap third-party APIs behind a small number of application-specific classes; write Learning Tests to document and verify third-party behavior; use the Adapter pattern against APIs that don't exist yet.

**Three Laws of TDD** (ch09, ch22): (1) No production code until a failing unit test exists. (2) No more of a test than is sufficient to fail (non-compiling counts as failing). (3) No more production code than is sufficient to pass the current failing test. Run this loop in ~30-second cycles.

**F.I.R.S.T.** (ch09): tests must be Fast, Independent, Repeatable, Self-Validating, Timely (written just before the production code they test).

**Classes** (ch10): SRP — one reason to change (test: can you describe the class in ~25 words without "and/or/but/if"?). OCP — open for extension, closed for modification (new variant = new subclass, not edited code). DIP — depend on abstractions, inject concrete details via constructor.

**Systems** (ch11): separate construction (object graph wiring, ideally all in `main` or a DI container) from use; apply Dependency Injection/IoC; handle cross-cutting concerns (logging, persistence, transactions) via AOP-style mechanisms, not scattered manual code.

**Concurrency** (ch13): treat concurrency as its own SRP-driven concern — extract it from business logic; limit the scope of shared data; prefer copies over sharing; keep threads as independent as possible.

**Ch17 Smells & Heuristics Catalog**: ~91 numbered entries across six categories — Comments (C), Environment (E), Functions (F), General (G), Names (N), Tests (T) — distilled from Fowler's *Refactoring* plus Martin's field experience. Use as a review checklist, scanned top-to-bottom or looked up by ID (e.g., G5 = Duplication, F2 = Argument count).

**"First, Do No Harm"** (ch18): a professional's first duty, split into two obligations — do no harm to *function* (don't ship bugs; test everything you reasonably can) and do no harm to *structure* (don't degrade the design; keep coupling low via Boy Scout Rule "merciless refactoring").

**Commitment language — Saying No (ch19) vs. Saying Yes (ch20)**: Adversarial Roles — devs defend technical reality, managers defend business commitments; the best outcome comes from honest pushback, not silent compliance. "No Trying" (Yoda's Law) — never say "I'll try"; state facts plainly. Real commitment = Say-Mean-Do: "I will X by Y," stated to a person, backed by follow-through — never faked by cutting tests/refactoring/regression under pressure.

**PERT estimation** (ch27): for each task gather Optimistic (O), Nominal (N), Pessimistic (P); expected duration µ = (O + 4N + P) / 6; standard deviation σ = (P − O) / 6. For a sequence of tasks, sum µ values and combine σ via root-sum-of-squares. Pair with Wideband Delphi (Planning Poker, Flying Fingers, Affinity Estimation) to generate the inputs. An estimate is a probability distribution, not a promise.

**Test Automation Pyramid** (Mike Cohn, ch25): layered strategy from broad/fast/cheap at the base to narrow/slow/expensive at the top — unit → component → integration → system → manual exploratory. Each layer decouples from the others via mocks/test doubles.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-clean-code.md) | Clean Code | Boy Scout Rule; Beck's Rules of Simple Code |
| [ch02](chapters/ch02-meaningful-names.md) | Meaningful Names | Intention-Revealing Names; Context via Enclosure |
| [ch03](chapters/ch03-functions.md) | Functions | Small!; Do One Thing; Stepdown Rule; Command-Query Separation |
| [ch04](chapters/ch04-comments.md) | Comments | Comments ≠ fix for bad code; Good/Bad Comment taxonomy |
| [ch05](chapters/ch05-formatting.md) | Formatting | Newspaper Metaphor; Vertical/Horizontal Formatting Rules |
| [ch06](chapters/ch06-objects-and-data-structures.md) | Objects and Data Structures | Data/Object Anti-Symmetry; Law of Demeter |
| [ch07](chapters/ch07-error-handling.md) | Error Handling | Exceptions over Return Codes; Try-Catch-Finally First; Special Case Pattern |
| [ch08](chapters/ch08-boundaries.md) | Boundaries | Learning Tests; Boundary Wrapping; Adapter Pattern |
| [ch09](chapters/ch09-unit-tests.md) | Unit Tests | Three Laws of TDD; F.I.R.S.T.; Build-Operate-Check |
| [ch10](chapters/ch10-classes.md) | Classes | SRP; OCP; DIP |
| [ch11](chapters/ch11-systems.md) | Systems | Separation of Construction from Use; DI/IoC; AOP |
| [ch12](chapters/ch12-emergence.md) | Emergence | Kent Beck's Four Rules of Simple Design |
| [ch13](chapters/ch13-concurrency.md) | Concurrency | SRP for concurrency; Limit shared data; Use copies; Independent threads |
| [ch14](chapters/ch14-successive-refinement.md) | Successive Refinement | Write-then-clean; TDD-protected incremental refactoring |
| [ch15](chapters/ch15-junit-internals.md) | JUnit Internals | Boy Scout Rule on good code; Iterative refactoring with reversal |
| [ch16](chapters/ch16-refactoring-serialdate.md) | Refactoring SerialDate | Make It Work Then Right; Boy Scout Rule; Professional Code Review |
| [ch17](chapters/ch17-smells-and-heuristics.md) | Smells and Heuristics | The Smells & Heuristics Catalog (C/E/F/G/N/T) |
| [ch18](chapters/ch18-professionalism.md) | Professionalism | First Do No Harm; Boy Scout Rule; 60-Hour Work Week |
| [ch19](chapters/ch19-saying-no.md) | Saying No | Adversarial Roles; High Stakes; No Trying (Yoda's Law) |
| [ch20](chapters/ch20-saying-yes.md) | Saying Yes | Language of Commitment (Say-Mean-Do); Committing with Discipline |
| [ch21](chapters/ch21-coding.md) | Coding | 3 AM Code; The Flow Zone; Writer's Block; Pacing Yourself |
| [ch22](chapters/ch22-test-driven-development.md) | Test Driven Development | Three Laws of TDD |
| [ch23](chapters/ch23-practicing.md) | Practicing | Coding Dojo; Kata |
| [ch24](chapters/ch24-acceptance-testing.md) | Acceptance Testing | Acceptance Tests as Definition of Done |
| [ch25](chapters/ch25-testing-strategies.md) | Testing Strategies | Test Automation Pyramid |
| [ch26](chapters/ch26-time-management.md) | Time Management | Focus-Manna; Time Boxing / Pomodoro |
| [ch27](chapters/ch27-estimation.md) | Estimation | PERT; Wideband Delphi |
| [ch28](chapters/ch28-pressure.md) | Pressure | Avoid then Weather; Crisis Discipline test |
| [ch29](chapters/ch29-collaboration.md) | Collaboration | Programmers vs. People; Cerebellums; Solo vs. Pair vs. Team |
| [ch30](chapters/ch30-teams-and-projects.md) | Teams and Projects | Does It Blend?; Velocity-based reallocation |
| [ch31](chapters/ch31-mentoring-apprenticeship-craftsmanship.md) | Mentoring, Apprenticeship, Craftsmanship | Software Craftsmanship Apprenticeship Model |
| [ch32](chapters/ch32-tooling-appendix.md) | Tooling (Appendix A) | The Professional Toolkit |

## Topic Index

- **Acceptance testing / definition of done** → ch24
- **AOP / cross-cutting concerns** → ch11
- **Boundaries / third-party code** → ch08
- **Boy Scout Rule** → ch01, ch15, ch16, ch18
- **Classes (SRP/OCP/DIP)** → ch10
- **Code smells** → ch17
- **Coding discipline (state, focus)** → ch21
- **Collaboration / pairing / teams** → ch29, ch30
- **Comments** → ch04
- **Commitment language (say/mean/do)** → ch20
- **Concurrency** → ch13
- **Craftsmanship / mentoring / apprenticeship** → ch31
- **Emergent/simple design (Four Rules)** → ch12
- **Error handling** → ch07
- **Estimation / PERT / Wideband Delphi** → ch27
- **Formatting (vertical/horizontal)** → ch05
- **Functions** → ch03
- **JUnit / refactoring case studies** → ch15, ch16
- **Kata / deliberate practice** → ch23
- **Law of Demeter** → ch06
- **Legacy code / refactoring** → ch14, ch16
- **Naming** → ch02
- **Objects vs. data structures** → ch06
- **Pressure / crisis discipline** → ch28
- **Professionalism** → ch18
- **Refactoring (successive)** → ch14, ch15, ch16
- **Saying no** → ch19
- **Saying yes** → ch20
- **Systems / architecture / DI** → ch11
- **TDD (Three Laws)** → ch09, ch22
- **Testing strategy / pyramid** → ch25
- **Time management / Pomodoro** → ch26
- **Tooling** → ch32
- **Unit tests / F.I.R.S.T.** → ch09

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase,
combine with project-specific tools. For topics beyond this book, check related skills
or ask the agent directly.
