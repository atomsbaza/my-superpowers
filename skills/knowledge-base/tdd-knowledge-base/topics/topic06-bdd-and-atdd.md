# Topic 6: BDD and ATDD

## Core Idea
TDD is a developer tool that answers "is the code correct?" — but it doesn't by itself bridge to business meaning. BDD and ATDD extend the red-green-refactor discipline into collaboration with non-programmers, using natural language and cross-role conversation so that "correct code" and "the right feature" become the same target.

## Frameworks Introduced
- **BDD (Behavior-Driven Development)**: Focus on system behavior and user scenarios, expressed with "Given/When/Then" (Gherkin) syntax in plain natural language.
  - When to use: whenever specifications need to be understandable and validatable by non-programmers (product owners, business stakeholders) — not just developers.
  - How: write scenarios as executable specifications; because they stay in sync with the system (they fail when behavior drifts), they double as "living documentation" rather than documentation that quietly rots.
- **ATDD (Acceptance Test-Driven Development)**: Focus on meeting specific business acceptance criteria, answering "does the system do what it should?"
  - When to use: at the acceptance-test layer of the testing pyramid, and specifically before development begins on a feature, to prevent the "business gap" (technically correct code that misses the actual requirement).
  - How: the "Three Amigos" — a Business representative, a Developer, and a Tester — collaborate to define acceptance tests together, before any code is written. The research is explicit that this is a *process* (a conversation), not just a document format.

## Key Concepts
- **Gherkin**: A domain-specific language using Given/When/Then syntax to describe system behavior in plain, structured English.
- **Given/When/Then**: The three-part scenario grammar — Given sets up initial context, When describes the triggering action, Then states the expected outcome.
- **Living Documentation**: Scenarios that remain accurate because they are also executable tests; if the behavior changes and the doc isn't updated, the scenario fails, surfacing the drift immediately instead of letting the doc go stale.
- **Three Amigos (Business/Dev/Test)**: The three-role collaboration pattern for writing acceptance criteria — business defines what's valuable, dev defines what's feasible, test defines what's verifiable and what edge cases exist.
- **Business Gap**: The failure mode ATDD is designed to prevent — a system that is technically well-built (passes all unit tests) but doesn't solve the actual user/business problem, typically because acceptance criteria were decided unilaterally or too late.

## Mental Models
- TDD asks "is the code correct?" (developer-facing, implementation-level).
- BDD asks "what should the system do, described in language everyone can read?" (behavior-facing, scenario-level).
- ATDD asks "does the system do what it should, according to business criteria agreed up front?" (acceptance-facing, cross-role agreement).
- These three are not competing methodologies but layers of the same discipline aimed at progressively wider audiences: TDD for developers, BDD for shared vocabulary, ATDD for the go/no-go business gate. The research explicitly frames this as the natural companion to Outside-In testing (Topic 4) and sits at the top of the testing pyramid (Topic 5) as the acceptance-test layer.

## Anti-patterns
- **Skipping the Three Amigos conversation**: writing Gherkin scenarios unilaterally (e.g., a developer writing them alone after the fact) defeats the purpose — the research is explicit that the value comes from the *collaboration before coding begins*, not the Given/When/Then syntax itself.
- **Gherkin as implementation script, not business spec**: a scenario written around UI mechanics or internal method calls ("Given the user clicks button #save-btn") rather than business outcomes stops being readable by non-programmers, which defeats BDD's stated benefit of enabling non-programmer validation. (This specific failure mode is inferred by extension from the research's general warning against tests coupled to implementation details — e.g., "The Inspector" anti-pattern and DHH's critique of brittle, implementation-coupled tests — rather than a BDD-specific anti-pattern named in the sources.)
- **Letting acceptance tests become the only tests**: the research's pyramid guidance is that acceptance/ATDD tests should be a "minimal suite" layered on top of a large base of fast unit tests — treating ATDD as a replacement for unit-level TDD inverts the pyramid and reintroduces the Slow Poke anti-pattern (Topic 8) at the acceptance layer.

## Code Examples
```gherkin
Feature: Withdraw cash from account

  Scenario: Successful withdrawal within balance
    Given an account with a balance of $100
    When the customer requests a withdrawal of $40
    Then the withdrawal is approved
    And the account balance is $60

  Scenario: Withdrawal exceeds balance
    Given an account with a balance of $100
    When the customer requests a withdrawal of $150
    Then the withdrawal is declined
    And the account balance remains $100
```
- **What it demonstrates**: a business-readable scenario pair (happy path + edge case) that a Business Amigo could review and sign off on without reading code — the Given/When/Then structure separates setup, action, and expected outcome, and the scenario describes behavior/outcome, not implementation.

## Reference Tables
| Practice | Focus | Question Answered | Stakeholders |
| :--- | :--- | :--- | :--- |
| TDD | Implementation correctness | "Is the code correct?" | Developers |
| BDD | System behavior and user scenarios | "What should the system do?" (in shared language) | Developers + non-programmers |
| ATDD | Business acceptance criteria | "Does the system do what it should?" | Business, Developer, Tester (Three Amigos) |

(Table content reconstructed directly from Section 3 of the Briefing Doc, "Collaborative Frameworks: TDD, BDD, and ATDD.")

## Worked Example
Reconstructing a plausible Three Amigos session for a feature, "apply a discount code at checkout," from the research's description of the process:

1. **Business** amigo states the goal: "Customers should be able to enter a discount code at checkout and see the reduced total before paying." They flag that codes can be invalid or expired.
2. **Developer** amigo asks clarifying questions about edge cases: What happens with a code that's valid but already used? Can two codes stack? They surface technical constraints (e.g., discount validation is a separate service call).
3. **Tester** amigo pushes for coverage of negative and boundary cases: empty code field, expired code, code for a different region, network failure during validation.
4. Together they converge on acceptance scenarios *before* coding starts:
   ```gherkin
   Scenario: Valid discount code reduces total
     Given a cart with a subtotal of $50
     When the customer applies discount code "SAVE10"
     Then the total is reduced by 10%
     And the discount code is shown as applied

   Scenario: Expired discount code is rejected
     Given a cart with a subtotal of $50
     When the customer applies an expired discount code
     Then an error message explains the code has expired
     And the subtotal remains unchanged
   ```
5. These scenarios become the acceptance-test layer of the pyramid (Topic 5) and only afterward does the developer drop into TDD's red-green-refactor loop (Topic 2) to implement the underlying logic, likely Outside-In (Topic 4), using these scenarios as the outer failing test.

## Key Takeaways
1. BDD's core mechanism is a shared vocabulary (Given/When/Then / Gherkin) that lets non-programmers read and validate specifications directly.
2. ATDD's core mechanism is a *process* — the Three Amigos collaborating before coding starts — not just a test format; skipping the conversation defeats the purpose even if Gherkin syntax is used.
3. BDD scenarios function as living documentation only because they are executable and fail on drift; documentation that isn't wired to test execution doesn't get this property.
4. ATDD sits at the acceptance layer of the testing pyramid and should remain a minimal suite on top of a large unit-test base, not a replacement for TDD.
5. The "business gap" — technically correct code that misses the real requirement — is the specific failure ATDD is designed to prevent by involving Business, Dev, and Test together up front.
6. TDD, BDD, and ATDD answer three different questions ("is the code correct?" / "what should it do?" / "does it do what it should?") aimed at progressively wider audiences, not three competing methodologies.

## Connects To
- **Topic 5 (Testing Levels and the Pyramid)**: acceptance tests (ATDD) form the top, business-facing layer of the pyramid, meant to stay a "minimal suite" above the unit-test foundation.
- **Topic 4 (Outside-In vs Inside-Out)**: Outside-In testing shares ATDD/BDD's premise of starting from user-facing scenarios and business requirements before drilling into implementation; the research frames Outside-In as the natural companion to ATDD's Three Amigos process.
- **Topic 8 (Anti-Patterns and Pitfalls)**: BDD/ATDD scenarios are vulnerable to the same anti-patterns as unit tests (The Inspector, Excessive Setup, brittleness from implementation coupling) if written around mechanics instead of business outcomes.
- **Dan North (external concept)**: widely credited as the originator of BDD, though the research corpus itself does not name him directly — flagged here as external knowledge, not sourced from the provided material.
- **Cucumber (external concept)**: the best-known Gherkin-executing tool associated with BDD; likewise not explicitly named in the provided sources and included as commonly-known external context.
