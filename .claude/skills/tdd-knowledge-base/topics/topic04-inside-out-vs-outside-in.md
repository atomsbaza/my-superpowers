# Topic 4: Inside-Out vs Outside-In Design Strategies

## Core Idea
Inside-Out and Outside-In are two directional strategies for where TDD begins: Inside-Out starts at core business logic and builds outward toward the UI, while Outside-In starts at a user-facing scenario and drills inward toward the logic. Neither is universally superior — the research frames the choice as a function of project phase and context, not doctrine.

## Frameworks Introduced
- **Inside-Out (Bottom-Up)**: Flow is Logic → Services → APIs → UI. Developer-driven, focused on technical quality and component isolation; design emerges from implementation.
  - When to use: legacy modernization, API-first development, microservices, technical-debt reduction — cases where domain logic is already established.
  - How: begin by writing tests against the core business logic or database interactions with no dependents yet, then build each successive layer (service, API, UI) on top of the layer already proven correct beneath it.
- **Outside-In (Top-Down)**: Flow is UI → APIs → Services → Logic. Collaborative — involves product owners and QA — and focuses on user experience and business value; design is "broad-brush," driven by roles and interactions.
  - When to use: new feature development, customer-facing applications, and scenarios where business requirements are unclear and need to be discovered through the UI-level test.
  - How: write a failing acceptance/UI-level test for the user scenario first, then stub or fake every collaborator the scenario needs beneath it, progressively replacing each stub with a real, tested implementation until the top-level test goes green without help.

## Key Concepts
- **Business Gap**: the risk, specific to pure Inside-Out work, that a technically solid, well-covered implementation nonetheless misses what the user or business actually needed, because nothing forced the requirement to be validated end-to-end.
- **YAGNI ("You Ain't Gonna Need It")**: the principle of not building capability the current requirement doesn't call for; Outside-In development is claimed to structurally resist YAGNI violations because nothing gets built below the UI unless a failing outer test demands it.
- **"Quick-and-dirty" internal implementations**: the risk, specific to pure Outside-In work, that developers fake or hard-code inner-layer behavior just enough to turn the outer test green, deferring real design of the internals.
- **Broad-brush design**: the Outside-In habit of sketching roles and interactions loosely at the start (via the outer test and its stubs) rather than committing to a detailed internal data model up front.

## Mental Models
- **Two ends of one pipe**: both strategies build the same Logic ↔ Services ↔ APIs ↔ UI chain; they differ only in which end you touch first and which end therefore gets validated earliest.
- **Foundation-first vs. contract-first**: Inside-Out treats the domain model as the foundation to pour before anything is built on top; Outside-In treats the user-facing contract as the thing that must be right first, with the foundation poured underneath it as needed.
- **Discovery vs. confirmation**: Outside-In is a discovery process — the outer test itself surfaces what the lower layers must do; Inside-Out is closer to confirmation — you already believe you know the domain and are proving it works, then exposing it.
- **The research explicitly correlates this axis with the Detroit/London schools (Topic 3)**: Inside-Out design is associated with Detroit/state-verification/emerging design; Outside-In design is associated with London/interaction-verification/broad-brush design via mocked roles. The correlation is presented as strong but not absolute — the two axes (direction, and school/verification style) are conceptually separable.

## Anti-patterns
- **Pure Inside-Out without an outer check**: building comprehensively tested, "heavy" data models and services with no acceptance-level test validating they solve the actual user problem — the Business Gap. High unit coverage and a solid technical foundation can coexist with a product that doesn't fit the requirement, discovered only late during integration.
- **Pure Outside-In without following through on the internals**: leaving "quick-and-dirty" fakes or shortcuts inside the lower layers once the outer test passes, instead of returning to give those layers real design and tests — the outer-green test creates false confidence that the feature is actually done.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Dimension | Inside-Out | Outside-In |
| :--- | :--- | :--- |
| **Flow** | Logic → Services → APIs → UI | UI → APIs → Services → Logic |
| **Characteristics** | Developer-driven; technical quality and component isolation; design emerges from implementation | Collaborative (product owners + QA involved); user experience and business value; broad-brush design via roles/interactions |
| **Advantages** | Fast feedback via unit tests; high code coverage; solid technical foundations | Business alignment; surfaces user-perspective issues early; resists YAGNI by only building what the UI requires |
| **Disadvantages** | Risk of "Business Gap" (requirements missed despite technical polish); late discovery of integration issues; temptation toward "heavy" data models the UI doesn't need | Outer tests stay red for long periods; requires complex test setups (stubs for every lower layer); UI-level tests are comparatively slow and brittle; tempts "quick-and-dirty" internals |
| **Best Use Cases** | Legacy modernization, API-first development, microservices, technical-debt reduction | New feature development, customer-facing applications, unclear/evolving business requirements |

## Worked Example
Consider building a new checkout flow.

**Inside-Out approach:** Start by TDD-ing the `Order` and `Pricing` domain logic in isolation — tax calculation, discount application, inventory decrement — each backed by fast unit tests with no UI or API yet in existence. Once the core logic is solid and covered, wrap it in a service layer, then an API endpoint, then finally wire up the checkout UI last. Risk: the pricing engine could end up modeling promotions in a way that's technically elegant but doesn't match how the UI actually needs to present a discount to the shopper — the gap surfaces only once the UI is finally connected.

**Outside-In approach:** Start by writing a failing acceptance test that drives the checkout UI as a shopper would: "add item to cart, enter payment, click Place Order, see confirmation." Everything beneath the UI — the payment API call, the order service, the pricing logic — is stubbed to make this single scenario pass first (e.g., the payment API stub always "succeeds"). The team then works inward, replacing each stub with a real, independently tested implementation (a real payment adapter, a real pricing service) until the acceptance test passes without any fakes left behind. Risk: under time pressure, the pricing logic stub might quietly become the shipped implementation without ever getting proper unit-level design and test coverage.

A pragmatic team often blends both: Outside-In to shape the checkout contract and confirm business alignment, Inside-Out discipline applied to each inner layer as it gets "filled in," so neither the Business Gap nor the quick-and-dirty-internals failure mode is left unaddressed.

## Key Takeaways
1. Inside-Out and Outside-In are complementary directions through the same architecture, not competing methodologies — most real systems get built with a mix.
2. Choose Outside-In/London style for new features, to force business alignment and avoid YAGNI violations via broad-brush, role-driven design.
3. Choose Inside-Out/Detroit style for legacy modernization or technical-debt reduction, where the domain logic is already established and the priority is a solid, well-covered foundation.
4. Pure Inside-Out risks a "Business Gap" — technically excellent code that doesn't solve the right problem, discovered only at integration time.
5. Pure Outside-In risks "quick-and-dirty" internals — a passing acceptance test masking under-designed, under-tested lower layers.
6. This direction axis strongly correlates with, but is conceptually distinct from, the Detroit-vs-London (Classicist-vs-Mockist) axis in Topic 3 — direction is about where you start; school is about how you isolate and verify.
7. Use the Three Amigos practice (Business, Developer, Tester collaborating on acceptance criteria before coding) as a structural guard against the Business Gap regardless of which direction you choose.

## Connects To
- **Topic 3 (Classicist vs Mockist Schools)**: Detroit/Classicist design is Inside-Out with state verification and emerging design; London/Mockist design is Outside-In with interaction verification and broad-brush, mock-driven design — the two axes track each other closely in the research but are not identical.
- **Topic 6 (BDD & ATDD)**: Outside-In at the acceptance level is effectively what BDD/ATDD formalizes — starting from a user- or business-readable scenario (e.g., Gherkin Given/When/Then) and working inward, with the Three Amigos collaborating on that outer scenario before code exists.
- **Testing Pyramid (Topic 5)**: Inside-Out naturally produces a pyramid shape (many fast unit tests at the base); Outside-In naturally starts at the top of the pyramid (a slow acceptance/UI test) and pushes the team to backfill the base underneath it.
- **YAGNI**: the principle most directly reinforced by Outside-In practice, since nothing below the UI gets implemented until an outer failing test demands it.
