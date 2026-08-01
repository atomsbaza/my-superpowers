# Chapter 5: Replication

## Core Idea

Replication keeps copies of the same data on multiple nodes for availability, latency, and read throughput, but copies diverge whenever writes are asynchronous or concurrent. The design question is not “is it replicated?” but which consistency guarantees, failure behavior, and conflict-resolution rules clients receive.

## Frameworks Introduced

- **Leader–follower replication**: One leader accepts writes; followers apply the ordered replication log and may serve reads.
  - When to use: a single write order is useful and read scaling or failover matters.
  - How: route writes to the leader, ship a log, monitor follower lag, and define promotion/failover rules.
- **Synchronous versus asynchronous replication**: Synchronous acknowledgement reduces acknowledged-data loss but couples write latency and availability to a follower; asynchronous replication improves availability but permits lag and loss during failover.
  - When to use: select a durability/latency point per workload, often using a mix of synchronous and asynchronous followers.
- **Session consistency guarantees**: Read-your-writes, monotonic reads, and consistent-prefix reads are weaker than linearizability but often solve user-visible anomalies at lower cost.
  - When to use: user sessions read from replicas or a system intentionally accepts lag.
  - How: route a user to a sufficiently caught-up replica, track a log position, or wait until the replica has applied the relevant position.
- **Multi-leader conflict convergence**: Multiple leaders accept writes and later reconcile concurrent updates.
  - When to use: multi-datacenter writes, offline clients, or collaborative editing where one global leader is unavailable or too slow.
  - How: avoid conflicts by partitioning ownership when possible; otherwise use last-write-wins only when data loss is acceptable, or merge with domain-specific logic/CRDT-like structures.
- **Quorum replication**: In a leaderless system with `N` replicas, choose write quorum `W` and read quorum `R` so `W + R > N` for overlap.
  - When to use: tolerate node outages while allowing reads and writes from multiple replicas.
  - How: combine quorum reads with read repair/anti-entropy, version tracking, and explicit caveats for sloppy quorums and concurrent writes.
- **Happens-before and version vectors**: Track causal ancestry so a system can distinguish overwrites from concurrent writes.
  - When to use: conflict detection where silently discarding concurrent updates would lose user intent.
  - How: attach causal versions, discard versions dominated by a newer one, and retain/merge incomparable versions.

## Key Concepts

- **Leader/primary**: Replica that accepts writes and defines their order.
- **Follower/secondary**: Replica that applies the leader’s changes.
- **Replication lag**: Difference between a leader’s committed position and a follower’s applied position.
- **Failover**: Promoting a new leader after failure.
- **Read repair**: Fixing a stale replica as a side effect of a read.
- **Anti-entropy**: Background comparison/synchronization of replicas.
- **Quorum**: Minimum number of replicas required to acknowledge a read or write.
- **Sloppy quorum**: Temporarily writing to non-home replicas during an outage.
- **Happens-before**: A causal ordering relation between operations.
- **Version vector**: Per-replica causal version information used to detect concurrency.

## Mental Models

- Replication lag is a user-visible time dimension: “what did this session know when it read?”
- Acknowledged durability and read freshness are separate axes; tune them independently.
- Quorum overlap is a topology statement, not a complete consistency proof; repairs, clocks, conflicts, and membership changes still matter.
- If a conflict can be prevented by assigning ownership, that is usually easier to reason about than merging arbitrary values later.

## Anti-patterns

- **Failing over to the most convenient replica**: The newest leader may be missing acknowledged writes or create divergent histories.
- **Assuming a follower read is immediately consistent**: Asynchronous replication makes stale reads normal.
- **Using last-write-wins as a universal conflict strategy**: It can discard concurrent intent and depends on problematic timestamps.
- **Treating `W + R > N` as linearizability**: Sloppy quorums, concurrent writes, and unavailable replicas weaken the guarantee.

## Code Examples

```text
N = 3                 # replicas
W = 2                 # write acknowledgement threshold
R = 2                 # read threshold

write(k, v): wait_for_acks(W)
read(k):    choose_latest_version(wait_for_replies(R))
```

- **What it demonstrates**: A quorum configuration can tolerate one unavailable replica, but it still needs conflict detection and repair semantics.

```text
version = {A: 4, B: 2}
if incoming.version dominates version: replace()
elif neither dominates: retain both and merge()
```

- **What it demonstrates**: Causal versions distinguish a later overwrite from two concurrent updates.

## Reference Tables

| Strategy | Write path | Main benefit | Main risk |
|---|---|---|---|
| Single leader | one ordered writer | simple conflict model | failover and leader bottleneck |
| Multi-leader | several writers | multi-DC/offline latency | conflict resolution |
| Leaderless | quorum among replicas | flexible availability | repair, conflicts, and stale reads |

## Worked Example

Two offline shopping-cart clients start from `[milk]`. Client A adds flour; client B adds eggs. If the server uses version metadata, A’s write supersedes the original cart, while B’s write is concurrent rather than an overwrite. The server keeps both versions or merges them. When A later adds bacon, its client first merges the versions it has seen, producing a candidate such as `[milk, flour, eggs, bacon]`; the server records which concurrent version it subsumes. The important artifact is not the exact merge algorithm but the rule: preserve causal history long enough to avoid mistaking concurrency for an ordinary overwrite.

## Key Takeaways

1. Decide which reads may be stale and make that guarantee explicit.
2. Synchronous replication spends latency/availability to reduce acknowledged-write loss.
3. Session guarantees often provide a useful middle ground between eventual consistency and linearizability.
4. Prevent conflicts through ownership when possible; otherwise detect and resolve them deliberately.
5. Replication requires both a steady-state protocol and an operational plan for lag, outage, repair, and failover.

## Connects To

- **Chapter 6**: Partitioning determines which data is replicated together and how requests route.
- **Chapter 8–9**: Failover, clocks, ordering, and consensus constrain safe replication.
- **Chapter 11**: Replication logs are also the substrate for change streams and event processing.

