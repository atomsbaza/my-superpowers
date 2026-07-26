# Clean Architecture: Patterns Reference

## Plugin Architecture (Dependency Inversion via Polymorphism)
**When to use**: Any time a high-level module (business rules) must not depend on a low-level module (UI, database, IO, framework) that it calls.
**How**: Insert an interface owned by the high-level module; the low-level module implements it. Source-code dependency points opposite to runtime flow of control. The low-level component becomes a swappable plugin — like UNIX device drivers implementing `open/close/read/write/seek`.
**Trade-offs**: Requires an extra interface/seam for every inverted dependency; pays off as independent deployability/developability and the ability to defer or swap implementations without touching policy.

## The Dependency Rule / Clean Architecture Circles
**When to use**: As the default target shape for any nontrivial system — Entities, Use Cases, Interface Adapters, Frameworks & Drivers as concentric rings.
**How**: Source-code dependencies point only inward. Nothing in an inner ring may name a class, function, variable, or data format from an outer ring. When control must flow outward, define an "output port" interface in the inner ring and implement it outward (Dependency Inversion at the boundary). Ring count is schematic; the rule is not.
**Trade-offs**: Extra indirection (interfaces, DTOs) at every crossing; buys framework/UI/DB independence and testability without infrastructure running.

## Humble Object Pattern
**When to use**: Any boundary where one side is inherently hard to unit test (GUI rendering, raw DB access, raw service I/O).
**How**: Split behavior into a "humble" module holding only mechanical, untestable residue, and a "testable" sibling holding all logic/decisions. Recurs as Presenter/View, Interactor/Gateway, and Service Listener/external service.
**Trade-offs**: Adds a class per split; concentrates untestable code into the smallest possible surface, making almost everything else verifiable.

## Presenter / View-Model Split
**When to use**: Building any UI (web, thick client, console).
**How**: Presenter (testable) converts application data (Date, Currency, etc.) into a plain ViewModel of strings/booleans/enums, precomputing formatting, red/black flags, grayed-out states. View (humble) does nothing but copy ViewModel fields onto the screen.
**Trade-offs**: More classes/objects per screen; eliminates all display logic from the untestable View layer.

## Screaming Architecture
**When to use**: Deciding the top-level directory/package layout of any application.
**How**: Top-level structure should announce the business domain and use cases ("Health Care System"), not the framework or delivery mechanism ("Rails app"). Frameworks, DB, and web are details decided later; a reader should learn all use cases without knowing if it's web, console, or thick client.
**Trade-offs**: Resists conventional framework scaffolding/tutorials; pays off in domain clarity and deferred technology lock-in.

## The Main Component as a Plugin
**When to use**: Bootstrapping any application, especially ones needing multiple configurations (Dev/Test/Prod, per-customer, per-jurisdiction).
**How**: Treat `Main` as the outermost, "dirtiest" component — it creates Factories/Strategies, resolves DI graphs, and hands control to high-level policy, but nothing depends on it. Use factories with string class names (not direct references) so `Main` isn't forced to recompile when concrete classes change. Swap entire `Main` implementations per environment instead of branching inside one.
**Trade-offs**: Some duplication across `Main` variants; keeps environment/config detail fully out of business logic.

## Package by Component
**When to use**: A monolith intended as a stepping stone toward microservices, wanting one clean entry point per business capability.
**How**: Bundle all responsibilities for one capability (business logic + persistence) behind a single public interface (e.g., `OrdersComponent`) in one package; keep the internal business/persistence split as package-private implementation detail.
**Trade-offs**: Less standard/documented than layer-by-layer; requires discipline to keep the interface coarse-grained, but resists the "relaxed layering" bypass that plain layered packages allow.

## Compiler-Enforced Boundaries (Access Modifier Discipline)
**When to use**: Any of the four organizational styles (by layer, by feature, ports and adapters, by component) — the style only matters if enforced.
**How**: Mark every type the most restrictive visibility possible; only genuine cross-package entry points are `public`. This prevents "relaxed layering" (e.g., a controller injecting a repository directly, skipping the service layer that enforces authorization).
**Trade-offs**: None significant — cost is discipline, not code; without it, all four styles degrade into the same unencapsulated structure at runtime under deadline pressure.

## Partial Boundaries
**When to use**: When a full architectural boundary is anticipated but not yet justified.
**How**: Three cheaper variants, decreasing in cost and protection — (1) *Skip the Last Step*: build full reciprocal interfaces/DTOs but deploy as one component; (2) *One-Dimensional Boundary (Strategy)*: single interface, one-directional dependency inversion only; (3) *Facade*: a class exposing service methods with no interface at all, leaving a full transitive dependency.
**Trade-offs**: Cheaper than a full boundary but erodes without deployability pressure forcing discipline; revisit periodically or accept costly re-separation later.

## Database Gateways / Data Mappers
**When to use**: Keeping SQL and persistence-framework specifics out of the use-case layer.
**How**: Define a gateway interface near the use-case layer (e.g., `getLastNamesOfUsersWhoLoggedInAfter(Date)`); implement it (the humble half, using actual SQL or a "data mapper" — the accurate name for what's commonly called an ORM) in the database layer. Interactors depend only on the interface.
**Trade-offs**: An interface per query pattern; makes interactors testable via stubs and the database technology fully swappable.

## HAL / PAL / OSAL Layering (Clean Embedded Architecture)
**When to use**: Embedded systems needing to survive hardware/OS churn and support off-target testing.
**How**: Insert a Hardware Abstraction Layer between firmware and software, shaped by what software needs (e.g., `Indicate_LowBattery()`), never by raw hardware capability; a Processor Abstraction Layer confines compiler/silicon-specific extensions; an OS Abstraction Layer isolates RTOS/OS APIs. Replace scattered `#ifdef BOARD_V2` blocks with a single HAL interface resolved at link/runtime.
**Trade-offs**: Extra layers of indirection at the hardware edge; the payoff is code testable off-target and portable across processors/RTOS vendors.

## Testing API (Test Boundary)
**When to use**: Verifying business rules without depending on a volatile UI or expensive resources.
**How**: Build a dedicated API — a superset of the interactors/interface adapters the real UI uses — granting "superpowers" (bypass auth, bypass DB cost, force state). Route business-rule test verification through it instead of driving the GUI. Isolate the superpowered implementation into its own deployable component if dangerous in production.
**Trade-offs**: Extra API surface to maintain; prevents the Fragile Tests Problem where UI/navigation changes break hundreds of unrelated tests and make developers afraid to refactor.

## Segregation of Mutability / Event Sourcing
**When to use**: Designing for concurrency without ad hoc locking.
**How**: Push as much logic as possible into immutable components; isolate the smaller mutable remainder behind transactional-memory-style protection (compare-and-swap/retry). Event Sourcing takes this further: persist only append-only transactions (CR, never U/D) and derive current state by replay, optionally from periodic snapshots.
**Trade-offs**: Event sourcing costs storage/replay compute; both eliminate entire classes of race conditions and concurrent-update bugs by construction rather than by locking discipline.

## Component Cohesion Balance (REP / CCP / CRP)
**When to use**: Deciding which classes belong together in a component.
**How**: REP (Reuse/Release Equivalence) — only group classes that share a reuse theme and can be versioned/released together. CCP (Common Closure) — group classes that change for the same reasons at the same time, minimizing redeploy scope (SRP at the component level). CRP (Common Reuse) — never force consumers to depend on classes they don't use (ISP at the component level). Favor CCP early in a project's life; shift toward REP/CRP as reuse by others increases.
**Trade-offs**: The three principles actively conflict (a tension triangle); there is no permanent correct answer — component boundaries should jitter as the project matures.

## Component Coupling (ADP / SDP / SAP + Main Sequence)
**When to use**: Deciding how components should depend on each other and diagnosing structural rigidity.
**How**: ADP — keep the component dependency graph acyclic; break cycles via a new interface (DIP) or an extracted shared component. SDP — depend in the direction of increasing stability (I = Fan-out/(Fan-in+Fan-out)); never let a stable component depend on a volatile one. SAP — stable components should be abstract (A = ratio of abstract classes) so they remain extensible without modification. Plot components on the A/I graph; D = |A+I-1| measures distance from the ideal Main Sequence.
**Trade-offs**: Requires ongoing measurement and refactoring as the graph evolves; components near (0,0) are rigid (Zone of Pain), near (1,1) are dead weight (Zone of Uselessness).

## Abstract Factory (DIP Object Creation)
**When to use**: Any time a volatile concrete class must be instantiated inside code that should otherwise depend only on abstractions.
**How**: Define an abstract factory interface with a creation method (e.g., `ServiceFactory.makeSvc()`); implement it in a concrete factory instantiated only inside `Main`. The high-level `Application` calls the factory, never `new`s the concrete class directly.
**Trade-offs**: One extra interface + concrete factory per creation seam; concentrates the unavoidable concrete-instantiation dependency into a single quarantined location instead of scattering it.

## Two-Dimensional Component Separation (Actor × Level)
**When to use**: Architecting a system with multiple distinct actors (user/stakeholder groups), from scratch.
**How**: First identify actors (sources of change) and derive each actor's use cases (SRP applied at the system level); factor out abstract use cases when concrete ones are nearly identical. Then separate components along a second, independent axis — Dependency Rule level (views/presenters/interactors/controllers) — so every actor-specific slice still respects inward dependency direction. Keep deployment-unit grouping (how many jars) as a separate, later, reversible decision.
**Trade-offs**: More components at design time than a naive single-axis split; isolates both "which actor" and "which policy level" changes independently, and lets you defer final packaging granularity.

## Request/Response Models Crossing Boundaries (DTOs)
**When to use**: Every time data moves across an architectural boundary (Controller → Interactor, Interactor → Presenter, service-to-service).
**How**: Define plain, dependency-free data structures shaped for the receiving (inner) side — never derive them from framework types (e.g., `HttpRequest`) and never pass Entity objects or ORM row structures directly across a boundary.
**Trade-offs**: Requires mapping/conversion code at each crossing; prevents "tramp data" and keeps inner circles ignorant of outer-circle formats, so either side can change independently.
