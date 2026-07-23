---
name: khononov-ddd
description: "Knowledge base from \"Learning Domain-Driven Design\" by Vlad Khononov. Use when applying DDD strategic/tactical patterns, analyzing business domains and subdomains, designing bounded contexts, choosing business-logic or architectural patterns, running EventStorming, or referencing specific chapters/concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Learning Domain-Driven Design
**Author**: Vlad Khononov | **Pages**: ~342 | **Chapters**: 17 (16 + Appendix A case study) | **Generated**: 2026-07-24

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `bounded contexts`, `event sourcing`, `microservices`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch04` or `ch10`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**Subdomain classification (ch01, ch11)** — Every business domain decomposes into subdomains, each one **core** (competitive advantage, complex, build in-house with best engineers, never buy/outsource), **generic** (solved industry-wide the same way — auth, encryption; buy/adopt, never build), or **supporting** (necessary, simple/CRUD, no edge; build cheaply). Test: "Would someone pay for just this piece?" → core. "Cheaper to buy than build?" → generic. Distill past department boundaries to *coherent use cases* — a "generic" department often hides a core algorithm. Types drift over time (Core↔Generic↔Supporting) as competitive dynamics change — re-derive strategy when a competitor commoditizes your edge, an off-the-shelf tool becomes inadequate, or a "simple" piece starts driving profit.

**Ubiquitous Language (ch02)** — A single shared vocabulary of business terms used by domain experts, engineers, and product across conversation, docs, tests, and code. Talk to domain experts directly, never through translators. Eliminate synonyms and ambiguous terms so each term has exactly one meaning; let it evolve.

**Bounded Context (ch03)** — Because a single ubiquitous language can't stay consistent org-wide (different departments hold genuinely conflicting models of the same term), split the language into multiple smaller ones, each valid only inside its bounded context. Subdomains are *discovered*; bounded contexts are *designed*. Start wide around immature/core subdomains, narrow only as knowledge stabilizes.

**Context Mapping — 7 patterns (ch04)**, grouped by team relationship:
1. **Partnership** — high-trust, tightly synced teams, continuous mutual integration.
2. **Shared Kernel** — joint ownership of a narrow shared model; duplicating it costs more than coordinating it.
3. **Customer-Supplier** (umbrella, upstream/downstream power imbalance) containing:
   4. **Conformist** — downstream just adopts upstream's model (upstream unmotivated/standard, ACL not worth it).
   5. **Anticorruption Layer (ACL)** — downstream protects its own model (downstream is core, or upstream is legacy/unstable).
   6. **Open-Host Service (OHS)** — upstream exposes a stable published language to protect many consumers while evolving freely.
7. **Separate Ways** — no integration at all; only for cheap-to-duplicate generic subdomains, never core.
Decay path: Partnership → Customer-Supplier → Separate Ways. Maintain a living Context Map.

**Tactical pattern spectrum (ch05-07, ch10, ch11)** — walk forward one step at a time as complexity grows, don't over-engineer upfront:
- **Transaction Script** — one procedure per operation; supporting/simple logic; only hard requirement is atomicity.
- **Active Record** — wraps a DB row/tree, bundles CRUD with light domain logic; use when data is structured (hierarchies) but logic stays simple.
- **Domain Model** — POCOs expressing the ubiquitous language, built from DDD Building Blocks; for core subdomains with entangled state/rules/invariants.
- **Event-Sourced Domain Model** — persist the sequence of domain events (not current state) as source of truth; state is always derived by replay. Use when *why/how* state changed matters (audit, analytics, compliance).

**DDD Building Blocks (ch06)**:
- **Value Object** — identified purely by its values; immutable, compared by value, centralizes validation.
- **Entity** — has identity; lives only inside an Aggregate, never standalone.
- **Aggregate** — a transactional consistency boundary spanning multiple objects; single aggregate root as entry point; exposes commands as the only mutation path; references other aggregates only by ID; commits atomically with optimistic concurrency (version field).
- **Domain Event** — broadcasts something that already happened, for other aggregates/systems to react to.
- **Domain Service** — stateless orchestration of logic/reads across multiple aggregates that doesn't belong to any single one.

**Architectural patterns — 3 (ch08)**:
- **Layered Architecture** (Presentation → Business Logic → Data Access, each depends only on the layer below) — fits Transaction Script / Active Record.
- **Ports & Adapters (Hexagonal/Onion/Clean)** — business logic defines ports; infrastructure implements adapters; business logic depends on nothing — fits Domain Model.
- **CQRS** — segregates a single strongly-consistent command model from any number of disposable, regenerable read projections — fits Event-Sourced Domain Model (mandatory there) or polyglot-persistence needs.

**Tactical Design Decision Tree (ch10)** — chain: monetary/audit/deep-analytics need? → Event-Sourced Domain Model. Else complex business logic? → Domain Model. Else complex data structures? → Active Record. Else → Transaction Script. Each pattern implies a testing shape: Domain Model family → Testing Pyramid (mostly unit); Active Record → Testing Diamond (mostly integration); Transaction Script → Reversed Pyramid (mostly end-to-end).

**EventStorming (ch12)** — Alberto Brandolini's collaborative sticky-note workshop; models a business process as a timeline of domain events, then progressively enriches with commands, policies, read models, external systems, aggregates, bounded contexts. Its real value is knowledge-sharing/language alignment among participants, not the artifact.

**Microservices as Deep Modules (ch14)** — Judge a microservice by Ousterhout's deep-module heuristic: narrow public interface hiding large, complex implementation = deep (good); interface complexity approaching implementation complexity = shallow (bad). DDD gives three candidate boundaries: **Bounded Context** = widest safe boundary; **Aggregate** = narrowest safe boundary; **Subdomain** = safest default (naturally deep, "what not how").

**Communication patterns (ch09)**: Model Translation (stateless via proxy/API gateway, or stateful with own storage) for ACL/OHS; **Saga** (simple event→command matching, no branching) vs **Process Manager** (stateful, branching multi-step workflow); **Outbox pattern** (atomically commit state + events, relay separately) for reliable at-least-once event publishing.

**Event types (ch15)**: Event Notification (minimal payload + reference, forces follow-up query), Event-Carried State Transfer (full/partial state snapshot for local caching), Domain Event (rich, modeled for the domain not integration convenience) — picking the wrong type recreates a distributed big ball of mud.

**Data Mesh (ch16)**: 4 principles — Decompose Data Around Domains (align analytical models with bounded contexts), Data as a Product (discoverable, versioned, SLA'd output ports), Enable Autonomy (shared platform, not bespoke tooling per team), Build an Ecosystem (federated governance).

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-analyzing-business-domains.md) | Analyzing Business Domains | Core/Generic/Supporting subdomains, Distillation, Complexity/Differentiation Test |
| [ch02](chapters/ch02-discovering-domain-knowledge.md) | Discovering Domain Knowledge | Ubiquitous Language |
| [ch03](chapters/ch03-managing-domain-complexity.md) | Managing Domain Complexity | Bounded Context |
| [ch04](chapters/ch04-integrating-bounded-contexts.md) | Integrating Bounded Contexts | Context Mapping (7 patterns), Context Map |
| [ch05](chapters/ch05-implementing-simple-business-logic.md) | Implementing Simple Business Logic | Transaction Script, Active Record |
| [ch06](chapters/ch06-tackling-complex-business-logic.md) | Tackling Complex Business Logic | Domain Model, Building Blocks (VO/Entity/Aggregate/Domain Event/Domain Service) |
| [ch07](chapters/ch07-modeling-the-dimension-of-time.md) | Modeling the Dimension of Time | Event Sourcing |
| [ch08](chapters/ch08-architectural-patterns.md) | Architectural Patterns | Layered Architecture, Ports & Adapters, CQRS |
| [ch09](chapters/ch09-communication-patterns.md) | Communication Patterns | Model Translation, Saga, Process Manager, Outbox |
| [ch10](chapters/ch10-design-heuristics.md) | Design Heuristics | Tactical Design Decision Tree, Testing Pyramid/Diamond/Reversed |
| [ch11](chapters/ch11-evolving-design-decisions.md) | Evolving Design Decisions | Subdomain type migration, Tactical pattern migration path |
| [ch12](chapters/ch12-eventstorming.md) | EventStorming | EventStorming 10-step process |
| [ch13](chapters/ch13-ddd-in-the-real-world.md) | DDD in the Real World | Strategic Analysis, Modernization Strategy, Strangler Pattern, Undercover DDD |
| [ch14](chapters/ch14-microservices.md) | Microservices | Microservices as Deep Modules, DDD boundary alignment |
| [ch15](chapters/ch15-event-driven-architecture.md) | Event-Driven Architecture | Event Notification, ECST, Domain Event, Distributed Big Ball of Mud |
| [ch16](chapters/ch16-data-mesh.md) | Data Mesh | Data Mesh's 4 principles |
| [ch17](chapters/ch17-appendix-a-case-study.md) | Appendix A: Case Study | Reverse subdomain identification, "Don't ignore pain," Widen-then-narrow BCs |

## Topic Index

- **Active Record** → ch05, ch11
- **Aggregate** → ch06, ch10, ch11, ch14
- **Anticorruption Layer (ACL)** → ch04, ch09, ch13
- **Big Ball of Mud (Distributed)** → ch15
- **Bounded Context** → ch03, ch04, ch10, ch14
- **Building Blocks (tactical)** → ch06
- **Complexity/Differentiation Test** → ch01
- **Context Mapping** → ch04
- **Core/Generic/Supporting Subdomains** → ch01, ch11, ch13, ch17
- **CQRS** → ch08
- **Customer-Supplier** → ch04, ch09
- **Data Mesh** → ch16
- **Deep Modules (microservices)** → ch14
- **Domain Event** → ch06, ch09, ch15
- **Domain Model pattern** → ch06, ch10, ch11
- **Domain Service** → ch06
- **Entity** → ch06
- **Event Sourcing / Event-Sourced Domain Model** → ch07, ch08, ch10, ch11
- **Event-Carried State Transfer (ECST)** → ch15
- **Event Notification** → ch15
- **EventStorming** → ch12, ch13
- **Layered Architecture** → ch08
- **Microservices** → ch14
- **Model Translation** → ch09
- **Open-Host Service (OHS)** → ch04, ch09, ch15
- **Outbox pattern** → ch09
- **Ports & Adapters (Hexagonal)** → ch08
- **Process Manager** → ch09
- **Saga** → ch09
- **Separate Ways** → ch04
- **Shared Kernel** → ch04
- **Strangler Pattern** → ch13
- **Subdomain type migration / evolving design** → ch11, ch17
- **Tactical Design Decision Tree** → ch10
- **Testing Pyramid / Diamond / Reversed Pyramid** → ch10
- **Transaction Script** → ch05, ch11
- **Ubiquitous Language** → ch02, ch13
- **Undercover DDD** → ch13
- **Value Object** → ch06

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase,
combine with project-specific tools. For topics beyond this book, check related skills
or ask the agent directly.
