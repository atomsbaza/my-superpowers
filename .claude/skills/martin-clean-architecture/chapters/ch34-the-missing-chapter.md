# Chapter 34: The Missing Chapter

## Core Idea
By Simon Brown: good architectural intent (layers, boundaries, dependency rules) can be completely destroyed by sloppy implementation details — specifically, overuse of the `public` access modifier turns any of the four organizational styles (package by layer, by feature, ports and adapters, by component) into the exact same, unencapsulated structure; the compiler, not code review discipline, should enforce your architecture.

## Frameworks Introduced
- **Package by Layer**: horizontal slicing by technical role (web / service / persistence), "strict layered architecture" only depends on the next lower layer.
  - When to use: quick starts, small systems; standard in most tutorials/books.
  - How: separate packages for controllers, services (interface + impl), repositories (interface + impl).
- **Package by Feature**: vertical slicing by domain concept/feature/aggregate root, all related types in one package.
  - When to use: when the codebase should "scream" its business domain and you want all code for one feature co-located.
  - How: refactor package-by-layer into a single package per feature (e.g., all `Orders`-related classes together).
- **Ports and Adapters** (hexagonal / boundaries-controllers-entities): domain-focused "inside" independent of technical "outside" (UI, DB, third-party integrations); outside depends on inside, never the reverse.
  - When to use: when you want the domain expressed in ubiquitous language, fully isolated from delivery/persistence mechanisms.
  - How: put domain types (e.g., `Orders`, not `OrdersRepository`) in an inside package; outside packages (web, persistence) depend inward only.
- **Package by Component**: Simon Brown's own preferred hybrid — bundle all responsibilities for one coarse-grained component (business logic + persistence) behind a single clean interface, in one package.
  - When to use: monolith that should behave like a stepping stone to microservices; want a single entry point per business capability.
  - How: create one component interface (e.g., `OrdersComponent`) per capability; keep its internal business/persistence separation as an implementation detail invisible to consumers.

## Key Concepts
- **Relaxed layered architecture**: a layered design where layers are allowed to skip their adjacent neighbor (e.g., a controller directly injecting a repository, bypassing the service layer) — sometimes intentional (CQRS), often an accidental erosion of the architecture.
- **Organization vs. encapsulation**: packages that only group code (all types `public`) provide organization but no encapsulation; packages that restrict visibility (package-private/`internal`) provide real architectural enforcement.
- **The Périphérique anti-pattern**: named after the Paris ring road; when all "outside"/infrastructure code sits in one source tree, infrastructure code in one area (e.g., a web controller) can bypass the domain and directly call another infrastructure area (e.g., a repository) — a risk specific to the simplified two-source-tree version of ports and adapters.
- **C4 model**: Simon Brown's own hierarchical model (containers → components → classes) for describing software structure; his definition of "component" ("a grouping of related functionality behind a nice clean interface, residing inside an execution environment") differs from Uncle Bob's ("smallest deployable unit, e.g. a jar file").
- **Published vs. public types**: module systems (OSGi, Java 9 modules) let you mark types `public` within a module while publishing only a subset externally — a finer-grained decoupling mechanism than plain package visibility.

## Mental Models
- Think of access modifiers as **the only enforcement that survives deadline pressure**: "we enforce it through code review" degrades under schedule stress; `public`/package-private/`internal` is enforced by the compiler every single build.
- Use the **"if everything is public, all four styles are identical"** test: draw the dependency diagram for your chosen style, then ask which arrows would still be prevented if every type were `public` — if none, your architecture exists only in documentation, not in code.
- Think of source-tree splitting (separate Maven/Gradle/MSBuild modules per component) as a **stronger boundary than packages**, at the cost of build complexity — reserve it for boundaries you actually need enforced at compile time.

## Anti-patterns
- **Marking all types `public` by reflex**: eliminates any real difference between package-by-layer, package-by-feature, ports-and-adapters, and package-by-component — they become syntactically identical, indistinguishable "big balls of mud" waiting to happen.
- **Relying on static-analysis tools or code review alone to enforce layer rules**: fallible, slow feedback loop; violations ("relaxed layering") creep in under deadline pressure.
- **The Périphérique anti-pattern**: collapsing all infrastructure into a single "outside" source tree without access-modifier discipline, allowing infrastructure-to-infrastructure calls that bypass the domain.

## Reference Tables
| Strategy | Slicing | What's public (minimum) | Key strength | Key weakness |
|---|---|---|---|---|
| **Package by Layer** | Horizontal, by technical role | `OrdersService`, `OrdersRepository` interfaces (impls can be package-private) | Simple, fast to start, matches most tutorials | Doesn't "scream" the business domain; two unrelated domains look identical; easy to skip layers |
| **Package by Feature** | Vertical, by domain concept/feature | Only the entry-point type (e.g., `OrdersController`); everything else package-private | Reveals business domain in top-level structure; all code for a feature is co-located | Nothing outside the package can reach feature internals except through the one public entry point (may be too restrictive) |
| **Ports and Adapters** | Inside (domain) vs. outside (infrastructure) | `OrdersService`, `Orders` interfaces (inbound dependencies force public); impls package-private | Domain fully isolated from delivery/persistence tech; domain named in ubiquitous language | "Périphérique" risk if outside code lives in one flat source tree without modifier discipline |
| **Package by Component** | By coarse-grained business capability | Only the component interface (e.g., `OrdersComponent`) | Single entry point per capability; stepping stone to microservices; internal biz/persistence split hidden | Requires discipline to keep the interface genuinely coarse-grained; less standard/less documented than the other three |

## Worked Example
Running example across the chapter: an online bookstore's "view order status" use case, implemented with `OrdersController` (web), `OrdersService`/`OrdersServiceImpl` (business logic), `OrdersRepository`/`JdbcOrdersRepository` (persistence). Brown shows this same use case coded four ways (layer, feature, ports-and-adapters, component), and then demonstrates the failure mode: a new team member, wanting to move fast, discovers the existing `OrdersRepository` interface and dependency-injects it directly into `OrdersController`, bypassing `OrdersService` entirely — the dependency arrows still point "downward" so a naive acyclic-graph check passes, but the business-logic layer (which might enforce authorization) has been silently circumvented. This is the "relaxed layered architecture" failure. The fix demonstrated: apply the most restrictive access modifier possible to each type per style (per the reference table above) so the compiler — not reviewer vigilance — makes the bypass impossible to compile.

## Key Takeaways
1. Choosing an organizational style (layer/feature/ports-and-adapters/component) is necessary but not sufficient — implementation details (access modifiers) determine whether the style is real or cosmetic.
2. Default to the most restrictive access modifier for every type; only the type(s) with genuine inbound cross-package dependencies should be `public`.
3. Watch for "relaxed layering" — an inbound dependency quietly skipping a layer (e.g., controller → repository) — especially when a layer is responsible for cross-cutting concerns like authorization.
4. Prefer compiler-enforced boundaries (access modifiers, module systems, separate source trees/modules) over documentation, code review, or post-hoc static analysis for architecture enforcement.
5. In simplified two-tree ports-and-adapters (domain vs. infrastructure), watch specifically for the Périphérique anti-pattern — infrastructure-to-infrastructure shortcuts bypassing the domain.
6. Package by Component (Brown's own preference) treats each business capability as a single clean-interfaced unit and is presented as a natural stepping stone toward microservices.

## Connects To
- **Ch 33 (Case Study: Video Sales)**: this chapter picks up immediately after that case study to address exactly how to implement the component boundaries described there in real code.
- **Ch 12–14 (Component Principles: REP, CCP, CRP)**: the four organizational styles here are concrete answers to "how do I actually draw the package/module lines" that those principles argue for abstractly.
- **Dependency Rule (Ch 22)**: "relaxed layering" is a direct, in-the-wild violation of the Dependency Rule, made possible specifically by over-permissive access modifiers.
