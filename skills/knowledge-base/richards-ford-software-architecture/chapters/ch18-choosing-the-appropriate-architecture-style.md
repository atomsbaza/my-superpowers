# Chapter 18: Choosing the Appropriate Architecture Style

## Core Idea

Architecture style selection should follow characteristics, domain, team, process, and operational context—not fashion. The right style is the least-worst fit for the current problem and the organization’s ability to build and operate it. A monolith can be an excellent choice; distribution is justified only by real structural or operational pressure.

## Frameworks Introduced

- **Decision criteria**:
  1. Identify the dominant architecture characteristics.
  2. Understand domain boundaries and isomorphism.
  3. Consider team structure, process, and operational capability.
  4. Compare candidate styles and their trade-offs.
  5. Revisit the choice as evidence changes.
- **Domain/architecture isomorphism**: when structural boundaries mirror domain boundaries, the architecture becomes easier to reason about and evolve.
- **Monolith case study**: use a modular monolith when strong local transactions, simplicity, or organizational constraints dominate.
- **Distributed case study**: use independent quanta when different capabilities need distinct scaling, release, or availability characteristics.

## Key Concepts

- **Architecture fashion** — adoption driven by industry popularity rather than fit.
- **Decision criteria** — prioritized characteristics and context used to compare styles.
- **Domain/architecture isomorphism** — alignment between business structure and architecture structure.
- **Modular monolith** — one deployment unit with explicit internal domain boundaries.
- **Operational maturity** — organizational ability to deploy, observe, secure, and support a style.
- **Least-worst architecture** — the option with the best overall trade-off for the situation.

## Mental Models

Choose a style by asking, “Which characteristics must differ across this boundary?” If the answer is none, distribution may only add failure and operations cost.

Consider the team as part of the architecture. A style requiring independent service ownership cannot succeed if teams share every release, database, and on-call rotation.

Use evolutionary choices. A modular monolith can preserve domain boundaries and become a safer starting point for future extraction than a premature distributed system.

## Anti-patterns

- **Fashion-driven architecture**: adopting microservices, event-driven, or data-grid technology without a characteristic that requires it.
- **One-style religion**: treating a style as universally superior.
- **Domain mismatch**: splitting or layering in ways that fight business change.
- **Operational denial**: choosing a style the team cannot monitor, deploy, secure, or recover.

## Code Examples

A style decision matrix:

```text
Driver                  Layered  Modular monolith  Microservices  Event-driven
Local transactions      strong   strong             weak           eventual
Independent deployment  weak     weak/moderate      strong         strong
Team autonomy            weak     moderate           strong         strong
Operational simplicity   strong   strong             weak           weak
High burst elasticity    moderate moderate          strong         strong
```

Ratings are prompts for discussion, not universal scores.

## Reference Tables

| Context | Likely starting point | Revisit when |
|---|---|---|
| Small team, cohesive domain | Modular monolith | Release or scaling coupling is measured |
| Stable sequential transformation | Pipeline | Stages need independent scale or state |
| Stable core with many variants | Microkernel | Extension contracts become the main risk |
| Many coarse business capabilities | Service-based | Data/team independence becomes critical |
| High-volume async workflows | Event-driven | Ordering and consistency dominate |
| Central database bottleneck | Space-based | Throughput and in-memory recovery are proven needs |

## Worked Example

The Silicon Sandwiches case starts with a modular monolith because ordering, payment, and franchise rules need local consistency and the team is small. The architecture partitions by domain, not only by technical layer. Later, a global promotion creates an elasticity requirement and payment must deploy independently. The team extracts only the capability whose characteristic differs, preserving the monolith for the rest. This is more deliberate than converting every module into a service.

## Key Takeaways

1. Select architecture style from prioritized characteristics and context.
2. Team structure and operational ability are architectural inputs.
3. A modular monolith is often a strong evolutionary starting point.
4. Re-evaluate style choices as measured constraints change.

## Connects To

- **Chapters 4–6:** define, identify, and measure the criteria.
- **Chapter 7:** makes deployment and runtime scope explicit.
- **Chapter 20:** validates the choice through risk assessment.

