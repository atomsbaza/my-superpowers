# Chapter 25: Testing Strategies

## Core Idea
Unit and acceptance tests alone are insufficient; a professional team needs a layered testing strategy — the Test Automation Pyramid — combined with a QA partnership so thorough that "QA finds nothing wrong."

## Frameworks Introduced
- **The Test Automation Pyramid** (Mike Cohn, *Succeeding with Agile*, pp. 311-312): a graphical hierarchy of test types by volume and level, from many fast low-level tests at the base to few slow high-level tests at the top.
  - When to use: as the organizing model for a team's overall testing strategy, not just individual test suites.
  - How: build broad coverage with unit tests, narrow toward component, integration, system, and finally manual exploratory tests at the peak; each layer decouples from others via mocks/test-doubles.

## Key Concepts
- **QA Should Find Nothing**: the development team's goal is that QA, running the system, discovers no defects — any bug QA finds should trigger the team asking "how did this happen?" and preventing recurrence.
- **QA as Specifiers**: QA works with business to write automated acceptance tests (especially corner, boundary, and unhappy-path cases) that serve as the system's true specification.
- **QA as Characterizers**: QA also performs exploratory testing to describe the system's actual observed behavior back to development and business, without interpreting requirements.
- **Unit tests**: written by programmers, in the production language, before the production code (TDD); aim for near-100% true coverage (typically 90s%), asserting behavior rather than merely executing code.
- **Component tests**: acceptance tests wrapping a single system component, feeding it input and checking output while other components are mocked; written by QA/business with developer help (e.g., FitNesse, JBehave, Cucumber, Selenium/Watir); cover roughly half the system, mostly happy-path and obvious edge cases.
- **Integration tests**: "choreography" tests that assemble multiple components and verify they communicate correctly; they test plumbing, not business rules, and are written by architects/lead designers; run periodically (not on every CI build) due to longer runtimes.
- **System tests**: automated tests against the whole integrated system, verifying correct construction and interoperation (including throughput/performance) rather than business correctness; written by architects/tech leads; cover roughly 10% of the system and run relatively infrequently.
- **Manual exploratory tests**: unscripted, unautomated testing where humans use creativity to surface unexpected behaviors; goal is discovery of "peculiarities," not coverage — a written test plan defeats the purpose.

## Mental Models
- Testing is a pyramid, not a single layer: volume and speed decrease while scope and cost increase as you move up from unit tests to manual exploration.
- Each layer answers a different question: unit tests ask "is the code right?", component tests ask "does this component satisfy the business rule?", integration/system tests ask "is the system wired together correctly?", and exploratory tests ask "does it behave well under real human use?"
- QA and development are partners, not adversaries — QA's findings are signals for process improvement, not scorekeeping against developers.

## Anti-patterns
- **Over-reliance on manual/GUI-level tests (inverted pyramid)**: pushing most verification into slow, expensive, human-driven or GUI-level tests wastes effort duplicating what fast unit tests should already guarantee, and slows feedback dramatically.
- **False coverage**: unit tests that execute code without asserting behavior create an illusion of safety while catching nothing.
- **Treating QA bugs as normal**: accepting defects found by QA as routine rather than as signals to fix the development process lets systemic quality problems persist.
- **Skipping the middle layers**: relying only on unit tests plus manual QA, without component/integration/system tests, leaves architectural wiring and cross-component behavior unverified.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Layer | What it tests | Relative volume/speed | Written by |
|---|---|---|---|
| Unit tests | Lowest-level correctness of code, specified before implementation (TDD) | Largest volume (~90%+ coverage), fastest, run on every CI build | Programmers |
| Component tests | Individual component against its business rules, input/output at component boundary | ~Half the system; happy-path + obvious edge cases | QA/business, with dev help |
| Integration tests | Communication/plumbing between assembled groups of components | Fewer; longer runtime, run periodically (nightly/weekly) | Architects/lead designers |
| System tests | Whole integrated system's construction and interoperation, throughput/performance | ~10% of system; run infrequently | Architects/tech leads |
| Manual exploratory tests | Unexpected behaviors via human creativity, no scripted coverage goal | Smallest volume, slowest, unautomated | Whole team / specialists |

## Worked Example
(omit — no specific concrete case in this chapter)

## Key Takeaways
1. Build a full testing hierarchy — unit, component, integration, system, and manual exploratory — rather than stopping at unit and acceptance tests.
2. Treat "QA finds nothing" as the team's standing goal; any QA-found defect should trigger root-cause reflection, not just a fix.
3. Push the bulk of test volume and unhappy-path coverage down to unit tests, where feedback is fastest and cheapest.
4. Use component tests to make business rules the readable, business-legible specification of the system.
5. Reserve integration and system tests for verifying architecture and wiring, not business correctness — and run them on a slower cadence given their cost.
6. Preserve manual exploratory testing as an unscripted, creativity-driven activity aimed at surfacing peculiarities, not coverage.
7. Position QA as partners acting as specifiers (writing corner/boundary/unhappy-path acceptance tests) and characterizers (exploratory testing), not adversaries.

## Connects To
- **Ch9 (Clean Code, Unit Tests)**: supplies the craftsmanship rules (F.I.R.S.T., one assert, readability) that make the unit-test base of the pyramid trustworthy.
- **Ch8 (Clean Code, Boundaries)**: mocking/test-doubling other components at each pyramid layer relies on the boundary-wrapping techniques described there.
- **Ch22 (The Clean Coder, Test Driven Development)**: TDD is explicitly named as the discipline producing the pyramid's unit-test base.
- **Ch24 (The Clean Coder, Acceptance Testing)**: component tests here are described as "some of the acceptance tests mentioned in the previous chapter" — direct continuation of that chapter's QA-as-specifier role.
- **External concept — Test Automation Pyramid, Mike Cohn**: the chapter's central model is drawn from Cohn's *Succeeding with Agile* (2009), cited as [COHN09].
