# Khononov DDD Cheatsheet — Reasoning Aid

## 1. Subdomain type → strategy (Ch1, Ch11)
| Type | Test | Do |
|---|---|---|
| Core | "Would someone pay for just this piece?" | Build in-house, best engineers, heaviest patterns. Never buy/outsource/duplicate. |
| Generic | Cheaper to integrate off-the-shelf/OSS than build | Buy/adopt. Never build from scratch. |
| Supporting | Simple/CRUD, no edge, no ready-made option | Build cheaply or outsource; don't over-invest talent. |

Classify to *coherent use cases*, not departments. "It looks easy" = red flag for core.
**Type drifts** — re-derive when: competitor commoditizes edge (Core→Generic); off-the-shelf tool becomes inadequate (Generic→Core); "simple" piece drives profit, profit-correlated not just complex (Supporting→Core); complexity stops paying off (Core→Supporting).

## 2. Ubiquitous Language (Ch2)
Talk to domain experts directly, no translators. Zero jargon. One term = one meaning (split ambiguous, merge false synonyms). Investing in UL early beats getting tactical patterns right — strongest success predictor (Ch17).

## 3. Bounded Context sizing (Ch3, Ch10)
Split into separate BCs when experts genuinely disagree on a term — don't prefix, don't force consensus. Subdomains are *discovered*; BCs are *designed*. **Start wide** around immature/core subdomains (cheap to refactor logically); narrow as knowledge stabilizes. Supporting/generic can be narrow early. Keep coherent use-cases on one BC.

## 4. Context Mapping — pick by team relationship (Ch4)
| Pattern | Relationship | Use when |
|---|---|---|
| Partnership | High-trust, tightly synced | Continuous integration possible; breaks under distance. |
| Shared Kernel | Joint ownership, narrow scope | Duplicating a volatile/core model costs more than coordinating it. |
| Conformist | Upstream powerful, unmotivated | Upstream model is standard/"good enough"; ACL not worth it. |
| Anticorruption Layer | Downstream protects itself | Downstream is core, OR upstream legacy/unstable. Never Conformist here. |
| Open-Host Service | Supplier protects many consumers | Supplier evolves freely; exposes stable published language (ACL's mirror). |
| Separate Ways | Won't/can't collaborate | Cheap-to-duplicate generic subdomain only — never core. |

Decay path: Partnership → Customer-Supplier (team relocates) → Separate Ways (chronic friction). Keep a living Context Map.

## 5. Business-logic decision tree (Ch5-7, Ch10)
1. Tracks money / needs audit / deep analytics? → **Event-Sourced Domain Model**
2. Complex rules/invariants (not CRUD)? → **Domain Model**
3. Complex data structures? → **Active Record**
4. Else → **Transaction Script**

Heavy pattern on simple subdomain = accidental complexity; light pattern on core = duplicated, drifting logic.

| Pattern | Handles | Effort | Test shape | Misuse failure |
|---|---|---|---|---|
| Transaction Script | Procedural (ETL, ACL glue) | Lowest | Reversed pyramid (e2e) | Duplicates as complexity grows |
| Active Record | Simple logic, complex data | Low-Med | Diamond (integration) | Scatters into service layer ("anemic") |
| Domain Model | Entangled invariants | Med-High | Pyramid (unit) | Accidental complexity if logic is simple |
| Event-Sourced DM | + time/audit needs | Highest | Pyramid | Schema/ops pain if unneeded |

Aggregate rules: one instance per transaction; reference others by ID only; size = smallest boundary for *strong* consistency, rest eventually consistent. Wanting two aggregates in one transaction means the boundary is wrong. Be pragmatic: weigh corruption risk against prevention cost.

## 6. Architecture follows business logic (Ch8, Ch10)
| Business logic | Architecture | Why |
|---|---|---|
| Transaction Script | Minimal 3-layer | Logic legitimately depends on data access |
| Active Record | Layered + service layer | Needs a reusable orchestration façade |
| Domain Model | Ports & Adapters | Aggregates need zero infra dependency (DIP) |
| Event-Sourced DM | **CQRS mandatory** | Event streams are only queryable by ID otherwise |

CQRS is addable to any pattern needing multiple read models. Default to synchronous checkpoint-catchup projections; async only as a supplement (fragile under out-of-order/duplicate delivery). Commands may return data, but only from the command model, never a projection.

## 7. Reliable communication (Ch9, Ch15)
Never publish events from inside the aggregate (pre-commit leak) or right after a bare commit (crash = lost event). Use the **Outbox pattern**: atomic commit + async relay, at-least-once.
**Saga** (implicit trigger, linear event→command, no branching) vs **Process Manager** (explicit state + if/else) — branching is the tell. Neither replaces a correctly-drawn aggregate boundary.
Event type by consumer need: **Notification** (minimal + re-query, safest) · **ECST** (state snapshot, risks consumers reimplementing your projection logic) · **Domain Event** (rich fact — curate public/private split; never expose raw internal event-sourced streams). Fix temporal coupling with an explicit notification, never an artificial delay.

## 8. Evolving decisions (Ch11, Ch13, Ch17)
Migrate one step at a time, triggered by **pain** (hard to extend, duplication, chatty contexts): Transaction Script → Active Record → Domain Model → Event-Sourced. Brownfield order: value objects → state-based aggregates (validate boundaries) → event sourcing; skipping straight to event sourcing is high-risk. History migration: **Generating Past Transitions** (inferred, lossy) vs **Modeling Migration Events** (one explicit legacy-marker, honest but permanent). Reverse-check: infer subdomain type from the pattern requirements demand, compare to business's stated importance — disagreement is signal. Modernize logical boundaries before physical; use the Strangler pattern (new BC + façade + gradual migration + frozen legacy), never big-bang rewrite. "Undercover DDD": justify by engineering risk, not book authority, when the org won't buy the methodology by name.

## 9. Microservice sizing (Ch14)
Judge by the **deep-module test**: narrow interface hiding large implementation. If a split forces the interface to grow, it's shallower, not better. Widest→narrowest: **Bounded Context** > **Subdomain** (safest default) > **Aggregate** (only if rarely touches siblings).

## 10. Smells & tells
| Smell | Signal | Fix |
|---|---|---|
| "Method as a Service" | Global complexity exploded | Re-draw around subdomains; compress via OHS/ACL |
| Chatty contexts / distributed monolith | Boundaries drawn on aggregates, coupling unchecked | Widen boundary or fix integration pattern |
| Suicidal boundary (BC splits one aggregate) | Accidental BC, e.g. logic offloaded to a DB team | Never let org splits become unexamined boundaries |
| Anemic domain model ("aggregates everywhere") | Domain Model with no real invariants/commands | Push logic into commands, or admit it's Active Record |
| Subscribing to raw internal domain events | Temporal+functional+implementation coupling | Publish a curated published language |
| Artificial delay to fix ordering | Temporal coupling hidden, not fixed | Explicit notification event instead |
| Rising cost-per-feature / growing bugs | Pattern no longer matches complexity | Re-run decision tree; migrate one step |
| Aggregate holds eventually-consistent-only data | Boundary drawn for convenience | Reference by ID; shrink to strong-consistency need |
| Core subdomain on Transaction Script/outsourced | Wrong pattern/integration for core | Escalate pattern; bring in-house |
| ETL reading an operational DB's schema directly | Analytics coupled to implementation | Expose analytical output port (OHS) — Data Mesh fix |

## 11. Testing strategy by pattern (Ch10)
Domain Model / Event-Sourced → **Pyramid** (unit-heavy). Active Record → **Diamond** (integration-heavy). Transaction Script → **Reversed pyramid** (e2e-heavy, too thin to unit-isolate).

## 12. EventStorming (Ch12)
Use for: building UL, modeling a new process, recovering lost legacy knowledge, onboarding. Skip for trivial sequential processes. Flow: events → timeline → pain points → pivotal events → commands → policies → read models → external systems → aggregates → bounded contexts. Shared understanding is the goal; the model is a bonus.
