# Chapter 15: Space-Based Architecture Style

## Core Idea

Space-based architecture addresses high and variable load by moving processing and data into a grid of independently scalable processing units, reducing dependence on a centralized database bottleneck. It is powerful for elastic, high-volume workloads, but introduces distributed data, collision, consistency, and operational complexity.

## Frameworks Introduced

- **Processing unit**: a deployable unit containing application logic, in-memory data, and access to virtualized middleware.
- **Virtualized middleware**: messaging, data grid, processing grid, and deployment management capabilities that make many units behave as a coordinated space.
- **Data pumps**: move data between in-memory processing units and persistent stores.
- **Data writers/readers**: coordinate persistence and retrieval while preserving throughput and consistency expectations.
- **Data collision management**: resolve concurrent updates to the same business data.
- **Replicated versus distributed caching**: trade consistency and locality against shared visibility and capacity.

## Key Concepts

- **Space** — the collection of processing units and virtualized middleware.
- **Processing unit** — a horizontally scalable execution and data slice.
- **Data grid** — distributed in-memory data management.
- **Messaging grid** — communication and routing among units.
- **Processing grid** — distribution of computational work.
- **Data pump** — asynchronous movement between memory and persistent storage.
- **Data collision** — conflicting concurrent updates.
- **Near cache** — a local cache placed close to a processing unit.

## Mental Models

Use space-based architecture when a centralized persistence tier is the dominant bottleneck and the workload can be partitioned, cached, or processed in memory.

Treat in-memory state as a distributed data system, not merely a faster cache. Define ownership, replication, eviction, recovery, persistence, and collision behavior.

Separate scale claims from consistency claims. A data grid can improve throughput while making strong cross-unit transactions more difficult.

## Anti-patterns

- **Database bottleneck avoidance by denial**: moving data in memory without defining persistence and recovery.
- **Unbounded in-memory state**: allowing traffic growth to exhaust processing-unit memory.
- **Cache as source of truth without a recovery plan**.
- **Collision blindness**: assuming parallel updates cannot conflict.

## Code Examples

A simplified write path:

```text
request -> processing unit
        -> update local in-memory state
        -> publish change / enqueue data pump
        -> persistent store
        -> acknowledge according to durability policy
```

The acknowledgment point determines the trade-off between latency, durability, and recovery behavior.

## Reference Tables

| Mechanism | Purpose | Main concern |
|---|---|---|
| Messaging grid | Route work/events | Ordering, delivery, backpressure |
| Data grid | Share in-memory state | Consistency, partition, recovery |
| Processing grid | Distribute computation | Scheduling and idempotency |
| Data pump | Persist or reload state | Lag, replay, durability |
| Near cache | Localize reads | Staleness and invalidation |

## Worked Example

An online ticketing system receives bursts for a popular event. A centralized database cannot handle the write contention. Processing units partition inventory and hold temporary reservation state; messaging coordinates reservation commands; data writers persist committed sales. Data collisions are handled by ownership or version checks, and a deployment manager adds units as load increases. The design is attractive because the bottleneck is clear, but the team must specify what happens when a unit fails during a reservation.

## Key Takeaways

1. Space-based architecture targets centralized bottlenecks through partitioned processing and in-memory state.
2. Virtualized middleware carries significant operational responsibility.
3. Durability, collision, recovery, and consistency must be explicit.
4. This style is powerful but costly; use it only when its characteristics are required.

## Connects To

- **Chapter 9:** distributed fallacies apply to every grid and data pump.
- **Chapter 13:** service-based styles may be sufficient when the database is not the limiting constraint.
- **Chapter 18:** choose space-based architecture from measured throughput and elasticity needs.

