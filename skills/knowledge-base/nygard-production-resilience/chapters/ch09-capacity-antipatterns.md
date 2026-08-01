# Chapter 9 — Capacity Antipatterns

## Core Idea

Capacity is frequently lost through individually reasonable decisions that multiply under load. The antipatterns in this chapter turn small amounts of work, state, or latency into resource contention and waste. They are especially dangerous because a system can look healthy at low traffic.

## Frameworks Introduced

- **Resource-pool accounting:** every pool needs a bounded size, a wait policy, a timeout, and an owner.
- **Work amplification:** measure how one user action expands into requests, queries, bytes, objects, and session state.
- **Request discipline:** interaction and transport choices are part of capacity design.
- **Data lifecycle:** historical data, cookies, indexes, and partitions affect current request cost.

## Key Concepts

### Resource pool contention

Threads, database connections, sockets, memory buffers, and worker processes are all pools. If callers can wait indefinitely, the pool becomes a queue with no visible bound. If the pool is too large, it can overload the downstream resource. Define admission and rejection behavior explicitly:

```text
acquire with deadline
if unavailable: reject or degrade
always release in finally/cleanup
```

The pool should be sized from measured service time and dependency limits, not from the number of incoming users.

### Excessive dynamic work

Dynamic pages, server-side includes, per-request personalization, and repeated template work can consume CPU and database capacity even when the final content changes rarely. Separate stable content from the small dynamic portion. Precompute what can be precomputed and cache only when invalidation is understood.

### Interaction and request timing

An interface can make users generate a storm: polling too frequently, issuing one request per field, auto-refreshing after a timeout, or allowing rapid duplicate submissions. Debounce actions, coalesce requests, use backoff, and make idempotency explicit. A retrying client is part of the workload.

### Session thrashing and overstaying sessions

Large server-side sessions consume memory and make failover expensive. Sessions that never expire accumulate abandoned state. Store only the minimum needed, set an intentional lifetime, and make the application tolerate a session being lost or moved. Do not confuse convenience with a requirement to retain every interaction indefinitely.

### Response formatting and payload waste

Verbose JSON/XML/HTML, repeated whitespace, expensive spacer images, and deeply nested tables all consume bandwidth, parsing time, memory, or rendering work. Payload size is a capacity variable. Measure bytes and object counts, not only server CPU.

### Reload amplification

When users press reload, browsers and clients may repeat expensive requests. A timeout page that invites immediate retry can worsen an incident. Use request identifiers, idempotent operations, server-side deduplication where appropriate, and clear status semantics.

### Serialize on source address

Serializing work by client IP or another coarse source key can cause unrelated users behind one NAT or proxy to block one another. If ordering is required, use the narrowest correct business key and bound the queue. Do not use network identity as a proxy for user identity without verifying the traffic model.

### Database and data-layout waste

Handcrafted SQL assembled inconsistently creates correctness and plan problems. Missing or indiscriminate indexes trade query speed for write cost and storage. Unbounded historical data makes current queries progressively more expensive. Partitioning and archival can help, but only when access patterns and maintenance operations are designed together. Cookies and other client-carried state should be bounded because they are sent repeatedly.

## Reference Table

| Antipattern | Capacity lost through | Safer design question |
|---|---|---|
| Unbounded pool wait | Threads and memory retained | What is the deadline and rejection behavior? |
| Excess dynamic content | Repeated computation and queries | What can be precomputed or cached? |
| Polling storm | Excess request rate | Can events, backoff, or coalescing reduce calls? |
| Large sessions | Memory and failover cost | What state truly must persist? |
| Verbose response | Bytes, parsing, and rendering | What is the minimum useful representation? |
| Reload amplification | Duplicate expensive work | Is the operation idempotent and deduplicated? |
| Coarse serialization | Unrelated users block | What is the correct ordering key? |
| Unmanaged data growth | Query and maintenance cost | What is the lifecycle for old data? |

## Worked Example

A dashboard polls 30 endpoints every five seconds. Each endpoint renders HTML, reads the same account data, and includes a 2 MB historical payload. At 1,000 users this becomes 6,000 requests/second and 12 GB/s of response traffic before business actions occur. A redesign can combine endpoints, send only changed data, use a bounded polling interval with backoff, cache stable aggregates, and archive old history. The user-visible feature remains while its work amplification is reduced.

## Key Takeaways

1. Count work from user action to dependency, not just HTTP requests.
2. Bound every pool, queue, session, payload, and data query.
3. Treat retries, reloads, and client interaction as production load.
4. Review data and interface design as capacity design.

## Connects To

- Chapter 4 identifies several of these behaviors as stability risks as well as capacity risks.
- Chapter 5 supplies containment patterns for waiting and dependency failure.
- Chapter 10 turns the diagnosis into resource-pool, caching, and precomputation patterns.

