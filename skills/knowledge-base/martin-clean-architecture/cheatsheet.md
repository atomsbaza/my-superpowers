# Clean Architecture Cheatsheet — Making the Call Like Uncle Bob

One page for active decisions. Not a glossary — every line answers "what do I DO."

## 1. Where does this boundary go? (decision rules)

- **Draw a boundary only where there's a real axis of change** — two things changing at different rates/for different reasons, observed or strongly anticipated. Never speculatively (Ch17, Ch25). If nobody can name the second rate-of-change, there's no boundary yet.
- **Test**: "does the higher-level thing need to know this?" If no → put an interface on the high-level side, implementation on the low-level side, regardless of physical form (Ch17,19).
- **A service/microservice boundary is architectural only if it separates policy from detail AND follows the Dependency Rule.** A service split that's purely functional (TaxiUI/TaxiFinder/TaxiSelector) is just an expensive function call — proven by the "Kitty test": if one new cross-cutting feature forces every service to change, they were never decoupled (Ch27).
- **Boundary strength ladder — pick the weakest one that satisfies your *current* isolation need**: monolith (source-level) → deployment component → local process → service. Higher rungs cost latency + ops complexity; only climb when real operational/dev/deploy pressure demands it, and be willing to climb back down (Ch16,18).
- **Can't decide yet whether you'll need a boundary?** Use a partial boundary, cheapest-to-strongest: Facade (no protection, transitive dep remains) → One-Dimensional/Strategy interface (one-way protection) → Skip-the-Last-Step (full design, shared deployment — protection erodes without deploy pressure forcing discipline) (Ch24).
- **Watch-and-wait, not up-front**: note candidate axes as they appear; add the boundary at the point where implementation cost < cost of continuing to ignore it. Review this tradeoff repeatedly, not once (Ch25).

## 2. Which layer does this class belong in?

| Ask | If yes → | Level |
|---|---|---|
| Would this rule make/save the business money even done manually with pen and paper? | **Entity** | Highest — zero knowledge of anything outward |
| Does this rule only make sense because the system is automated (screen flow, gating, validation order)? | **Use Case** | Depends on Entities only |
| Does this convert data between the use case's shape and an external agency's shape (DB row↔domain, HTTP↔DTO)? | **Interface Adapter** (Controller/Presenter/Gateway) | Depends on Use Cases |
| Is this glue for a specific DB/web framework/library? | **Frameworks & Drivers** | Outermost — depends on everything inward, nothing depends on it |

Data crossing any boundary must be a plain struct/DTO owned by the *inner* side's shape — never an Entity, never a framework-native object (ORM row, HttpRequest) (Ch22).

## 3. SOLID smell → principle diagnosis

| Symptom | Violated principle | Fix |
|---|---|---|
| Two unrelated teams keep merge-conflicting in the same file/class | SRP | Split by actor; extract shared code only if it's truly one actor's logic |
| Adding a feature requires editing existing, working code | OCP | Insert an interface between the stable and volatile parts; add, don't modify |
| Caller needs an `if`/type-check to treat implementations differently | LSP | Fix the contract, or externalize the deviation to config — never hardcode a vendor/type check |
| Client imports a class/interface and only calls one of its five methods | ISP | Segregate into per-client interfaces |
| High-level module `new`s, derives from, or overrides a concrete volatile class | DIP | Depend on an abstraction; push concretion to an Abstract Factory / Main |

## 4. Packaging strategy trade-off (component grouping)

| Force | Pulls components... | When it dominates |
|---|---|---|
| REP (granule of reuse = granule of release) | larger, coherent | when others will version/reuse this component |
| CCP (same reason/rate of change together) | larger, cohesive | early in a project — prioritize develop-ability |
| CRP (don't force deps on unused classes) | smaller, precise | as reuse/consumers multiply — prioritize dependency safety |

No fixed answer — the right size **jitters** as the project matures (early: favor CCP; later: favor REP/CRP) (Ch13).

Package-*by* choice (Ch34): Layer (fast start, doesn't scream domain) < Feature (screams domain, one entry point) < Ports-and-Adapters (domain fully isolated, "Périphérique" risk if outside code shares one tree) < Component (one clean interface per business capability — Brown's pick, best microservice stepping stone). **Whichever you pick is fake unless enforced by access modifiers** — if everything is `public`, all four styles produce the identical, unencapsulated structure. Compiler > code review for enforcing architecture.

## 5. Coupling thresholds & defaults

- **Depend in the direction of stability** (SDP): never let a component you want to keep changeable be depended on by something less changeable than it.
- **A component should be as abstract as it is stable** (SAP): I≈0 (stable, many dependents) should be mostly interfaces; I≈1 (unstable) should be concrete.
- **Metrics**: `I = Fan-out/(Fan-in+Fan-out)`; `A = abstract classes/total classes`; `D = |A+I-1|`. D→0 = on the Main Sequence (target). Zone of Pain (0,0): stable+concrete=rigid — tolerable only for genuinely nonvolatile utility code. Zone of Uselessness (1,1): abstract with no implementers — dead weight.
- **No cycles, ever** (ADP). Break with DIP (interface on the depended-upon side) or extract a shared component.
- **Never derive Entities/use cases from a framework base class.** Confine framework knowledge (DI annotations, ORM base classes) to Main or a thin proxy. Frameworks are an "asymmetric marriage" — you bear all the coupling risk, the author bears none (Ch32).
- **Database and web are both details, not architecture.** The *data model* is significant; the storage/transport tech is not. If a stakeholder mandates a specific DB/UI for non-technical reasons, bolt it on the side rather than let it shape the core (Ch30,31).

## 6. Polymorphism vs. inheritance vs. other

- Use **inheritance** only when you truly need LSP-safe substitutability of behavior across many call sites (a real "is-a" contract) — not merely to reuse fields/methods (Ch5,9).
- Use **interface + Dependency Inversion** (not inheritance) when the goal is decoupling a caller from a specific implementation you want to swap or defer deciding on.
- Use **plain data + functions / composition** when data doesn't need runtime-polymorphic dispatch — simpler, and keeps assignment/mutation disciplined per functional-programming principles (segregate mutability; push logic into the immutable core).

## 7. Fast tells & smells

- Database types, SQL, or ORM row objects appearing in a use case or entity → boundary violation.
- A "reusable framework" being designed before any real consuming application exists → premature reuse; build one usable app first, generalize later, ideally from ≥2 concurrent consumers.
- A class needs recompiling for a reason unrelated to its own responsibility → SRP/ISP violation upstream.
- Tests break in bulk from an unrelated UI/navigation change → tests are structurally coupled to volatile detail; insert a Testing API.
- Thousands of repeated `#ifdef`/environment-branch blocks scattered through logic → missing HAL-style boundary; centralize behind one interface.
- A "microservice" architecture where one new feature touches every service → Decoupling Fallacy; the real coupling is shared data/behavior, not the process boundary.
- Top-level folder names scream a framework ("app/controllers", "Spring config") instead of the business domain → Screaming Architecture failure.
- A stakeholder-imposed tech decision (DB vendor, web framework) is baked into the core instead of bolted to the side → treat it as a detail regardless of political pressure.
