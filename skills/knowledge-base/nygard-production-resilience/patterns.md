# Patterns

## Timeouts
**When to use**: Every network, database, queue, lock, pool checkout, and external-process wait.
**How**: Choose a bound from the caller's useful response budget; propagate remaining time; handle timeout as a normal failure path; release resources.
**Trade-offs**: A timeout prevents indefinite blockage but does not cancel work automatically. Ensure the downstream operation and cleanup are safe after the caller gives up.

## Circuit Breaker
**When to use**: A dependency can fail repeatedly or become slow enough that continued calls would damage the caller.
**How**: Count meaningful failures or slow responses; open the circuit; return fallback/controlled failure; after a cool-down, allow limited probes; close only after recovery.
**Trade-offs**: Too-sensitive thresholds cause unnecessary outages; too-lax thresholds allow cascades. Expose state and choose fallback semantics deliberately.

## Bulkheads
**When to use**: Multiple features or dependencies share threads, connections, memory, queues, or worker capacity.
**How**: Partition resource pools or concurrency limits by workload; reserve capacity for critical paths; cap queues; reject excess work explicitly.
**Trade-offs**: Isolation lowers maximum sharing efficiency and requires sizing. That cost buys predictable damage containment.

## Steady State
**When to use**: Operators need to recognize abnormal behavior before users report it.
**How**: Define normal ranges for traffic, latency, pools, memory, queues, dependency health, and business transactions. Alert on meaningful deviation, not every fluctuation.
**Trade-offs**: Baselines drift as releases and traffic change; treat them as living operational knowledge.

## Fail Fast
**When to use**: Work cannot succeed within the caller's deadline or the system has no capacity to process it safely.
**How**: Check prerequisites early; reject or degrade before consuming scarce resources; return a useful error and preserve capacity for other work.
**Trade-offs**: Users see an explicit failure instead of a slow one. Pair with retries only when the retry is bounded and useful.

## Handshaking
**When to use**: A connection can be alive but not ready, compatible, authorized, or safe to use.
**How**: Exchange protocol version, identity, capabilities, readiness, and required configuration before sending normal traffic.
**Trade-offs**: Adds setup work but prevents ambiguous failures and makes failover transitions explicit.

## Test Harness
**When to use**: Integration behavior, protocols, failover, load, and partial failures matter more than isolated unit behavior.
**How**: Build repeatable tests around real endpoints or faithful substitutes; inject failure, delay, bad data, load spikes, and version combinations; observe resource effects.
**Trade-offs**: Slower and harder to maintain than unit tests, but finds failures that unit tests cannot model.

## Decoupling Middleware
**When to use**: A producer and consumer should not share request latency, availability, or traffic rate.
**How**: Queue work; make messages durable and idempotent; bound queue growth; expose lag and dead-letter paths; decide what happens when the consumer is unavailable.
**Trade-offs**: Adds eventual consistency, operational components, and duplicate-delivery handling.

## Bounded resource pools
**When to use**: Connections, threads, sessions, caches, or other expensive resources are reused.
**How**: Bound pool size and wait time; size pools against downstream capacity; monitor utilization, queueing, and leaks; release on every path.
**Trade-offs**: A pool reduces setup cost but can become a contention or blocked-thread failure amplifier.

## Precompute and cache carefully
**When to use**: Content is expensive to generate and changes less often than it is read.
**How**: Precompute stable content; cache only valuable objects; cap memory; provide invalidation/flush; measure hit rate and regeneration cost; use small “punch-outs” for personalized data.
**Trade-offs**: Stale data, invalidation complexity, and memory pressure can outweigh the speed gain.

## Zero-downtime release
**When to use**: The service must change without taking all capacity offline.
**How**: Maintain compatibility during expansion and rollout; deploy new code beside old; shift traffic gradually; verify health and business signals; clean up old versions only after rollback is no longer needed.
**Trade-offs**: Requires compatibility discipline, observability, and more than one version running at once.
