# Patterns Reference — Learning Domain-Driven Design (Khononov)

## Strategic: Context Mapping Patterns

## Partnership
**When to use**: Two teams with well-established, high-trust communication (often co-located or highly synchronized) need to integrate their bounded contexts.
**How**: Coordinate ad hoc, continuously integrate changes on both sides; no formal contract enforcement beyond mutual trust.
**Trade-offs**: Fast and flexible, but breaks down without frequent synchronization — unsuitable for distributed or poorly aligned teams.

## Shared Kernel
**When to use**: Duplicating a volatile (often core) model across contexts costs more than jointly owning a limited overlapping model; also useful for same-team contexts or temporary legacy modernization.
**How**: Multiple teams share and jointly maintain a minimal slice of model/code; every change triggers integration tests across all consumers.
**Trade-offs**: Keep scope minimal — over-sharing multiplies blast radius; violates single-team ownership, so use only as a deliberate, justified exception.

## Customer-Supplier (Conformist)
**When to use**: Upstream has no motivation to accommodate downstream, and the upstream model is an industry standard or "good enough."
**How**: Downstream simply adopts the upstream's model as-is, no translation layer.
**Trade-offs**: Cheapest option, but if downstream is core or the upstream is unstable/legacy, conforming pollutes downstream's model with foreign concepts.

## Anticorruption Layer (ACL)
**When to use**: Downstream owns a core subdomain, or the upstream model is inefficient/legacy/frequently changing — downstream must not let it leak in.
**How**: Build a downstream-owned translation component (inline proxy, or async message proxy for events) that converts the upstream's model into concepts native to downstream's own language.
**Trade-offs**: Isolates downstream from upstream churn at the cost of extra translation code to build and maintain.

## Open-Host Service (OHS)
**When to use**: A supplier wants to protect all its consumers (not just one) from internal churn, often serving many consumers at once.
**How**: Decouple the internal implementation model from a stable, explicit "published language"; optionally expose multiple versions simultaneously.
**Trade-offs**: Supplier bears the translation cost once, benefiting every consumer — mirror image of ACL (translation moves to the supplier side).

## Separate Ways
**When to use**: Teams are unwilling/unable to collaborate (political/communication barriers), or duplicating an easy generic subdomain is cheaper than integrating.
**How**: Each side implements its own version independently; no integration contract exists.
**Trade-offs**: Never use for core subdomains — duplicating your competitive advantage undermines the whole point of investing in it.

## Context Map
**When to use**: Always — as a living, team-maintained artifact.
**How**: Visualize all bounded contexts and the integration pattern used between each pair; each team updates its own integrations.
**Trade-offs**: A map showing many ACLs pointing at one upstream is itself a diagnostic signal of an organizational problem, not just a technical one.

---

## Tactical: Business Logic Patterns

## Transaction Script
**When to use**: Supporting/generic subdomains with simple, procedural logic (ETL-style); also as ACL/adapter glue.
**How**: One procedure per public operation; the only hard requirement is atomicity (fully succeed or fully fail), typically via a wrapping DB transaction.
**Trade-offs**: Logic duplicates across scripts as complexity grows; never use for core subdomains.

## Active Record
**When to use**: Same complexity ceiling as Transaction Script, but data is structured as complex object trees (one-to-many, many-to-many).
**How**: Wrap each data structure in an object bundling CRUD methods with the data, typically via an ORM; business logic (a transaction script) manipulates these objects inside a transaction.
**Trade-offs**: Separates data from behavior ("anemic" critique); tolerates only CRUD plus basic validation.

## Domain Model
**When to use**: Core subdomains with entangled state transitions, business rules, and invariants that must always hold.
**How**: Build from DDD building blocks — value objects (immutable, identified by value), entities (identity, mutable only via their aggregate), aggregates (transactional consistency boundary, mutated only through the aggregate root's public commands), domain services (stateless, cross-aggregate reads only).
**Trade-offs**: More code/ceremony than Active Record, but reduces "degrees of freedom" (Goldratt) by encapsulating invariants instead of exposing raw mutable state.

## Event-Sourced Domain Model
**When to use**: Core subdomains needing audit trails, retroactive analysis, or deep behavioral insight into *how* state changed, not just current values.
**How**: Persist the sequence of domain events (not current state) to an append-only event store; reconstitute state by replaying events via `Apply` methods; commands operate on the replayed state and append new events with optimistic concurrency.
**Trade-offs**: Enables time-travel and unlimited future projections; steep learning curve, requires CQRS to query effectively, and schema evolution of events is harder than an `ALTER TABLE`.

## Aggregate
**When to use**: A business invariant spans multiple objects that must update together, atomically, in one transaction.
**How**: Designate one entity as the aggregate root — the sole entry point exposing public "commands"; keep the aggregate as small as possible, referencing other aggregates only by ID; commit one aggregate instance per transaction.
**Trade-offs**: The urge to modify two aggregates in one transaction is a signal the boundary is drawn wrong, not a case for a bigger aggregate — use a saga/process manager instead.

## Value Object
**When to use**: Default choice for anything identified purely by its values (money, phone numbers, addresses, statuses).
**How**: Make it immutable, override equality to compare by value, centralize validation and behavior that returns new instances.
**Trade-offs**: Eliminates primitive obsession and scattered validation; adding an explicit ID to something that should be a value object breaks the "same value = same instance" guarantee.

---

## Architectural Patterns

## Layered Architecture
**When to use**: Business logic implemented as Transaction Script or Active Record, which legitimately depends on the data access layer.
**How**: Presentation → Business Logic → Data Access, each layer depending only on the one beneath; optionally insert a service layer as a façade/orchestrator.
**Trade-offs**: Simple and familiar; fights the Domain Model pattern's need for zero infrastructure dependency, so don't force a domain model into it.

## Ports & Adapters (Hexagonal)
**When to use**: Business logic implemented via Domain Model or Event-Sourced Domain Model, which must stay free of infrastructure dependencies.
**How**: Business logic defines "ports" (interfaces); infrastructure implements them as "adapters," inverting the dependency (Dependency Inversion Principle); add an application layer as the public-interface façade.
**Trade-offs**: Same underlying structure as onion/clean architecture, different vocabulary; more setup than layered architecture but keeps the domain persistence-ignorant.

## CQRS
**When to use**: Multiple persistent representations of the same data are needed (polyglot persistence, OLTP/OLAP split); mandatory with event-sourced domain models since raw event streams can't be queried across aggregates.
**How**: A single strongly-consistent command execution model handles writes and invariants; any number of disposable, regenerable read models are built by a projection engine — prefer synchronous checkpoint-based projection over async message-bus projection by default.
**Trade-offs**: Commands may return data, but only from the command model, never a projection; async projection is more fragile under out-of-order/duplicate delivery.

---

## Communication Patterns

## Outbox Pattern
**When to use**: Any time an aggregate's state change must reliably trigger a published domain event.
**How**: Commit updated state and new events atomically in one transaction (dedicated outbox table or embedded array); a separate message relay (poll or transaction-log tailing) publishes and marks events sent, guaranteeing at-least-once delivery.
**Trade-offs**: Replaces both "publish from inside the aggregate" (may fire before commit) and "publish after commit" (can silently lose events on crash); duplicate delivery is possible, so consumers must be idempotent.

## Saga
**When to use**: A simple, implicitly-triggered event-to-command matching flow spanning multiple aggregates/contexts, with no branching logic.
**How**: Subscribe to a domain event, issue the corresponding command (with a compensating command on failure); route command execution through an outbox-style async relay so a mid-process crash never loses a command.
**Trade-offs**: If the flow needs if/else branching, it's actually a Process Manager, not a saga.

## Process Manager
**When to use**: A genuinely stateful, multi-step business process with conditional branching (e.g., booking with approval/rerouting).
**How**: Persist explicit process state (as a state-based or event-sourced aggregate); decide the next command based on that state and business logic; requires explicit instantiation since no single triggering event exists.
**Trade-offs**: More machinery than a saga; only use when branching logic genuinely requires it.

## Model Translation (Stateless / Stateful)
**When to use**: Whenever an ACL or OHS must convert between a source and target model across a customer-supplier relationship.
**How**: Stateless — an inline proxy or API gateway translates on the fly (works for both sync calls and, via a message proxy, async events). Stateful — needed when the translation must aggregate multiple requests or unify multiple sources; requires its own persistent storage.
**Trade-offs**: Stateless is simpler and preferred by default; reach for stateful translation only when aggregation/unification genuinely demands it.

## Event Types (Notification, ECST, Domain Event)
**When to use**: Choose per integration based on how much data the consumer needs and what consistency guarantee is required.
**How**: Event Notification = minimal payload + reference, forces a follow-up query. Event-Carried State Transfer (ECST) = full/partial state snapshot for local caching. Domain Event = rich description of one business happening, modeled for the domain, published only as a curated subset (never expose raw internal/event-sourced streams).
**Trade-offs**: Exposing raw internal domain events to multiple subscribers recreates monolithic coupling across service boundaries (temporal, functional, and implementation coupling) — a "distributed big ball of mud."

---

## Process / Technique Patterns

## EventStorming
**When to use**: Building a ubiquitous language, modeling a business process, recovering lost domain knowledge in legacy systems, or onboarding.
**How**: 10-step collaborative workshop with colored sticky notes on a wall — Unstructured Exploration, Timelines, Pain Points, Pivotal Events, Commands, Policies, Read Models, External Systems, Aggregates, Bounded Contexts.
**Trade-offs**: The workshop's knowledge-sharing is the real value, not the diagram; ineffective for trivial sequential processes; remote sessions lose collaborative effectiveness.

## Undercover DDD
**When to use**: Management or the team isn't bought into DDD as a named methodology, but its practices would still add value.
**How**: Cultivate the ubiquitous language through ordinary conversation; justify bounded contexts and tactical patterns by engineering logic and business risk rather than citing DDD literature; demonstrate event sourcing's value directly instead of prescribing it.
**Trade-offs**: Slower to build organizational momentum, but avoids the friction of "selling" a formal methodology to a skeptical org.

## Data Mesh (4 Principles)
**When to use**: A single enterprise-wide analytical model (data warehouse/lake) has become impractical to design and maintain.
**How**: (1) Decompose Data Around Domains — each bounded context owns its own OLAP model, not just its OLTP model. (2) Data as a Product — expose analytical data via discoverable, versioned, SLA-backed output ports. (3) Enable Autonomy — a shared platform team provides blueprints/tooling so domain teams self-serve. (4) Build an Ecosystem — federated governance keeps distributed data products interoperable.
**Trade-offs**: Avoids the DWH/lake failure mode of ETL scripts coupling directly to internal operational schemas; requires real investment in a platform team and governance body to work.

## Strangler Pattern (Modernization)
**When to use**: Migrating functionality out of a legacy bounded context without a big-bang rewrite.
**How**: Build a new bounded context, freeze the legacy one except hotfixes, route requests through a façade to old or new code during migration, optionally share one database temporarily until legacy is retired.
**Trade-offs**: Slower than a rewrite but far lower risk; pair with logical-boundary refactoring (namespaces/modules) as the safe first step before physical separation.
