# Chapter 9: Consistency and Consensus

## Core Idea

Consistency is a guarantee about what readers may observe; consensus is a protocol for nodes to agree on one value/order despite failures. Stronger guarantees simplify application reasoning but cost latency and availability across network partitions. Separate linearizability, causal/total ordering, atomic commit, and consensus instead of treating them as synonyms.

## Frameworks Introduced

- **Linearizability**: Each operation appears to take effect atomically at one point between its invocation and response, and real-time order is respected.
  - When to use: locks, leader election, uniqueness checks, compare-and-set, or APIs where a completed write must be visible to a later read.
  - How: provide one current value/order to all clients; use a single leader with safe failover or a consensus-backed register; quantify the cross-region latency cost.
- **Causal consistency**: Preserve the happens-before relation while allowing concurrent operations to be observed in different orders.
  - When to use: systems that need understandable causality but cannot afford a global total order.
  - How: propagate dependency/version metadata and ensure a replica does not expose an effect before its causes.
- **Total order broadcast**: Deliver the same messages to all nodes in the same order, with reliable delivery.
  - When to use: replicated state machines, unique sequencing, and implementing a linearizable log/register.
  - How: define delivery and ordering scope, ensure messages are not lost/duplicated, and coordinate the ordering service.
- **Two-phase commit versus consensus**: 2PC atomically commits a transaction across participants but can block if the coordinator fails; consensus chooses a value/order with stronger progress properties under its model.
  - When to use: choose between atomic transaction boundaries and a replicated decision log.
  - How: treat the coordinator’s commit record as a promise requiring durable recovery; do not mistake 2PC or 2PL for consensus.
- **Consensus properties**: Uniform agreement, integrity, validity, and termination define what a fault-tolerant consensus algorithm must provide.
  - When to use: leader election, membership, configuration, or any one-value decision among nodes.
  - How: use a proven consensus implementation and understand its quorum, epoch, recovery, and timing assumptions.
- **CAP as a narrow trade-off**: Under a network partition, a system cannot simultaneously provide linearizable consistency and availability for every request. It is not a complete architecture guide.

## Key Concepts

- **Linearizability**: Single-copy, real-time-respecting semantics for individual operations.
- **Serializability**: Transaction results equivalent to some serial order.
- **Causality**: A cause precedes its effects; concurrent events need not have one true order.
- **Lamport timestamp**: Logical timestamp that respects happens-before but cannot identify all concurrency.
- **Total order broadcast**: Reliable delivery of the same ordered sequence to all subscribers.
- **Atomic commit**: All participants commit or all abort.
- **Two-phase commit (2PC)**: Prepare/vote followed by a durable commit/abort decision.
- **Consensus**: Nodes agree on one value despite failures.
- **Epoch/term**: Monotonically increasing leadership generation used to reject stale leaders.
- **Coordination service**: Linearizable primitives for membership, locks, leader election, or configuration.

## Mental Models

- Linearizability is about real-time visibility; serializability is about transaction histories. A system can have one without the other.
- Causality gives a partial order; assigning numbers does not automatically give a meaningful total order.
- A coordinator can be unavailable while a participant is uncertain; atomic commit must account for the in-doubt state.
- Coordination services are small consensus-backed control planes, not general-purpose databases for application data.

## Anti-patterns

- **Calling a replicated store “strongly consistent” without naming the guarantee**: linearizable, causal, read-after-write, and eventual semantics differ.
- **Using wall-clock timestamps as a total order**: clocks can drift and concurrent events can share/reverse timestamps.
- **Confusing 2PC with consensus or 2PL**: they solve different problems and fail differently.
- **Treating CAP as “pick two” at all times**: the impossibility concerns behavior during a partition and a particular consistency/availability definition.

## Code Examples

```text
compare_and_set(key, expected, replacement):
  atomically:
    if register[key] == expected:
      register[key] = replacement
      return success
    return failure
```

- **What it demonstrates**: A linearizable compare-and-set can support uniqueness and leader/lock decisions; eventual reads cannot safely substitute for it.

```text
coordinator -> PREPARE -> participants
participants -> YES/NO -> coordinator
coordinator: persist COMMIT only if every vote is YES
coordinator -> COMMIT/ABORT -> participants (retry until learned)
```

- **What it demonstrates**: 2PC has a durable commit point and an in-doubt period in which participants may hold locks while waiting for the coordinator.

## Reference Tables

| Mechanism | Orders/guarantees | Typical use | Failure cost |
|---|---|---|---|
| Linearizable register | one current value, real-time order | CAS, leader election | coordination latency/partition unavailability |
| Causal consistency | preserves dependencies | collaborative/user-facing feeds | metadata and delayed visibility |
| Total order broadcast | same sequence everywhere | replicated log/state machine | ordering service/quorum dependency |
| 2PC | all-or-nothing commit | distributed transaction | coordinator failure can block |
| Consensus | one agreed decision | membership/leader/configuration | quorum and recovery complexity |

## Worked Example

An application reserves usernames. With only eventually consistent replicas, two clients can each read “available” and write the same name. A linearizable compare-and-set on a single ownership register, or an ordered log where the first claim wins, makes the decision unique. If the operation also updates several databases, 2PC can coordinate the commit but adds a blocking failure mode; an alternative is to record the claim in one strongly ordered system and derive other views asynchronously.

## Key Takeaways

1. Name the exact consistency and ordering guarantee an operation needs.
2. Linearizability simplifies single-object coordination but can reduce availability during partitions.
3. Causal ordering is weaker than a total order but often sufficient and cheaper.
4. 2PC provides atomic commit, not consensus or nonblocking progress.
5. Use proven consensus-backed coordination for leadership, membership, and uniqueness decisions.

## Connects To

- **Chapter 5**: Replication determines which consistency guarantees are feasible.
- **Chapter 7**: Serializability concerns transaction histories; linearizability concerns individual operations in real time.
- **Chapter 8**: Timing and failure models define what consensus/coordination can promise.

