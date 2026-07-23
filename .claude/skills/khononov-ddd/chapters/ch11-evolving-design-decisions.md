# Chapter 11: Evolving Design Decisions

## Core Idea
DDD design decisions are not permanent — as the business domain, organization, domain knowledge, and system grow, subdomain types and tactical/strategic patterns must be re-evaluated and deliberately migrated to stay aligned with reality.

## Frameworks Introduced
- **Subdomain type migrations** (Core↔Generic, Supporting↔Generic, Core↔Supporting): a subdomain's classification (Core/Supporting/Generic) is not fixed at initial analysis — it shifts as competitive dynamics, off-the-shelf solutions, and business strategy change.
  - When to use: whenever a subdomain's competitive relevance changes — a competitor commoditizes what was a differentiator (Core→Generic), an off-the-shelf tool no longer meets needs and is replaced in-house (Generic→Core), complexity in a "simple" supporting subdomain turns out to drive profit (Supporting→Core), or a core subdomain's complexity turns out not to be profitable (Core→Supporting).
  - How: watch for the trigger signals — a competitor's product commoditizing your advantage; recurring business-intelligence failures pointing to inadequacy of an off-the-shelf tool; increasing complexity in a supposedly-simple supporting subdomain (a red flag unless it demonstrably improves profit — otherwise it's accidental complexity); a core subdomain whose complexity no longer pays for itself. Once the type changes, re-derive both strategic (bounded context integration pattern) and tactical (design pattern) decisions from the new type — don't leave stale decisions in place.
- **Tactical pattern migration path** (Transaction Script → Active Record → Domain Model → Event-Sourced Domain Model): as a subdomain's business logic complexity grows (often signaling a Supporting/Generic→Core shift), the implementation pattern should be walked forward one step at a time, not jumped or over-engineered up front.
  - When to use: pain in evolving the existing implementation — difficulty modifying/extending the code, growing inconsistencies and duplication, complicated data-structure handling — is the signal to move to the next pattern. Don't preemptively apply the most sophisticated pattern to every subdomain; that wastes effort on subdomains that don't need it.
  - How (per step): (1) Transaction Script→Active Record — when working directly with data structures becomes unwieldy, encapsulate them in active record objects that abstract storage mapping. (2) Active Record→Domain Model — make active records' setters private to force compilation errors that surface hidden state-mutating logic scattered across scripts; move that logic inside the record; identify value objects and transactional/consistency boundaries; decompose into aggregates using the "smallest strongly-consistent boundary" principle, referencing other aggregates only by ID; define each aggregate's root as the sole public entry point. (3) Domain Model→Event-Sourced Domain Model — once aggregate boundaries are solid, replace direct state mutation with domain events representing the aggregate's lifecycle; migrate historical "timeless" state via either generating approximate past events (Generating Past Transitions) or an explicit migration event (Modeling Migration Events).

## Key Concepts
- **Generating Past Transitions**: reconstructing an approximate event stream for existing aggregates by inferring plausible past events that would project into the current known state; loses fidelity on events not derivable from the final state (e.g., unknown number of past "contacted" touches).
- **Modeling Migration Events**: instead of guessing history, emit one explicit `migrated-from-legacy` event capturing the pre-migration state as-is; honest about missing history but leaves permanent legacy artifacts that downstream projections (e.g., CQRS) must always account for.
- **Organizational change**: shifts in team structure, geography, or communication quality that force bounded context integration patterns to be re-derived, independent of any domain change.
- **Partnership to Customer-Supplier**: when a partnership (requiring tight collaboration) degrades — e.g., a team relocates to a distant development center — the relationship should shift to a more structured customer-supplier arrangement.
- **Customer-Supplier to Separate Ways**: when even a customer-supplier relationship suffers chronic communication/political friction, it can become more cost-effective to duplicate functionality (separate ways) than to keep chasing integration issues.
- **Growth-driven accidental complexity**: complexity introduced by extending a system without revisiting its design boundaries (subdomains, bounded contexts, aggregates) — distinct from essential complexity inherent to the business domain.
- **Coherent use cases heuristic**: a technique for re-splitting blurred subdomain boundaries as the domain grows, by grouping use cases that operate on the same data.
- **Chatty bounded contexts**: bounded contexts that can't complete operations without constantly calling other contexts — a growth-driven signal of poor boundary placement needing redesign.

## Mental Models
- Design decisions are hypotheses to be revisited, not permanent commitments — subdomain types, integration patterns, and tactical patterns are all snapshots of a point-in-time understanding.
- "Pain" as signal: difficulty implementing new requirements in the current design (whether a subdomain's tactical pattern or a bounded context's boundaries) is diagnostic information, not just an annoyance — treat it as a call to reassess.
- Broad-then-narrow boundaries: when domain knowledge is immature, prefer broader bounded context boundaries (cheaper to be wrong); decompose into narrower contexts/microservices only once the domain logic stabilizes.
- Growth follows the same DDD process as initial design: re-analyze the business domain/strategic layer first, then re-derive models, then re-implement — don't patch tactically without revisiting strategy.

## Anti-patterns
- **Treating an initial DDD design as final/immutable**: subdomain classifications, bounded context boundaries, and tactical patterns chosen at project start will become wrong as the business evolves; failing to revisit them turns thoughtful design into a maintenance nightmare.
- **Applying the most sophisticated tactical pattern everywhere upfront**: using domain model or event sourcing for subdomains that don't need it is wasteful and ineffective — patterns should be earned through demonstrated complexity, not assumed preemptively.
- **Letting bounded contexts become "jack of all trades"**: allowing a context to accumulate unrelated logic over time instead of extracting focused sub-contexts is accidental complexity.
- **Letting aggregates grow via convenience**: adding new functionality to existing aggregates without checking whether the new data actually needs strong consistency with the rest — violates the "smallest aggregate boundary" principle and reintroduces accidental complexity.
- **Confusing accidental complexity for a subdomain-type change**: rising complexity in a supporting subdomain is only a sign of Supporting→Core migration if it correlates with increased profitability; otherwise it's just complexity that should be cut, not a reason to invest more.

## Code Examples
(omit — not code-heavy; chapter's snippets illustrate the Active Record→Domain Model refactor by making setters private to surface hidden state-mutating logic, then moving that logic inside the object, e.g. turning an external `ApplyBonus.Execute()` that mutates `player.Points` directly into a `Player.ApplyBonus(percentage)` method.)

## Reference Tables
| Trigger | From | To |
|---|---|---|
| Competitor commoditizes your differentiator | Core subdomain | Generic subdomain |
| In-house build outperforms inadequate off-the-shelf tool | Generic subdomain | Core subdomain |
| Open-source/off-the-shelf alternative surpasses in-house supporting solution | Supporting subdomain | Generic subdomain |
| Supporting logic optimization starts driving profit | Supporting subdomain | Core subdomain |
| Core subdomain's complexity no longer justified by profit | Core subdomain | Supporting subdomain |
| Integration complexity of generic solution outweighs benefit | Generic subdomain | Supporting subdomain |
| Subdomain becomes core (no longer safe to duplicate) | Separate Ways | Customer-Supplier |
| Team relocates / collaboration degrades | Partnership | Customer-Supplier |
| Chronic communication/political friction | Customer-Supplier | Separate Ways |
| New teams added, context too wide for one team | Single wide bounded context | Split bounded contexts |
| Domain knowledge stabilizes after being unclear | Broad bounded context | Narrower bounded context / microservice |
| Business functionality grows without boundary review | Focused subdomain/context/aggregate | Bloated ("big ball of mud") |

## Worked Example
BuyIT's marketing team builds a simple in-house vendor-contracts CRUD system — a textbook Supporting subdomain. Years later an open-source contracts-management tool ships with OCR and full-text search, features BuyIT had backlogged due to low business impact. BuyIT scraps the in-house build and integrates the OSS tool: the subdomain becomes Generic. Later, BuyIT decides the integration overhead of the OSS tool isn't worth the benefit and reverts to its in-house system — the subdomain swings back from Generic to Supporting. This illustrates that subdomain type is not a one-time label: it tracks the current best available option and can migrate back and forth as the external landscape and cost/benefit calculus change, and each swing should trigger re-evaluation of the bounded context's integration pattern (e.g., separate ways vs. integration) and its tactical implementation pattern.

## Key Takeaways
1. Regularly re-derive a subdomain's type (Core/Supporting/Generic) from current competitive reality, not from the original analysis — competitor moves, off-the-shelf tools, and profitability shifts all invalidate past classifications.
2. Let implementation "pain" — difficulty adding functionality, growing inconsistencies, chatty context calls — be the trigger for migrating tactical patterns (Transaction Script → Active Record → Domain Model → Event-Sourced) one step at a time, not upfront over-engineering.
3. When migrating to event sourcing, explicitly choose and document your history-recovery strategy: approximate generated events (readable but lossy) vs. an explicit migration event (honest but permanent legacy baggage in projections).
4. Organizational changes — new teams, geographic distribution, communication breakdown — independently force bounded context integration patterns to evolve (Partnership→Customer-Supplier→Separate Ways), regardless of domain changes.
5. Treat growth as a driver of accidental complexity: proactively re-split blurred subdomains, de-bloat "jack of all trades" bounded contexts, and shrink aggregates back to their smallest strongly-consistent boundary.
6. Prefer broader bounded context boundaries while domain knowledge is immature; narrow them into microservices only once the domain stabilizes — this minimizes the cost of being wrong.
7. Use EventStorming (Chapter 12) as a proactive tool against domain-knowledge decay — documentation staleness and staff turnover erode understanding faster than most teams expect.

## Connects To
- **Ch1**: subdomain types (Core/Supporting/Generic) are the foundational classification this chapter shows evolving over time.
- **Ch2**: business domain analysis that first identifies the subdomains subject to these migrations.
- **Ch4**: bounded context integration patterns (partnership, customer-supplier, conformist, ACL, OHS, separate ways) whose migrations this chapter details.
- **Ch5/Ch6/Ch7**: the tactical pattern spectrum (transaction script, active record, domain model, event-sourced domain model) this chapter's migration path walks through step by step.
- **Ch10**: Design Heuristics — the broader signal-reading skill this chapter applies specifically to change-over-time triggers.
- **Ch12**: EventStorming — recommended tool for recovering/preserving domain knowledge before it decays into a legacy system.
- **Ch14**: microservices — referenced as the eventual decomposition target once broad bounded contexts stabilize.
- **Heraclitus's "the only constant is change"**: the chapter's closing philosophical frame for why design must be treated as continuously revisable.
