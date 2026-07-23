# Chapter 4: Integrating Bounded Contexts

## Core Idea
Bounded contexts are not independent — they must integrate through contracts, and DDD offers seven context mapping patterns for that integration, grouped by the nature of the collaboration (or lack of it) between the teams that own each side.

## Frameworks Introduced
- **Context Mapping patterns**: Partnership, Shared Kernel, Customer-Supplier (umbrella category containing Conformist, Anticorruption Layer, Open-Host Service), Separate Ways
  - When to use: pick the pattern that reflects the actual quality of communication and the actual balance of power between the teams — the pattern is a description of an organizational relationship first, a technical mechanism second.
  - How: identify whether the two bounded contexts' teams cooperate closely (Cooperation category), have an upstream/downstream power imbalance (Customer-Supplier category), or cannot/should not collaborate at all (Separate Ways); then apply the specific pattern within that category and plot the result on a Context Map.

## Key Concepts
- **Contract**: the touchpoint where two bounded contexts, each with its own model and ubiquitous language, must agree on an integration interface.
- **Cooperation category**: bounded contexts implemented by teams with well-established communication (often the same team, or teams with interdependent goals) — includes Partnership and Shared Kernel.
- **Customer-Supplier category**: an upstream (supplier) provides a service consumed by a downstream (customer); the two teams can succeed independently, which typically creates a power imbalance in who dictates the contract — includes Conformist, Anticorruption Layer, and Open-Host Service.
- **Separate Ways category**: the teams choose not to integrate at all and instead duplicate functionality, because collaboration would cost more than duplication.
- **Context Map**: a visual diagram plotting a system's bounded contexts and the integration pattern used between each pair, giving insight into high-level design, team communication patterns, and organizational issues.
- **Published Language**: the integration-oriented protocol a supplier exposes in an Open-Host Service, decoupled from its internal implementation model.

## Mental Models
- The integration pattern chosen between two bounded contexts is a mirror of the real organizational relationship between the teams that own them — technical integration design and Conway's Law are inseparable here.
- Power imbalance, not technical preference, decides who conforms to whom in Customer-Supplier relationships: whichever side can succeed independently of the other tends to hold the leverage.
- Cost of duplication vs. cost of coordination is the deciding calculus for Shared Kernel and Separate Ways alike — both patterns exist because sometimes integrating is more expensive than not integrating.
- Anticorruption Layer and Open-Host Service are mirror images of the same translation problem: ACL puts the translation on the consumer's side, Open-Host Service puts it on the supplier's side.

## Anti-patterns
- **Conformist chosen when Anticorruption Layer was needed**: if the downstream context contains a core subdomain, or the upstream model is a legacy mess, or the supplier's contract changes frequently, blindly conforming lets foreign concepts and instability leak into and pollute the downstream's model — the fix is an ACL that isolates the translation.
- **Shared Kernel without minimized scope**: exposing more of the shared model than strictly necessary for integration multiplies the blast radius of every change, coupling the lifecycles of all participating bounded contexts more tightly than needed.
- **Shared Kernel across teams without justification**: introducing a shared kernel between bounded contexts owned by different teams violates the single-team-ownership principle from Chapter 3; it should be a deliberate, justified exception (e.g., communication constraints, legacy modernization, or same-team contexts), not a default.
- **Partnership for geographically distributed or poorly synchronized teams**: partnership demands frequent synchronization and continuous integration; without well-established collaboration practices, it breaks down into conflict and drift.
- **Separate Ways for core subdomains**: duplicating a core subdomain's implementation defies the very strategy of investing maximally in the domain that differentiates the business.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Pattern | Team Relationship | When to Use |
|---|---|---|
| Partnership | Two teams with well-established, high-trust communication; ad hoc, two-way coordination | Co-located or highly synchronized teams who can continuously integrate changes without one side blocking the other |
| Shared Kernel | Multiple teams (or one team across contexts) share and jointly own a limited overlapping model | Cost of duplicating a volatile (often core) subdomain's model exceeds the cost of coordinating shared code; also useful for same-team contexts or as a temporary legacy-modernization step |
| Conformist | Upstream has no motivation to accommodate downstream; downstream accepts the upstream model as-is | The upstream's model is an industry standard or otherwise "good enough" for downstream needs, and building a translation layer isn't worth the effort |
| Anticorruption Layer | Upstream is powerful/unresponsive; downstream refuses to let the upstream model corrupt its own | Downstream contains a core subdomain, the upstream model is inefficient/legacy, or the upstream contract changes often |
| Open-Host Service | Supplier is motivated to protect and serve its consumers; power skews toward consumers | Supplier wants to evolve its internal implementation freely while exposing a stable, consumer-friendly published language (often to many consumers, possibly at multiple versions) |
| Separate Ways | Teams unwilling or unable to collaborate | Communication/political barriers, an easy-to-duplicate generic subdomain, or model differences too large to bridge cost-effectively (never for core subdomains) |
| Context Map | N/A (a visualization, not a team-relationship pattern) | Always — to give the organization a shared, maintained overview of bounded contexts and their integration patterns |

## Worked Example
The book's running illustration for Anticorruption Layer vs. Open-Host Service works like this: imagine a legacy upstream system with an inconvenient, frequently-changing model. A downstream bounded context that implements a core subdomain cannot afford to let its own ubiquitous language be shaped by that legacy mess, so it builds an anticorruption layer — a translation component sitting at the boundary that converts the upstream's model into concepts native to the downstream's own language. Changes in the upstream now only ripple through the translation layer, never into the downstream's core model.

Now flip the perspective to the supplier's side: if that same upstream team instead wanted to actively protect *all* of its consumers (not just one) from its internal churn, it would implement an Open-Host Service — decoupling its internal implementation model from a stable public "published language," and optionally exposing multiple versions of that published language simultaneously so consumers can migrate on their own schedule. Where ACL is the consumer unilaterally protecting itself, Open-Host Service is the supplier proactively protecting everyone downstream.

A separate concrete example given for Shared Kernel: an enterprise permissions model, where each user's authorization can be granted directly or inherited from an organizational unit. Multiple bounded contexts need this exact model, and it must stay consistent everywhere it's used — a case where the shared kernel is kept intentionally narrow (just the integration contracts and data structures needed), with every change to it triggering integration tests across all consuming contexts.

## Key Takeaways
1. Every bounded context integration reduces to a contract, and the right pattern for that contract follows the real communication and power dynamics between the owning teams — not a technical preference.
2. Cooperation patterns (Partnership, Shared Kernel) require sustained high-trust collaboration and continuous integration; without that, they fail.
3. In Customer-Supplier relationships, decide explicitly whether the downstream conforms (Conformist), translates (Anticorruption Layer), or the upstream protects consumers via a published language (Open-Host Service) — the choice hinges on whether the downstream is core, how bad the upstream model is, and how often it changes.
4. Reserve Anticorruption Layers for cases where conforming would corrupt a core subdomain's model or import instability from a poor/legacy upstream.
5. Never use Separate Ways to duplicate a core subdomain — that undermines the entire point of investing in what differentiates the business.
6. Keep a Shared Kernel's scope minimal and its changes continuously tested; treat it as a pragmatic, justified exception to single-team bounded-context ownership, not a default integration style.
7. Maintain a Context Map as a living, team-shared artifact (each team updates its own integrations) — it surfaces organizational as well as technical issues, such as one upstream team whose downstreams all resort to anticorruption layers.

## Connects To
- **Ch3**: Managing Domain Complexity — bounded context boundaries and single-team ownership are the precondition these integration patterns build on; Shared Kernel deliberately relaxes that ownership principle.
- **Ch9**: Communication Patterns — explores concrete implementation techniques for these integration patterns, including different ways to build an anticorruption layer.
- **Ch14**: Microservices — bounded context integration patterns map directly onto microservice-to-microservice integration and team-topology decisions.
- **External concept**: Context Mapper (tool for managing context maps as code) and Conway's Law (organizational communication structures shape system integration architecture).
