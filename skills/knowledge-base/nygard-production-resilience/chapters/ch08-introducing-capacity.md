# Chapter 8 — Introducing Capacity

## Core Idea

Capacity is the amount of useful work a system can perform under defined conditions while meeting its service objectives. It is not a single number and it is not the same as hardware size. Capacity depends on workload, concurrency, data, latency targets, topology, dependencies, and the resource that becomes limiting first.

## Frameworks Introduced

- **Capacity envelope:** describe capacity together with workload and service-level constraints.
- **Constraint chain:** the narrowest resource or dependency determines the current system limit.
- **Interrelated resources:** increasing one resource can expose or worsen another bottleneck.
- **Scale direction:** vertical scaling changes the size of a node; horizontal scaling adds nodes, but both require an architecture that can use the added resource.

## Key Concepts

### Define useful work

Requests per second is meaningful only when the request mix is known. A read-only cache hit, a search over a large index, and a transaction that calls several external services are different units of work. Define capacity using a workload model:

```text
capacity = useful transactions completed
           while latency, error rate, and resource limits remain acceptable
```

The conditions should include a time window and a recovery requirement. A system that handles a burst by accumulating an hour-long queue has not necessarily handled the workload successfully.

### Constraints

Common constraints include CPU, memory, garbage collection, disk throughput, network bandwidth, connection pools, thread pools, locks, file descriptors, database sessions, queue depth, and third-party quotas. A request may consume several of these at once. The visible failure may occur at the last resource to saturate, while the root cause is an earlier slowdown.

For each important flow, map:

1. work arrival rate;
2. service time at each stage;
3. concurrency or queue limit;
4. failure behavior when the stage is unavailable;
5. cleanup and recovery behavior.

### Interrelations

Capacity changes propagate. More application threads can increase database contention. More cache can increase garbage-collection pauses. A larger queue can hide overload temporarily while increasing memory use and eventual latency. More replicas can improve compute capacity while increasing coordination, cache invalidation, or database load.

This is why local optimization often disappoints. The question is not “which component is slow?” but “which constraint limits the useful end-to-end flow, and what work does a proposed change add elsewhere?”

### Scalability

Vertical scaling is simple when a single process can use the larger machine, but it has hard limits and a larger failure domain. Horizontal scaling can improve availability and throughput, but requires routing, state management, data partitioning, coordination, and operational automation. “Add another server” is an architectural change, not a provisioning command.

## Anti-patterns and Myths

- **Hardware as a universal fix:** hardware cannot remove serialized work, poor queries, lock contention, or a provider quota.
- **Linear scaling assumption:** doubling nodes rarely doubles useful throughput because shared resources and coordination remain.
- **Average utilization as safety:** low average CPU can coexist with saturated pools, tail latency, or periodic bursts.
- **Bigger pools are always better:** oversized pools can overwhelm the dependency they protect.
- **One benchmark number:** capacity is workload-specific and changes with data, code, and configuration.

## Capacity Model Example

For a synchronous stage with a stable service time, a rough concurrency relationship is:

```text
concurrency ≈ arrival rate × average service time
```

If an endpoint receives 100 requests/second and occupies a thread for 0.5 seconds, it needs roughly 50 concurrent workers before queueing overhead. If a dependency slows to 2 seconds, the same arrival rate needs roughly 200 workers—or, preferably, bounded admission and a clear timeout policy. The arithmetic is only a model; measure the actual system and account for variance.

## Reference Table

| Capacity dimension | Useful question |
|---|---|
| Workload | What transaction mix and arrival pattern are assumed? |
| Latency | What percentile must remain within the target? |
| Saturation | Which resource reaches its limit first? |
| State | Does each additional node carry or share user state? |
| Dependency | What external quota or latency bounds the flow? |
| Recovery | Does the system return to steady state after a burst? |

## Worked Example

An image-processing service is CPU-light but has a 50-connection storage pool. Each job uploads a file, writes metadata, and waits for storage confirmation. Increasing worker threads from 50 to 200 does not increase useful capacity; it increases pool wait and memory. A bounded worker pool sized to storage capacity, plus a queue with explicit rejection, may produce lower peak throughput but much better stability and predictable latency.

## Key Takeaways

1. State capacity as “this workload, under these objectives, in this topology.”
2. Find the constraint chain rather than tuning a single visible metric.
3. Treat pool sizes, queues, and concurrency as protective limits.
4. Verify scalability experimentally; do not infer it from machine count.

## Connects To

- Chapter 7 shows why realistic capacity testing matters.
- Chapter 9 explains common ways applications waste capacity.
- Chapter 10 presents patterns that increase useful capacity deliberately.

