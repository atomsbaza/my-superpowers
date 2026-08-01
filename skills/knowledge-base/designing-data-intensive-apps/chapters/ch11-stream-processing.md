# Chapter 11: Stream Processing

## Core Idea

Streams represent data that becomes available over time. They enable low-latency reactions and continuous derived views, but require explicit rules for delivery, ordering, offsets, time, late data, joins, replay, and failure recovery. A durable log and idempotent/state-aware consumers make “real time” a manageable dataflow problem.

## Frameworks Introduced

- **Messaging delivery and consumer ownership**: Direct messaging, broker queues, and log-based systems make different choices about load balancing, fan-out, acknowledgement, and replay.
  - When to use: choose based on whether each message is work for one consumer, a broadcast event, or durable history for many consumers.
  - How: define backpressure, redelivery, retention, offset ownership, and what happens when consumers cannot keep up.
- **Partitioned log**: Append events to ordered partitions; consumers track offsets and can replay from an earlier position.
  - When to use: durable event streams, CDC, integration, and multiple independent consumers.
  - How: partition by a key whose order must be preserved, commit offsets with state carefully, and retain enough history for recovery/reprocessing.
- **Change data capture and event sourcing**: Derive a stream from database changes or store domain events as the source of truth.
  - When to use: keep search/index/cache systems synchronized or reconstruct state/history.
  - How: define event identity/order, take an initial snapshot, capture changes, compact/rebuild derived state, and distinguish commands from events.
- **Event time versus processing time**: Event time is when the fact occurred; processing time is when a processor observed it.
  - When to use: windows, metrics, fraud detection, and late/out-of-order events.
  - How: choose window semantics, use watermarks/heuristics for completeness, and specify how corrections are emitted.
- **Stream joins**: Stream–stream joins need a time window; stream–table joins enrich an event using current table state; table–table joins maintain a derived view.
  - When to use: combine events, reference data, or changing materialized tables.
  - How: state the time/ordering assumption and define behavior when one side arrives late or is updated.
- **Fault tolerance through replay and idempotence**: Rebuild state from the log or checkpoints; duplicate processing must not duplicate external effects.
  - When to use: at-least-once delivery, retries, consumer restarts, and stateful processors.
  - How: use deterministic state updates, idempotency keys, transactional offset/state commits, or compensating records.

## Key Concepts

- **Event stream**: Unbounded sequence of records arriving over time.
- **Message broker**: Mediates delivery/queueing between producers and consumers.
- **Partitioned log**: Durable ordered log split into independent partitions.
- **Consumer offset**: Position a consumer has processed/committed.
- **Backpressure**: Slowing producers when consumers cannot keep up.
- **Change data capture (CDC)**: Stream of database changes.
- **Event sourcing**: Store domain events and derive current state.
- **Event time**: Timestamp of the real-world event.
- **Processing time**: Timestamp when the processor handles the event.
- **Watermark**: Heuristic that the system has likely seen events up to a time.
- **Window**: Bounded interval used to aggregate/join an unbounded stream.
- **Idempotence**: Repeating an operation has the same logical effect as doing it once.

## Mental Models

- A log is both a transport and a durable database of facts; consumers are independent materialized views.
- “Exactly once” usually means exactly-once effect under a defined boundary, not that a message is physically delivered once.
- Event time is part of the data model; processing time is an implementation observation.
- A replayable event stream makes application evolution a recomputation problem, but schema and semantics must remain interpretable.

## Anti-patterns

- **Using processing time for business time**: Late events are assigned to the wrong window and metrics become irreconcilable.
- **Committing offsets before durable state/effects**: A crash can lose the event while the offset says it was processed.
- **Assuming a queue is a log**: Work-queue acknowledgement and replayable history are different semantics.
- **Calling an external side effect exactly once without an idempotency key**: Retries can repeat a payment, email, or mutation.

## Code Examples

```text
for event in log.read_from(offset):
  state = update(state, event)             # deterministic
  publish(view_key(event), state)
  commit(offset=event.offset, state=state)  # one recovery boundary
```

- **What it demonstrates**: State, derived output, and progress need a coordinated recovery story; otherwise replay can create gaps or duplicates.

```text
window = [event_time - 5 minutes, event_time]
aggregate = count(events where event_time in window)
emit_correction_when_late_event_arrives()
```

- **What it demonstrates**: A time window must specify its clock and correction policy, not just its duration.

## Reference Tables

| System | Consumer behavior | Replay | Typical use |
|---|---|---|---|
| Direct messaging | producer targets consumer | usually limited | low-latency point-to-point |
| Queue/broker | one consumer in a group handles work | redelivery/retention varies | task distribution |
| Partitioned log | consumers own offsets | native replay | events, CDC, multiple views |

| Join | State needed | Time assumption |
|---|---|---|
| Stream–stream | both sides/window state | matching event-time range |
| Stream–table | current table/materialized state | table version visible at processing |
| Table–table | two maintained views | updates trigger recomputation |

## Worked Example

An order service emits `OrderPlaced` and `PaymentCaptured` events into a partitioned log keyed by order ID. A stream processor maintains an order-status view. The payment event may arrive late, so the processor keeps state for a bounded window and emits a correction when the second event appears. It writes the view with an idempotency key `(order_id, version)` and commits its offset only with durable state. After a crash, replay reconstructs the view; downstream consumers see the same logical result even if internal processing repeats.

## Key Takeaways

1. Choose queue versus log semantics based on replay, fan-out, and consumer independence.
2. Partition by the key whose order/state must be local.
3. Make event time, lateness, windows, and corrections explicit.
4. Assume retries and duplicates; make state updates and side effects idempotent.
5. Treat offsets, state, and published output as one recovery design.

## Connects To

- **Chapter 4**: Replay and mixed consumers make schema evolution a stream concern.
- **Chapter 5**: Logs and replication provide ordering, durability, and change streams.
- **Chapter 10–12**: Streams incrementally maintain the derived data that batch jobs can rebuild.

