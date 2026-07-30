# Chapter 2: A Pragmatic Approach

## Core Idea
Good software design comes from a small set of disciplined habits — eliminate duplicated knowledge, keep components independent (orthogonal), keep decisions reversible, and get end-to-end feedback early — applied consistently across code, architecture, and process.

## Frameworks Introduced
- **DRY (Don't Repeat Yourself)**: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."
  - When to use: Any time the same piece of knowledge (a business rule, a data value, a comment, a schema) could end up expressed in two places.
  - How: Identify the source of duplication — imposed (environment forces it), inadvertent (design mistake, e.g., unnormalized data), impatient (copy-paste under time pressure), or interdeveloper (two people reinvent the same thing) — then eliminate it via code generation, calculated fields, accessor functions, or better team communication.
- **Orthogonality**: Two or more things are orthogonal if changes in one do not affect any of the others — independence and decoupling borrowed from geometry.
  - When to use: When designing components, modules, team structure, or even tool/editor choices.
  - How: Give each component a single, well-defined responsibility (cohesion); design self-contained modules whose external interfaces can stay stable while internals change; avoid global data and unnecessary coupling between layers (UI, business logic, database).
- **Reversibility**: No important decision is final; keep architectural, vendor, and platform choices soft so they can be undone or swapped without excessive cost.
  - When to use: When locking in a database vendor, a deployment model (standalone vs. client-server vs. n-tier), or any third-party dependency.
  - How: Abstract the volatile decision behind a well-defined interface so it can be swapped later; favor configuration over hard-coded choices; treat decisions as "written in the sand," not "carved in stone."
- **Tracer Bullets**: Build a thin, working, end-to-end path through the whole system early, then flesh it out iteratively, instead of specifying everything up front and integrating only at the end.
  - When to use: New projects with many unknowns — vague requirements, unfamiliar technology, or a changing environment.
  - How: Implement a minimal but real (non-throwaway) slice connecting every major component (UI to library to server, etc.); demonstrate it to users; adjust aim based on feedback; keep augmenting the same skeleton rather than replacing it.
- **Prototyping**: Build deliberately disposable code (or non-code artifacts like Post-it notes) to explore one risky or uncertain aspect of a system, then throw it away.
  - When to use: Architecture decisions, unproven algorithms, third-party tool evaluation, UI layout, or performance questions — anything carrying risk or uncertainty.
  - How: Ignore correctness, completeness, robustness, and style deliberately; use a high-level language for speed; make everyone aware the code is disposable so it doesn't get shipped by accident.
- **Estimating**: All estimates are based on models; build one deliberately rather than guessing.
  - When to use: Whenever someone asks "how long / how much / how big."
  - How: Understand what's being asked and its required accuracy; build a rough mental model of the system; decompose into components; assign values to parameters (focus effort on multiplicative, not additive, parameters); calculate a range of answers; track your estimates over time to calibrate; scale your units (days/weeks/months) to match the accuracy you actually intend to convey.

## Key Concepts
- **The Four "I"s of Duplication**: Imposed, Inadvertent, Impatient, Interdeveloper — a taxonomy of how duplication creeps into a codebase.
- **Uniform Access Principle (Meyer)**: All services a module offers should be available through a uniform notation, regardless of whether implemented via storage or computation — the rationale for always using accessor methods.
- **Cohesion (Yourdon and Constantine)**: A component having a single, well-defined purpose — the internal complement to external orthogonality.
- **Butterfly effect / nonlinear systems**: Small early decisions in a project compound; the later a critical decision is revisited, the more expensive it is to change ("narrower version of reality... fewer options").
- **Domain Language**: A small, tailored language (or notation) built around the vocabulary of the problem domain, used to express solutions more directly than a general-purpose language would allow.
- **CORBA / abstraction as reversibility mechanism**: Using an architectural layer (like CORBA) to insulate a project from changes in implementation language or platform.

## Mental Models
- Think of orthogonality using the helicopter analogy: a nonorthogonal control system means every input has secondary effects on every other input, so a "simple" fix (lower the collective) triggers a cascade of compensating corrections — exactly what happens when modules are tightly coupled.
- Think of tracer bullets as "code that glows in the dark" — not a mockup, but a thin, real, working path from end to end that you extend, versus a prototype which you build to learn from and discard.
- Think of critical project decisions as "written in the sand at the beach," not carved in stone — reversibility is a design property you must engineer for, not an accident.
- Use "stone soup"-style incremental estimating for schedules: don't commit the whole plan up front; check requirements, analyze risk, design/implement/integrate, validate with users, then refine the next iteration's estimate based on the last.

## Anti-patterns
- **Unnormalized data / duplicated attributes across classes**: E.g., both `Truck` and `DeliveryRoute` holding a `driver` field — leads to ambiguity about which copy is authoritative when data changes.
- **Documentation and comments that restate the code**: Comments should explain *why*, not duplicate the logic already expressed in code; duplicated knowledge between code and comments inevitably drifts out of sync.
- **Copy-paste under deadline pressure ("impatient duplication")**: Feels like a time-saver but multiplies future maintenance cost — the Y2K crisis is cited as a large-scale example of exactly this failure mode.
- **Treating decisions as irreversible by default**: Locking in a vendor, database, or deployment model without an abstraction layer turns a business change into an expensive rewrite.
- **Confusing tracer bullets with prototypes**: Throwing away a tracer-bullet skeleton (or, conversely, shipping prototype code) misapplies each technique's purpose — one is lean-but-permanent, the other is disposable-by-design.
- **Giving a single hard-and-fast schedule number before any iteration has run**: For all but the most trivial or repeat projects, this is described as "just guessing."

## Code Examples
```cpp
// Inadvertent duplication: length is derivable, so storing it duplicates knowledge
class Line {
public:
    Point start;
    Point end;
    double length;   // duplicated: changes to start/end don't update this
};

// Fixed: DRY via a calculated field
class Line {
public:
    Point start;
    Point end;
    double length() { return start.distanceTo(end); }
};
```
- **What it demonstrates**: DRY applies to data, not just text — a field derivable from other fields is duplicated knowledge, and should be computed rather than stored (unless caching for performance, in which case the violation must be localized behind accessor methods).

## Reference Tables
| Estimate duration | Quote estimate in |
|---|---|
| 1–15 days | days |
| 3–8 weeks | weeks |
| 8–30 weeks | months |
| 30+ weeks | think hard before giving an estimate |

| Duplication type | Cause | Primary fix |
|---|---|---|
| Imposed | Environment/language forces it (e.g., header files) | Code generation, active synchronization |
| Inadvertent | Design mistake (unnormalized data) | Normalize the model, calculated fields |
| Impatient | Time pressure, copy-paste | Discipline, parameterize instead of duplicating literals |
| Interdeveloper | Team members unknowingly duplicate functionality | Communication, shared utility library, code review |

## Worked Example
The helicopter-controls story illustrates orthogonality by negation: you're piloting a helicopter when the pilot faints, hovering 100 feet up. You reason that lowering the collective pitch lever should start a gentle descent — a single, independent action. But lowering the collective also drops the nose and starts a spiral, so you must simultaneously add backward cyclic and press the tail-rotor pedal to compensate — and each of those corrections then perturbs the other controls again. The workload becomes "phenomenal" because every input has secondary effects on every other input: the system is decidedly non-orthogonal. The authors then contrast this with a well-designed orthogonal system, such as a codebase where the database layer is fully independent of the UI layer — you can change the interface without touching the database, or swap databases without touching the interface. The moral: nonorthogonal systems are inherently harder to change safely because there is no such thing as "a local fix" — a change anywhere ripples everywhere, exactly like fighting a spiraling helicopter with your hands and feet in constant motion.

## Key Takeaways
1. Apply DRY beyond code — to comments, documentation, database schemas, and requirements — since knowledge, not text, is the actual unit of duplication.
2. Diagnose which of the four kinds of duplication (imposed/inadvertent/impatient/interdeveloper) you're facing before choosing a fix; each has a different root cause and remedy.
3. Design for orthogonality deliberately: give each component one well-defined responsibility so a change in one place doesn't cascade elsewhere.
4. Treat major architectural and vendor decisions as reversible by default — hide them behind interfaces so a bad early bet doesn't become permanent.
5. Build tracer bullets (a thin, real, end-to-end path) on projects with high uncertainty, rather than fully specifying everything up front; reserve throwaway prototypes for exploring one risky question at a time.
6. Never give an off-the-cuff estimate — build a quick model, decompose it, and answer "I'll get back to you" instead.
7. Track your estimate accuracy over time; a wrong estimate is diagnostic information about your model, not just bad luck.

## Connects To
- **Ch 1**: DRY is the technical formalization of the "duplicate knowledge = contradiction" theme first raised via Star Trek's fictional AI-crashing trick in Chapter 1.
- **Ch 4**: Design by Contract (Ch 4) is essentially orthogonality applied at the interface level — contracts let modules stay decoupled while still guaranteeing correctness.
- **Modern software engineering**: DRY is now a default heuristic in code review and linting (e.g., duplicate-code detectors); orthogonality underlies microservices and hexagonal/clean architecture; tracer bullets map directly onto today's "walking skeleton" and continuous-deployment MVP practices.
