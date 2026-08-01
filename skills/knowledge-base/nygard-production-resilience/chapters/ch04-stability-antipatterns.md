# Chapter 4: Stability Antipatterns

## Core Idea

Eleven recurring forces create, accelerate, or multiply failures: Integration Points, Chain Reactions, Cascading Failures, Users, Blocked Threads, Attacks of Self-Denial, Scaling Effects, Unbalanced Capacities, Slow Responses, SLA Inversion, and Unbounded Result Sets.

## Frameworks Introduced

- **Integration Points**: Every socket, RPC, database call, feed, queue, or process boundary can hang, fail, or return harmful data.
- **Chain Reactions / Cascading Failures**: A node or dependency failure shifts load or causes retries until peers fail too.
- **Users / Attacks of Self-Denial**: Normal user behavior, promotions, reloads, or shared links can create an internal traffic attack.
- **Blocked Threads**: Threads waiting forever consume the ability to do any other work.
- **Scaling Effects / Unbalanced Capacities**: Removing one node or overloading one layer can push the survivors or bottleneck past safe limits.
- **Slow Responses / SLA Inversion**: Slowness creates more traffic, while dependency SLAs can make a promised end-to-end SLA impossible.
- **Unbounded Result Sets**: Data that is usually small can grow until memory, CPU, or network capacity is exhausted.

## Key Concepts

- **Failure amplification**: The system’s reaction increases the original disturbance.
- **Resource pool contention**: Threads compete for a finite pool and block when checkout exceeds return.
- **SLA dependency chain**: End-to-end availability is constrained by every required dependency.

## Mental Models

- Any integration point is an untrusted boundary, including a local database.
- A failed node redistributes its work; calculate the new load before calling redundancy “safe.”
- Use the worst credible result size, not the normal result size, for memory and loop design.

## Anti-patterns

- Infinite waits, unbounded retries, shared pools, synchronous fan-out, oversized responses, and unlimited queries.
- Marketing or UI flows that make a single resource globally popular without isolation.
- Promising an availability target weaker dependencies cannot support.

## Code Examples

```text
deadline = caller_deadline
for dependency in dependencies:
    remaining = deadline - now()
    if remaining <= 0: fail_fast()
    call(dependency, timeout=remaining)
```

## Reference Table

| Antipattern | Amplifier | First containment question |
|---|---|---|
| Integration Points | Dependency wait/failure | What is the timeout and fallback? |
| Blocked Threads | Infinite resource wait | What bounds checkout and queueing? |
| Self-Denial | User-generated impulse | Can this traffic be isolated or throttled? |
| SLA Inversion | Weak dependency | Can the feature degrade independently? |
| Unbounded Results | Data growth | What limit, page, or stream boundary exists? |

## Worked Example

An eight-node farm loses one node. The remaining seven take roughly 14.3% of total load instead of 12.5%; if the lost node was already failing because of load, the same failure mode becomes more likely on every survivor. A bulkhead, lower admission rate, and capacity headroom can stop this chain.

## Key Takeaways

1. Review every boundary for waits, retries, resource use, and worst-case data.
2. Treat user traffic and marketing events as possible internal attacks.
3. Design for partial functionality when dependencies fail.

## Connects To

- **Ch 5**: Maps each antipattern to containment patterns.
- **Ch 9**: Applies the same thinking to capacity waste.
- **Ch 13**: Turns availability promises into dependency-aware requirements.
