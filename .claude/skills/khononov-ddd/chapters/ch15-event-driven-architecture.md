# Chapter 15: Event-Driven Architecture

## Core Idea
Events are not a "secret sauce" that automatically decouples a system — careless event-driven integration can turn a modular monolith into a distributed big ball of mud. Choosing the correct type of event (notification, ECST, or domain event) for each integration is what actually decouples or couples a distributed system.

## Frameworks Introduced
- **Types of Events** (Event Notification, Event-Carried State Transfer, Domain Event): a message is an event ("something that has already happened," named in past tense, cannot be rejected) or a command ("an operation that has to be carried out," which can be rejected). Within events, three distinct types serve different integration purposes.
  - When to use: choose the type based on how much data the consumer needs and what consistency guarantee is required — don't default to exposing everything.
  - How: event notification = minimal payload + reference link, forcing a follow-up query; ECST = full or partial snapshot of changed state for local caching; domain event = rich description of a business happening, modeled for the domain, not for integration convenience.
- **Distributed Big Ball of Mud avoidance**: uncontrolled exposure of an event-sourced aggregate's internal domain events to multiple external subscribers recreates monolithic coupling across service boundaries.
  - When to use: whenever a producer is event-sourced and considering letting consumers subscribe directly to its internal domain events.
  - How: encapsulate projection logic in the producer via a consumer-driven, published-language model (open-host service); use event notifications to resolve temporal coupling instead of artificial processing delays; keep domain events private/internal by default, publish only a deliberately designed public set.

## Key Concepts
- **Event**: a message describing a change that has already happened; cannot be rejected, only compensated via a follow-up command.
- **Command**: a message describing an operation that must be carried out; can be rejected by its recipient.
- **Event Notification**: a terse event that signals something happened without carrying enough data to act on it — consumer must query back for details.
- **Event-Carried State Transfer (ECST)**: an event carrying a full or partial snapshot of the producer's changed state, used as an asynchronous data-replication/local-cache mechanism.
- **Domain Event**: an event modeled to describe a significant business occurrence, containing all data about that occurrence but not intended as a state-caching mechanism.
- **Temporal Coupling**: two components depend on a strict order of execution; artificial delays are a fragile workaround, not a fix.
- **Functional Coupling**: multiple components independently implement the same business logic (e.g., the same projection), so a change in one requires a synchronized change in the other.
- **Implementation Coupling**: consumers subscribed to a producer's full internal event stream break whenever the producer's internal schema or event set changes.
- **Published Language / Public Events**: a deliberately designed, decoupled event model exposed at the bounded context boundary, distinct from the internal (private) implementation events.
- **Saga Pattern**: an event-driven execution flow used to orchestrate cross-context processes and issue compensating actions when an event's effect must be undone.

## Mental Models
- Event notification is like an emergency alert broadcast (WEA/EU-Alert): short, just enough to prompt you to seek details elsewhere — useful for security (no sensitive data on the wire) and concurrency (forces a fresh query instead of trusting stale data).
- "Assume the worst" (Andrew Grove's paranoia principle): networks are slow, servers fail, events arrive out of order or duplicated — event-driven systems must be built assuming failure, not hoping for reliability.
- Domain events sit conceptually between event notification and ECST: like ECST they carry full detail about themselves, but like notifications they're not meant to reconstruct full aggregate state — each domain event only covers one slice of the aggregate's lifecycle.
- Treat a bounded context's events as part of its public interface, symmetric with the open-host service concept from Chapter 9 — public events belong in the published language, not a leak of internal implementation.

## Anti-patterns
- **Distributed Big Ball of Mud**: letting every downstream consumer subscribe directly to a producer's full internal (often event-sourced) domain event stream. This produces simultaneous temporal, functional, and implementation coupling — consumers duplicate projection logic, break on internal schema changes, and require fragile ordering hacks (e.g., artificial processing delays) to stay consistent, exactly reproducing monolithic entanglement across service boundaries.

## Code Examples
```json
{
  "type": "delivery-confirmed",
  "event-id": "14101928-4d79-4da6-9486-dbc4837bc612",
  "correlation-id": "08011958-6066-4815-8dbe-dee6d9e5ebac",
  "delivery-id": "05011927-a328-4860-a106-737b2929db4e",
  "timestamp": 1615718833,
  "payload": {
    "confirmed-by": "17bc9223-bdd6-4382-954d-f1410fd286bd",
    "delivery-time": 1615701406
  }
}
```
- **What it demonstrates**: baseline event schema — metadata (type, event-id, correlation-id, timestamp) separated from payload; the payload's shape is what determines whether the event is a notification, ECST, or domain event.

## Reference Tables
| Event Type | Purpose | Coupling Risk |
|---|---|---|
| Event Notification | Signal that something happened; minimal payload plus a reference for consumers to query further detail | Low implementation coupling; adds a synchronous follow-up query and requires consumer authorization to fetch details |
| Event-Carried State Transfer | Asynchronous data replication — lets consumers hold a local cache of producer state (full or partial snapshot) | Risk of functional coupling if consumers reimplement producer-side projection logic; eventual consistency only |
| Domain Event | Describes a significant business occurrence, modeled for the domain's own sake (not integration) | High implementation coupling if internal/event-sourced domain events are exposed wholesale; should be curated into a public subset |

## Worked Example
A CRM bounded context (event-sourced) exposed its full internal domain event stream. Marketing subscribed to project a flattened customer snapshot; when AdsOptimization was added, it independently subscribed to the same events and built the *same* projection — functional coupling (duplicated logic, must change in lockstep) plus implementation coupling (any CRM schema/event change breaks both subscribers). Reporting subscribed only to a subset of CRM events as notifications to trigger fetching AdsOptimization's calculated results, but since AdsOptimization consumed the same underlying events, Reporting needed to run *after* AdsOptimization finished — so engineers bolted on an artificial 5-minute processing delay, which is temporal coupling disguised as a fix (breaks under load, network delay, or AdsOptimization outage).

Refactor: CRM stops exposing raw internal domain events. It encapsulates its projection logic and publishes a purpose-built, consumer-driven published-language model (open-host service) that both Marketing and AdsOptimization consume directly — eliminating duplicated projection logic and implementation leakage. To fix the Reporting/AdsOptimization ordering problem, AdsOptimization publishes an event notification when its calculation completes, and Reporting reacts by querying for the up-to-date result — replacing the fragile timing delay with an explicit signal.

## Key Takeaways
1. An event is something that already happened (past tense, cannot be rejected); a command is an instruction that can be rejected — don't conflate the two message types.
2. Match event type to need: use event notification when consumers need only a trigger plus security/concurrency-safe follow-up query; use ECST when consumers need a local cache and can tolerate eventual consistency; use domain events sparingly for cross-context communication, as a curated public subset.
3. Assume the worst: design for slow networks, out-of-order and duplicated delivery, and server failure — use the outbox pattern for reliable publishing, support consumer-side deduplication/reordering, and use sagas/process managers for cross-context compensation.
4. Maintain public vs. private events explicitly — never expose an event-sourced aggregate's full internal event stream as the integration contract; publish a deliberately designed set as part of the bounded context's published language.
5. Evaluate consistency requirements per integration: eventually-consistent needs favor ECST; read-your-last-write needs favor event notification plus synchronous query-back.
6. Encapsulating projection logic in the producer (rather than letting every consumer reimplement it) eliminates both functional and implementation coupling simultaneously.
7. Temporal coupling should be resolved with explicit triggering events (notifications), never with artificial delays that merely hide — not remove — the ordering dependency.

## Connects To
- **Ch 7 (Modeling the Dimension of Time / Event Sourcing)**: event sourcing captures state transitions *inside* a bounded context; EDA is about communication *between* components — conflating the two produces the distributed-big-ball-of-mud failure mode in this chapter.
- **Ch 9 (Communication Patterns)**: open-host service and published language are the mechanisms used to expose curated public events instead of leaking implementation events; sagas were introduced there as an event-driven execution flow.
- **Ch 14 (Microservices)**: microservice systems are the primary setting where EDA is applied and where uncontrolled event coupling most severely undermines the intended service independence.
- **Distributed Big Ball of Mud, temporal/functional/implementation coupling**: the chapter's central cautionary framework for diagnosing why an event-driven system has failed to decouple.
