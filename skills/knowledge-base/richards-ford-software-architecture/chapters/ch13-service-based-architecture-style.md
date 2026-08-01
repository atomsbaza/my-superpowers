# Chapter 13: Service-Based Architecture Style

## Core Idea

Service-based architecture is a pragmatic distributed style: a small number of coarse-grained services expose domain or business capabilities, often sharing or partitioning a database according to the required consistency and ownership model. It can provide some independent scaling and domain separation without the operational overhead of very fine-grained microservices.

## Frameworks Introduced

- **Coarse-grained services**: make services large enough to provide meaningful capabilities and reduce network chatter.
- **Topology variants**:
  - **Single shared database:** simpler transactions and reporting, but strong coupling.
  - **Schema/database per service:** stronger ownership and isolation, with more integration complexity.
  - **Hybrid partitioning:** isolate high-change or high-scale domains while retaining shared data where justified.
- **Service granularity**: choose boundaries from business capability, data ownership, and architecture characteristics.
- **Database partitioning**: align data ownership with services while acknowledging distributed transaction and reporting costs.

## Key Concepts

- **Service-based architecture** — a set of coarse-grained services around business capabilities.
- **Service granularity** — the size and responsibility scope of each service.
- **Shared database** — multiple services access a common data store or schema.
- **Database partitioning** — assigning data ownership to separate databases or schemas.
- **Service contract** — interface and behavioral agreement between services.
- **Hybrid topology** — combines shared and isolated data approaches.

## Mental Models

Use service-based architecture as a middle ground when domain separation and scale matter but the organization is not ready for dozens of independently operated services.

Choose granularity from change and data boundaries, not from the number of nouns in the domain model. A service should hide useful complexity and own a coherent capability.

Treat a shared database as an explicit coupling decision. It can simplify transactions and reporting while making deployment, schema change, and service autonomy harder.

## Anti-patterns

- **Mini-service explosion**: splitting coarse capabilities into tiny services before operational maturity exists.
- **Shared database without ownership**: every service reads and writes every table.
- **Remote CRUD façade**: services expose tables rather than business capabilities.
- **Synchronous service chain**: a user request depends on many remote services in sequence.

## Code Examples

A service boundary should expose capability, not storage:

```text
POST /orders/{id}/confirm
  -> Order service owns order invariants
  -> Payment service authorizes payment through a contract
  -> event: OrderConfirmed
```

If both services must update one local database transaction, the boundary may not yet be operationally independent.

## Reference Tables

| Data topology | Benefit | Cost |
|---|---|---|
| Shared database | Local joins and transactions | Schema coupling and shared failure domain |
| Database per service | Ownership and independent evolution | Integration, reporting, consistency |
| Hybrid | Pragmatic migration and targeted isolation | More rules and architectural complexity |

## Worked Example

An order platform starts with Ordering, Inventory, and Shipping services sharing one relational database. Orders and inventory need atomic reservation in the first release, so the shared database is an explicit decision. As scale and team ownership diverge, inventory moves behind its own service and exposes a reservation contract. The order workflow becomes a saga with compensating behavior. The architecture evolves only when independence is worth the consistency and operational cost.

## Key Takeaways

1. Service-based architecture is a pragmatic distributed compromise.
2. Coarse-grained services reduce network and operational overhead.
3. Database topology is central to service independence.
4. Start with the consistency model and business ownership, not the service count.

## Connects To

- **Chapter 7:** services become quanta only when deployment and synchronous coupling support independence.
- **Chapter 14:** event-driven communication can reduce service chains.
- **Chapter 17:** microservices push these ideas toward finer boundaries and stronger autonomy.

