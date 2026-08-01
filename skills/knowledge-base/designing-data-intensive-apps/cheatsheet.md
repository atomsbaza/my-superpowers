# Decision Cheatsheet

## Start with the question

| If the dominant need is… | Start by evaluating… |
|---|---|
| point reads/writes | partition key, B-tree vs LSM, replication |
| range scans/aggregates | range locality, column storage, OLAP separation |
| many-hop relationships | graph model and traversal indexes |
| low-latency derived state | partitioned log, CDC, stream processor |
| rebuildable analytical/search views | batch pipeline and versioned publication |
| cross-row invariant | transaction isolation, predicate protection, or coordination |

## Reliability and scale rules

- When a component can fail, ask how the system detects, contains, recovers, and verifies the fault.
- When someone says “scalable,” name the load parameter: QPS, data volume, fan-out, read/write mix, active users, or skew.
- Report p50/p95/p99, not only averages. Fan-out makes tail latency compound.
- If failures are correlated (software bug, bad config, shared dependency), more identical replicas may not help.
- Prefer many logical partitions over `hash(key) mod N`; changing `N` remaps almost everything.

## Data-model decisions

- Embed bounded data with the same lifecycle; reference shared, independently updated, or unbounded data.
- Normalize when integrity and flexible joins dominate; denormalize only with a clear update path.
- Choose a graph when the query is a variable-length traversal; choose relational when arbitrary joins/constraints matter.
- Treat schema-on-read as an implicit schema that still needs tests and migrations.

## Replication and consistency

- Need one write order? Use a leader or ordered log.
- Need multi-DC/offline writes? Use multi-leader/leaderless design and define conflict convergence.
- Need only a good user session? Prefer read-your-writes, monotonic reads, or consistent-prefix reads over global linearizability.
- For quorum systems, check `W + R > N`, then separately analyze sloppy quorums, concurrent writes, repairs, and stale reads.
- Use last-write-wins only when losing concurrent intent is acceptable.

## Transactions and coordination

- Dirty reads/writes → read committed may suffice.
- Stable snapshots → snapshot isolation/MVCC.
- Set/predicate invariants → serializable isolation, predicate/index-range locks, SSI, or a materialized conflict row.
- A lease without fencing is unsafe. The protected resource must reject stale tokens.
- 2PC is atomic commit and can block; it is not 2PL and is not consensus.
- Use linearizable compare-and-set/consensus for uniqueness, leader election, and membership—not for every derived view.

## Batch and stream

- Large bounded history → batch; unbounded low-latency input → stream; most robust systems use both.
- Small side fits memory → broadcast join. Both large → reduce-side or co-partitioned join.
- A queue distributes work; a log preserves replayable history.
- Event-time result → define windows, lateness, watermarks, and corrections. Processing time is not business time.
- Assume at-least-once processing. Make state updates and external effects idempotent.

## Derived-data correctness

- Identify the system of record and make every cache/index/view replaceable from it.
- For evolution/repair: replay into a new generation, validate, then atomically publish.
- Put duplicate suppression and final invariant checks at the end-to-end boundary.
- Measure correctness/integrity, freshness, availability, provenance, and privacy separately.

## Fast smells

| Smell | Likely issue |
|---|---|
| “The average latency is fine” | tail/queueing problem |
| “The timeout means it failed” | ambiguous remote outcome |
| “The replica is up” | may still be stale or divergent |
| “We write DB and index separately” | dual-write divergence |
| “Exactly once delivery” | effect-level idempotence not specified |
| “The cache is the source of truth” | no repair/rebuild path |

