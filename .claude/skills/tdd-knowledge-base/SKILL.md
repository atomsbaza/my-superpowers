---
name: tdd-knowledge-base
description: "Research-synthesized knowledge base on Test-Driven Development (NotebookLM deep research, 89 sources). Use when applying TDD practices, choosing between Detroit/classicist and London/mockist testing styles, designing test strategy (inside-out vs outside-in, testing pyramid), avoiding TDD anti-patterns, running TDD katas, or referencing named techniques (Transformation Priority Premise, Canon TDD, Characterization Testing) and practitioner perspectives (Kent Beck, Martin Fowler, Uncle Bob, DHH)."
---

<!-- argument-hint: [topic, framework name, or topic number] -->

# Test-Driven Development: A Research-Synthesized Knowledge Base
**Source**: NotebookLM deep web research (89 sources) | **Topics**: 13 | **Generated**: 2026-07-24

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `classicist vs mockist`, `red-green-refactor`, `TDD anti-patterns`, or another indexed topic; I find and read the relevant topic file
- **With topic number** — ask for `topic03` or `topic08`; I load that specific topic
- **Browse** — ask "what topics do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant topic file before answering.

**Note on provenance:** unlike book-derived skills, this knowledge base is synthesized from
web research rather than a single authoritative source. Named techniques and quotes are
attributed to their original practitioners where the research identifies them; a few
technique mechanics (noted in Topic 10) are flagged where the research left gaps that
were filled with general software-engineering knowledge rather than a verified source.

---

## Core Frameworks & Mental Models

**Red-Green-Refactor Cycle** (Kent Beck). Six steps, applied per unit of behavior, not once per feature: (1) Create a Test from a specific requirement, before production code exists. (2) Run Tests — Red: it must fail, proving it's valid and not already satisfied. (3) Write Code — the minimum needed to pass. (4) Run Tests — Green. (5) Refactor — clean up without changing behavior; improve design here, not during Green, using the passing suite as your safety net. (6) Repeat. Never skip Red.

**Canon TDD / Test List**. Before writing the first test, brainstorm plain-language test scenarios (happy path, edges, errors) as a running list. Pick the simplest/most informative item, turn it into a failing test, and finish that red-green-refactor loop before chasing newly-discovered cases — append those to the list instead.

**Green Bar Patterns** — three ways to reach Green, chosen by confidence level: **Fake It** (return a hardcoded constant, generalize as more tests arrive) when you want a fast green bar without committing to real logic; **Obvious Implementation** (write the real logic directly) when the solution is simple and known; **Triangulation** (wait until ≥2 specific tests jointly demand a generalization before writing it) when you don't yet trust the abstraction.

**Detroit/Classicist vs London/Mockist** — the unresolved question "what is a unit, what should be isolated?" splits TDD into two schools.
- *Detroit (Kent Beck; state verification)*: unit = a module (class or small cluster). Use real collaborators; mock only "awkward" ones (network, filesystem, time). Verify final state. Isolation means tests isolated from each other, not the unit from its collaborators. Prefer for well-understood domain logic, legacy modernization, refactor-heavy work — tests stay decoupled from implementation detail.
- *London (Freeman & Pryce, GOOS; interaction verification)*: unit = a single class (the SUT), isolated via mocks for every collaborator. Verify by asserting the right calls were made. An awkward-to-mock dependency is a design smell to fix, not tolerate. Prefer for discovering design through new feature work, outside-in from a user scenario.
Trade-off: Detroit tests survive refactors better but give less design feedback and weaker fault localization; London tests give tight design feedback and localize failures precisely but are more Vulnerable to refactors that don't change behavior.

**Inside-Out vs Outside-In** — directional strategy, chosen by project phase, not doctrine.
- *Inside-Out (bottom-up)*: Logic → Services → APIs → UI. Developer-driven; pairs naturally with Detroit/state verification. Use for legacy modernization, API-first work, microservices — domain logic already established.
- *Outside-In (top-down)*: UI → APIs → Services → Logic. Collaborative (product + QA); pairs with London/interaction verification. Write a failing acceptance-level test for the user scenario, stub every collaborator beneath it, then replace stubs one at a time with real tested code until the top test goes green unaided. Use for new features and unclear requirements needing UI-level discovery.

**The Testing Pyramid**. Layers, widest/fastest at base: Unit → Integration → Contract → Acceptance (ATDD) → E2E, narrowest/slowest/most fragile at top. Design the suite's overall shape (many fast unit tests, progressively fewer slow ones above) rather than picking a level per test in isolation.

**Transformation Priority Premise** (Robert C. Martin). When multiple code changes could make the current failing test pass, scan a priority list from simplest to most complex mechanical transformation (e.g., `null`→constant) and apply the simplest one that works; only escalate complexity when the tests force it. Applied during the "make it green" step.

**BDD / ATDD**. TDD proves code is correct; it doesn't by itself prove it's the *right* feature. BDD expresses behavior in Given/When/Then (Gherkin) so non-programmers can read and validate specs, doubling as living documentation. ATDD's Three Amigos (Business + Developer + Tester) define acceptance criteria together *before* coding, to close the "business gap."

**Named Anti-Patterns** (test-review checklist — a match is a signal to refactor the test or the design it exposes):
- *The Liar* — a test that passes without truly verifying the requirement.
- *The Mockery* — over-mocked tests confirming only mock interactions, not real behavior.
- *The Inspector* — assertions reaching into internal state; brittle to safe (behavior-preserving) refactors.
- *Vulnerable Tests* — typically London-style tests that break on internal refactors despite unchanged output.
- *Excessive Setup* — huge arrange blocks that obscure test intent.
- *The Slow Poke* — tests too slow to run often, eroding fast feedback.
- *Mocking What You Don't Own* — mocking third-party code directly instead of via an owned adapter.
- *Test-Induced Design Damage* (DHH) — architectural indirection added purely for testability, with no other justification.

**"Is TDD Dead?" resolution** (DHH vs Beck/Fowler, 2014). The debate's lasting output is not a new method but a shift in emphasis: the shared goal across schools is **self-testing code** (Fowler) — a suite that gives confidence to change the system — and TDD is *one* route to that goal, not a mandatory ritual to follow dogmatically regardless of context.

**Legacy Code**: never apply red-green-refactor directly to untested legacy code. First use **Characterization Testing** — exercise existing code, observe actual (not ideal) outputs, and lock them in as the current contract — before any refactor. For large/tangled systems where per-path characterization is impractical, use the **Golden Master Technique**: capture bulk output over representative inputs as a baseline, then diff post-refactor output against it.

**XP's Five Core Values in testing**: Communication (tests convey intent to new readers), Simplicity (e.g., Test Data Builders keep setup manageable), Feedback (instant pass/fail), Courage (high coverage enables refactoring "big balls of mud"), Respect (test code gets the same care as production code — same style, refactoring discipline, and patterns like Builders/Factories).

---

## Topic Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [topic01](topics/topic01-history-and-origins.md) | History and Origins | XP context; Detroit vs London school origins |
| [topic02](topics/topic02-red-green-refactor-and-canon-tdd.md) | Red-Green-Refactor and Canon TDD | The 6-step cycle; Test List; Green Bar Patterns |
| [topic03](topics/topic03-classicist-vs-mockist.md) | Classicist vs Mockist | Detroit (state verification) vs London (interaction verification) |
| [topic04](topics/topic04-inside-out-vs-outside-in.md) | Inside-Out vs Outside-In | Bottom-up vs top-down design flow |
| [topic05](topics/topic05-testing-levels-and-pyramid.md) | Testing Levels and Pyramid | Unit/Integration/Contract/Acceptance/E2E layering |
| [topic06](topics/topic06-bdd-and-atdd.md) | BDD and ATDD | Gherkin; Three Amigos |
| [topic07](topics/topic07-benefits-and-evidence.md) | Benefits and Evidence | Empirical findings on defects, cost, technical debt |
| [topic08](topics/topic08-anti-patterns-and-pitfalls.md) | Anti-Patterns and Pitfalls | Named anti-pattern catalog |
| [topic09](topics/topic09-transformation-priority-premise.md) | Transformation Priority Premise | TPP prioritized transformation list |
| [topic10](topics/topic10-tdd-for-legacy-code.md) | TDD for Legacy Code | Characterization Testing; Golden Master |
| [topic11](topics/topic11-tdd-katas-and-practice.md) | TDD Katas and Practice | Coding Kata (e.g., Bowling Game) |
| [topic12](topics/topic12-is-tdd-dead-debate.md) | Is TDD Dead? Debate | DHH vs Beck/Fowler; self-testing code |
| [topic13](topics/topic13-xp-values-and-test-code-quality.md) | XP Values and Test Code Quality | Five Core Values; test code as production code |

## Concept Index

- **ATDD / Acceptance Tests** → topic05, topic06
- **BDD / Gherkin** → topic06
- **Bowling Game Kata** → topic11
- **Canon TDD / Test List** → topic02
- **Characterization Testing** → topic10
- **Classicist vs Mockist** → topic01, topic03
- **Coding Kata** → topic11
- **Contract Tests** → topic05
- **Detroit School (state verification)** → topic01, topic03
- **DHH / "Is TDD Dead?"** → topic12
- **Excessive Setup (anti-pattern)** → topic08
- **Fake It / Obvious Implementation / Triangulation** → topic02
- **Golden Master Technique** → topic10
- **Inside-Out vs Outside-In** → topic04
- **London School (interaction verification)** → topic01, topic03
- **Mocking What You Don't Own** → topic03, topic08
- **Red-Green-Refactor Cycle** → topic02
- **Self-Testing Code (Fowler)** → topic12
- **Test Data Builder** → topic13
- **Testing Pyramid** → topic05
- **The Inspector / The Liar / The Mockery / The Slow Poke** → topic08
- **Three Amigos** → topic04, topic05, topic06
- **Transformation Priority Premise (TPP)** → topic09
- **Vulnerable Tests** → topic03, topic08
- **XP's Five Core Values** → topic13
- **XP (Extreme Programming) origins** → topic01

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and named patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the synthesized research content only, not a single canonical source — treat it
as a well-organized survey of practitioner consensus and debate, not gospel from one author.
For hands-on implementation in your codebase, combine with project-specific tools and the
existing `tdd` workflow skill (test-first implementation loop) or `tdd-loop` skill (automated
loop verification) — this skill is the reference/knowledge layer, those are the doing layer.
For topics beyond this research, check related skills or ask the agent directly.
