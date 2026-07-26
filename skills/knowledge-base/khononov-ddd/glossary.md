# Khononov DDD Glossary

**Active Record** — object wrapping a DB row/table, bundling CRUD data access with simple domain logic; for supporting/generic subdomains with complex data structures but simple logic (Ch 5, Ch 8, Ch 10, Ch 11, Ch 17)

**Aggregate** — hierarchy of entities/value objects sharing one transactional consistency boundary, mutable only via its root's public commands; narrowest valid microservice boundary (Ch 6, Ch 8, Ch 14, Ch 17)

**Aggregate Root** — the single entity in an aggregate exposing its public interface; sole entry point for mutation (Ch 6)

**Anticorruption Layer (ACL)** — downstream-owned translation layer isolating a bounded context's model from an upstream's model (Ch 4, Ch 9, Ch 14)

**Bounded Context** — explicit boundary within which one model and ubiquitous language stay consistent; widest valid microservice boundary (Ch 3, Ch 14)

**Business Domain** — a company's main area of activity; decomposes into subdomains (Ch 1)

**CQRS (Command-Query Responsibility Segregation)** — segregates a strongly-consistent command execution model from disposable, regenerable read-model projections; mandatory with event-sourced domain models (Ch 8, Ch 10, Ch 16)

**Conformist** — downstream accepts an upstream's model as-is with no translation, used when the upstream is a de facto standard (Ch 4)

**Context Map** — diagram plotting bounded contexts and the integration pattern used between each pair (Ch 4)

**Core Subdomain** — a company's source of competitive advantage; complex, in-house, constantly evolving (Ch 1, Ch 11)

**Customer-Supplier** — upstream/downstream relationship with a power imbalance; umbrella for Conformist, ACL, Open-Host Service (Ch 4)

**Data Mesh** — decomposes analytical (OLAP) models along bounded-context boundaries; four principles: decompose around domains, data as a product, enable autonomy, build an ecosystem (Ch 16)

**Deep Module (Microservices as Deep Modules)** — a good microservice has a narrow public interface hiding a large, complex implementation (Ousterhout); the evaluation lens for service boundaries (Ch 14)

**Domain Event** — immutable, past-tense message announcing a significant business occurrence, published by an aggregate; also an event type modeled for the domain rather than integration convenience (Ch 6, Ch 15, Ch 17)

**Domain Expert** — subject-matter authority and source (not transcriber) of business knowledge (Ch 1, Ch 2)

**Domain Model** — object model incorporating both behavior and data, built from DDD's tactical building blocks; for core subdomains with complex logic (Ch 6, Ch 8, Ch 10, Ch 11)

**Domain Service** — stateless object hosting logic that doesn't belong to any single aggregate, orchestrating reads across multiple aggregates (Ch 6)

**Entity** — object requiring an explicit identity field because attributes alone can't guarantee uniqueness; mutable, exists only inside an aggregate (Ch 6)

**Event-Carried State Transfer (ECST)** — event carrying a full/partial snapshot of producer state for consumer-side caching/replication (Ch 15)

**Event Notification** — terse event signaling something happened without enough data to act on; forces a follow-up query (Ch 15)

**Event Sourcing** — persists the sequence of domain events (not current state) as the source of truth; state is derived by replaying events (Ch 7)

**Event-Sourced Domain Model** — the domain model pattern combined with event sourcing as its persistence mechanism; requires CQRS (Ch 7, Ch 8, Ch 10)

**EventStorming** — collaborative workshop technique modeling a business process via sticky notes on a timeline; 10 steps: Unstructured Exploration, Timelines, Pain Points, Pivotal Events, Commands, Policies, Read Models, External Systems, Aggregates, Bounded Contexts (Ch 12)

**Event Store** — append-only database storing domain events, supporting Fetch/Append with optimistic concurrency (Ch 7)

**Generic Subdomain** — a business activity done the same way everywhere, using widely available solutions; complex but non-differentiating (Ch 1, Ch 11)

**Layered Architecture** — presentation, business logic, and data access layers, each depending only on the layer beneath; pairs with transaction script/active record (Ch 8, Ch 10)

**Microservice** — a service with a micro (small) public interface, judged by the deep-module heuristic, not size (Ch 14)

**Open-Host Service (OHS)** — upstream-owned service exposing a stable published language decoupled from its internal model, to protect all consumers (Ch 4, Ch 9, Ch 14)

**Outbox Pattern** — atomically commits aggregate state and its domain events in one transaction, then relays them for reliable at-least-once publishing (Ch 9)

**Partnership** — cooperative integration pattern between teams with high-trust, frequent two-way coordination (Ch 4)

**Ports & Adapters (Hexagonal Architecture)** — business logic defines ports (interfaces) that infrastructure implements as adapters, inverting dependency via DIP; required for the domain model pattern (Ch 8, Ch 10)

**Process Manager** — central component holding explicit state for a multi-step business process with conditional branching logic, explicitly instantiated (Ch 9)

**Published Language** — the integration-oriented protocol a supplier (Open-Host Service) exposes, decoupled from its internal implementation model (Ch 4, Ch 9, Ch 15)

**Saga** — long-running process reacting to domain events by issuing commands to other aggregates/contexts, including compensating actions; implicitly triggered, no branching (Ch 9, Ch 15)

**Separate Ways** — teams choose not to integrate at all and duplicate functionality instead; never for core subdomains (Ch 4)

**Shared Kernel** — multiple teams jointly own and share a limited overlapping model, kept intentionally narrow (Ch 4)

**Subdomain** — fine-grained area of business activity; one of three types: Core, Generic, Supporting (Ch 1)

**Supporting Subdomain** — necessary but non-differentiating activity with simple, CRUD-like logic and low entry barriers (Ch 1, Ch 11)

**Tactical Design Decision Tree** — decision chain: business logic pattern → architectural pattern → testing strategy, driven by subdomain complexity (money/audit/analytics → event-sourced domain model; complex logic → domain model; complex data → active record; else → transaction script) (Ch 10)

**Transaction Script** — organizes business logic as one procedure per public operation/request; for simple, procedural logic (Ch 5, Ch 8, Ch 10, Ch 11)

**Ubiquitous Language** — single, precise, shared vocabulary of business terms used by all stakeholders, consistent only within a bounded context (Ch 2, Ch 3)

**Undercover DDD** — applying DDD's practices without naming the methodology, to sidestep organizational resistance (Ch 13)

**Value Object** — immutable object identified solely by its values, with no explicit ID, centralizing validation and behavior (Ch 6)
