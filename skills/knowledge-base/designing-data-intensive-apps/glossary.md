# Glossary

**Asynchronous replication** — A write is acknowledged before every replica applies it; replicas may lag (Ch 5).

**Atomic commit** — All participants commit or all abort (Ch 9).

**Backpressure** — Slowing a producer when downstream consumers cannot keep up (Ch 11).

**Backward compatibility** — New readers can decode data written by older code (Ch 4).

**Batch process** — Offline computation over a bounded input (Ch 10).

**B-tree** — Ordered page-based index updated in place (Ch 3).

**Byzantine fault** — Arbitrary or malicious component behavior (Ch 8–9).

**CAP theorem** — During a network partition, linearizable consistency and availability cannot both be guaranteed for every request (Ch 9).

**Causality** — The happens-before relation between an operation and its effects (Ch 5, 9).

**Change data capture (CDC)** — A stream of database changes used to update derived systems (Ch 11).

**Compaction** — Merging immutable storage files and discarding obsolete records (Ch 3).

**Consensus** — Agreement on one value/order despite defined failures (Ch 9).

**Consistency** — A guarantee about which states/observations are allowed; distinct from application invariants and isolation (Ch 7, 9).

**Consumer offset** — A stream reader’s position in a partitioned log (Ch 11).

**Data locality** — Keeping data needed by a common access path close together (Ch 2–3).

**Data skew** — Uneven distribution of records or traffic across partitions/tasks (Ch 6, 10).

**Declarative query** — States the desired result rather than the execution algorithm (Ch 2).

**Derived data** — Replaceable output computed from other data (Ch 10–12).

**Durability** — A committed result survives failures according to a stated guarantee (Ch 7).

**Event sourcing** — Storing domain events and deriving current state from them (Ch 11).

**Event time** — Time at which a real-world event occurred (Ch 11).

**Fencing token** — Monotonic ownership number checked by a protected resource (Ch 8).

**Failover** — Promoting another replica/leader after failure (Ch 5, 9).

**Fault** — A component deviating from its specification; not the same as system failure (Ch 1, 8).

**Forward compatibility** — Older readers safely handle data written by newer code (Ch 4).

**Happens-before** — Causal ordering relation used to detect concurrent operations (Ch 5, 9).

**Idempotence** — Repeating an operation has one logical effect (Ch 8, 11–12).

**Index** — Auxiliary structure that accelerates a query at write/storage cost (Ch 3, 10–12).

**Isolation** — Rules controlling what concurrent transactions can observe (Ch 7).

**Leader/follower** — Replication arrangement with one write leader and read/apply followers (Ch 5).

**Linearizability** — Each operation appears atomic at a point between call and response, respecting real time (Ch 9).

**Load parameter** — Measure of demand such as QPS, active users, data volume, or read/write ratio (Ch 1).

**Log** — Append-only ordered record of changes/messages, often replayable (Ch 5, 11).

**LSM-tree** — Log-structured storage using memory buffers, sorted files, and compaction (Ch 3).

**Materialized view** — Persisted result maintained from source data/events (Ch 3, 10–12).

**Monotonic read** — A session does not move backward to an older observed state (Ch 5).

**MVCC/snapshot isolation** — Versioned writes let transactions read a consistent snapshot (Ch 7).

**OLAP** — Analytical processing dominated by scans and aggregations (Ch 3).

**OLTP** — Operational processing dominated by small concurrent reads/writes (Ch 3).

**Partition/shard** — A subset of records owned by one node or replica group (Ch 6).

**Partitioned log** — Durable log split into independently ordered partitions (Ch 11).

**Percentile** — Distribution point such as p95 or p99; useful for tail latency (Ch 1).

**Quorum** — Required number of replica acknowledgements for a read/write (Ch 5, 9).

**Read repair** — Correcting a stale replica during a read (Ch 5).

**Read skew** — One transaction observes inconsistent committed versions (Ch 7).

**Read-your-writes** — A session’s later read includes its completed writes (Ch 5).

**Rebalancing** — Moving partition ownership as nodes/load change (Ch 6).

**Replication lag** — Difference between source and replica apply positions (Ch 5).

**Response time** — Client-observed elapsed time, including queueing and network delay (Ch 1).

**Schema** — Expected structure, types, and compatibility rules for data (Ch 2, 4, 11).

**Serializability** — Transaction outcome equivalent to some serial execution (Ch 7, 9).

**Shared-nothing** — Nodes own independent resources and coordinate through the network (Ch 6).

**Snapshot isolation** — Transactions read a stable versioned snapshot (Ch 7).

**SSTable** — Immutable sorted string table on disk (Ch 3).

**Stream process** — Continuous computation over an unbounded event sequence (Ch 11).

**System of record** — Authoritative source from which other data can be derived (Ch 10–12).

**Tail latency** — High-percentile response time experienced by slow requests (Ch 1).

**Total order broadcast** — Reliable delivery of the same messages in the same order (Ch 9).

**Transaction** — Unit of reads/writes with specified atomicity, isolation, and durability behavior (Ch 7).

**Two-phase commit (2PC)** — Prepare/vote followed by a durable commit/abort decision (Ch 9).

**WAL** — Write-ahead log recording changes before in-place data updates (Ch 3).

**Watermark** — Estimate that event-time input is complete up to a point (Ch 11).

**Write skew** — Concurrent valid-looking updates jointly violate an invariant (Ch 7).

