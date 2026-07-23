# Topic 8: Anti-Patterns and Pitfalls

## Core Idea
Across the TDD literature a recurring set of named failure modes shows up whenever tests are written for the wrong reasons — to pad coverage, to avoid setup pain, or to lock down implementation instead of behavior. These anti-patterns are not random bugs; they are predictable consequences of specific bad habits, which is why naming them turns "this test feels off" into a checklist you can run against any suite.

## Frameworks Introduced
- **The TDD Anti-Pattern Catalog** (the named anti-pattern list itself as the framework)
  - When to use: as a code-review / test-review checklist, applied to any test file before merging or during a suite health audit
  - How: scan the test suite against each named anti-pattern below; a test that matches a name is a signal to refactor the test (or the design it exposes), not to ignore the smell

## Key Concepts
- **The Liar**: a test that passes but does not actually verify the requirement it claims to cover — green, but meaningless.
- **The Slow Poke**: a test (or suite) so slow to run that it discourages developers from running it frequently, eroding the fast-feedback loop TDD depends on.
- **The Mockery**: a test so saturated with mocks/stubs that it only confirms the code called the mock correctly, giving no confidence the system behaves correctly end-to-end.
- **The Inspector**: a test that reaches into an object's internal state to make assertions, violating encapsulation and breaking on any internal refactor even when observable behavior is unchanged.
- **Excessive Setup**: a test that requires large amounts of arrange/setup code just to get the system into a testable state, making the test hard to read and hiding the actual behavior under test.
- **Test-Induced Damage**: production code deliberately deformed (e.g., everything made public, unnecessary interfaces/indirection added) purely to satisfy testability, at the expense of the overall architecture — DHH's central 2014 critique.
- **Vulnerable Tests**: tests (typically London-school, mock-heavy) that break whenever an internal implementation detail changes, even though the external output is still correct — a symptom of over-specifying interactions rather than outcomes.
- **Mocking What You Don't Own**: mocking third-party libraries, frameworks, or external APIs directly in tests instead of wrapping them behind an adapter/gateway you own and mocking that — couples your test suite to an interface you don't control and can't guarantee matches reality.

## Mental Models
- **Two axes of failure**: anti-patterns split into *false confidence* problems (The Liar, The Mockery — tests that look protective but aren't) and *friction* problems (The Slow Poke, Excessive Setup — tests that are honest but too costly to keep running).
- **Coupling direction matters**: The Inspector, Vulnerable Tests, and Test-Induced Damage are all variations of one root cause — tests (or the design) coupled to *how* something is done rather than *what* it produces. Coupling to behavior survives refactoring; coupling to implementation does not.
- **The mock is a promise, not a fact**: Mocking What You Don't Own and The Mockery both stem from treating a stand-in object as equivalent to the real dependency; if the real API changes shape, the mock silently drifts out of sync while tests stay green.
- **Pain is signal, not noise**: several sources frame Excessive Setup and Test-Induced Damage not as "just write better tests" but as feedback that the production design itself has a coupling or responsibility problem — the fix is often in the code under test, not the test.

## Anti-patterns
- **The Liar**: passes without truly testing the requirement — false sense of safety.
- **The Slow Poke**: too slow to run often — kills the tight feedback loop TDD relies on.
- **The Mockery**: over-mocked to the point of only testing mock interactions — no real confidence.
- **The Inspector**: asserts on internal state — brittle to safe refactors, violates encapsulation.
- **Excessive Setup**: huge arrange blocks — obscures intent, expensive to maintain.
- **Test-Induced Damage**: architecture warped purely for testability — DHH's core complaint from the 2014 debate.
- **Vulnerable Tests**: London-style tests tied to internal calls — break on refactor despite correct output.
- **Mocking What You Don't Own**: mocking third-party code directly instead of via an owned adapter — couples tests to an interface you can't control.

## Code Examples
(omit — this topic is a checklist, not code-heavy)

## Reference Tables
| Anti-pattern | Symptom | Fix |
|---|---|---|
| The Liar | Test passes but doesn't actually exercise/verify the requirement | Assert on real requirement outcomes; delete or rewrite tests that pass trivially |
| The Slow Poke | Suite/tests take too long, developers stop running them | Push slow tests out of the fast unit tier; parallelize; isolate I/O; run slow suite less frequently (CI-only) |
| The Mockery | Test only verifies mocks were called, not real behavior | Reduce mock count; prefer state verification (Detroit-style) for core logic; reserve mocks for true boundaries |
| The Inspector | Assertions reach into private/internal state | Assert only on public API / observable output; make internals actually private |
| Excessive Setup | Hundreds of lines of arrange code per test | Extract test data builders/factories; simplify the design under test to reduce required collaborators |
| Test-Induced Damage | Production code reshaped (excess interfaces, everything public) purely for testability | Favor testing through natural seams; don't add indirection whose only purpose is a test double |
| Vulnerable Tests | Test breaks on internal refactor even though output is unchanged | Test behavior/output, not call sequences; loosen mock verification to what truly matters |
| Mocking What You Don't Own | Tests mock third-party library/API types directly | Wrap external dependency in an adapter you own; mock the adapter, not the library |

## Worked Example
(omit — this topic has no single running example, it's a checklist)

## Key Takeaways
1. Treat this catalog as a literal review checklist: for every test file, ask which named anti-pattern (if any) it resembles before approving it.
2. False-confidence anti-patterns (The Liar, The Mockery) are more dangerous than friction anti-patterns (The Slow Poke, Excessive Setup) because they hide risk instead of just costing time.
3. Excessive Setup and Test-Induced Damage are often symptoms of a design problem, not a test-writing problem — fix the collaborator count or responsibility split before adding more test scaffolding.
4. Vulnerable Tests and The Inspector both come from asserting on "how" instead of "what" — prefer output/state verification over call/implementation verification whenever the school of choice allows it.
5. Always mock through an adapter you own; never mock a third-party type directly — this single rule prevents most instances of Mocking What You Don't Own.
6. When a mock-heavy design keeps breaking on refactors, treat it as a prompt to swap some mocks for real collaborators once the design has stabilized, converting brittle unit tests into more resilient "mini-acceptance tests."
7. Use this catalog during retrospectives on slow or brittle suites — most chronic test-suite pain maps onto one of these eight named causes.

## Connects To
- **Topic 3 (Classicist vs Mockist Schools)**: The Mockery, The Inspector, and Vulnerable Tests are largely London-school-specific risks that arise from heavy interaction-based testing; Detroit-style state verification sidesteps several of them by design.
- **Topic 12 (The "Is TDD Dead" Debate)**: DHH's critique of Test-Induced Design Damage and heavy mocking is the direct real-world flashpoint for this topic's Test-Induced Damage and Mocking What You Don't Own entries; Beck and Fowler's response ("mock almost nothing") reinforces the fixes in the reference table.
- **External concept — "Don't mock what you don't own"**: a London School best practice cited directly in the research as the rule underlying the Mocking What You Don't Own anti-pattern.
