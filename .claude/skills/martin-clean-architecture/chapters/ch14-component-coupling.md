# Chapter 14: Component Coupling

## Core Idea
Three principles govern how components should depend on each other — ADP forbids cycles, SDP says depend toward stability, and SAP says stable components must also be abstract — and together SDP+SAP form the component-level equivalent of the Dependency Inversion Principle, with two quantitative metrics (I, A) and a derived distance metric (D) to measure conformance.

## Frameworks Introduced
- **ADP (Acyclic Dependencies Principle)**: "Allow no cycles in the component dependency graph."
  - When to use: always — cyclic component dependencies cause the "morning after syndrome" (your code breaks because someone else changed a component you depend on, and it depends back on yours).
  - How: keep the dependency graph a DAG. Break any cycle with (1) Dependency Inversion Principle — create an interface for the needed methods and put it in the depended-upon component so the dependency inverts, or (2) extract a new component containing the shared classes that both original components now depend on.
- **SDP (Stable Dependencies Principle)**: "Depend in the direction of stability."
  - When to use: whenever wiring dependencies between components, especially between volatile and non-volatile ones.
  - How: never let a component you intend to keep easy-to-change (volatile) be depended upon by a component that is hard to change (stable) — dependents make a component resistant to change regardless of the code's own design intent. Fix violations via DIP: extract an interface into a new, very stable abstract component (I=0) that both sides depend on.
- **SAP (Stable Abstractions Principle)**: "A component should be as abstract as it is stable."
  - When to use: when deciding where high-level policy should live.
  - How: stable components (I=0, many dependents, hard to change) should consist mainly of interfaces/abstract classes so they can still be extended without modification (OCP). Unstable components (I=1) should be concrete, since their instability makes concrete code easy to change safely.

## Key Concepts
- **Fan-in**: count of classes outside a component that depend on classes inside it.
- **Fan-out**: count of classes inside a component that depend on classes outside it.
- **I (Instability)**: `I = Fan-out / (Fan-in + Fan-out)`, range [0,1]. I=0 = maximally stable (responsible, independent); I=1 = maximally unstable (irresponsible, dependent).
- **A (Abstractness)**: `A = Na / Nc` where Na = number of abstract classes/interfaces, Nc = total classes in component. Range [0,1].
- **The Main Sequence**: the line connecting (1,0) and (0,1) on the A/I graph — the locus of ideal component positions (maximally distant from both zones of exclusion).
- **Zone of Pain**: the region near (0,0) — highly stable AND concrete — components here are rigid: hard to change and can't be extended. Only tolerable for genuinely nonvolatile concrete things (e.g., a String utility library or a database schema, though schemas are volatile and thus painful).
- **Zone of Uselessness**: the region near (1,1) — maximally abstract with no dependents — leftover abstract classes nobody implements.
- **D (Distance from Main Sequence)**: `D = |A + I - 1|`, range [0,1]. 0 = on the Main Sequence (ideal); can be used per-component or aggregated (mean/variance) across a design, and tracked over time/releases to catch architectural drift.
- **Abstract component**: a component containing only interfaces, no executable code — common and necessary in statically typed languages to create a maximally stable (I=0) dependency target.
- **Morning after syndrome**: the failure mode ADP prevents — your working code breaks overnight because someone changed a dependency, made worse/impossible to resolve cleanly when dependencies cycle.

## Mental Models
- Think of I as "how much work is required to change this component" — driven purely by dependency count, not by size/complexity/clarity.
- Use the Main Sequence like a design code-smell detector: plot components on the A/I graph; anything far from the line (high D) is either a rigid trap (Zone of Pain) or dead weight (Zone of Uselessness) and deserves a closer look.
- SDP + SAP together = DIP for components: DIP is binary at the class level (abstract or not), but at the component level a component can be *partially* abstract and partially stable — dependencies still flow toward abstraction overall.
- Treat cycles like technical debt with compounding interest: as a system grows, cycle-breaking (via new components) is not a one-time fix but an ongoing "jitter" of the dependency graph — component structure is not designed top-down, it evolves bottom-up as SRP/CCP/CRP/ADP pressures accumulate.

## Anti-patterns
- **Cyclic component dependencies**: makes it impossible to build/test/release components in isolation; effectively merges cyclic components into one giant component for release purposes, causing "morning after syndrome" across all their developers.
- **Hanging a dependency on a volatile component**: a developer in a "stable" component depending on a "flexible" one destroys the flexible component's intended ease-of-change — violates SDP even though no source in the flexible component changed.
- **Designing the component structure top-down before any code exists**: fails because you don't yet know common-closure groupings, reusable elements, or where cycles will emerge; component dependency diagrams describe buildability/maintainability, not the application's function, so they can't be front-loaded.
- **Putting high-level policy in unstable, concrete components**: makes core business/architectural decisions volatile and easy to accidentally break.
- **Overusing the weekly/biweekly build as a substitute for managing dependencies**: postpones but does not solve the morning-after problem; integration burden keeps growing until it swallows the week.

## Code Examples
No code samples in this chapter (diagram-driven, conceptual).

## Reference Tables
| Metric | Formula | Range | Meaning at 0 | Meaning at 1 |
|---|---|---|---|---|
| I (Instability) | Fan-out / (Fan-in + Fan-out) | [0,1] | Maximally stable: responsible, independent | Maximally unstable: irresponsible, dependent |
| A (Abstractness) | Na / Nc | [0,1] | No abstract classes/interfaces | Nothing but abstract classes/interfaces |
| D (Distance) | \|A + I − 1\| | [0,1] | On the Main Sequence (ideal) | Maximally far from ideal (either zone of exclusion) |

| Zone | Position | Problem |
|---|---|---|
| Zone of Pain | near (0,0) | stable + concrete = rigid, hard to change, can't extend (tolerable only if genuinely nonvolatile, e.g. String) |
| Zone of Uselessness | near (1,1) | abstract + no dependents = useless, unimplemented leftovers |
| Main Sequence | line from (1,0) to (0,1) | ideal — component's abstractness matches its stability |

## Worked Example
Components `Entities`, `Database`, `Interactors`, `Presenters`, `View`, `Controllers`, `Authorizer`, `Main` form a clean DAG: Entities/Database/Interactors sit at the bottom (build/release first), then Presenters, View, Controllers, Authorizer, and finally Main (built/released last, and releasing it affects nothing else). A new requirement makes `User` (in Entities) use `Permissions` (in Authorizer) — but Authorizer already (transitively) depends on Entities, so this creates a cycle. Now Database, Entities, Authorizer, and Interactors are effectively fused into one release unit: testing Entities alone requires building Authorizer and Interactors too, and there's no longer a well-defined build order. Fix: either (1) DIP — define the interface `User` needs inside Entities, and have Authorizer implement it, inverting the dependency back to Entities→Authorizer becoming Authorizer→Entities-interface; or (2) extract a new component holding the shared class(es) that both Entities and Authorizer depend on, restoring the DAG.

For SDP: component `Stable` depends on component `Flexible` (which was designed to be easy to change) because class `U` in Stable uses class `C` in Flexible. This violates SDP — I(Stable) is much lower than I(Flexible), yet Stable now blocks Flexible's changes. Fix: create a new abstract component `UServer` containing interface `US` declaring the methods `U` needs; `C` implements `US`. Now both Stable and Flexible depend on UServer (I=0, maximally stable), Flexible keeps I=1 (unstable, as intended), and dependencies flow toward decreasing I.

## Key Takeaways
1. Keep the component dependency graph a strict DAG — detect and break cycles immediately via DIP (new interface) or extracting a shared component.
2. Never let a component you want to remain easy-to-change be depended on by more-stable components; if it must be, insert an abstract interface component between them.
3. Stable components should be made of interfaces/abstract classes (high A) so they remain extensible without modification — this is how you keep I=0 components from becoming architecturally rigid.
4. Use Fan-in/Fan-out to compute I, and abstract-class ratio to compute A, then use D to flag components that don't fit the Main Sequence — track D over releases to catch architectural drift early.
5. Component structure is not designed up front; it evolves and "jitters" as SRP/CCP/CRP/ADP pressures accumulate through the project's life.
6. High-level business/architectural policy belongs in stable, abstract components — never in unstable, concrete ones.

## Connects To
- **Ch 13**: Component Cohesion — decides what goes *inside* a component; Ch 14 decides how those components *depend* on each other.
- **DIP (Dependency Inversion Principle)**: the class-level analog to what SDP+SAP achieve at the component level; used directly to break dependency cycles.
- **OCP (Open Closed Principle)**: SAP's justification for making stable components abstract — extend without modifying.
- **Ch 27 "Services: Great and Small"**: referenced footnote on "The Kitty Problem," related to maintainability-vs-reusability tension.
