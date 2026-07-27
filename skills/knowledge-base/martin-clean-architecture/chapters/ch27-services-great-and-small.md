# Chapter 27: Services: Great and Small

## Core Idea
Services — including micro-services — are not, by themselves, an architecture: they are just function calls across process/platform boundaries, and unless their internal design follows the Dependency Rule and SOLID principles, they remain just as coupled by shared data and cross-cutting concerns as any monolith, while pretending to be decoupled.

## Frameworks Introduced
- **Services-are-not-architecture**: "The architecture of a system is defined by boundaries that separate high-level policy from low-level detail and follow the Dependency Rule. Services that simply separate application behaviors are little more than expensive function calls, and are not necessarily architecturally significant."
  - When to use: Whenever evaluating whether a proposed service/micro-service split constitutes real architecture or just physical distribution of function calls.
  - How: Ask whether the boundary between services separates high-level policy from low-level detail and follows the Dependency Rule; if it merely partitions behavior without that discipline, it's not an architectural boundary — it's an implementation/deployment detail.
- **Component-based services**: Design each service internally with SOLID-structured components (abstract base classes + pluggable derivative jar/Gem/DLL components) so new features extend the service via the Open-Closed Principle instead of requiring a redeploy of the whole service.
  - When to use: When a cross-cutting feature (like the Kitty problem) would otherwise require changing every service in a service-oriented system.
  - How: Extract feature-specific logic into abstract base classes in the service; add new features as separate loadable components (e.g., new jar files) that extend those base classes via Template Method or Strategy, loaded dynamically without changing existing components.

## Key Concepts
- **The Decoupling Fallacy**: The mistaken belief that services are strongly decoupled just because they run in separate processes — in reality they remain coupled through shared data records and the required agreement on how to interpret shared fields.
- **The Fallacy of Independent Development and Deployment**: The mistaken belief that dozens/hundreds/thousands of services can always be independently developed and deployed — true only to the extent they aren't coupled by data or cross-cutting behavior; monoliths and component-based systems can scale just as well.
- **Cross-cutting concern**: A feature or requirement (like the Kitty problem's kitten-delivery feature) that touches every functional service/component in a system, exposing hidden coupling that a purely functional/service decomposition can't isolate.
- **The Kitty Problem**: The chapter's central case study — a taxi-aggregator system built from independently-owned micro-services (TaxiUI, TaxiFinder, TaxiSelector, TaxiDispatcher) that all must change simultaneously when a new cross-cutting feature (kitten delivery) is introduced, disproving the claimed independence.
- **Template Method / Strategy (as decoupling mechanism)**: Design patterns used to let new feature components (e.g., `Kittens`) override abstract base-class behavior from existing components (e.g., `Rides`) without modifying them, preserving the Open-Closed Principle across service boundaries.
- **Boundaries run through services, not between them**: The chapter's key structural claim — architectural boundaries are defined by the internal component design of a service, not by the fact that a service exists as a separately deployed process.

## Mental Models
- Think of services the way you think of function calls: some function calls are architecturally significant (they cross a boundary separating policy from detail) and most aren't — the same split applies to services.
- Use "how many of these services have to change to add this one new cross-cutting feature?" as a real-world stress test of claimed service independence — if the answer is "all of them," the services are coupled regardless of being separately deployed.
- Think of a well-designed service as itself containing an architecture (components + Dependency Rule) — the service is a container for boundaries, not a boundary itself.

## Anti-patterns
- **Treating service decomposition as automatically architecturally significant**: Assuming that because two behaviors run in different processes they are decoupled, when they are actually tightly coupled by a shared data record's format and semantics.
- **Functional decomposition into services without SOLID internals**: Splitting a system into services purely along functional lines (TaxiUI / TaxiFinder / TaxiSelector / TaxiDispatcher) makes the system maximally vulnerable to any cross-cutting feature, because there's no polymorphic seam for new behavior to plug into.
- **Assuming service count scales team independence linearly**: Believing more micro-services automatically means more independently-operating teams, when coupling through shared data/behavior forces coordinated development and deployment regardless of process boundaries — "the number of micro-services will be roughly equal to the number of programmers" (footnote, wry warning against over-fragmentation).

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
A taxi-aggregator system is built as four micro-services — `TaxiUI` (customer-facing), `TaxiFinder` (matches available taxis), `TaxiSelector` (applies customer criteria), `TaxiDispatcher` (books the taxi) — each owned by a separate small team, believed to be independently developable and deployable. Marketing then requests a cross-cutting "kitten delivery" feature: drivers allergic to cats must be excluded, customers with cat allergies must avoid vehicles used for kitten delivery in the last 3 days, and only participating taxi suppliers qualify. Implementing this touches *every* service in the diagram, disproving independence (the Kitty Problem). The object-oriented fix: extract ride-specific logic into a `Rides` component and the new logic into a `Kittens` component, both overriding shared abstract base classes (via Template Method/Strategy) that preserve the original service structure. Only `TaxiUI` needs a code change to route to the new feature; `Kittens` is added as a new deployable unit (jar/Gem/DLL) loaded dynamically — the same pattern can be applied inside each *service* individually, giving each service its own internal component architecture that follows the Dependency Rule, so cross-cutting features become new pluggable components rather than forced changes to every service.

## Key Takeaways
1. Never assume a service boundary is an architectural boundary — check whether it separates high-level policy from low-level detail via the Dependency Rule; otherwise it's just a distributed function call.
2. Watch for cross-cutting concerns as the real test of service independence: if one new feature forces changes across many services, they were coupled by shared data/behavior all along (the Decoupling Fallacy).
3. Design each service's internals with SOLID structure (abstract base classes + pluggable derivative components) so new features can be added as loadable extensions (Open-Closed Principle) instead of triggering a redeploy of the whole service.
4. Architectural boundaries run *through* services (dividing them into components), not *between* services — put the design effort into each service's internal component architecture.
5. Don't over-fragment services assuming team count scales with service count — coordinate development/deployment wherever real data or behavioral coupling exists, regardless of process boundaries.

## Connects To
- **Ch 25 (Layers and Boundaries)**: The micro-service boundary example (`MoveManagement`/`PlayerManagement`) introduced there is directly revisited here with the caveat that most service splits are not architecturally significant.
- **Ch 8 (Open-Closed Principle)**: Component-based services rely on OCP to let new feature components extend existing ones without modification.
- **SOLID principles**: The chapter explicitly invokes SOLID (especially the Dependency Rule and OCP) as the mechanism for making service internals genuinely decoupled, in contrast to the naive assumption that service boundaries alone provide decoupling.
