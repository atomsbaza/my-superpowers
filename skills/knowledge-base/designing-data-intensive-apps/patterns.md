# Patterns and Techniques

## Measure Load, Not “Scalability”
**When to use**: Capacity planning, SLO design, or architecture comparison.
**How**: Name the load parameters, measure throughput and latency distributions, identify bottlenecks, and model what happens when each parameter grows.
**Trade-offs**: More instrumentation and a workload model up front; far less ambiguity than a generic scalability claim.

## Aggregate Locality
**When to use**: Choosing between document embedding, references, and normalized relations.
**How**: Group bounded data with the same lifecycle and access path; reference independently owned, shared, or unbounded data.
**Trade-offs**: Embedding improves reads but duplicates/limits relationships; normalization improves integrity but adds joins.

## LSM Storage Engine
**When to use**: Write-heavy key/value workloads and sequential I/O.
**How**: Write to a memtable, flush sorted immutable files, use sparse indexes/filters, and compact in the background.
**Trade-offs**: High write throughput versus compaction, read amplification, space amplification, and operational tuning.

## Schema-Evolution Contract
**When to use**: Rolling deploys, long-lived files, replication logs, RPC, or replayable messages.
**How**: Prefer additive changes, stable field tags, optional/defaulted fields, and explicit reader/writer compatibility tests.
**Trade-offs**: Compatibility constraints limit destructive refactors but allow old/new versions to coexist safely.

## Session Guarantees
**When to use**: Reading from lagging replicas without paying for global linearizability.
**How**: Provide read-your-writes, monotonic reads, or consistent-prefix reads using routing, log positions, or dependency metadata.
**Trade-offs**: Better user experience and availability than strong consistency; clients may still see stale data.

## Quorum Read/Write
**When to use**: Leaderless replication with node-outage tolerance.
**How**: Select `N`, `W`, and `R`; combine overlap with versioning, read repair, anti-entropy, and stale-read monitoring.
**Trade-offs**: Flexible availability versus conflict, repair, and membership complexity; quorum overlap is not a full linearizability guarantee.

## Fixed Logical Partitions
**When to use**: Horizontally scalable data with planned node growth/shrinkage.
**How**: Create more logical partitions than physical nodes, move whole partitions, version routing metadata, and throttle transfers.
**Trade-offs**: Predictable rebalancing and routing versus partition-count planning and possible uneven partition sizes.

## Materialize a Conflict
**When to use**: A cross-row invariant is hard to protect with ordinary row locks.
**How**: Represent the predicate as a shared guard/lock row or unique key, then make every competing operation update it transactionally.
**Trade-offs**: Clear correctness boundary versus extra contention and a possible coordination hot spot.

## Fenced Lease
**When to use**: A distributed lock protects storage or an external side effect.
**How**: Issue an increasing token with the lease; pass it to the resource; reject operations with an older token.
**Trade-offs**: Requires resource cooperation, but prevents stale owners after process pauses and lease expiry.

## MapReduce Join
**When to use**: Large batch inputs need grouping by a join key.
**How**: Use reduce-side repartition/sort for general joins; use broadcast, co-partitioned, or merge joins when preconditions reduce shuffle.
**Trade-offs**: Generality versus network/sort cost; skew can dominate any nominal parallelism.

## Replayable Log Consumer
**When to use**: CDC, event sourcing, multiple derived views, or recovery after failure.
**How**: Store offsets, make state updates deterministic/idempotent, retain enough history, and coordinate offset/state publication.
**Trade-offs**: Rebuildability and independent consumers versus retention, state management, and duplicate handling.

## Event-Time Window
**When to use**: Stream metrics/joins where events can be late or out of order.
**How**: Define event-time windows, lateness/watermark policy, state retention, and correction/retraction behavior.
**Trade-offs**: More accurate business-time results versus delayed finality and state/storage cost.

## Versioned Derived View
**When to use**: A cache, index, warehouse table, or client view may need repair or application-logic evolution.
**How**: Derive from an authoritative log/snapshot, write a new generation, validate counts/samples/checksums, then publish atomically.
**Trade-offs**: Rebuild cost and storage for safe rollout, rollback, and auditability.

## End-to-End Idempotency
**When to use**: Remote calls, retries, at-least-once delivery, or ambiguous timeouts.
**How**: Carry a stable operation ID, deduplicate at the user-visible effect boundary, and return the recorded result for repeats.
**Trade-offs**: Idempotency state/retention and API design in exchange for safe retries.

