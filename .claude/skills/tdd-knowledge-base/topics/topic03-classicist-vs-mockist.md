# Topic 3: Classicist (Detroit) vs Mockist (London) Schools

## Core Idea
TDD split into two schools over one unresolved question — "what is a unit, and what should be isolated?" — and the answer each gives (state verification of a real module vs. interaction verification of a single mocked-out class) cascades into different design flows, different refactoring safety, and different debugging experiences.

## Frameworks Introduced
- **Detroit School (Classicist)**: state verification, minimal mocking, module-level units. Originated with Kent Beck (Detroit, late 1990s), the original XP lineage.
  - When to use: when you want tests decoupled from implementation detail so refactors stay cheap; well-suited to well-understood domain logic, legacy modernization, and code where the "real" collaborators are cheap and fast to run.
  - How: define the unit as a module — a class or a small set of related classes working together — and test it with real collaborators, reaching for a test double only when a collaborator is "awkward" (e.g., an external API, the filesystem, the network, or nondeterministic time). Verify by checking the final state of the system after the operation, not how it got there. Isolation here means isolating *tests from each other* (so they can run in parallel and stay independent), not isolating the unit from its own collaborators.
- **London School (Mockist)**: interaction verification, extensive mocking, class-level units. Distilled by Steve Freeman & Nat Pryce (London Extreme Tuesday Club, early 2000s) in *Growing Object-Oriented Software, Guided by Tests* (GOOS).
  - When to use: when discovering a design through the roles objects play and how they collaborate — particularly for new feature work driven outside-in from a user scenario, where the "shape" of the collaborators is still being decided.
  - How: define the unit as a single class — the Subject/System Under Test (SUT) — and isolate it completely from its dependencies by replacing every collaborator with a mock. Verify by checking interactions: were the right methods called, with the right arguments, in the right way? A dependency that is awkward to mock is treated as a design smell to fix immediately, not a testing inconvenience to work around.

## Key Concepts
- **State Verification**: asserting on the final observable state of the object or system after the operation under test, characteristic of the Detroit school.
- **Interaction Verification**: asserting on *how* the SUT called its collaborators (which methods, with what arguments, how many times), characteristic of the London school.
- **Subject/System Under Test (SUT)**: the specific class or method a given test is verifying; in the London school this is deliberately narrowed to one class per test.
- **Test Double**: the umbrella term for any stand-in object used in place of a real dependency; the taxonomy includes:
  - **Stub** — returns hardcoded answers to calls made during the test.
  - **Mock** — verifies interactions (calls and parameters) between objects.
  - **Fake** — a working but simplified implementation (e.g., an in-memory database in place of a real one).
  - (Spies are named in the taxonomy definition of "test double" in the research but not separately defined — treat as a double that records calls for later inspection, an interaction-verification tool the London school leans on.)
- **"Don't mock what you don't own"**: a London-school best practice warning against mocking third-party libraries or external APIs directly; instead, write a thin adapter layer around the external dependency and mock the adapter, so the mock's contract is one you actually control.
- **Vulnerable tests**: London-style tests that hardcode specific internal calls can break during a refactor even when behavior is unchanged, because the mock expectations are tied to implementation detail rather than outcome.

## Mental Models
- **"If an object is hard to test, then it's hard to use"** (Detroit School Maxim) — testing difficulty is treated as direct architectural feedback: friction in writing a test signals a real design problem, not just an inconvenient test.
- **"Programmer tests should be sensitive to behaviour changes and insensitive to structural changes"** (Kent Beck) — the design goal behind Detroit's preference for state verification: a test suite should scream when behavior breaks and stay silent through internal refactors.
- **Design flow follows verification style** — Detroit's state verification pairs naturally with **Inside-Out** design (start from core logic, build outward, let design emerge through implementation); London's interaction verification pairs naturally with **Outside-In** design (start from a user scenario, use mocked roles to drive the design of collaborators before they exist). See Topic 4.
- **Two schools as a fork, not a contradiction** — Detroit and London are divergent, defensible answers to the same open question about units and isolation, not a right-vs-wrong split; the trade-offs below determine which fits a given situation, not which is "correct" TDD.

## Anti-patterns
- **The Mockery**: using mocks for every single interaction, producing tests that pass without proving the system actually works when its parts are integrated — the systemic risk of leaning too far into the London style.
- **The Inspector**: tests that rely too heavily on checking an object's internal state, breaking on every minor refactor even when behavior is unchanged — the systemic risk of leaning too far into naive state verification without respecting encapsulation.
- **Mocking types you don't own**: mocking a third-party library or external API directly instead of writing an adapter and mocking that — creates brittle tests that assume implementation details of code outside your control, and the mock can silently drift from the real library's actual behavior.
- **Vulnerable tests from over-mocking**: hardcoding expectations about exactly which internal calls happen turns tests into a second copy of the implementation, so tests fail on refactors that don't change behavior — the concrete failure mode Kent Beck's quote above warns against.

## Code Examples
(omit — the research does not include a concrete reconstructable mock-vs-state-check code sample; see the Worked Example below for a prose-level illustration instead)

## Reference Tables
| Feature | Detroit School (Classicist) | London School (Mockist) |
| :--- | :--- | :--- |
| **Origin** | Kent Beck (Detroit, late 1990s) | Steve Freeman & Nat Pryce (London, early 2000s) |
| **Primary Goal** | Is the code correct? | How does the system behave? |
| **Unit Definition** | A module (a class, function, or set of related classes). | A single class or method. |
| **Isolation** | Isolation of tests from each other (allowing parallel, independent runs). | Isolation of the Subject/System Under Test (SUT) from its dependencies. |
| **Mocking / Test Doubles** | Minimal; real objects used unless a collaborator is "awkward" (e.g., external APIs). | Extensive; mocks and stubs used for all collaborators. |
| **Verification** | State verification — checking the final state of an object or system. | Interaction verification — checking whether specific methods were called, how, and with what. |
| **Design Style / Flow** | Inside-Out — starts with core logic, design emerges via implementation. | Outside-In — starts with user scenarios, broad-brush design via roles/interactions. |
| **Refactoring ease** | Generally easier — tests aren't tied to internal implementation details. | Often more "vulnerable" — mocks hardcode specific internal calls, so tests can break on refactors that don't change behavior. |
| **Bug Localization** | Weaker — a bug in one class can cascade and fail many tests of dependent classes. | Stronger — a failing test almost always pinpoints the bug to the single class under test. |
| **Design Influence** | Design feedback arrives indirectly, through difficulty of setting up real collaborators. | Forces immediate confrontation of a dependency's "awkwardness" — if it's hard to mock, it's treated as hard to use, prompting design reconsideration right away. |

## Worked Example
Consider testing an `OrderProcessor` that validates an order, charges a payment gateway, and then updates an inventory count.

- **Detroit-style test**: instantiate the real `Order`, a real (or in-memory `Fake`) inventory store, and only stub the one genuinely awkward collaborator — the external `PaymentGateway` API — since hitting a real payment provider in a test is impractical. Run `process(order)` and then assert on **state**: the order's status is now `"completed"`, and the inventory count decreased by the ordered quantity. The test doesn't care how many internal methods were called to get there, only that the end state is correct.
- **London-style test**: instantiate `OrderProcessor` as the SUT and replace *all* of its collaborators — `Order`, `PaymentGateway`, and `InventoryStore` — with mocks. Run `process(order)` and assert on **interactions**: `paymentGateway.charge()` was called exactly once with the order's total, and `inventoryStore.decrement()` was called with the correct product ID and quantity. The test proves the SUT orchestrates its collaborators correctly, in complete isolation from whether those collaborators actually behave correctly themselves (that's covered by their own tests).

If a later refactor merges `InventoryStore.decrement()` into a single `InventoryStore.reserve()` call that also checks stock levels, the Detroit test above still passes unchanged (the end state is the same). The London test breaks, even though behavior is identical, because it hardcoded the old interaction — the concrete instance of a "vulnerable test."

## Key Takeaways
1. The real dividing line isn't "mocks vs no mocks" — it's what a test is allowed to know about: Detroit tests know about outcomes, London tests know about collaborations.
2. Detroit-style tests buy refactoring safety at the cost of weaker bug localization; London-style tests buy precise bug localization at the cost of refactor fragility — pick based on which failure mode is more expensive for your codebase.
3. In the London school, an awkward-to-mock dependency is treated as a live design signal, not a testing inconvenience — that feedback loop is a deliberate feature, not a side effect.
4. "Don't mock what you don't own" applies regardless of school: wrap third-party/external dependencies in an adapter you control, and mock the adapter, not the library.
5. Design flow and verification style aren't independent choices — Inside-Out naturally pairs with Detroit/state verification, Outside-In naturally pairs with London/interaction verification (Topic 4 develops this pairing further).
6. Overcommitting to either school produces a named anti-pattern: too much mocking risks "The Mockery" (tests that don't prove integration works); too much state-checking of internals risks "The Inspector" (tests that break on every refactor).
7. Treat Detroit vs London as a spectrum a team calibrates per-module, not a global, once-and-for-all methodology choice — most real codebases in the research's framing use both, matched to context.

## Connects To
- **Topic 4 (Inside-Out vs Outside-In)**: the design-flow counterpart to this split — Detroit's state verification drives Inside-Out design, London's interaction verification drives Outside-In design; read together for the full picture of how verification style shapes development order.
- **Topic 12 (The "Is TDD Dead?" Debate)**: this Detroit/London divide is a direct fault line in that debate — much of the criticism of "mock-heavy" TDD in the wider community is really a critique of the London school specifically, not TDD as a whole.
- **Topic 8 (Anti-Patterns & Pitfalls)**: "The Mockery" and "The Inspector" anti-patterns named here are the general anti-pattern catalog's concrete instances of over-committing to one school.
- **Topic 13 (XP Values & Test Code Quality)**: Kent Beck's "sensitive to behaviour, insensitive to structure" quote ties this topic directly to the XP value of Courage (confidence to refactor) and Respect (treating test code with care).
- **Steve Freeman & Nat Pryce's *Growing Object-Oriented Software, Guided by Tests* (GOOS)**: the foundational text that formalized and popularized the London School's mock-driven, outside-in approach — the primary external reference for anyone going deeper on this topic than the research corpus covers.
