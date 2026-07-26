# Topic 10: TDD for Legacy Code

## Core Idea
Legacy code — code that lacks tests and was never built with testability in mind — cannot be safely brought under red-green-refactor directly; it must first be wrapped in tests that capture its *existing* behavior, so that behavior-preserving changes and eventual TDD can proceed without silently breaking what already works.

## Frameworks Introduced
- **Characterization Testing**: Tests that describe what code *actually* does, not what it *should* do — the inverse orientation of standard TDD, where tests specify desired behavior before it exists.
  - When to use: Before touching any legacy code that lacks a test suite — as the first step, prior to any refactor or feature addition.
  - How: Exercise the existing code with a range of inputs, observe its real outputs (including quirks and bugs), and write assertions that lock in those observed outputs as the current contract. The test suite's job is to detect *any* behavior change, not to validate correctness.
- **The Golden Master Technique**: A bulk, output-comparison form of characterization testing used when code is too complex or tangled to characterize test-by-test.
  - When to use: For highly complex, opaque, or tightly coupled legacy systems where writing individual characterization tests for every code path is impractical — e.g., a large calculation engine or report generator with no clear internal seams.
  - How: Run the legacy system across a large batch of representative or historical inputs, capture its outputs verbatim as the "Golden Master" baseline. After each refactor step, re-run the same inputs through the changed code and diff the results against the Golden Master — any mismatch signals an unintended behavior change.

> **Honesty note on sourcing**: the research pass behind this topic explicitly flagged that the precise mechanics of Characterization Tests and the Golden Master technique were *not* detailed in the collected sources. The formulations above draw on general software engineering knowledge (traceable to Michael Feathers' *Working Effectively With Legacy Code*) rather than a verified passage from this research corpus — treat them as a reasonable synthesis, not a direct citation.

## Key Concepts
- **Legacy Code**: In this context, code without an automated test suite, regardless of age — the defining trait is untested-ness, not how old the code is.
- **Testability Gap**: The structural problem that legacy code was written without regard for dependency injection, seams, or isolation, making it hard to exercise in a test harness without first making small structural changes.
- **Characterization Test vs. Specification Test**: A characterization test asserts "this is what happens now" (descriptive, can encode bugs); a standard TDD test asserts "this is what should happen" (prescriptive, drives design). Confusing the two leads to accidentally freezing a bug into the "expected" test suite.
- **Regression Safety Net**: The purpose of both techniques — not to prove the code is correct, but to give a refactor a fast, reliable way to detect any change in observable behavior.

## Mental Models
- **Wrap before you cut**: legacy code work follows a strict ordering — establish a characterization/Golden Master safety net first, only then refactor or add features. Skipping the wrap step turns "safe" refactoring into a gamble.
- **Describe, don't design, first**: characterization testing temporarily inverts the TDD mindset — you are documenting reality, not designing behavior. Only after the safety net exists do you resume normal red-green-refactor for new work.
- **Bugs are part of the contract until proven otherwise**: a characterization test may lock in a bug. That's expected — removing the bug is a deliberate, separate, test-updating decision, not an accidental side effect of refactoring.
- **Coarse-to-fine safety nets**: Golden Master gives broad, low-effort coverage over an opaque system; characterization tests give narrower, more precise coverage once the system is broken into smaller, understandable seams. Teams often start coarse (Golden Master) and narrow over time.

## Anti-patterns
- **Refactoring without a safety net first**: Changing legacy code's structure before capturing any characterization tests or Golden Master baseline — there is nothing to catch a broken behavior, so "refactoring" is really just risky rewriting.
- **Treating characterization tests as permanent specifications**: Leaving a characterization test (including a locked-in bug) unexamined forever, instead of revisiting it once the surrounding code is understood and deciding deliberately whether the behavior it encodes is actually correct.
- **Skipping Golden Master comparison after refactor steps**: Capturing the baseline once but not re-diffing outputs after each incremental change, which forfeits the fast-feedback benefit and lets regressions accumulate silently across several changes.

## Code Examples
(Omitted — this topic is process-oriented; see Worked Example below for a compact reconstructable walkthrough instead of literal code.)

## Reference Tables
| Technique | Purpose | When to Use |
|---|---|---|
| Characterization Testing | Lock down specific, understood behaviors of a code unit test-by-test | Code with identifiable seams/units that can be exercised individually |
| Golden Master Technique | Lock down aggregate output of a whole system across many inputs at once | Highly tangled/opaque systems where per-unit testing isn't practical |

## Worked Example
1. **Start**: A legacy `calculateInvoiceTotal(order)` function has no tests, unclear internal logic, and several conditional branches whose intent isn't documented anywhere.
2. **Capture a Golden Master**: Run `calculateInvoiceTotal` against a large batch of real historical orders (or generated random ones covering edge cases like zero items, discounts, and negative quantities). Save each input/output pair verbatim as the Golden Master baseline.
3. **Write characterization tests**: For the specific branches you're about to touch, write individual tests asserting the function's *current* output for representative inputs — including any surprising behavior (e.g., a discount that doesn't apply below a certain order size due to what looks like an off-by-one bug). These become fast, targeted checks layered on top of the coarser Golden Master.
4. **Refactor safely**: Extract a smaller `applyDiscount` function out of the tangled logic, rename variables, simplify conditionals — small steps, running the characterization tests after each one.
5. **Re-verify against the Golden Master**: Periodically re-run the full historical input batch and diff against the saved baseline to confirm no output has silently drifted, even in code paths the characterization tests didn't specifically target.
6. **Resume normal TDD**: Once the function is decomposed into testable, well-named units with real specification tests, new features on top of it can follow standard red-green-refactor rather than characterization testing.

## Key Takeaways
1. Never refactor legacy code before it has some form of behavior-locking safety net — characterization tests or a Golden Master baseline come first, always.
2. Characterization tests describe current reality, including bugs; treat any bug they encode as a deliberate, separate decision to fix later, not something to silently "correct" mid-refactor.
3. Reach for the Golden Master technique specifically when a system is too tangled or opaque for per-unit characterization tests to be practical — it trades precision for broad, low-effort coverage.
4. Re-run Golden Master comparisons after every refactor increment, not just once at the start — the value is in continuous drift detection, not a one-time snapshot.
5. Treat this topic's core techniques as a synthesis from general engineering knowledge (via Feathers' book) rather than a directly-sourced finding — verify mechanics independently before treating them as authoritative in a specific codebase context.

## Connects To
- **Topic 2 (Red-Green-Refactor & Canon TDD)**: legacy-code work is a controlled detour from canonical TDD — you build the safety net first (characterization/Golden Master), then resume standard red-green-refactor for new behavior.
- **Topic 5 (Testing Levels & Pyramid)**: Golden Master tests often function like coarse, slow, high-level regression tests (closer to end-to-end) that sit above the pyramid until the system is decomposed enough for faster unit-level characterization tests.
- **Topic 8 (Anti-Patterns & Pitfalls)**: refactoring without a safety net is a specific, high-risk instance of the general anti-pattern of changing code without adequate test coverage.
- **External concept**: Michael Feathers' *Working Effectively With Legacy Code* — the origin of the "legacy code = untested code" framing and the broader toolkit (including seams) that this topic's techniques are drawn from.
