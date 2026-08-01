# Chapter 9: Foundations

## Core Idea

Architecture styles are families of structural decisions, not universal solutions. Before comparing styles, understand the difference between monolithic and distributed architectures and the assumptions that make distributed systems difficult.

## Frameworks Introduced

- **Fundamental patterns**: Big Ball of Mud, Unitary Architecture, Client/Server, and three-tier structures.
  - **When to use:** as vocabulary for recognizing an existing system, not as a ranking of “good” and “bad” architectures.
- **Monolithic versus distributed trade-off**:
  - **Monolith strengths:** local calls, simple transactions, simple deployment, fewer operational surfaces.
  - **Distributed strengths:** independent deployment, targeted scaling, fault isolation, and team autonomy when boundaries are real.
- **Eight fallacies of distributed computing**:
  1. The network is reliable.
  2. Latency is zero.
  3. Bandwidth is infinite.
  4. The network is secure.
  5. The topology never changes.
  6. There is only one administrator.
  7. Transport cost is zero.
  8. The network is homogeneous.

## Key Concepts

- **Big Ball of Mud** — a system whose boundaries and dependencies have become difficult to understand and change.
- **Unitary architecture** — a single deployment unit with little or no internal separation.
- **Client/server** — clients request capabilities from a server over a boundary.
- **Three-tier** — presentation, business, and data tiers; a common technical partition.
- **Distributed architecture** — multiple runtime or deployment units communicating over a network.
- **Distributed transaction** — a business operation spanning multiple independently managed resources.
- **Contract maintenance** — versioning and evolving communication agreements between units.

## Mental Models

Use a monolith when local calls, transactions, and simple operations produce more value than independent scaling or deployment. Use distribution when a measured characteristic justifies the additional latency, failure, data, and operational complexity.

Treat the network as a failure boundary. Every remote call needs a timeout, error model, compatibility contract, and observability context.

The more distributed the system, the more architecture must account for partial failure. A process can be alive while a dependency, route, broker, administrator, or version is not.

## Anti-patterns

- **Distributed monolith**: many deployable artifacts that must coordinate releases and synchronous calls.
- **Fallacy-driven design**: assuming network behavior resembles an in-process method call.
- **Remote transaction optimism**: assuming distributed writes have the same atomicity and rollback semantics as a local transaction.
- **Shared operational assumptions**: assuming one administrator, topology, or security domain controls every unit.

## Code Examples

A remote call boundary should expose failure behavior:

```text
result = inventory.reserve(item, deadline=200ms)
if timeout: return PendingReservation
if rejected: return OutOfStock
if transport_error: trip circuit and degrade safely
```

The important design is not the syntax; it is the explicit timeout, outcome model, and degraded behavior.

## Reference Tables

| Concern | Local monolith | Distributed system |
|---|---|---|
| Call cost | Memory/process call | Serialization, network, queue, retry |
| Failure | Often process-wide | Partial and ambiguous |
| Transaction | Local atomicity is easier | Requires coordination or eventual consistency |
| Deployment | Coordinated | Potentially independent |
| Operations | Fewer moving parts | More observability and automation |

## Worked Example

A team moves pricing into a service to “scale independently,” but checkout, pricing, and tax still require three synchronous calls and a coordinated database change. Under latency or one service failure, checkout fails. The architecture has gained distribution without gaining independence. A modular monolith or a true bounded service with a stable quote contract would better match the current driver.

## Key Takeaways

1. Architecture styles are trade-off bundles, not universal maturity levels.
2. Distribution introduces latency, partial failure, contract, and data challenges.
3. Use the eight fallacies as a review checklist for every network boundary.
4. Earn distribution through measurable independence, scale, or fault isolation.

## Connects To

- **Chapter 7:** defines the quantum and scope of distributed characteristics.
- **Chapters 10–17:** apply the trade-offs to concrete styles.
- **Chapter 18:** chooses a style from business and operational context.

