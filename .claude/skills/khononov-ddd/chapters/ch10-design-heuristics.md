# Chapter 10: Design Heuristics

## Core Idea
This chapter bridges strategic analysis (Part I) and tactical patterns (Part II), giving rule-of-thumb decision trees — not hard rules — for choosing bounded context boundaries, business logic patterns, architectural patterns, and testing strategies based on subdomain type.

## Frameworks Introduced
- **Tactical Design Decision Tree**: A unified decision tree (Figure 10-7) chaining business logic pattern -> architectural pattern -> testing strategy, all driven by subdomain complexity/type.
  - When to use: At the start of implementing any subdomain, once its type (core/supporting/generic) and complexity are known, to pick a default set of tactical patterns.
  - How: Follow the chain — ask whether the subdomain involves monetary transactions/audit/deep analytics -> event-sourced domain model; else ask if business logic is complex -> domain model; else ask if data structures are complex -> active record; else transaction script. Each business logic pattern then implies an architectural pattern and testing strategy (see Reference Tables below).
- **Testing Strategy heuristics** (Testing Pyramid, Testing Diamond, Reversed Testing Pyramid): Three shapes of test-suite emphasis, each matched to a business logic implementation pattern.
  - When to use: When deciding where to invest testing effort (unit vs integration vs end-to-end) for a given component.
  - How: Domain model / event-sourced domain model -> Testing Pyramid (mostly unit tests, since aggregates/value objects are natural test units). Active record -> Testing Diamond (mostly integration tests, since logic spans service + business logic layers). Transaction script -> Reversed Testing Pyramid (mostly end-to-end tests, since logic is simple and layers are minimal, so verifying the full flow is more effective than unit-isolating trivial code).

## Key Concepts
- **Heuristic**: A rule of thumb — not mathematically guaranteed correct in all cases, but sufficient for the immediate goal by focusing on the dominant signal and ignoring noise.
- **Bounded context sizing heuristic**: Start with wider bounded context boundaries (especially around core subdomains) and decompose into smaller ones only as domain knowledge matures, because refactoring logical boundaries inside one bounded context is far cheaper than refactoring physical boundaries across bounded contexts.
- **Business logic pattern selection heuristic**: Ask in order — (1) does it track money/require audit log/need deep behavioral analytics? -> event-sourced domain model; (2) is business logic complex? -> domain model; (3) are data structures complex? -> active record; (4) otherwise -> transaction script.
- **Complexity heuristic**: Complex business logic means complicated business rules, invariants, and algorithms; simple business logic is mostly input validation. A second lens: does the ubiquitous language mainly describe CRUD, or does it describe rich business processes and rules?
- **Architectural pattern selection heuristic**: Event-sourced domain model requires CQRS (otherwise querying is crippled — fetch by ID only); domain model requires ports & adapters (otherwise the layered architecture makes it hard to keep aggregates/value objects persistence-ignorant); active record pairs with layered architecture plus an application/service layer; transaction script pairs with a minimal three-layer architecture. Exception: CQRS can benefit any pattern, not just event-sourced domain model, whenever multiple persistence read models are needed.
- **Decision tree as validation tool**: If the "correct" pattern for a subdomain you assumed is core turns out to be active record/transaction script (or vice versa for a supposed supporting subdomain), treat that mismatch as a signal to revisit your subdomain classification, not just your pattern choice.

## Mental Models
- **Subdomain type drives pattern, not the other way around**: The chapter reframes tactical pattern selection as a downstream consequence of strategic subdomain analysis from Part I — complexity and volatility (core vs. supporting vs. generic) determine which patterns fit, so getting the strategic classification right pays off tactically.
- **Boundary size as a function of the model, not a target**: Rather than optimizing for small bounded contexts (a common but misguided proxy for "good microservices"), let the model's natural cohesion determine the boundary size; treat size as an output, not an input.
- **Cost asymmetry between logical and physical refactoring**: Wide boundaries are a hedge against being wrong — mistakes inside one bounded context are cheap to fix, mistakes that span bounded context/service boundaries are expensive and require cross-team coordination.
- **Heuristics as defaults, not laws**: The whole framework is explicitly a personal, opinionated default (favor simple tools, escalate to advanced patterns only when needed) that teams may legitimately override based on their own experience (e.g., a team fluent in event sourcing might use it everywhere).

## Anti-patterns
- **Optimizing bounded context boundaries for smallness**: Treating "smaller is better" as the goal for bounded contexts (conflating them with microservices) produces boundaries that don't reflect the actual model, causing frequent cross-boundary changes and technical debt.
- **Defaulting to Domain Model + full DDD tactical patterns for every subdomain regardless of complexity**: Applying advanced patterns (domain model, event sourcing, CQRS) to simple/supporting/generic subdomains adds unnecessary complexity where a transaction script or active record would suffice — a core subdomain's competitive advantage is not necessarily technical, so not every important subdomain needs the heaviest pattern.
- **Picking a testing strategy independent of the implementation pattern**: Using a pyramid-heavy unit-test strategy for an active-record or transaction-script codebase (or an end-to-end-heavy strategy for a domain model) misallocates testing effort relative to where the real complexity and risk live.
- **Narrow bounded contexts too early in a volatile core subdomain**: Committing to fine-grained boundaries before domain knowledge stabilizes locks in guesses that are expensive to undo once physically separated.

## Code Examples
(omit — this chapter is decision-making guidance, not code)

## Reference Tables

**Tactical Design Decision Tree** (business logic pattern -> architectural pattern -> testing strategy)

| Decision Point | Signal | Recommended Pattern |
|---|---|---|
| 1. Does the subdomain track money/monetary transactions, require a consistent audit log, or need deep behavioral analytics? | Yes | Business logic: **Event-sourced domain model** |
| | No -> go to 2 | |
| 2. Is the subdomain's business logic complex (complicated rules, invariants, algorithms; language describes rich processes, not just CRUD)? | Yes | Business logic: **Domain model** |
| | No -> go to 3 | |
| 3. Does the subdomain involve complex data structures? | Yes | Business logic: **Active record** |
| | No | Business logic: **Transaction script** |

| Business Logic Pattern | Architectural Pattern | Testing Strategy |
|---|---|---|
| Event-sourced domain model | **CQRS** (required — otherwise querying is limited to fetch-by-ID) | **Testing Pyramid** (mostly unit tests) |
| Domain model | **Ports & adapters** (required — keeps aggregates/value objects persistence-ignorant) | **Testing Pyramid** (mostly unit tests) |
| Active record | **Layered architecture + application/service layer** | **Testing Diamond** (mostly integration tests) |
| Transaction script | **Minimal layered architecture** (three layers) | **Reversed Testing Pyramid** (mostly end-to-end tests) |

Exception: CQRS is not exclusive to event-sourced domain model — apply it alongside any of the other three patterns whenever a subdomain needs multiple persistence/read models.

**Bounded context sizing heuristic**

| Signal | Recommendation |
|---|---|
| Subdomain is core, domain knowledge still immature / requirements volatile | Start with wide bounded context boundaries; include frequently-interacting subdomains (core, supporting, or generic) to hedge against boundary mistakes |
| Subdomain is supporting or generic | Boundaries are safer to draw narrow early — these subdomains are more formalized and less volatile |
| Domain knowledge matures over time | Decompose wide boundaries into smaller ones as understanding improves (logical refactor, not physical) |

## Worked Example
WolfDesk's ticket lifecycle management system is a core subdomain requiring deep analysis of its behavior so an algorithm can be optimized over time. Walking the decision tree: Step 1 asks whether it needs deep behavioral analytics — yes — so the business logic pattern is the **event-sourced domain model**. That pattern requires **CQRS** as the architectural pattern (plain event sourcing without CQRS would limit querying to fetch-by-ID). CQRS/event-sourced domain model maps to the **Testing Pyramid**, so the testing strategy emphasizes unit tests against aggregates and value objects, with fewer integration and end-to-end tests. Contrast this with WolfDesk's supporting subdomain for agent shift management: it doesn't require audit/analytics (skip step 1) and likely has moderate-to-simple business logic, so it lands on **active record + layered architecture (with service layer) + Testing Diamond** (integration-test-heavy), or even **transaction script + minimal layered architecture + Reversed Testing Pyramid** if the logic is simple enough — illustrating how the same tree yields very different tactical choices depending on subdomain type.

## Key Takeaways
1. Bounded context boundaries should be a function of the model's cohesion, not an optimization target for smallness — start wide around core subdomains and narrow only as knowledge matures, since logical refactoring is far cheaper than physical.
2. Choose business logic patterns via a sequential heuristic: monetary/audit/analytics needs -> event-sourced domain model; complex logic -> domain model; complex data -> active record; otherwise -> transaction script.
3. Architectural pattern follows directly from business logic pattern: event-sourced domain model needs CQRS, domain model needs ports & adapters, active record needs layered + service layer, transaction script needs minimal layered architecture.
4. Testing strategy should match the implementation pattern's structure: domain models get a Testing Pyramid, active record gets a Testing Diamond, transaction script gets a Reversed Testing Pyramid.
5. Use a mismatch between assumed subdomain type and the pattern the heuristics recommend as a signal to revisit your strategic classification of that subdomain, not just to override the heuristic.
6. These are heuristics, not hard rules — teams with deep experience in an advanced pattern (e.g., event sourcing) may reasonably apply it broadly if that reduces their overall complexity; default to simple tools and escalate only when needed.
7. A core subdomain's competitive advantage is not necessarily technical — don't assume "core" automatically means "needs the heaviest pattern."

## Connects To
- **Ch 1-9**: This chapter is the explicit synthesis of everything before it — strategic subdomain analysis (Ch 1-4) combined with the tactical patterns for business logic (Ch 5-7), time modeling (Ch 7), architecture (Ch 8), and communication (Ch 9) are unified here into decision trees.
- **Ch 3**: Bounded context definition and boundary-drawing tradeoffs are revisited here with a concrete sizing heuristic.
- **Ch 5-7**: The four business logic patterns (transaction script, active record, domain model, event-sourced domain model) analyzed in depth there are the leaves of this chapter's decision tree.
- **Ch 8**: The three architectural patterns (layered, ports & adapters, CQRS) map directly onto the business logic pattern choice made here.
- **Ch 11**: Evolving Design Decisions — the natural next step once heuristics have been applied: verifying and revisiting these decisions over time as domain knowledge changes.
- **External concept**: Testing Pyramid (Mike Cohn) — the classic unit/integration/e2e emphasis shape this chapter adapts and inverts (Testing Diamond, Reversed Testing Pyramid) for different implementation patterns.
