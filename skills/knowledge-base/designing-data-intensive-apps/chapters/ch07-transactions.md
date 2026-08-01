# Chapter 7: Transactions

## Core Idea

Transactions bundle reads and writes into an abstraction that protects application invariants, but the word “transaction” does not specify one isolation guarantee. Understand ACID, identify the anomaly a workload can tolerate, and choose the weakest isolation/strongest mechanism that preserves correctness.

## Frameworks Introduced

- **ACID as a design checklist**: Atomicity groups effects, consistency preserves application invariants, isolation controls concurrent visibility, and durability survives successful commit.
  - When to use: define what a transaction promises and which parts are database versus application responsibilities.
  - How: name the invariant, failure boundary, visibility rule, and durable commit point; do not treat “ACID” as a single implementation.
- **Read committed**: No dirty reads and no dirty writes, but repeated reads may observe different committed values.
  - When to use: simple workflows where read skew and lost updates are prevented separately.
- **Snapshot isolation/MVCC**: Each transaction reads from a consistent snapshot while writes are checked for conflicts.
  - When to use: long reads and concurrent workloads where blocking readers is undesirable.
  - How: assign a snapshot, hide later/in-progress writes, and detect conflicting writes at commit.
- **Serializable execution**: The outcome is equivalent to running transactions one at a time.
  - When to use: cross-row invariants, uniqueness, booking, money movement, or any write-skew-sensitive workflow.
  - How: use actual serial execution, two-phase locking (2PL), or serializable snapshot isolation (SSI); each has different performance/failure behavior.
- **Lost update and write-skew diagnosis**: A read-modify-write cycle can overwrite a concurrent update; two transactions can each make a locally valid decision that jointly violates an invariant.
  - When to use: review application logic that checks a condition before writing.
  - How: use atomic operations, explicit locks, compare-and-set, conflict detection, materialized conflict rows, or serializable isolation.

## Key Concepts

- **Atomicity**: All effects of a transaction happen or none do.
- **Consistency**: Application invariants hold before and after a committed transaction.
- **Isolation**: Concurrent transactions do not observe prohibited intermediate/interleaved states.
- **Durability**: A committed result survives crashes according to the stated guarantee.
- **Dirty read**: Reading uncommitted data from another transaction.
- **Dirty write**: Overwriting uncommitted data.
- **Read skew**: One transaction observes different committed versions during a logical read.
- **Lost update**: A later write silently overwrites a concurrent update.
- **Write skew**: Concurrent transactions update different rows based on a shared, now-invalid premise.
- **Phantom**: A predicate query sees a row appear/disappear because another transaction changes the matching set.

## Mental Models

- Isolation is about histories, not just locks: ask which interleavings are allowed.
- A business rule over a set of rows is a predicate; row-level locking may not protect the absence of a matching row.
- Snapshot isolation gives a stable view, not automatically serializable decisions.
- Materializing a conflict (for example, a lock row per room) turns an implicit predicate conflict into a concrete row that can be locked.

## Anti-patterns

- **Calling a database “ACID” without naming isolation**: Different systems use the same label for materially different behavior.
- **Checking then writing without atomicity/locking**: The check can be invalidated before the write.
- **Assuming snapshot isolation prevents write skew**: Transactions can read the same snapshot and update different rows successfully.
- **Using application retries without idempotence**: A timeout may leave the transaction committed; blindly repeating the operation can duplicate effects.

## Code Examples

```sql
BEGIN TRANSACTION;

SELECT 1
FROM bookings
WHERE room_id = :room
  AND starts_at < :new_end
  AND ends_at > :new_start
FOR UPDATE;

-- Insert only if the protected predicate has no conflicting row.
INSERT INTO bookings(room_id, starts_at, ends_at)
VALUES (:room, :new_start, :new_end);
COMMIT;
```

- **What it demonstrates**: A booking invariant needs protection against a concurrent matching row; a plain pre-check without predicate/index-range protection is vulnerable to write skew or phantoms.

## Reference Tables

| Isolation/technique | Prevents | Does not automatically prevent |
|---|---|---|
| Read committed | dirty reads/writes | read skew, lost updates, write skew |
| Snapshot isolation | dirty reads, many read anomalies | write skew, all serialization anomalies |
| 2PL serializability | conflicting interleavings | blocking/deadlocks and performance cost |
| SSI serializability | dangerous snapshot dependencies | aborts/retries under contention |

## Worked Example

Two doctors are on call, and the invariant is “at least one doctor remains on call.” Each transaction reads two on-call rows, sees two doctors, and takes one doctor off call. Under snapshot isolation, both transactions can commit because they write different rows. The invariant is violated. Fixes include serializable isolation/SSI, locking a shared “on-call roster” row, or materializing a single guard row that every status change must update. The right fix depends on contention, latency, and whether abort/retry is acceptable.

## Key Takeaways

1. State the application invariant before choosing an isolation level.
2. Read committed is not repeatable read; snapshot isolation is not serializability.
3. Protect read-modify-write operations with atomic updates, compare-and-set, locks, or conflict detection.
4. Predicate constraints require predicate/index-range protection or materialized conflicts.
5. Distributed transactions and retries make commit/operation identity part of correctness.

## Connects To

- **Chapter 6**: Partitioning makes cross-partition transactions and serializability more difficult.
- **Chapter 8–9**: Distributed commit, ordering, and consensus add failure modes beyond local isolation.
- **Chapter 11–12**: Idempotence and end-to-end checks extend transaction-like guarantees across dataflows.

