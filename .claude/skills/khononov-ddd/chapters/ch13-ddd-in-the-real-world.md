# Chapter 13: Domain-Driven Design in the Real World

## Core Idea
DDD is not a greenfield, all-or-nothing discipline reserved for teams of experts — it delivers the most value on brownfield, legacy, big-ball-of-mud codebases, and can be applied incrementally, pragmatically, and even without ever naming it to a skeptical organization.

## Frameworks Introduced
- **Strategic Analysis** (Understand the Business Domain, Explore the Current Design): before touching code, map the organization's business domain, subdomains, and current architecture to find where DDD investment pays off.
  - When to use: at the start of any engagement with an existing (brownfield) system, before proposing any modernization.
  - How: identify the business domain, customers, and value proposition; use the org chart as a heuristic to find subdomain boundaries; classify subdomains as core (the company's "secret sauce," or — paradoxically — the worst-designed component the business refuses to rewrite because it's too risky), generic (off-the-shelf/subscription/OSS replaceable), or supporting (custom but not a competitive advantage). Then explore the current design: identify high-level components by their decoupled lifecycles (not necessarily formal bounded contexts), evaluate the tactical design (do implementation patterns match subdomain complexity?), and chart a context map of the current architecture to spot suboptimal strategic decisions (multiple teams on one component, duplicated core-subdomain implementations, outsourced core subdomains, integration friction, awkward models leaking from legacy/external systems). Use EventStorming to recover lost domain knowledge uncovered along the way.
- **Modernization Strategy** (Strategic Modernization, Tactical Modernization): think big but start small — decide where to invest in fixing design, and whether to fix it strategically (boundaries) or tactically (patterns), gradually rather than via a "big rewrite."
  - When to use: after strategic analysis has surfaced pain points, when planning how to actually improve an existing system's design.
  - How: first align logical boundaries (namespaces, modules, packages, and non-code artifacts like stored procedures) with subdomain boundaries — a low-risk refactor since it repositions types without changing logic. Then, strategically, decide where to convert logical boundaries into physical bounded contexts (multiple teams on one codebase, or conflicting models colliding) and fix integration patterns (customer-supplier variants, anticorruption layers, open-host services, separate ways) as organizational relationships evolve. Tactically, target the most painful mismatches — core subdomains stuck on transaction script or active record — and modernize either via the strangler pattern (build a new bounded context, freeze the legacy one except hotfixes, migrate functionality gradually behind a façade, optionally sharing one database temporarily until the legacy system is retired) or via in-place refactoring (state-based aggregates before event-sourced ones; value objects first; gather related logic, then analyze transactional boundaries before finalizing aggregate design; wrap the result in anticorruption layers and open-host services).
- **Undercover Domain-Driven Design**: introduce DDD's practices as ordinary professional engineering technique — not as a named organizational methodology — to sidestep the difficulty of "selling" DDD to skeptical management or teams.
  - When to use: when management or the team isn't bought into DDD as a formal initiative, but the practices still add value quietly.
  - How: cultivate the ubiquitous language through everyday conversation (listen for inconsistent terms, ask domain experts for clarification, use their language in code and communication) without ever branding it "DDD"; justify bounded contexts and tactical patterns (aggregates, transactional boundaries, avoiding stored-procedure logic duplication) by appealing to the underlying engineering logic and business risk, not by citing the DDD book as authority; sell event sourcing by demonstrating state-based vs. event-based models directly to domain experts and letting them advocate for it once they see the value (especially around modeling time).

## Key Concepts
- **Brownfield modernization**: improving the design of an existing, proven system rather than designing from scratch — the setting where DDD is most valuable, not least.
- **Big rewrite (anti-goal)**: an attempt to rebuild an entire system from scratch "correctly," rarely successful and rarely supported by management.
- **Think big, start small**: a philosophy of setting a long-term design vision but pursuing it via small, safe, incremental steps rather than one large risky change.
- **Cultivating a ubiquitous language incrementally**: building shared vocabulary gradually through ordinary communication with domain experts (watercooler talk, clarifying inconsistent terms) rather than a formal top-down mandate.
- **Selling Domain-Driven Design**: the practical challenge of getting management and teams to buy into a methodology that spans engineering and business stakeholders; addressed either by formal advocacy or by going undercover.
- **Pragmatic DDD**: applying DDD's underlying reasoning — business domain drives design decisions — without necessarily adopting every tactical pattern (aggregates, event sourcing, etc.) verbatim.
- **Strangler pattern**: gradually migrating functionality from a legacy bounded context into a new one (named after strangler fig trees that grow over and eventually replace their host), typically paired with a façade that routes requests to legacy or modernized code until migration completes.
- **Logical vs. physical boundaries**: logical boundaries (namespaces/modules/packages aligned to subdomains) are a safe first step; physical boundaries (separate bounded contexts/services) are a higher-risk, higher-payoff step taken only where clearly justified.
- **EventStorming as knowledge recovery**: reused from earlier in the book specifically as the tool for recovering lost domain knowledge in undocumented legacy codebases.

## Mental Models
- **Core subdomains hide in the ugliest code**: the software components everyone hates but the business refuses to rewrite are often core subdomains in disguise — the "worst-designed" heuristic is a legitimate subdomain-classification signal, not just a complaint.
- **Modernize like a strangler fig, not a demolition crew**: sustainable legacy replacement grows a new system alongside the old one and lets the old one wither, rather than tearing it down first.
- **DDD as toolbox, not mandate**: individual patterns (ubiquitous language, bounded contexts, aggregates, event sourcing) can be adopted independently based on whether they solve a real problem in front of you — DDD is defined by letting the business domain drive design decisions, not by using aggregates or value objects per se.
- **Appeal to logic, not authority**: when justifying a DDD pattern to colleagues, explain the underlying risk or complexity it addresses ("why can't a transaction span two aggregates?") rather than citing DDD literature.

## Anti-patterns
- **Big-bang rewrites**: rewriting a whole system from scratch "this time correctly" — rarely successful, rarely gets management support, and carries far more risk than the business value it promises.
- **Treating DDD as all-or-nothing**: believing you must adopt every pattern (aggregates, event sourcing, bounded contexts, etc.) or it "doesn't count" as DDD — this belief blocks incremental adoption on brownfield projects where wholesale adoption is impractical.
- **Refactoring active record straight to event-sourced domain model**: skipping the intermediate state-based aggregate step is far riskier than first finding correct aggregate boundaries with a state-based model, then moving to event sourcing once boundaries are proven.
- **Forcing DDD terminology onto a resistant organization**: appealing to authority ("the DDD book says so") instead of the underlying engineering rationale alienates skeptical teams and management; go undercover instead.
- **Prematurely carving out the smallest possible bounded contexts**: as flagged from Chapter 10, decomposing too early/too finely on a brownfield system is risky — favor turning boundaries physical only where multiple teams or conflicting models create real friction.

## Code Examples
(omit — not code-heavy)

## Reference Tables
(omit if none)

## Worked Example
A team inherits a monolithic e-commerce platform. Strategic analysis: the org chart reveals separate departments for catalog, pricing/promotions, and fulfillment; the pricing engine is a tangled, feared, frequently-changed piece of code that the business won't let anyone rewrite outright — a signal it's a core subdomain, not just legacy debt. Catalog search runs on a licensed third-party engine (generic subdomain); fulfillment tracking is custom but rarely touched (supporting subdomain). Exploring the current design shows all three subdomains crammed into one deployable monolith with no logical separation, and pricing logic duplicated between application code and database stored procedures.

Modernization strategy: first, reorganize the codebase into namespaces/modules matching catalog, pricing, and fulfillment (a safe, logic-preserving refactor), and rename or relocate the stored procedures to match. Strategic modernization: since two separate teams now want to iterate on pricing and fulfillment independently, pricing is extracted into its own bounded context (physical boundary) using the strangler pattern — a new pricing service is built, a façade routes requests to old or new logic during migration, both temporarily share the pricing database, and the legacy pricing module is frozen except for hotfixes until fully replaced. Fulfillment, having only one team and no conflicting models, stays as a logical module for now. Tactical modernization: within the new pricing context, the team runs an EventStorming session with domain experts to recover lost pricing rules, discovers the domain is highly time-sensitive (promotions, price history), and — after demonstrating state-based vs. event-based models to the domain experts directly — the experts themselves advocate for an event-sourced aggregate. The team gets there gradually: value objects first, then state-based aggregates with validated transactional boundaries, then event sourcing. Throughout, the team never brands any of this "we're doing DDD now" to management — it's simply presented as incremental technical improvement justified by concrete risk and cost arguments (undercover DDD).

## Key Takeaways
1. Brownfield, legacy projects — not greenfield ones — are where DDD delivers the most value, because they already have accumulated technical debt and proven business viability worth protecting.
2. Start any modernization effort with strategic analysis: understand the business domain and subdomain types, then map the current design's components and context map before deciding what to change.
3. Prefer small, incremental, reversible steps (logical before physical boundaries, state-based before event-sourced aggregates, value objects before full aggregates) over big-bang rewrites.
4. Use the strangler pattern plus a façade to migrate legacy functionality gradually, allowing temporary database sharing only as a bridge to eventual legacy retirement.
5. DDD is not all-or-nothing — apply the patterns that solve real problems in your context; the defining trait of DDD is letting the business domain drive design decisions, not using any specific tactical pattern.
6. When management or the team resists DDD as a named methodology, apply its practices "undercover": justify decisions with engineering logic and business risk, not appeals to authority.
7. EventStorming remains the go-to tool for recovering lost domain knowledge in undocumented or poorly understood legacy codebases.

## Connects To
- **Ch 1**: subdomain classification (core/generic/supporting) applied here as the first step of strategic analysis on an existing organization.
- **Ch 10**: design heuristics and the risk of premature bounded context decomposition, directly referenced when deciding whether to turn logical boundaries into physical ones.
- **Ch 11**: evolving design decisions and migrating tactical patterns, extended here with brownfield-specific nuances (state-based before event-sourced, gradual aggregate refactoring).
- **Ch 12**: EventStorming as the practical mechanism for recovering lost domain knowledge and cultivating a ubiquitous language, reused throughout this chapter.
- **Ch 17 (Appendix A case study)**: the concrete worked version of this chapter's brownfield modernization advice.
- **Strangler fig pattern (Martin Fowler)**: the external architectural pattern this chapter's migration strategy is named after and builds on.
