# Chapter 7: Scope of Architecture Characteristics

## Core Idea

Architecture characteristics apply at a scope: a function, module, component, service, deployment unit, or whole system. The concept of an architectural quantum makes the scope visible by identifying an independently deployable artifact with high functional cohesion and synchronous connascence. Quantum boundaries strongly influence how characteristics such as scalability, availability, and deployability behave.

## Frameworks Introduced

- **Architecture quantum**: an independently deployable artifact with high functional cohesion and synchronous connascence.
  - **When to use:** when choosing monolithic versus distributed boundaries or reasoning about deployment and failure domains.
  - **How:** identify what must deploy together, what shares synchronous runtime coupling, and where data or operational ownership resides.
- **Granularity**: the size and number of architectural units relative to their responsibilities and operational cost.
- **Bounded Context**: a domain boundary in which a model and language are consistent; it can inform a quantum boundary but is not identical to one.
- **Connascence across boundaries**: a way to reason about the hidden synchronization cost of distribution.

## Key Concepts

- **Independently deployable** — can be released without requiring another artifact to release at the same time.
- **Functional cohesion** — the unit’s responsibilities contribute to a coherent business capability.
- **Synchronous connascence** — elements must coordinate in real time for a transaction to complete.
- **Quantum** — a deployment and runtime boundary whose characteristics must be evaluated together.
- **Granularity** — how finely responsibilities are divided into units.
- **Bounded Context** — a domain language boundary that limits model ambiguity.
- **Transitive dependency** — a dependency that affects a unit indirectly through another unit.

## Mental Models

Treat every quantum as a package of qualities. If a service is independently deployable but shares a synchronous database transaction with four other services, its deployability and availability are not independent in practice.

Use bounded contexts to discover domain boundaries; use operational coupling to verify whether those boundaries can become deployment boundaries.

Prefer fewer, deeper units when the organization cannot support many operational surfaces. Prefer more independent quanta when deployability, scale, or fault isolation has measurable value.

## Anti-patterns

- **Quantum blindness**: discussing a service’s characteristics without including its database, runtime, or synchronous dependencies.
- **Distributed by noun**: creating a unit for every domain object without functional cohesion.
- **False independence**: separate deployment artifacts that require coordinated schema or protocol changes.
- **Granularity by fashion**: selecting service count before measuring coupling and operational capacity.

## Code Examples

A quantum inventory can be represented as a table:

```text
Quantum: Ordering
deploys: order-api + order-db
sync dependencies: inventory-reservation
async dependencies: fulfillment-events
characteristics: availability, auditability, deployability
release constraint: order-db migration must remain backward compatible
```

## Reference Tables

| Question | Monolithic quantum | Distributed quanta |
|---|---|---|
| Deployment | One coordinated unit | Multiple release units |
| Synchronous calls | Usually local | Network and runtime coupling |
| Data | Often shared transaction | Isolation or distributed consistency |
| Failure domain | Broad | Potentially isolated, but more partial failures |
| Operations | Fewer surfaces | More automation and observability |

## Worked Example

In the Going, Going, Gone auction scenario, real-time bidding, bidder identity, auction management, and streaming have different load and latency pressures. A single monolith is easy to deploy but couples every change and failure domain. A distributed design is justified only where the quanta can be independently deployed and operated: for example, a streaming quantum may scale differently from the auction transaction quantum. Shared synchronous data access would undermine that independence, so the design must choose data ownership and event or API contracts deliberately.

## Key Takeaways

1. Architecture characteristics have scope; define the unit being evaluated.
2. A quantum includes deployment, runtime, data, and synchronous coupling.
3. Domain boundaries are candidates, not automatic deployment boundaries.
4. Distribution earns its complexity when independence, scale, or fault isolation matters.

## Connects To

- **Chapter 3:** supplies connascence vocabulary.
- **Chapter 8:** identifies components and partitions.
- **Chapter 18:** compares styles using characteristics and operational context.

