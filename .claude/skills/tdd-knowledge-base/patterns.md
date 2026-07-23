# TDD Patterns Reference

## Red-Green-Refactor Cycle
**When to use**: For every unit of behavior added, in every TDD session.
**How**: Write a failing test (Red) tied to one requirement; confirm it actually fails; write the minimum code to pass (Green); refactor only while Green, since the passing suite is the safety net; repeat.
**Trade-offs**: Skipping Red confirmation lets untrustworthy tests slip in; refactoring while Red removes your only safety net.

## Canon TDD / Test List
**When to use**: At the start of any TDD session and continuously as new cases surface.
**How**: Brainstorm test scenarios as plain-language bullets (happy path, edge cases, errors). Pick the simplest/most informative item, implement it fully, then append new ideas discovered mid-cycle to the list instead of chasing them immediately.
**Trade-offs**: Keeps each cycle short and focused; requires discipline not to abandon the current cycle for a shinier idea.

## Fake It ('Til You Make It)
**When to use**: You want a fast green bar and aren't ready to commit to real logic.
**How**: Return a hardcoded constant that satisfies the current test, then evolve it toward real logic as more tests arrive.
**Trade-offs**: Fast, but a constant left un-redeemed becomes a silent permanent bug — always plan to generalize it.

## Obvious Implementation
**When to use**: The correct logic is simple and already known with confidence.
**How**: Skip faking it; write the real implementation directly.
**Trade-offs**: Overconfidence on non-trivial logic skips useful test-driven feedback and can hide untested bugs.

## Triangulation
**When to use**: Uncertain what the correct general abstraction should be.
**How**: Hold off generalizing until at least two specific tests jointly demand the same generalization; let the second test force the abstraction.
**Trade-offs**: Guards against guessing wrong from one example; used on truly obvious cases it just slows progress with redundant tests.

## Transformation Priority Premise (TPP)
**When to use**: During the "make it green" step, when more than one transformation could satisfy the failing test.
**How**: Climb a priority ladder from simplest to most complex (null→constant, constant→variable, statement→statements, unconditional→if, scalar→array, if→loop, statement→recursion), picking the simplest transformation that passes the current test; escalate only when a new test forces it.
**Trade-offs**: Prevents "getting stuck" on premature complexity requiring a painful rewrite; requires discipline to resist jumping to a general solution early.

## Detroit-style (Classicist / State Verification) Testing
**When to use**: Well-understood domain logic, legacy modernization, tech-debt reduction; when refactor safety matters most.
**How**: Test a module (class or related classes) with real collaborators, reserving test doubles for awkward dependencies (external APIs, filesystem, network). Assert on final state, not how it was reached.
**Trade-offs**: Refactors stay cheap since tests aren't coupled to internals; weaker bug localization since a bug can cascade and fail many dependent tests.

## London-style (Mockist / Interaction Verification) Testing
**When to use**: New feature development where design is discovered through roles and collaboration between objects.
**How**: Isolate the Subject Under Test from every collaborator via mocks; verify the right methods were called with the right arguments. Treat a hard-to-mock dependency as a design smell to fix immediately.
**Trade-offs**: Strong bug localization (a failure pinpoints the exact class); tests are "vulnerable" — they can break on refactors that don't change behavior.

## Don't Mock What You Don't Own
**When to use**: Any time a test would need to mock a third-party library or external API.
**How**: Wrap the external dependency in a thin adapter you control, and mock the adapter instead of the library directly.
**Trade-offs**: Prevents tests from drifting out of sync with a real API's actual behavior; adds one layer of indirection to maintain.

## Inside-Out (Bottom-Up) Design
**When to use**: Legacy modernization, API-first development, microservices — domain logic is already established.
**How**: Flow Logic → Services → APIs → UI. Write tests against core business logic first with no dependents, then build each layer on the proven layer beneath it.
**Trade-offs**: Fast feedback and high coverage on core logic; risks a "Business Gap" — a technically solid implementation that misses what the user actually needed.

## Outside-In (Top-Down) Design
**When to use**: New feature development, customer-facing work, unclear/evolving requirements.
**How**: Write a failing acceptance/UI-level test for the user scenario first; stub every collaborator it needs; progressively replace each stub with a real, tested implementation until the outer test passes unaided.
**Trade-offs**: Structurally resists YAGNI and forces business alignment; outer tests stay red for long periods and risks "quick-and-dirty" internals left unfinished once the outer test goes green.

## Testing Pyramid
**When to use**: As a portfolio strategy for the shape of an entire test suite, not any single test.
**How**: Write many fast unit tests as the base; a smaller layer of integration tests; contract tests at system boundaries; a minimal layer of acceptance/E2E tests confirming the system is wired correctly.
**Trade-offs**: Balances confidence against cost/speed; inverting it ("ice cream cone" — too many slow E2E tests) creates a slow, dreaded suite.

## BDD / Gherkin Scenarios
**When to use**: Specifications need to be readable and validatable by non-programmers.
**How**: Express behavior as Given/When/Then scenarios in plain language; because they're executable, they double as living documentation that fails when behavior drifts.
**Trade-offs**: Enables shared vocabulary across roles; scenarios written around UI mechanics instead of business outcomes lose readability and defeat the purpose.

## ATDD / Three Amigos
**When to use**: Before development begins on a feature, to prevent a Business Gap.
**How**: A Business representative, a Developer, and a Tester collaborate to define acceptance criteria together, before any code is written — the value is in the conversation, not just the resulting document.
**Trade-offs**: Closes the gap between "technically correct" and "actually needed"; skipping the conversation and writing scenarios unilaterally defeats the purpose even with correct Gherkin syntax.

## Characterization Testing
**When to use**: Before touching any legacy code that lacks a test suite, prior to any refactor or feature addition.
**How**: Exercise the existing code with a range of inputs, observe its real (possibly buggy) outputs, and write assertions that lock in those outputs as the current contract — describing what the code does, not what it should do.
**Trade-offs**: Gives a safety net for refactoring; can freeze a bug into the "expected" suite if not later revisited deliberately.

## Golden Master Technique
**When to use**: Highly complex, opaque, or tightly coupled legacy systems where per-unit characterization tests are impractical.
**How**: Run the system across a large batch of representative/historical inputs, capture outputs verbatim as a baseline; after each refactor step, re-run the same inputs and diff against the baseline.
**Trade-offs**: Broad, low-effort coverage; trades precision for coverage, and must be re-diffed after every increment or regressions accumulate silently.

## TDD Katas (Deliberate Practice)
**When to use**: Outside feature/deadline work, to sharpen red-green-refactor discipline in a low-stakes setting.
**How**: Pick a small, well-known problem (Bowling Game, FizzBuzz, String Calculator); solve it from scratch with strict TDD; repeat the same kata multiple times, each pass focused on a specific skill (smaller steps, Fake It vs. Obvious Implementation, faster cycles).
**Trade-offs**: Builds fluency so mechanics don't compete for attention during real work; a kata done once, not repeated, forfeits most of the deliberate-practice value.

## Test Data Builder
**When to use**: Any test construction of a complex object where most fields don't matter to the specific test.
**How**: Build a Builder-pattern class with sensible defaults for every field and fluent `withX()` overrides; each test calls only the fields it actually cares about (e.g., `anOrder().withStatus(CANCELLED).build()`).
**Trade-offs**: Keeps setup readable and DRY, and isolates the blast radius of new required fields to one place; adds a maintenance class of its own.
