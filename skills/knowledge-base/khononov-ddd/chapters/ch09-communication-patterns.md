# Chapter 9: Communication Patterns

## Core Idea
Beyond a single bounded context's internal design, systems need patterns for translating models across bounded-context boundaries, reliably publishing aggregate state changes as events, and orchestrating business processes that span multiple aggregates or components.

## Frameworks Introduced
- **Model Translation** (Stateless and Stateful): the mechanism by which an anticorruption layer (ACL, downstream-owned) or open-host service (OHS, upstream-owned) converts between a source model and a target model.
  - When to use: whenever bounded contexts are in a customer-supplier relationship and one side cannot simply conform to the other's model.
  - How: **Stateless** translation happens on the fly via a proxy — inline in the codebase for synchronous calls, or via an API gateway (Kong, KrakenD, AWS API Gateway) which can also serve multiple published-language versions and act as a shared ACL/"interchange context." For asynchronous communication, a **message proxy** subscribes to source events, translates them, filters noise, and republishes to the target — this is essential for an OHS so raw domain events never leak the implementation model, and it separates private (internal) from public (published-language) events. **Stateful** translation is needed when the transformation must aggregate multiple incoming requests/messages into one, or unify data from multiple sources (e.g., backend-for-frontend); it requires its own persistent storage and cannot be done in a stateless API gateway — off-the-shelf stream/batch platforms (Kafka, Kinesis, NiFi, Glue, Spark) can substitute for custom code.
- **Saga** / **Process Manager**: two related but distinct patterns for cross-aggregate business processes. A **saga** is a long-running process (long in transactions, not necessarily time) that reacts to domain events by issuing commands to other components, including compensating actions on failure — strictly, it is simple *matching* of one event to one corresponding command, with no branching logic and implicit instantiation triggered by the first relevant event. A **process manager** is a central processing unit that holds explicit state for a multi-step business process and decides the next step based on that state and business logic (if/else branching) — it must be explicitly instantiated because no single triggering event exists.
  - When to use: saga for simple event-to-command matching flows spanning multiple aggregates/contexts; process manager for genuinely stateful multi-step workflows with conditional branching (e.g., trip booking with approval/rerouting logic).
  - How: subscribe to the relevant domain events, execute the corresponding aggregate commands, and for stateful cases persist as an event-sourced (or state-based) aggregate; move command execution out of the process/saga object itself into an async relay (an outbox-style `CommandIssuedEvent`) so failures don't lose issued commands.
- **Outbox pattern**: guarantees reliable, at-least-once publishing of an aggregate's domain events by committing state and events atomically, then relaying.
  - When to use: any time aggregate state changes must trigger published domain events — replaces both naive "publish from inside the aggregate" and "publish from the application layer after commit," both of which can desync database state from published events.
  - How: (1) commit the updated aggregate state and its new domain events in one atomic transaction (a dedicated outbox table for relational DBs, or an embedded `outbox` array on the record for NoSQL); (2) a message relay fetches unpublished events — either pull (poll the table, indexed) or push (transaction-log tailing / change streams, e.g., DynamoDB Streams); (3) relay publishes to the message bus; (4) on success, mark published or delete. Delivery is guaranteed at-least-once (relay crash after publish but before marking can cause a duplicate).

## Key Concepts
- **Anticorruption Layer (ACL)**: downstream-owned translation layer that adapts an upstream model to the downstream's own needs.
- **Open-Host Service (OHS)**: upstream-owned service that exposes a stable, integration-specific published language to protect consumers from its internal model.
- **Interchange context**: a bounded context whose sole purpose is translating/transforming models for convenient consumption by other components (e.g., a shared ACL behind an API gateway).
- **Published language**: the explicit, integration-optimized model an OHS exposes, distinct from its internal implementation model and from private (internal-only) domain events.
- **Message proxy**: an intermediary that subscribes to source events, applies model translation and filtering, and republishes to a target subscriber for asynchronous integration.
- **Outbox table / embedded outbox**: the durable store (dedicated table in RDBMS, embedded array in NoSQL documents) that co-commits domain events with aggregate state.
- **Message relay**: the component that fetches unpublished events from the outbox (pull or push) and publishes them to the message bus.
- **Saga vs. process manager**: saga = implicit, event-triggered, linear event-to-command matching with compensating actions; process manager = explicitly instantiated, stateful, branching business process.
- **Compensating action**: a command issued by a saga/process manager to undo or reconcile the effects of a prior step when a later step fails (e.g., `TrackPublishingRejection`).
- **Eventual consistency across aggregates**: only data within a single aggregate boundary is strongly consistent; everything coordinated via sagas/process managers across aggregates is eventually consistent.

## Mental Models
- Translation logic is the same shape whether it lives in an ACL or an OHS — the difference is only who owns/operates it and which direction the model conversion runs.
- "If your saga has if-else branching, it's actually a process manager" — the presence of conditional flow-control logic is the litmus test that distinguishes the two patterns, not implementation mechanics (both can be built as event-sourced aggregates).
- The outbox pattern is the eventing analog of the two-phase-commit problem: rather than coordinating a distributed transaction between the database and the message bus, make the message durable in the *same* transaction as the state change, then relay asynchronously.
- Sagas/process managers are not a workaround for bad aggregate boundaries — if two pieces of data truly need strong consistency, they belong in the same aggregate; sagas exist for genuinely cross-aggregate, eventually-consistent coordination.

## Anti-patterns
- **Publishing domain events directly from inside the aggregate**: the event may be dispatched before the transaction commits (subscriber sees a state that isn't actually persisted yet), and if the transaction later fails/rolls back, the already-published event cannot be retracted.
- **Publishing domain events from the application layer after commit, without an outbox**: closes one race but opens another — if the process crashes or the message bus is unreachable between the commit and the publish call, the database is updated but the events are silently lost forever, leaving the system permanently inconsistent.
- **Exposing raw internal domain events as the OHS's public contract**: couples consumers to the implementation model and removes the ability to evolve internals independently; always translate to a published language and separate private from public events.
- **Using distributed transactions across bounded contexts/aggregates to fake atomicity**: contradicts the core aggregate design principle that only intra-aggregate data is strongly consistent; the correct tool for cross-aggregate coordination is a saga/process manager plus eventual consistency, not a two-phase commit.

## Code Examples
```csharp
public class CampaignPublishingSaga
{
    private readonly ICampaignRepository _repository;
    private readonly IList<IDomainEvent> _events;
    ...
    public void Process(CampaignActivated activated)
    {
        var campaign = _repository.Load(activated.CampaignId);
        var advertisingMaterials = campaign.GenerateAdvertisingMaterials();

        var commandIssuedEvent = new CommandIssuedEvent(
            target: Target.PublishingService,
            command: new SubmitAdvertisementCommand(activated.CampaignId, advertisingMaterials));

        _events.Append(activated);
        _events.Append(commandIssuedEvent);
    }

    public void Process(PublishingConfirmed confirmed)
    {
        var commandIssuedEvent = new CommandIssuedEvent(
            target: Target.CampaignAggregate,
            command: new TrackConfirmation(confirmed.CampaignId, confirmed.ConfirmationId));

        _events.Append(confirmed);
        _events.Append(commandIssuedEvent);
    }
}
```
- **What it demonstrates**: a stateful saga that never executes commands directly — it only appends `CommandIssuedEvent`s to its own event stream, letting an outbox-style relay execute them asynchronously so a mid-process crash never loses a command.

## Reference Tables
| Pattern | Coordinates | Failure Handling |
|---|---|---|
| Outbox | Aggregate state → message bus (single aggregate's own events) | At-least-once delivery; unpublished events retried by relay until marked published |
| Saga | Multiple aggregates/components, implicit trigger, linear event→command matching | Compensating commands issued per failed step (e.g., `TrackPublishingRejection`) |
| Process Manager | Multiple aggregates/components, explicit instantiation, branching multi-step workflow | Business-logic-driven next-step decisions, including cancellation/rollback branches (e.g., cancel flight if no hotel available) |

## Worked Example
An advertising campaign, upon activation, must be submitted to a publisher and reconciled based on the publisher's response — a flow spanning the `Campaign` aggregate and the `AdPublishing` context, too large to co-locate in one aggregate. Implemented as a saga: it listens for `CampaignActivated` and issues `SubmitAdvertisement` to `AdPublishing`; it listens for `PublishingConfirmed` and issues `TrackPublishingConfirmation` on `Campaign`; it listens for `PublishingRejected` and issues `TrackPublishingRejection` (the compensating action) on `Campaign`. The stateless version calls commands directly against repositories inside each `Process` handler. The more robust, stateful version (shown above) treats the saga itself as an event-sourced aggregate: each `Process` handler only appends domain events (including `CommandIssuedEvent` wrappers) to its own event list, and a separate outbox relay executes the wrapped commands against their target endpoints — guaranteeing the saga's own state transitions and its outbound commands survive process failure. The chapter contrasts this with the `BookingProcessManager` example (flight/hotel booking with manager approval and rerouting branches), which requires explicit instantiation, persistent state (`_destination`, `_route`, `_rejectedRoutes`, etc.), and conditional logic to decide the next command — making it a process manager rather than a saga.

## Key Takeaways
1. Never publish domain events directly from an aggregate or right after a bare commit — use the outbox pattern so state and events are atomically committed and reliably (at-least-once) relayed.
2. Choose stateless proxy-based translation (inline or API gateway) for simple ACL/OHS conversions; reach for stateful translation with its own storage only when aggregating or unifying multiple sources is required.
3. Always translate an OHS's internal domain events into an explicit published language — never expose raw internal events to consumers.
4. Use a saga for simple, implicitly-triggered event-to-command matching across aggregates; use a process manager when the flow needs explicit state, branching logic, and explicit instantiation.
5. Route saga/process manager command execution through an outbox-style asynchronous relay, not direct calls within the event handler, to survive process crashes mid-workflow.
6. Remember that only single-aggregate data is strongly consistent — sagas and process managers coordinate multiple aggregates under eventual consistency, and should never be used to compensate for poorly drawn aggregate boundaries.

## Connects To
- **Ch4 (Integrating Bounded Contexts)**: this chapter is the tactical implementation layer for the strategic integration patterns (partnership, shared kernel, customer-supplier, conformist, ACL, OHS) introduced there.
- **Ch6 (Tackling Complex Business Logic)**: revisits the aggregate design principle that only intra-aggregate data is strongly consistent, and how aggregates publish domain events.
- **Ch15 (Event-Driven Architecture)**: expands on the private-vs-public event distinction and published-language design introduced here for asynchronous OHS translation.
- **External concept**: distributed transactions and two-phase commit as the anti-pattern the outbox and saga patterns are designed to avoid; eventual consistency as the governing consistency model for cross-component coordination.
