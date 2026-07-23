# Topic 5: Testing Levels and the Testing Pyramid

## Core Idea
No single test type gives complete confidence at acceptable cost — TDD practitioners layer several levels of testing, each trading scope and realism for speed, and deliberately keep the fast, narrow layer largest so the suite as a whole stays both trustworthy and cheap to run.

## Frameworks Introduced
- **The Testing Pyramid**: A layered model — Unit Tests at the wide base, Integration Tests above them, Contract Tests validating boundaries between systems, Acceptance Tests (ATDD) verifying business criteria, and End-to-End (E2E) Tests at the narrow top. Volume decreases and cost/speed/fragility increase as you move up the pyramid; the research does not give exact ratios, but the consistent framing across sources is "many fast unit tests, progressively fewer slower tests above them."
  - When to use: as a portfolio strategy for the whole test suite, not a rule for any single test — decide the shape of the *suite*, then decide individual tests to fill it.
  - How: write the bulk of tests as isolated, fast unit tests during red-green-refactor; add a smaller layer of integration tests where components must be checked together; add contract tests at system/service boundaries; add a minimal layer of acceptance/E2E tests to confirm the system is "wired up" correctly end-to-end.

## Key Concepts
- **Unit Tests**: Smallest-scope tests that exercise a single unit in isolation, defining its contract and driving its design; high speed, low cost, and the largest layer of the pyramid.
- **Integration Tests**: Tests that verify multiple components work together correctly once combined, catching wiring and interaction problems unit tests can't see.
- **Contract Tests**: Tests that validate the communication boundary between two systems (e.g., a service and its consumer) so each side can evolve independently without breaking the other.
- **Acceptance Tests / ATDD**: Tests that verify the system meets user expectations and business criteria, typically specified collaboratively before coding via the "Three Amigos."
- **End-to-End (E2E) Tests**: Tests that validate an entire workflow from the user's perspective, exercising the real, wired-together system; the research notes these are especially important for London-school (mockist) practitioners as a check that heavily mocked units still integrate correctly in reality.
- **"Three Amigos"**: The collaboration pattern of Business Expert, Developer, and Tester jointly defining acceptance criteria before coding begins, intended to prevent a "Business Gap" between what's built and what's needed.

## Mental Models
- **Confidence vs. cost trade-off**: each layer up the pyramid buys more realism and end-to-end confidence but costs more in run time, flakiness, and maintenance — so higher layers should only cover what lower layers structurally cannot.
- **The pyramid as portfolio allocation, not a checklist**: like a financial portfolio, the goal is a balanced mix weighted toward the cheap, fast, reliable asset (unit tests), with smaller strategic allocations to more expensive, higher-fidelity layers.
- **E2E as a wiring check, not a design driver**: E2E and acceptance tests answer "is the system correctly assembled and does it satisfy the business goal," while unit tests (via TDD) answer "is this piece of logic correct and well-designed" — conflating the two jobs onto one layer is where teams get into trouble.
- **Mockist practitioners still need the top of the pyramid**: because London-school unit tests isolate collaborators via mocks, they cannot verify real integration — E2E tests are the counterbalancing check that mocked contracts hold in reality.

## Anti-patterns
- **Inverted pyramid / "ice cream cone"**: too many slow, brittle E2E or UI tests and too few fast unit tests, leading to a suite that is slow to run, expensive to maintain, and discourages frequent execution (related to the "Slow Poke" anti-pattern from Topic 8).
- **Skipping the middle layers**: relying only on unit tests plus E2E tests with no integration or contract tests leaves gaps at component and service boundaries — problems surface late, in the most expensive layer to debug.
- **Treating acceptance tests as a substitute for the Three Amigos conversation**: writing acceptance criteria without Business/Developer/Tester collaboration reintroduces the "Business Gap" the layer is meant to close.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Layer | Scope | Speed | Cost | Purpose |
|---|---|---|---|---|
| Unit | Single unit/class, isolated | Fastest | Lowest | Define contracts, drive design, catch logic errors early |
| Integration | Multiple components combined | Fast–moderate | Low–moderate | Verify components collaborate correctly |
| Contract | Boundary between two systems/services | Moderate | Moderate | Validate producer/consumer communication without full integration |
| Acceptance (ATDD) | Business-facing scenario | Slower | Higher | Confirm the system meets user/business expectations |
| End-to-End (E2E) | Entire workflow, real system | Slowest | Highest | Validate the fully wired system from the user's perspective |

## Worked Example
Reconstructed from the research's framing (not from a single cited example): imagine building a "checkout" feature. Unit tests, written first via red-green-refactor, cover the discount calculation, tax logic, and order-total logic in isolation — many small, fast tests driving the design of each piece. An integration test then verifies the checkout service correctly calls the inventory and pricing components together and gets a coherent total. A contract test validates that the checkout service's request/response shape matches what the payment-processing service expects, so either side can change internals without breaking the other. An acceptance test, written from a Three Amigos conversation, expresses the business rule "a customer with a valid coupon and in-stock items can complete checkout" in business language. Finally, a single E2E test drives the real UI or API through an actual purchase to confirm the whole system — inventory, pricing, payment, and UI — is correctly wired together. The unit layer is large (many tests, one per logic branch); the E2E layer is deliberately minimal (one or a few tests covering the critical path).

## Key Takeaways
1. Build the suite as a pyramid: many fast unit tests as the foundation, fewer integration and contract tests in the middle, and a minimal set of acceptance/E2E tests at the top.
2. Use unit tests (via TDD) to drive design and correctness of individual pieces; reserve E2E and acceptance tests for confirming the system is correctly wired and meets business goals.
3. London-school (mockist) teams especially need E2E tests, since heavy mocking at the unit level can't verify real integration.
4. Contract tests let independent services or components evolve without full integration testing, by pinning down the boundary between them.
5. Define acceptance criteria collaboratively via the "Three Amigos" before coding, to prevent gaps between business intent and what gets built.
6. An inverted pyramid (too many slow E2E tests, too few fast unit tests) is a recognized anti-pattern that slows down the whole team's feedback loop.
7. The pyramid describes the shape of the whole suite, not a rule for individual tests — decide test type by what question that test needs to answer.

## Connects To
- **Topic 6 (BDD & ATDD)**: expands on the Acceptance Tests / "Three Amigos" layer of the pyramid in depth, covering how acceptance criteria are specified and automated.
- **Topic 4 (Inside-Out vs Outside-In)**: Outside-In/London-style development starts near the top of the pyramid (a user scenario or UI test) and works down, making E2E and acceptance tests the entry point rather than the capstone.
- **Topic 3 (Classicist vs Mockist Schools)**: the mockist (London) school's heavy use of mocks at the unit level is the reason E2E tests are called out as "essential" for that school specifically.
- **Topic 8 (Anti-Patterns & Pitfalls)**: the "Slow Poke" anti-pattern (tests too slow to run often) is the direct symptom of an inverted or top-heavy pyramid.
- **External concept**: Mike Cohn's Testing Pyramid — the widely cited origin of the pyramid shape as a testing strategy metaphor; the research references the concept generically without quoting Cohn's original formulation, so treat the exact layer names/ratios above as this research's synthesis rather than a verbatim reproduction of Cohn's model.
