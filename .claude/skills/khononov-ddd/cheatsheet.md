# Khononov DDD Cheatsheet — Reasoning Aid

## 1. Subdomain type → strategy
| Type | Test | Do |
|---|---|---|
| Core | Would someone pay for just this? | Build in-house, best engineers, heaviest patterns. Never buy/outsource/duplicate. |
| Generic | Cheaper to buy/integrate than build | Buy/adopt, never build from scratch. |
| Supporting | Simple/CRUD, no edge, no ready-made option | Build cheaply or outsource; don't over-invest talent. |

Classify to coherent use cases, not departments. "Looks easy" = red flag for core.
Type drifts — re-derive on: competitor commoditizes edge (Core→Generic); off-the-shelf tool inadequate (Generic→Core); "simple" piece drives profit (Supporting→Core, only if profit-correlated); complexity stops paying off (Core→Supporting).

## 2. Ubiquitous Language
Talk to domain experts directly, no translators. Zero jargon, one term = one meaning. Investing in UL early beats getting patterns right — strongest success predictor (Ch17).

## 3. Bounded Context sizing
Split BCs when experts genuinely disagree on a term. Subdomains are *discovered*; BCs are *designed*. Start wide around immature/core subdomains (cheap to refactor logically); narrow as knowledge stabilizes.

## 4. Context Mapping — pick by team relationship, not tech
| Pattern | Use when |
|---|---|
| Partnership | High-trust, synced teams; continuous integration possible |
| Shared Kernel | Duplicating a volatile shared model costs more than coordinating it |
| Conformist | Upstream unmotivated, its model is "good enough"; ACL not worth it |
| Anticorruption Layer | Downstream is core, or upstream is legacy/unstable — never Conformist here |
| Open-Host Service | Supplier protects many consumers via a stable published language |
| Separate Ways | Won't/can't collaborate on a cheap-to-duplicate generic subdomain — never core |

Decay path: Partnership → Customer-Supplier → Separate Ways as collaboration degrades.

## 5. Business-logic decision tree
1. Money/audit/deep analytics? → **Event-Sourced Domain Model**
2. Complex rules/invariants (not CRUD)? → **Domain Model**
3. Complex data structures? → **Active Record**
4. Else → **Transaction Script**

Heavy pattern on simple subdomain = accidental complexity; light pattern on core = duplicated logic.

| Pattern | Architecture | Testing | Misuse failure |
|---|---|---|---|
| Transaction Script | Minimal 3-layer | Reversed pyramid (e2e) | Duplicates as complexity grows |
| Active Record | Layered + service layer | Diamond (integration) | Logic scatters ("anemic") |
| Domain Model | Ports & Adapters (zero infra dep) | Pyramid (unit) | Complexity if logic is simple |
| Event-Sourced DM | **CQRS mandatory** (else fetch-by-ID only) | Pyramid | Schema/ops pain if unneeded |

Aggregates: one instance per transaction; reference others by ID; size = smallest boundary for *strong* consistency, rest eventually consistent — wanting two aggregates in one transaction means the boundary is wrong. CQRS is addable to any pattern needing multiple read models; default sync checkpoint projections, async only as supplement.

## 6. Reliable communication
Never publish events from inside the aggregate or right after a bare commit — use the **Outbox pattern** (atomic commit + async relay, at-least-once). **Saga** = implicit trigger, linear event→command, no branching; **Process Manager** = explicit state + if/else (branching is the tell). Event type by need: **Notification** (minimal, re-query, safest) · **ECST** (state snapshot, risks duplicated projection logic) · **Domain Event** (curate public/private split; never expose raw internal streams). Fix temporal coupling with a notification, never a delay.

## 7. Evolving decisions
Migrate one step at a time on **pain** (hard to extend, duplication, chattiness): Transaction Script → Active Record → Domain Model → Event-Sourced. Brownfield order: value objects → state-based aggregates → event sourcing. History migration: generate approximate past events (lossy) vs. one explicit migration-marker event (honest, permanent). Reverse-check: infer subdomain type from the pattern requirements demand, compare to stated business importance — disagreement is signal. Logical boundaries before physical; Strangler pattern, never big-bang rewrite. "Undercover DDD": justify by risk, not book authority.

## 8. Microservice sizing
Deep-module test: narrow interface hiding large implementation; a split that grows the interface made it shallower. Widest→narrowest: Bounded Context > Subdomain (safest default) > Aggregate (only if rarely touches siblings).

## 9. Smells & tells
| Smell | Fix |
|---|---|
| "Method as a Service" (interfaces balloon) | Re-draw around subdomains; compress via OHS/ACL |
| Chatty contexts / distributed monolith | Widen boundary or fix integration pattern |
| Suicidal boundary (BC splits one aggregate via org handoff) | Never let org splits become unexamined boundaries |
| Anemic domain model ("aggregates everywhere") | Push logic into commands, or admit it's Active Record |
| Raw internal domain events exposed to subscribers | Publish a curated published language instead |
| Artificial delay to fix event ordering | Explicit notification event, not a timing hack |
| Core subdomain built cheap, outsourced, or duplicated | Escalate pattern; bring in-house |
| ETL reads an operational DB's schema directly | Expose an analytical output port — Data Mesh fix |

## 10. EventStorming
Use for building UL, modeling new/changed processes, recovering lost legacy knowledge, onboarding; skip for trivial sequential processes. Flow: events → timeline → pain points → pivotal events → commands → policies → read models → external systems → aggregates → bounded contexts. Shared understanding is the goal; the diagram is a bonus.
