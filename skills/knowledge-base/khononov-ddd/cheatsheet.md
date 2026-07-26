# Khononov DDD Cheatsheet — Reasoning Aid

## 1. Subdomain type → strategy
| Type | Test | Do |
|---|---|---|
| Core | Would someone pay for just this? | In-house, best engineers, heaviest patterns; never buy/outsource/duplicate |
| Generic | Cheaper to integrate than build | Buy/adopt, never build from scratch |
| Supporting | Simple/CRUD, no edge, no ready-made option | Build cheaply or outsource; don't over-invest talent |

Classify to coherent use cases, not departments. "Looks easy" = red flag for core. Type drifts — re-derive on: competitor commoditizes edge (Core→Generic); tool becomes inadequate (Generic→Core); "simple" piece drives profit, if profit-correlated (Supporting→Core); complexity stops paying off (Core→Supporting).

## 2. Ubiquitous Language
Talk to domain experts directly, no translators. Zero jargon, one term = one meaning. Investing in UL early beats getting patterns right — strongest success predictor across projects (Ch17).

## 3. Bounded Context sizing
Split BCs where experts genuinely disagree on a term. Subdomains are *discovered*, BCs are *designed*. Start wide around immature/core subdomains; narrow as knowledge stabilizes.

## 4. Context Mapping — pick by team relationship, not tech
| Pattern | Use when |
|---|---|
| Partnership | High-trust, synced teams; continuous integration possible |
| Shared Kernel | Duplicating a volatile model costs more than coordinating it |
| Conformist | Upstream unmotivated, model is "good enough"; ACL not worth it |
| Anticorruption Layer | Downstream is core, or upstream legacy/unstable — never Conformist |
| Open-Host Service | Supplier protects many consumers via a published language |
| Separate Ways | Cheap-to-duplicate generic subdomain, can't collaborate — never core |

Relationship decays: Partnership → Customer-Supplier → Separate Ways.

## 5. Business-logic decision tree
1. Money/audit/deep analytics? → **Event-Sourced Domain Model**
2. Complex rules/invariants (not CRUD)? → **Domain Model**
3. Complex data structures? → **Active Record**
4. Else → **Transaction Script**

Heavy pattern on simple subdomain = accidental complexity; light pattern on core = duplication.

| Pattern | Architecture | Testing | Misuse failure |
|---|---|---|---|
| Transaction Script | Minimal 3-layer | Reversed pyramid | Duplicates as complexity grows |
| Active Record | Layered + service layer | Diamond | Logic scatters ("anemic") |
| Domain Model | Ports & Adapters | Pyramid | Complexity if logic is simple |
| Event-Sourced DM | **CQRS mandatory** | Pyramid | Schema/ops pain if unneeded |

Aggregates: one instance per transaction; reference others by ID; size = smallest boundary for *strong* consistency, rest eventually consistent — wanting two per transaction means the boundary is wrong. CQRS is addable to any pattern needing multiple read models.

## 6. Reliable communication
Never publish events from inside the aggregate or right after a bare commit — use the **Outbox** (atomic commit + async relay, at-least-once). **Saga** = implicit trigger, linear event→command, no branching; **Process Manager** = explicit state + if/else (branching is the tell). Event type by need: **Notification** (minimal, re-query, safest) · **ECST** (state snapshot, risks duplicated logic) · **Domain Event** (curate public/private split, never raw streams). Fix ordering with a notification, never a delay.

## 7. Evolving decisions
Migrate one step on **pain** (hard to extend, duplication, chattiness): Transaction Script → Active Record → Domain Model → Event-Sourced. Brownfield order: value objects → state-based aggregates → event sourcing. History: approximate past events (lossy) vs. one explicit migration-marker event (honest, permanent). Reverse-check: infer subdomain type from the pattern requirements demand, compare to stated importance. Logical before physical boundaries; Strangler pattern, never big-bang. "Undercover DDD": justify by risk, not book authority.

## 8. Microservice sizing
Deep-module test: narrow interface hiding large implementation; a split that grows the interface is shallower, not better. Widest→narrowest: Bounded Context > Subdomain (default) > Aggregate (only if self-contained).

## 9. Smells & tells
| Smell | Fix |
|---|---|
| "Method as a Service" (interfaces balloon) | Re-draw around subdomains; compress via OHS/ACL |
| Chatty contexts / distributed monolith | Widen boundary or fix integration pattern |
| Suicidal boundary (BC splits one aggregate via org handoff) | Never let org splits become unexamined boundaries |
| Anemic domain model ("aggregates everywhere") | Push logic into commands, or admit it's Active Record |

## 10. EventStorming
Use for building UL, modeling new processes, recovering lost legacy knowledge, onboarding; skip trivial processes. Flow: events → timeline → pain points → pivotal events → commands → policies → read models → external systems → aggregates → bounded contexts. Shared understanding is the goal; the diagram is a bonus.

## 11. Data Mesh
Apply bounded-context logic to analytics: each BC owns/publishes its analytical model as a versioned product, not one shared warehouse. ETL reading an operational schema directly signals this is missing.
