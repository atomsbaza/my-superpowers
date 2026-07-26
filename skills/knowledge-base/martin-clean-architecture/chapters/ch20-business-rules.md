# Chapter 20: Business Rules

## Core Idea
Business rules come in two distinct kinds — Critical Business Rules/Data bound together in **Entities**, and application-specific orchestration rules captured in **Use Cases** — and these must be kept strictly separate from each other and from I/O, because they change for different reasons and at different rates.

## Frameworks Introduced
- **Entity**: an object binding a small set of Critical Business Rules to the Critical Business Data they operate on.
  - When to use: to represent a concept that is critical to the business itself and would exist even without any computer system (e.g., a Loan with balance, interest rate, payment schedule).
  - How: gather the Critical Business Data and the Critical Business Rules that operate on it into a single, separate module; keep it free of database, UI, or framework concerns; does not require an OO language — any binding of data + rules in one module qualifies.
- **Use Case**: a description of application-specific business rules — how a specific automated system is used (input, processing steps, output).
  - When to use: to encode rules that only make sense because the system is automated (e.g., gating screen flow, enforcing an order of data collection) — not rules that would hold true manually.
  - How: implement as an object with functions for the application-specific rules, holding input data, output data, and references to the Entities it orchestrates; never let it describe UI mechanics — only *what* data comes in/out.
- **Request and Response Models**: plain, dependency-free data structures for use case input/output.
  - When to use: always, as the sole way data enters/exits a use case.
  - How: define structures that do not derive from framework types (no `HttpRequest`/`HttpResponse`) and do not hold references to Entity objects, even though the data overlaps — keeping them separate per SRP/CCP.

## Key Concepts
- **Critical Business Rules**: rules/procedures that make or save the business money, true even if executed manually without a computer.
- **Critical Business Data**: the data those rules require to operate; exists independent of automation.
- **Entity**: object combining Critical Business Data + Critical Business Rules — "pure business and nothing else."
- **Use case**: application-specific rule set that only exists because the system is automated; "controls the dance of the Entities."
- **Application-specific business rules**: rules distinct from Critical Business Rules — meaningful only within an automated workflow.
- **Tramp data**: data passed through layers it doesn't belong to, a symptom of merging request/response models with Entities.

## Mental Models
- Ask "would this rule make/save money even executed manually by a clerk with an abacus?" — if yes, it's a Critical Business Rule and belongs in an Entity; if no, it's a use case rule.
- Use cases "control the dance of the Entities" — think of Entities as dancers who know no choreography, and use cases as the choreographer who knows nothing about the dancers' individual mechanics beyond calling their rules.
- Higher-level (Entity) code must never know about lower-level (use case) code — this is DIP applied vertically: Entities are general and reusable across many applications; use cases are specific to one application and closer to I/O.

## Anti-patterns
- **Putting request/response models on top of Entity objects (or deriving from them)**: seems convenient since data overlaps, but Entities and request/response models change for different reasons — coupling them violates SRP/CCP and produces tramp data and excess conditionals.
- **Letting request/response models derive from framework interfaces** (e.g., `HttpRequest`): binds use cases indirectly to the web framework, defeating the purpose of isolating business rules.
- **Describing UI mechanics inside a use case**: a use case should never reveal whether delivery is web, thick client, console, or service.

## Reference Tables
| Aspect | Entity | Use Case |
|---|---|---|
| Rule type | Critical Business Rules | Application-specific business rules |
| Would exist without automation? | Yes | No |
| Scope | Reusable across many applications/enterprise | Specific to one application |
| Level | Higher (farther from I/O) | Lower (closer to I/O) |
| Dependency direction | Knows nothing of use cases | Depends on / references Entities |
| Data | Critical Business Data | Request/response models (framework-free) |

## Worked Example
A bank's loan officer application: the bank requires that contact info be gathered and validated, and the applicant's credit score confirmed ≥ 500, before the system will proceed to the payment-estimation screen.
- This rule only makes sense in an automated system (a human clerk wouldn't need this exact gating) — so it's a **use case**, not a Critical Business Rule.
- The use case's last step references the `Customer` Entity, which holds the actual Critical Business Rules governing the bank-customer relationship (e.g., interest calculation).
- The use case takes a plain input structure (contact info, credit score) and produces a plain output structure — neither derives from any web/UI framework type, and neither directly is the `Customer` Entity.
- Because Entities (Loan, Customer) are general/enterprise concepts while the "gather-then-validate-then-proceed" gating logic is specific to this one application's screen flow, the use case depends on the Entity — never the reverse.

## Key Takeaways
1. Separate Critical Business Rules (Entities) from application-specific orchestration rules (Use Cases) — they change for different reasons and at different rates.
2. Entities must have zero knowledge of use cases; dependencies point from use case → Entity, following DIP.
3. Use cases must be blind to delivery mechanism (web/console/thick-client) — they describe data in/out and orchestration only.
4. Never let request/response models depend on frameworks or wrap Entity objects directly — keep them as independent, simple data structures.
5. Business rules are the reason the system exists — architect everything else (UI, DB, frameworks) as plugins around them.

## Connects To
- **Ch 19 (Policy and Level)**: Entities are the highest-level policy; use cases are a lower level that depends on Entities — a direct instance of level-based dependency direction.
- **Ch 22 (The Clean Architecture)**: Entities and Use Cases become the two innermost circles (Enterprise Business Rules, Application Business Rules) in the concentric diagram.
- **Dependency Inversion Principle**: the mechanism keeping Entities ignorant of use cases despite use cases needing to invoke them.
