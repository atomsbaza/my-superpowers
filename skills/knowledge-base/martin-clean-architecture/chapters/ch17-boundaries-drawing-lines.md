# Chapter 17: Boundaries: Drawing Lines

## Core Idea
Architecture is the discipline of drawing boundaries between things that matter (business rules) and things that don't (frameworks, databases, UI, IO) — with dependency arrows always pointing from low-value details toward high-value policy — so that decisions about details can be deferred indefinitely, exactly as third-party plugin systems isolate a stable core from replaceable plugins.

## Frameworks Introduced
- **Plugin architecture pattern**: core business rules are kept fully independent of any component that is optional or has multiple possible implementations (UI, database, frameworks); those components are structured as "plugins" to the core.
  - When to use: for any component whose implementation choice is a detail rather than a business-rule decision — UI technology, database technology, web frameworks, DI frameworks, messaging.
  - How: define the interface the core needs (e.g., `DatabaseInterface`) inside the business-rules component; put concrete implementations (e.g., `DatabaseAccess`) in a separate component that depends on and implements that interface. The boundary line is drawn across the inheritance/implementation relationship — dependency arrows point toward the business rules, never away from them. This makes the "detail" component swappable without the business rules knowing or caring.
- **Boundary placement rule — "axis of change"**: "Boundaries are drawn where there is an axis of change. The components on one side of the boundary change at different rates, and for different reasons, than the components on the other side."
  - When to use: to decide *where* to draw a boundary line at all.
  - How: identify pairs of concerns that change at different rates/for different reasons (GUI vs. business rules; business rules vs. DI framework) and place a boundary between them. This is explicitly the SRP applied to boundary placement.
- **"The IO is irrelevant" principle**: the business rules / domain model should not depend on or know about the interface (GUI, console, web) through which it's driven.
  - When to use: whenever building any interactive system, especially ones where stakeholders fixate on the GUI as "the system."
  - How: keep the model (data structures + functions implementing behavior) fully capable of running and being tested with no UI attached at all; the UI depends on the model, never the reverse.

## Key Concepts
- **Boundary**: a line separating software elements such that those on one side cannot know about those on the other; boundary crossings are managed via source-code dependency direction.
- **Premature decision**: a decision unrelated to actual business requirements/use cases (frameworks, DBs, web servers, utility libraries, DI) made too early, coupling the architecture to it and multiplying future development effort.
- **"Download and Go" rule**: FitNesse's self-imposed constraint (ship as a single jar) that drove early architectural decisions, including writing a custom bare-bones web server to avoid a premature framework dependency.
- **Deferred database decision via interface**: putting all data-access methods behind an interface (e.g., `WikiPage`) lets you stub/mock it, then implement it with progressively more permanent backends (in-memory hash table → flat files → optionally MySQL) without ever touching business logic.
- **Asymmetric dependency (ReSharper/Visual Studio example)**: when a lower-value/plugin component's source depends on a higher-value component's source, but not vice versa, the higher-value component is fully immune to changes in the plugin, while the plugin remains fully exposed to changes in the core — the desired relationship between business rules and everything else.
- **Three-tier "architecture" as topology, not architecture**: the author's footnote distinguishes physical deployment topology (three-tier) from actual architecture — a caution against premature topology commitments.

## Mental Models
- Use "does the business rule need to know this?" as the litmus test for every technology decision (database engine, web framework, REST vs. RPC, DI framework) — if the answer is no, put a boundary and an interface between the business rule and that decision, and defer the decision.
- Treat the database as "a tool the business rules use indirectly," never as "the embodiment of the business rules" — schema/query-language details belong entirely on the detail side of the boundary.
- Think of every replaceable component (UI framework, DB engine, message bus) as a plugin: the plugin depends on the core; the core never depends on the plugin. This produces the same asymmetric immunity seen between ReSharper (dependent, replaceable) and Visual Studio (independent, stable).
- Draw boundaries proactively at axes of change, even before you know exactly what's on the other side — this is what let FitNesse defer the MySQL decision for 18 months at zero cost, and let company P's failure (see below) have been avoided.

## Anti-patterns
- **Premature architecture commitment to a topology (Company P)**: adopting a rich three-tier "architecture" (GUI/middleware/DB tiers with full serialization/marshaling between them) before it was ever operationally necessary — the company never once deployed to a real server farm, yet paid the full multiplied development cost (three tiers × instantiations, four message protocols, eight protocol handlers) for every simple feature, forever.
- **Premature enterprise SOA adoption (Company W)**: imposing a full service-oriented architecture with a ServiceRegistry, dozens-of-fields messages, and BPEL orchestration on a small fleet-management operation — turned a trivial "add a contact to a sales record" change into a multi-service, multi-message, multi-redeploy ordeal, and made testing require standing up the entire service mesh.
- **Believing the GUI is "the system"**: leads stakeholders/developers to build and validate against the interface first, coupling the domain model to a specific IO technology it should never depend on.
- **Believing the database is "the embodiment of the business rules"**: a widely held but misguided belief per the author — it inverts the correct dependency direction and prevents deferring/changing the persistence technology.

## Reference Tables
No comparison/decision tables in this chapter.

## Worked Example
**FitNesse's deferred database decision:** the team defined all data access through a `WikiPage` interface before deciding on any storage technology. For the first ~3 months they used `MockWikiPage` (stubbed methods) while building wiki-text-to-HTML rendering — no storage needed yet. When storage became necessary, they implemented `InMemoryPage` (an in-RAM hash table), which let them build and ship a full working version of FitNesse (page creation, linking, formatting, running FIT tests) for about a year — minus persistence. When persistence was finally needed, they implemented `FileSystemWikiPage`, writing the hash tables to flat files — and three months later concluded flat files were "good enough," abandoning MySQL entirely. Later, a customer who specifically wanted MySQL simply wrote a `MySqlWikiPage` derivative in a day, without touching any business logic, because the interface boundary had been in place from the start. Net effect: 18 months without a running database meant no schema issues, no query issues, no DB server/connection/password issues, and fast tests — all because the boundary between business rules and the database (`WikiPage` interface, arrow pointing from `DatabaseAccess`/implementations toward the business-rules-owned interface) was drawn early and honored throughout.

## Key Takeaways
1. Draw boundaries at axes of change (SRP applied to architecture): separate anything that changes at a different rate/for a different reason.
2. Put interfaces for details (DB, UI, frameworks) inside the business-rules component; put concrete implementations in separate components that depend on those interfaces — never the reverse.
3. Defer technology decisions (database engine, web framework, DI container, REST vs. SOA) as long as possible; the longer you wait, the more information you'll have and the more experiments you can run.
4. Even if a technology decision has organizationally "already been made," architect as though it hadn't — keep the option to change or defer it.
5. The IO/GUI is irrelevant to the domain model — the model should be fully functional and testable without any UI attached.
6. Premature commitment to a topology or framework (three-tier, full SOA) can permanently multiply the cost of every future feature, even if the anticipated scale (server farms) never materializes.

## Connects To
- **Ch 18 (Boundary Anatomy)**: the immediate follow-on — once you know where to draw lines, this chapter's sequel covers the physical/runtime forms those boundaries can take (monolith, deployment component, local process, service).
- **SRP (Single Responsibility Principle)**: explicitly named as "where to draw our boundaries."
- **DIP (Dependency Inversion Principle) / SAP (Stable Abstractions Principle)**: the plugin pattern is explicitly an application of both — dependency arrows point from low-level details to high-level abstractions.
- **Ch 15 (What Is Architecture?)**: continues the "leave options open, defer details" theme with concrete boundary mechanics and real-world case studies.
