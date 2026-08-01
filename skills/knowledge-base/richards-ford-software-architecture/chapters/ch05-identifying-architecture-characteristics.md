# Chapter 5: Identifying Architectural Characteristics

## Core Idea

Architectural characteristics are often implicit. Requirements may name features and users while leaving the qualities that shape architecture hidden in business context, domain language, or operational expectations. The architect must extract, prioritize, and make those pressures explicit without inventing unnecessary complexity.

## Frameworks Introduced

- **Domain-concern extraction**: read the business domain for implied qualities such as auditability, security, availability, or scale.
  - **When to use:** before selecting a style or partitioning components.
  - **How:** ask what failure, growth, regulation, or change would threaten the business outcome.
- **Requirements extraction**: derive explicit characteristics from functional and nonfunctional requirements, constraints, and acceptance criteria.
- **Architecture katas**: short, focused exercises in which architects analyze a scenario, propose an architecture, and defend trade-offs.
- **Explicit versus implicit characteristics**:
  - **Explicit:** directly stated, such as “the system must be available 99.9% of the time.”
  - **Implicit:** required by context, such as auditability for regulated financial operations.

## Key Concepts

- **Domain concern** — a business property or risk that can shape system structure.
- **Requirement pressure** — a statement that forces or favors a structural choice.
- **Explicit characteristic** — directly requested or measurable in the requirements.
- **Implicit characteristic** — inferred from domain, constraints, user behavior, or organizational context.
- **Architecture kata** — a repeatable exercise for practicing architecture reasoning.
- **Silicon Sandwiches** — the book’s case study used to expose explicit and implicit architectural pressures.

## Mental Models

Use the “what would make this business fail?” question to find implicit characteristics. Lost orders suggest reliability and recoverability; franchise boundaries suggest data isolation; international expansion suggests localization and scalability.

Separate importance from preference. A stakeholder’s favorite tool is not automatically an architecture characteristic. Ask what measurable business outcome the preference protects.

Treat requirement analysis as a discovery conversation, not a one-time document reading. Domain experts often reveal the most important constraints through examples and exceptions.

## Anti-patterns

- **Requirements literalism**: designing only what is explicitly written.
- **Characteristic invention**: adding qualities because they are fashionable or familiar.
- **Architecture before drivers**: selecting a style before understanding domain pressures.
- **Unprioritized extraction**: carrying every possible quality into the decision without ranking it.

## Code Examples

A compact extraction worksheet:

```text
Domain statement: “shops are independently owned and may expand overseas”
Possible pressure: tenant/data isolation and localization
Evidence needed: ownership rules, legal regions, reporting boundaries
Characteristic scenario: one franchise cannot read another franchise's orders
Measure: authorization tests plus database-access policy checks
```

## Reference Tables

| Source | Questions | Likely output |
|---|---|---|
| Domain | What must be protected or scaled? | Implicit characteristics |
| Requirements | What measurable qualities are stated? | Explicit characteristics |
| Constraints | What cannot change? | Structural limits |
| Operations | How is the system deployed and supported? | Deployability, observability, recoverability |

## Worked Example

For the Silicon Sandwiches scenario, the visible features include ordering, pickup, delivery, promotions, payment, franchises, and overseas growth. The architect extracts characteristics rather than jumping to microservices: payment security and auditability; availability for ordering; localization; data isolation between franchises; elasticity for promotions; and deployability because shops may adopt changes at different rates. These become scenarios that can be weighed against cost and complexity.

## Key Takeaways

1. Read the domain for constraints that requirements do not name.
2. Make implicit characteristics explicit before architecture selection.
3. Require evidence and measures for important qualities.
4. Architecture katas train the reasoning process, not a single preferred style.

## Connects To

- **Chapter 4:** supplies the criteria for deciding whether an extracted quality is architectural.
- **Chapter 6:** turns characteristics into measures and governance.
- **Chapter 18:** uses prioritized characteristics to compare styles.

