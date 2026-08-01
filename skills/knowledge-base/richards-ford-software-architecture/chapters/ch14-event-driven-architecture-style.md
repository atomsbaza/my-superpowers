# Chapter 14: Event-Driven Architecture Style

## Core Idea

Event-driven architecture communicates through events and messages, enabling asynchronous processing, temporal decoupling, and multiple consumers. The style offers strong flexibility and scalability, but requires explicit decisions about topology, ordering, delivery, failure, idempotency, and data loss.

## Frameworks Introduced

- **Broker topology**: a central event broker manages channels, routing, and delivery between producers and consumers.
- **Mediator topology**: a mediator orchestrates event processing and can coordinate complex workflows.
- **Asynchronous capabilities**: decouple producers and consumers in time and rate, at the cost of immediate consistency and simpler debugging.
- **Request-reply**: retain asynchronous transport while providing a correlated response for interactions that need one.
- **Hybrid event-driven architecture**: combine request-based calls and events according to workflow needs.

## Key Concepts

- **Event** — a record that something happened.
- **Event producer** — creates and publishes an event.
- **Event consumer** — receives and processes an event.
- **Broker** — routes and stores messages between producers and consumers.
- **Mediator** — coordinates event flow and complex processing.
- **Choreography** — consumers react independently to events.
- **Request-reply** — asynchronous request and correlated response.
- **Idempotency** — repeated processing produces the same intended outcome.
- **Poison message** — a message that repeatedly fails processing.
- **At-least-once delivery** — messages may be delivered more than once.

## Mental Models

Use events when producers should not wait for every consumer, when multiple consumers need the same fact, or when temporal decoupling improves resilience. Use request-based communication when the caller needs an immediate authoritative result.

Treat the broker as part of the architecture quantum and failure domain. Broker capacity, retention, partitions, ordering, and recovery matter as much as application code.

Design event handling as at-least-once unless the platform and proof justify stronger semantics. Persist an idempotency key or use a transactional inbox/outbox approach.

## Anti-patterns

- **Event soup**: events have unclear ownership, semantics, or versioning.
- **Synchronous event chain**: consumers immediately call other services, recreating a hidden request chain.
- **Unbounded retry**: a poison message blocks a partition or generates an outage.
- **Lost event assumption**: publishing and state mutation are not coordinated.
- **Event as remote command**: an event claims something happened but actually demands a specific action from one consumer.

## Code Examples

An idempotent consumer:

```text
on(OrderConfirmed event):
    if inbox.contains(event.id): return
    transaction:
        apply_fulfillment(event)
        inbox.add(event.id)
```

An outbox coordinates local state and publication:

```text
transaction:
    update_order()
    insert_outbox(event)
publisher -> deliver outbox events -> mark delivered
```

## Reference Tables

| Choice | Good fit | Main trade-off |
|---|---|---|
| Broker topology | Many independent consumers | Broker governance and routing complexity |
| Mediator topology | Complex workflows and coordination | Central coupling and bottleneck risk |
| Choreography | Simple independent reactions | Harder global reasoning |
| Orchestration | Explicit multi-step process | Orchestrator becomes coupling point |
| Request-reply | Immediate result over async transport | Correlation and timeout complexity |

## Worked Example

When an order is confirmed, Inventory, Fulfillment, Analytics, and Notification consume `OrderConfirmed`. The order service writes the order and outbox event in one transaction. Each consumer records the event ID before applying side effects. Fulfillment retries transient failures and sends poison messages to a dead-letter channel. A customer-facing order status endpoint reads the current state rather than pretending that event publication is an immediate synchronous response.

## Key Takeaways

1. Event-driven architecture buys temporal and rate decoupling, not free simplicity.
2. Define topology, delivery, ordering, failure, idempotency, and evolution explicitly.
3. Use request-reply only where an immediate result is required.
4. Coordinate state changes and event publication to prevent loss or duplication damage.

## Connects To

- **Chapter 11:** filters and pipes provide a processing analogy.
- **Chapter 16:** orchestration makes workflow coordination explicit.
- **Chapter 17:** microservices use events but must control distributed coupling.

