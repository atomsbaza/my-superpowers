# Chapter 7: Modeling the Dimension of Time

## Core Idea
A state-based record only shows an aggregate's current values; it discards the story of how it got there. Event sourcing persists every change to an aggregate as an immutable domain event and treats that event stream — not any derived table — as the system's source of truth.

## Frameworks Introduced
- **Event Sourcing**: instead of persisting an aggregate's current state, persist the sequence of domain events describing every change to that state, and use the events themselves as the source of truth.
  - When to use: complex business logic in a core subdomain where deep insight into *why* and *how* state changed matters — analytics, audit/compliance, retroactive debugging — not merely *what* the current state is.
  - How: (1) load an aggregate's events from the event store; (2) reconstitute/project a state representation by applying each event in order; (3) execute the aggregate's command against that in-memory state to produce new domain events; (4) append the new events to the event store using optimistic concurrency (expected version check). State is never written directly — it is always derived by replaying events.

## Key Concepts
- **Event Store**: an append-only database that stores domain events; supports at minimum `Fetch(instanceId)` and `Append(instanceId, events, expectedVersion)`; disallows mutation or deletion of events except for rare cases like data migration.
- **Event-Sourced Domain Model**: the domain model pattern (value objects, aggregates, domain events) combined with event sourcing as the persistence mechanism — the term is used instead of plain "event sourcing" to emphasize it governs the domain model's aggregate lifecycles specifically.
- **Source of Truth**: the strongly consistent storage that all other representations are derived from — in this pattern, the event store, not any projected state table.
- **Projection**: the process (and resulting model) of applying a sequence of events, via `Apply(event)` methods, to build a state representation optimized for a specific purpose (current state, search, analysis, etc.).
- **Version**: a counter incremented on each applied event, representing the number of modifications made to the aggregate; used both for optimistic concurrency and for "time travel" (replaying only events up to a given version).
- **Time Traveling**: reconstituting an aggregate's state as of any past point by applying only the events up to that version.
- **Snapshotting**: caching a periodically computed projection so that rehydration only needs to apply events since the snapshot, rather than the full history — an optimization, not a default.
- **Forgettable Payload**: a pattern for physically "deleting" sensitive data in an append-only event store by encrypting the payload per-aggregate and deleting the external encryption key rather than the event.
- **Sharding by Aggregate ID**: scaling strategy for the event store — since all operations on an aggregate touch only its own event stream, events for one aggregate instance are co-located in a single shard.

## Mental Models
- Store what happened, not just what is true right now — the current state is just one possible projection of the event history.
- A ledger, not a snapshot: like financial accounting, the append-only log of transactions is authoritative; balances are always derived, never stored as truth.
- One event stream, many projections — the same events can be replayed into a current-state model, a search index, an analytics model, or any future model not yet imagined, without touching the source data.
- "Show me your tables and I won't need your flowchart" (Fred Brooks) — but a pure current-state table hides the flowchart entirely; event sourcing keeps the flowchart (the process) recoverable from the data itself.

## Anti-patterns
- **Mutating or deleting events in the event store**: breaks the append-only guarantee that makes the store a reliable source of truth and audit log; the only sanctioned exception is exceptional data migration, and GDPR-style deletion should use the forgettable payload pattern instead of physical deletion.
- **Writing to an operational database and a separate log file "for audit purposes"**: this is effectively an uncoordinated two-system transaction — if one write fails and the other succeeds, the log becomes eventually inconsistent with the real state, and nothing guarantees rollback of the log.
- **State-based model + same-transaction writes to a manual "logs" table**: consistent but not resilient to human error (an engineer can forget to append a log record), and without enforced structure the log table's schema tends to degrade into inconsistent ad hoc data over time.
- **State-based model + database trigger snapshotting rows into a "history" table**: automatically consistent and complete, but only captures *what* fields changed, never *why* — losing business context needed to build richer projections (e.g., search over historical values, analysis of follow-up counts).
- **Implementing snapshotting or sharding prematurely**: these are optimizations that address measured problems (10,000+ events per aggregate, storage scale); applying them without that justification is accidental complexity — first double-check aggregate boundaries.

## Code Examples
```csharp
public class TicketState
{
    public TicketId Id { get; private set; }
    public int Version { get; private set; }
    public bool IsEscalated { get; private set; }
    ...
    public void Apply(TicketInitialized @event)
    {
        Id = @event.Id;
        Version = 0;
        IsEscalated = false;
        ....
    }

    public void Apply(TicketEscalated @event)
    {
        IsEscalated = true;
        Version += 1;
    }
    ...
}

public class Ticket
{
    ...
    private List<DomainEvent> _domainEvents = new List<DomainEvent>();
    private TicketState _state;
    ...
    public Ticket(IEnumerable<IDomainEvents> events)
    {
        _state = new TicketState();
        foreach (var e in events)
        {
            AppendEvent(e);
        }
    }

    private void AppendEvent(IDomainEvent @event)
    {
        _domainEvents.Append(@event);
        // Dynamically call the correct overload of the "Apply" method.
        ((dynamic)state).Apply((dynamic)@event);
    }

    public void Execute(RequestEscalation cmd)
    {
        if (!_state.IsEscalated && _state.RemainingTimePercentage <= 0)
        {
            var escalatedEvent = new TicketEscalated(_id, cmd.Reason);
            AppendEvent(escalatedEvent);
        }
    }
    ...
}
```
- **What it demonstrates**: an event-sourced aggregate's constructor rehydrates state by replaying events through an `Apply` dispatch, and a command handler never mutates state directly — it only ever appends a new domain event, letting `AppendEvent` update the in-memory projection as a side effect.

## Reference Tables
| Aspect | Advantage | Disadvantage |
|---|---|---|
| Time traveling | Reconstitute any past state of an aggregate for analysis or retroactive debugging | — |
| Deep insight | Same event stream can be projected into unlimited new representations without re-deriving from a flat current-state table | — |
| Audit log | Strongly consistent, legally sufficient audit trail comes "for free" | — |
| Concurrency management | Can inspect exactly which events were concurrently appended and make a domain-driven decision instead of a blind conflict/overwrite exception | — |
| Learning curve | — | Sharply different from traditional CRUD-style persistence; requires team training and a mindset shift |
| Evolving the model | — | Changing an event's schema is far harder than an ALTER TABLE, since events are meant to be immutable (Greg Young wrote a whole book on this) |
| Architectural complexity | — | Introduces more moving parts (event store, projections, later CQRS) than a simple state-based model |
| Performance at scale | Sharding by aggregate ID scales cleanly since all operations are per-aggregate | Replaying grows costlier as events accumulate — noticeable in most systems only past ~10,000 events per aggregate, mitigated by snapshotting if genuinely needed |

## Worked Example
A telemarketing "lead" aggregate. The state-based table only shows columns like status, phone-number, created-on, updated-on — e.g., lead 12 shows `CONVERTED`, but nothing about the journey. The event-sourced version instead stores a stream: `lead-initialized` → `contacted` → `followup-set` → `contact-details-updated` (phone/name correction) → `contacted` (follow-up call) → `order-submitted` → `payment-confirmed`. Three different projections are built from this same stream:
1. **LeadStateProjection** — applies each event to rebuild the exact current-state row (status, contact info, `Version`), reproducing what the original table stored.
2. **LeadSearchModelProjection** — accumulates *all* historical values of first name, last name, and phone number into sets, so a sales agent can find a lead by an old phone number even after it changed.
3. **AnalysisModelProjection** — counts `FollowupSet` events per lead to answer a business-intelligence question ("how many follow-ups were scheduled?") that the original schema couldn't answer at all.

All three projections are derived purely by iterating the same six events and dispatching to type-specific `Apply` overloads — nothing new had to be captured retroactively, because the events already contained the full story.

## Key Takeaways
1. Persist events describing *what happened*, not just the resulting state — current state is always a derived projection, never the source of truth.
2. Prefer event sourcing for core subdomains needing audit trails, retroactive analysis, or deep behavioral insight — not as a default persistence strategy.
3. One event stream supports unlimited future projections (search models, analytics models, current-state models) without touching historical data.
4. The event store must be append-only; handle regulatory deletion (GDPR) via the forgettable payload pattern (encrypt + destroy the key), not by mutating events.
5. Don't reach for snapshotting or sharding until measured aggregate size/scale actually requires it — check aggregate boundaries first; premature optimization here is accidental complexity.
6. Ad hoc alternatives (separate log files, manual log-table inserts, DB-trigger history tables) each fail differently — dual-write inconsistency, missed manual calls, or losing the "why" behind a change — event sourcing avoids all three by making the event itself the unit of truth.
7. Optimistic concurrency in an event-sourced system can be smarter than a plain stale-read exception: inspect the actual concurrently appended events and decide, per business rule, whether they truly conflict.

## Connects To
- **Ch 6**: Tackling Complex Business Logic (Domain Model) — event-sourced domain model reuses the same aggregates, value objects, and domain events; the Ticket aggregate example continues directly from Chapter 6.
- **Ch 8**: Architectural Patterns — introduces CQRS, needed to persist the projected read models (search, analysis) described here rather than computing them in-memory each time.
- **Ch 11**: Evolving Design Decisions — covers migrating a domain model to an event-sourced domain model as business needs evolve.
- **Ch 10**: Design Heuristics — offers rules of thumb for choosing between state-based, domain model, and event-sourced domain model implementation patterns.
- **CQRS**: command-query responsibility segregation, the architectural pattern that pairs naturally with event sourcing to serve multiple read-optimized projections.
- **Event Store databases**: purpose-built append-only stores (e.g., EventStoreDB) implementing the `Fetch`/`Append` contract with optimistic concurrency described in this chapter.
