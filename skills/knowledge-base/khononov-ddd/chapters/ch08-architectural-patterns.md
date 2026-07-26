# Chapter 8: Architectural Patterns

## Core Idea
Architectural patterns organize how a codebase's technical concerns (input/output, business logic, persistence) are wired together and bounded from each other; choosing the right one — layered architecture, ports & adapters, or CQRS — determines how well the system can support its business logic pattern in the short term and stay maintainable in the long term.

## Frameworks Introduced
- **Layered Architecture**: organizes the codebase into horizontal layers — presentation layer (PL), business logic layer (BLL), and data access layer (DAL) — where each layer can depend only on the layer directly beneath it.
  - When to use: business logic implemented as transaction script or active record, where the business logic legitimately depends on the data access layer.
  - How: presentation layer handles all means of triggering behavior (GUI, CLI, API, event subscriptions, outgoing message topics); business logic layer implements the patterns from Chapters 5-7; data access layer wraps databases, object storage, message buses used internally, and external service integrations. Optionally insert a service layer between PL and BLL as a façade that exposes the system's public operations and orchestrates the underlying layers (e.g., wrapping a transaction in a controller action into a reusable `UserService.Create`).
- **Ports & Adapters (Hexagonal)**: applies the Dependency Inversion Principle to layered architecture — the business logic layer defines "ports" (interfaces) that the infrastructure layer must implement as "adapters," so business logic depends on nothing and infrastructure depends on business logic's abstractions.
  - When to use: business logic implemented with the domain model (or event-sourced domain model) pattern, which requires the business entities to have zero dependency on infrastructure.
  - How: merge presentation and data access layers conceptually into a single infrastructure layer; reverse the dependency so business logic is central and depends on no layer; add an application layer (equivalent to the service layer) as the public-interface façade; infrastructure implements concrete adapters for each port interface, wired via dependency injection or bootstrapping. Also known as hexagonal architecture, onion architecture, or clean architecture — same principles, different terminology (application layer = service layer = use case layer; business logic layer = domain layer = core layer).
- **CQRS (Command-Query Responsibility Segregation)**: shares ports & adapters' organizational principles but additionally segregates the system's data into a single strongly-consistent command execution model and any number of read-only projected models.
  - When to use: applications needing the same data represented in multiple models/databases (polyglot persistence), systems built on event-sourced domain models (mandatory, since events can't be queried across aggregates), or OLTP/OLAP needs requiring different data shapes.
  - How: the command execution model implements business logic, validates invariants, and is the sole source of truth with optimistic concurrency; read models are precached, disposable, regenerable projections built by a projection engine, updated either synchronously (catch-up subscription polling the OLTP store by checkpoint) or asynchronously (subscribing to committed-change messages on a bus). Commands may return data, but only data sourced from the strongly consistent command execution model — never from projections.

## Key Concepts
- **Presentation Layer**: the layer implementing all means for the system to receive requests and communicate output — GUI, CLI, API, event subscriptions, outgoing message topics.
- **Business Logic Layer**: the layer that implements and encapsulates business decisions, described by Evans as "the heart of software."
- **Data Access Layer**: the layer providing access to persistence mechanisms and external information providers, broader in modern systems than just "the database."
- **Dependency Inversion Principle (DIP)**: high-level modules (business logic) should not depend on low-level modules (infrastructure); both should depend on abstractions.
- **Polyglot Modeling / Persistence**: using multiple models and multiple databases, each suited to a different requirement, rather than forcing one "perfect" model or database to serve all needs.
- **Projecting Read Models**: the process of propagating changes from the command execution model into precached read models, analogous to refreshing a materialized view.
- **Model Segregation**: commands may only operate on the command execution model; queries may never mutate any persisted state, read model or command model.
- **Layers vs. Tiers**: a layer is a logical boundary sharing one deployment lifecycle; a tier is an independently deployable physical service — the two are often confused but are conceptually distinct.
- **Architectural Slices**: vertical partitioning of a bounded context by subdomain, layered on top of horizontal architectural patterns, so different subdomains within one context can use different architectures.

## Mental Models
- Architecture is about wiring, not about business rules: it governs what components know about each other and who depends on whom, while Chapters 5-7's patterns govern how the business logic itself is modeled.
- "Refactor" layered architecture into ports & adapters by mentally merging PL+DAL into "infrastructure," then flipping the dependency arrow via DIP — the two patterns are structurally close cousins, not opposites.
- Architectural patterns are scoped to a module/subdomain, not the whole bounded context or system — a single context spanning several subdomains can and often should mix patterns.
- A command execution model is a source of truth; read models are disposable caches that can always be wiped and rebuilt from the source of truth — never treat a projection as authoritative.

## Anti-patterns
- **Forcing a domain model into layered architecture**: the top-down dependency (BLL depends on DAL) fights the domain model's requirement that aggregates and value objects have zero infrastructure knowledge — technically possible but requires unnecessary hoop-jumping; use ports & adapters instead.
- **Believing commands must return nothing**: treating CQRS as "commands only ever return void, all reads must go through a read model" is a common misconception that produces accidental complexity and a bad user experience — the source text explicitly calls this "wrong."
- **Confusing layers with tiers**: treating a logical horizontal layer as if it were an independently deployable physical service (or vice versa) leads to wrong assumptions about lifecycle and deployment coupling.
- **Enforcing one contextwide architecture across mixed subdomains**: applying a single architectural pattern uniformly across core, supporting, and generic subdomains in one bounded context inadvertently introduces accidental complexity — different subdomain types call for different patterns.
- **Relying solely on asynchronous projections**: async projection is more exposed to distributed-computing failure modes (out-of-order or duplicate message processing corrupts read models) and makes adding/regenerating projections harder; the chapter advises always implementing synchronous projection first, with async as an optional addition on top.

## Code Examples
```csharp
namespace App.BusinessLogicLayer {
    public interface IMessaging {
        void Publish(Message payload);
        void Subscribe(Message type, Action callback);
    }
}

namespace App.Infrastructure.Adapters {
    public class SQSBus : IMessaging { ... }
}
```
- **What it demonstrates**: the port/adapter split at the heart of Ports & Adapters — the business logic layer owns the `IMessaging` interface (the port); infrastructure provides `SQSBus`, a concrete technology-specific adapter, so business logic never references SQS directly.

## Reference Tables
| Pattern | Business Logic Isolation | When to Use |
|---|---|---|
| Layered Architecture | Business logic layer depends directly on data access layer (top-down) | Business logic implemented as transaction script or active record |
| Ports & Adapters | Business logic depends on nothing; infrastructure implements ports defined by business logic (DIP applied) | Business logic implemented as a domain model or event-sourced domain model |
| CQRS | Same isolation as ports & adapters, plus command/read-model segregation of data | Multiple persistent models needed (polyglot persistence, OLTP/OLAP split); mandatory with event-sourced domain models |

## Worked Example
A `UserController.Create` action in the presentation layer originally opens a database transaction, constructs and saves a `User` active record, commits or rolls back, and returns a result — mixing orchestration with presentation. Extracting that orchestration into a `UserService.Create` (service layer) leaves the controller as a thin adapter that just forwards `contactDetails` to the service and returns its `OperationResult`. This service layer can be reused across multiple presentation surfaces (GUI and API) without duplicating orchestration, improves testability, and further decouples presentation from business logic — though it is optional and redundant when business logic is already a transaction script (which is itself effectively a service layer).

For CQRS, the worked scenario is a synchronous projection: the projection engine queries the OLTP command execution model for records changed after the last processed checkpoint (e.g., SQL Server's `rowversion` column), uses them to rebuild affected read models, then stores the new checkpoint for the next run. Resetting the checkpoint to 0 regenerates a read model from scratch — the mechanism that makes adding new projections after the fact safe and reliable, versus the harder-to-replay asynchronous message-bus alternative.

## Key Takeaways
1. Pick the architecture to match the business logic pattern already chosen: transaction script/active record pairs naturally with layered architecture; domain model requires ports & adapters' dependency inversion.
2. CQRS is not exclusive to event sourcing — any system needing multiple persistent representations of its data benefits from command/read-model segregation, but event-sourced domain models require it.
3. Prefer synchronous (checkpoint-based catch-up) projections over asynchronous ones by default; add async projection only as a supplement, because it is more fragile under out-of-order/duplicate delivery.
4. Commands are allowed — and often should — return data, as long as that data comes from the strongly consistent command execution model, not from a projection.
5. Architectural patterns apply per subdomain/module, not uniformly across a whole bounded context; mixing patterns within one context via vertical "architectural slices" is expected, not a smell.
6. Distinguish layers (logical, single deployment lifecycle) from tiers (physical, independently deployable) — conflating them leads to wrong assumptions about coupling and deployment.
7. A service/application layer is optional: skip it when the business logic pattern already exposes the needed public operations (transaction script); add it when orchestration needs to be extracted and reused (active record, domain model).

## Connects To
- **Ch 6**: Ports & Adapters is the architecture that makes the domain model pattern's zero-infrastructure-dependency requirement practical to implement.
- **Ch 7**: CQRS's relationship to event sourcing — projections solve the limited querying of an event-sourced model discussed there.
- **Ch 9**: Communication Patterns — the next chapter shifts from internal component organization to reliable interaction between components.
- **Ch 10**: Design Heuristics — revisits how different subdomain types (core/supporting/generic) call for different architectural and business-logic pattern choices.
- **Ch 11**: Evolving Design Decisions — the logical vertical boundaries (architectural slices) introduced here can later be refactored into physical bounded-context boundaries.
- **Hexagonal Architecture (Alistair Cockburn)**: the original name for ports & adapters; also known as onion architecture and clean architecture — same structure, different vocabulary.
