# Chapter 10 — Capacity Patterns

## Core Idea

Capacity improvements come from reducing unnecessary work, controlling concurrency, and using resources according to measured constraints. The patterns in this chapter are not invitations to maximize utilization. They are ways to increase useful work while preserving predictable behavior during bursts and failures.

## Frameworks Introduced

- **Resource pools:** make scarce resources explicit and bounded.
- **Careful caching:** trade computation and I/O for memory while managing freshness and invalidation.
- **Precomputation:** move repeatable work out of the request path.
- **Garbage-collector tuning:** adapt memory-management settings to object lifetime and workload rather than folklore.

## Key Concepts

### Resource pools

A pool protects both the caller and the dependency. It should expose at least:

- maximum and minimum size;
- acquisition timeout;
- health and validation policy;
- idle and lifetime limits;
- metrics for in-use, available, waiters, timeouts, and failures;
- guaranteed release on success, error, cancellation, and timeout.

Pool size should be constrained by the slowest safe downstream capacity. A database that can safely handle 40 concurrent operations should not receive 400 connections merely because the application has 400 threads.

### Use caching carefully

Caching is a capacity pattern and a correctness risk. Before adding a cache, define the key, scope, lifetime, maximum size, eviction policy, invalidation rule, and behavior when the cache is cold or unavailable. Measure hit rate, miss cost, stale reads, memory, and stampede behavior.

Cache failures can create a second outage: if every miss recomputes the same expensive value, a cold cache may overload the origin. Use request coalescing or bounded refresh work where appropriate. Avoid caching data whose invalidation semantics cannot be explained.

### Precompute content

If work is deterministic or changes on a known schedule, perform it before users request it. Static generation, materialized aggregates, scheduled reports, and prepared search indexes reduce request-path variability. A “punch-out” design can combine a precomputed base with a small dynamic fragment. This preserves freshness where required without rebuilding the entire response.

### Tune memory management from evidence

Garbage collection is a workload property. Measure allocation rate, object lifetimes, pause time, heap occupancy, promotion, and memory pressure. A larger heap may reduce collection frequency while increasing pause duration; a smaller heap may collect more often but recover memory sooner. Tune after removing avoidable allocation and response/session waste.

Configuration should be revisited when application behavior, data size, runtime version, or deployment topology changes. A setting that worked for one release is not a permanent truth.

## Safe Pattern Sequence

1. Establish a representative workload and baseline.
2. Identify the constraining resource and the work that consumes it.
3. Remove unnecessary work before adding a cache or pool.
4. Add a bound and a failure policy.
5. Instrument the new behavior.
6. Test cold start, steady state, burst, eviction, and dependency failure.
7. Recheck recovery after the load ends.

## Reference Table

| Pattern | Benefit | Main risk to control |
|---|---|---|
| Bounded pool | Prevents unlimited concurrency | Queue wait and rejected work |
| Cache | Avoids repeated computation/I/O | Staleness, stampede, memory growth |
| Precompute | Removes work from request path | Freshness and job failure |
| Punch-out | Limits dynamic portion | Invalidation and composition cost |
| GC tuning | Reduces memory-management disruption | Optimizing symptoms or creating pauses |

## Worked Example

An account summary takes 300 ms and queries four tables. It changes after transactions but is requested thousands of times per minute. A bounded cache with a short lifetime and transaction-triggered invalidation can reduce database work, but it must handle a cold-start burst. A single-flight refresh per account key prevents 100 concurrent misses from issuing 100 identical queries. Metrics distinguish cache hits, misses, stale responses, refresh failures, and origin latency.

## Key Takeaways

1. A pool is a protective boundary, not a license for unlimited waiting.
2. Caches require explicit freshness and failure semantics.
3. Precompute stable work and keep the request path small.
4. Tune runtime behavior from measurements and revisit it as the system evolves.

## Connects To

- Chapter 8 supplies the capacity model and constraint vocabulary.
- Chapter 9 identifies the waste these patterns address.
- Chapter 17 explains the transparency needed to operate pools, caches, and runtime settings safely.

