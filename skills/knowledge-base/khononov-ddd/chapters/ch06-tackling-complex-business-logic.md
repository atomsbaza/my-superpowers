# Chapter 6: Tackling Complex Business Logic

## Core Idea
When business logic involves entangled state transitions, rules, and invariants (not CRUD), the Domain Model pattern — built from DDD's tactical "Building Blocks" (value objects, entities, aggregates, domain events, domain services) — encapsulates that complexity so it lives in one place instead of leaking across the codebase.

## Frameworks Introduced
- **Domain Model**: "An object model of the domain that incorporates both behavior and data" (Fowler's term; Evans's tactical DDD patterns are its building blocks).
  - When to use: for core subdomains with complex business logic — entangled state transitions, business rules, and invariants that must be protected at all times (e.g., a help-desk ticket lifecycle with SLA, escalation, reassignment, and closure rules).
  - How: model objects as plain old objects (POCOs/POJOs/POPOs) free of infrastructural/technological concerns; express concepts and operations in the bounded context's ubiquitous language rather than generic CRUD verbs.
- **Building Blocks** (Value Object, Entity, Aggregate, Domain Event, Domain Service): the tactical toolkit Evans introduced to implement the Domain Model pattern.
  - When to use: Value Object — for anything identified purely by its values (properties of entities: money, addresses, statuses, measurements). Entity — only ever inside an Aggregate, never standalone, when an object needs identity because two instances can share all other values. Aggregate — when a business invariant spans multiple objects that must be updated together, atomically, in one transaction. Domain Event — to broadcast that something significant already happened in the domain, for other aggregates/systems to react to. Domain Service — when logic doesn't belong to any single aggregate or value object, or must orchestrate/read across multiple aggregates.
  - How: Value Objects are immutable, compared by value (override equality), and centralize validation + behavior that produces new instances. Aggregates expose a public interface of "commands" (methods or command objects) as the only way to mutate state, enforce invariants inside that boundary, use an aggregate root as the single entry point, use a version field for optimistic concurrency, and commit as one atomic transaction referencing other aggregates only by ID. Domain Services are stateless objects that orchestrate reads/calculations across multiple aggregates but never bypass the one-aggregate-per-transaction rule.

## Key Concepts
- **Value Object**: an object identified solely by the composition of its values, immutable, with no explicit ID field, since two instances with identical values are the same value.
- **Entity**: an object requiring an explicit identification field because its other attributes alone can't guarantee uniqueness (e.g., namesakes); mutable over its lifecycle; only implemented inside an aggregate, never independently.
- **Aggregate**: a hierarchy of entities and value objects sharing one transactional/consistency boundary, whose state can be mutated only through its own public commands.
- **Aggregate Root**: the single designated entity in an aggregate's hierarchy that exposes the aggregate's public interface; all mutation of internal entities happens only through it.
- **Invariants**: business rules that must hold true at all times; aggregates exist specifically to protect them by disallowing external mutation of internal state.
- **Domain Event**: a message, named in the past tense, describing a significant event that already occurred in the business domain, published by an aggregate for other components to subscribe to.
- **Domain Service**: a stateless object hosting business logic that doesn't naturally belong to any aggregate or value object, typically orchestrating reads across multiple aggregates; unrelated to "microservices" despite the shared word "service."
- **Degrees of Freedom / Managing Complexity**: Goldratt's measure of system complexity — the number of independent data points needed to fully describe a system's state; encapsulating invariants inside value objects/aggregates reduces degrees of freedom and thus reduces complexity, even if the code looks "busier."

## Mental Models
- **Complexity = degrees of freedom**: a class with more independently-settable fields is harder to control/predict than one where some fields are derived/constrained by invariants — even if the constrained class has more code. Aggregates and value objects intentionally reduce degrees of freedom by owning their invariants.
- **Consistency draws the aggregate boundary, not object-graph convenience**: include in an aggregate only what must be *strongly* consistent for its business rules to hold; anything that can be eventually consistent belongs in a different aggregate, referenced by ID only.
- **One aggregate instance per transaction is a design signal, not a limitation to route around**: if you feel the need to modify two aggregates in one transaction, that's a sign the aggregate boundary itself may be drawn wrong (or that a domain service / eventual process, covered later in the book, is the right tool).
- **Value objects turn conventions into types**: instead of "remember this string is a phone number," the type system encodes and enforces that fact, moving validation from scattered call sites into one cohesive, testable place — directly serving the ubiquitous language.

## Anti-patterns
- **Primitive obsession**: relying on primitives (strings, ints) to represent domain concepts (phone numbers, country codes, money) instead of value objects — duplicates validation logic, is easy to forget to validate, and hides intent behind naming conventions.
- **Redundant identity on a value**: adding an explicit ID field to something that should be a value object (e.g., a `ColorId` on a Color) opens a bug class where two rows have identical values but different IDs, breaking the "same value = same instance" guarantee.
- **Mutating aggregate internals from outside**: allowing external code to modify an aggregate's internal entities directly (bypassing the aggregate root's commands) scatters business logic across the application layer and risks corrupting invariants — this is the active-record failure mode the chapter contrasts against.
- **Aggregates too large**: including data that only needs eventual consistency inside the strong-consistency boundary hurts performance/scalability and unnecessarily widens the transaction; the fix is to reference other aggregates by ID.
- **Aggregates too small (implied)**: splitting apart objects whose invariants must be checked together (so a rule can't be enforced atomically) reintroduces the very state-corruption risk aggregates exist to prevent — e.g., the ticket/messages reassignment rule breaks if unread-message data is only eventually consistent.
- **Using domain services as a transaction loophole**: domain services can read across aggregates for calculations, but must never be used to modify more than one aggregate instance per transaction — that rule still holds.

## Code Examples
```csharp
public class Ticket
{
    ...
    List<Message> _messages;
    ...

    public void Execute(EvaluateAutomaticActions cmd)
    {
        if (this.IsEscalated && this.RemainingTimePercentage < 0.5 &&
            GetUnreadMessagesCount(for: AssignedAgent) > 0)
        {
            _agent = AssignNewAgent();
        }
    }

    public int GetUnreadMessagesCount(UserId id)
    {
        return _messages.Where(x => x.To == id && !x.WasRead).Count();
    }
    ...
}
```
- **What it demonstrates**: an aggregate command enforcing a multi-condition invariant ("reassign if escalated, time is nearly up, and the agent hasn't read messages") atomically against strongly consistent data — the reason the Message list must live inside the Ticket aggregate's boundary rather than being eventually consistent.

## Reference Tables
| Building Block | Identity? | Mutable? | Purpose |
|---|---|---|---|
| Value Object | No — identified by its values | No — immutable, operations return new instances | Model domain properties (money, name, phone, color) with encapsulated validation/behavior |
| Entity | Yes — explicit ID field | Yes, but only via its owning aggregate's commands | Represent a business object needing identity beyond its attribute values; never used standalone |
| Aggregate | Yes — has an ID (via its root) | Yes — via public commands only | Enforce invariants and transactional/consistency boundary over a hierarchy of entities + value objects |
| Domain Event | No (has an event ID for tracking, not entity identity) | No — immutable record of the past | Announce a significant fact that happened, in past tense, for other components to react to |
| Domain Service | N/A — stateless, no identity | N/A — holds no state | Host business logic/calculations that span multiple aggregates or fit no single aggregate/value object |

## Worked Example
The chapter builds a help-desk Ticket domain model from these requirements: tickets have priority-based SLAs; escalation cuts the agent's response time by 33%; an escalated ticket unopened within 50% of its time limit auto-reassigns to a new agent; tickets auto-close after 7 days of customer silence; escalated tickets can only be closed by the customer or manager; a closed ticket can be reopened within 7 days.

- `Person`/`Ticket` fields are modeled with value objects (`PersonId`, `Name`, `PhoneNumber`, `EmailAddress`, `Height`, `CountryCode`) instead of primitives, each encapsulating parsing, validation, and derived behavior (e.g., `Color.MixWith`, `Height.ToImperial()`).
- `Ticket` is the aggregate root; `Message` is an entity that exists only inside `Ticket`'s boundary and is mutated only through root commands like `Execute(AddMessage cmd)` or `Execute(AcknowledgeMessage cmd)`.
- The `Ticket` aggregate references `_customer`, `_products`, and `_assignedAgent` only by ID (their data can be eventually consistent), but keeps `_messages` inside its own boundary because the reassignment rule needs strongly consistent read/unread state.
- State changes are exposed as commands (e.g., `Execute(Escalate cmd)`, `Execute(RequestEscalation cmd)`), each validating invariants before mutating and appending a `DomainEvent` (e.g., `TicketEscalated`) to an internal list for later publishing.
- The application/service layer is thin: `Escalate(TicketId id, EscalationReason reason)` loads the aggregate, builds a command, calls `ticket.Execute(cmd)`, saves with optimistic concurrency (a `_version` field checked in the `UPDATE ... WHERE agg_version=@expected_version` SQL), and returns a result — all business logic stays inside `Ticket`.

## Key Takeaways
1. Reach for the Domain Model pattern only for core subdomains with genuinely complex, entangled business rules — not for CRUD-shaped logic (that's Chapter 5's territory).
2. Default to value objects "whenever you can" for anything identified by its values; they eliminate primitive obsession, centralize validation, and are inherently thread-safe because they're immutable.
3. Let an aggregate's public commands be the *only* way to mutate its state — this is what makes the aggregate a true consistency boundary and keeps business logic from leaking into the application layer.
4. Size aggregates by strong-consistency needs, not convenience: keep them as small as possible, and reference everything else by ID.
5. Never span a business transaction across more than one aggregate instance; treat the urge to do so as a signal to redraw the aggregate boundary.
6. Use domain events (past-tense names) as the aggregate's channel to the outside world for anything beyond direct command execution; use domain services strictly for cross-aggregate reads/calculations, never cross-aggregate writes.
7. Judge design complexity by "degrees of freedom" (Goldratt): code that encapsulates invariants and reduces independently-mutable state is less complex, even if it has more lines than a naive property bag.

## Connects To
- **Ch 5**: contrasts directly with Transaction Script and Active Record — the simple-logic patterns this chapter's Domain Model pattern is meant to replace once complexity crosses a threshold.
- **Ch 7**: extends the Domain Model pattern into the Event-Sourced Domain Model, making time (via events) a first-class part of aggregate state.
- **Ch 14**: revisits aggregate boundaries at the microservices level, where aggregate consistency boundaries often align with service boundaries.
- **Ch 9**: covers how domain events published by aggregates are reliably delivered to subscribers (communication patterns).
- **Eric Evans's "Blue Book" (Domain-Driven Design: Tackling Complexity in the Heart of Software)**: source of the tactical patterns (aggregate, value object, repository) that this chapter organizes under Fowler's "domain model" umbrella term.
- **Martin Fowler's Patterns of Enterprise Application Architecture**: origin of the Domain Model, Transaction Script, and Active Record pattern names used throughout Chapters 5-6.
