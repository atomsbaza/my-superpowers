# Chapter 35: Appendix A: Architecture Archaeology

## Core Idea
This is not a single narrative but a set of autobiographical career war-stories spanning Martin's 45 years in software (1970-early 1990s); read as a set, they show the same architectural lessons (isolate hardware/UI from business rules, respect the Dependency Rule, avoid over-architecture, don't chase premature reuse) being learned the hard way, repeatedly, across wildly different eras of hardware and constraints — the principles in the rest of the book are distilled from these recurring failures.

## Frameworks Introduced
- **Dependency-Normal vs. Dependency-Inverted Boundaries** (from the Union Accounting System story): a boundary is dependency-normal when compile-time dependency follows the flow of control (app → supervisor); dependency-inverted when flow of control crosses the boundary opposite to compile-time dependency (supervisor starts apps via a fixed jump address, with no compile-time knowledge of them).
  - When to use: analyzing any producer/consumer or plugin boundary to determine whether dependency inversion is actually present.
  - How: identify direction of flow of control vs. direction of compile-time dependency; they match = normal; they oppose = inverted (this is what makes something a true plugin).
- **"You can't make a reusable framework until you first make a usable framework"** (from the Architects Registry Exam story): reusable frameworks must be extracted from concrete usage across multiple real applications, not designed upfront in the abstract.
  - When to use: whenever asked to build a "reusable framework" before any concrete consuming application exists.
  - How: build one real, usable application first; only generalize into a framework once you have several real, simultaneous consumers pulling out the common shape.

## Key Concepts
- **Vectorization / indirect dispatch** (4-TEL COLT story): replacing direct subroutine calls with calls through a RAM-resident vector (jump) table, so individual compiled units (chips) can be independently replaced without recompiling/relinking the whole system — Martin explicitly calls this an unwitting reinvention of polymorphic dispatch and plugin architecture.
- **Rigid code / lockdown** (SAC dispatch-determination story): code so poorly understood (write-only, undocumented) that management forbids further modification, permanently freezing a business-critical component.
- **Hardware-coupled business rules** (SAC modem story): device-control code smeared throughout business logic and UI, with no abstracted interface, making a hardware swap (old modem → new modem) require an enormous, fragile hack instead of a clean adapter swap.
- **Forked codebase divergence** (SAC Europe story): geographically split teams forking a codebase to meet urgent regional needs, resulting in years of failed reintegration attempts because the two forks drifted too far from each other.
- **Over-architecture** (ROSE story): excessive layering with high inter-layer communication overhead can reduce team productivity so much that a fully-featured "enterprise" architecture loses to a small, "cute" competing tool built by a small team.
- **Premature reuse** (ETS Architects Registry Exam story): attempting to build a generalized, reusable framework before writing any real consuming application produces a framework that doesn't actually fit real usage and must be substantially rewritten.

## Mental Models
- Think of each story as answering "what specific failure taught this principle?" — e.g., the modem hack is the origin story for "isolate hardware from business rules, and abstract interfaces," stated in the text almost verbatim as the lesson learned.
- Use the **plugin test** from the Union Accounting story on any boundary you design: does flow of control cross opposite to compile-time dependency? If not, it's not really a plugin, no matter what you call it.
- Treat "we'll build the reusable framework first, then the apps will pop out fast" as a **red flag phrase** — Martin explicitly says he should have face-palmed at his own younger self for believing it.

## Anti-patterns
- **Smearing device/hardware control code throughout business and UI logic** (SAC modem story): a hardware vendor's undocumented protocol change forced Martin's team into "the worst hack imaginable" — intercepting and translating raw bus commands — because there was no abstracted device interface to swap instead.
- **Building a "reusable framework" before any concrete usable application exists** (ETS story): produced 45,000 lines of framework that didn't fit the very next application it was supposed to serve, requiring a full year to redo.
- **Pointing dependencies with the flow of control instead of toward policy** (ROSE story): ROSE's layers pointed GUI → representation → manipulation rules → database (flow-of-control direction, not toward high-level policy); Martin cites this misdirection as a contributing cause of the product's eventual demise.
- **Over-layering relative to problem size** (ROSE story): "architecting for the enterprise when all you really need is a cute little desktop tool is a recipe for failure" — matching architectural investment to actual problem scale matters as much as getting the structure right.
- **Locking down incomprehensible-but-critical code instead of refactoring it** (SAC dispatch-determination story): freezing "rigid" code avoids short-term breakage but permanently forfeits the ability to safely extend a component the business depends on economically.

## Worked Example
**4-TEL COLT Vectorization (mid-1970s).** The 4-TEL phone-line testing system ran firmware split across 30 EPROM chips (a single 30K binary image cut into 1K segments). Every bug fix or feature, however trivial, shifted instruction addresses across the entire image, forcing field engineers to physically replace all 30 chips at every site — a costly, error-prone logistics nightmare (mislabeled chips, broken pins, wrong chip swapped). Martin's fix ("Vectorization," ~3 months of work): split the 30K program into 32 independently compilable ≤1K source files, each fixed to load at a specific address; each file also emitted a small (40-byte, ≤20-entry) table of its subroutine addresses; at boot, these tables were loaded into a RAM "vector" area, and every cross-chip subroutine call was changed to an *indirect* call through its RAM vector entry. Result: any single chip could be recompiled and shipped alone, without touching the other 29 — independently deployable units, invented from scratch, that Martin later recognized as polymorphic dispatch / plugin architecture / objects, years before he knew the formal OO vocabulary. A side benefit: bugs could be live-patched over a dial-up connection by overwriting a vector entry to point at a hand-typed hex patch in spare RAM, avoiding an urgent truck-roll.

**ETS Architects Registry Exam (early 1990s).** Contracted to build 18 GUI "vignette" exam applications plus 18 matching scoring applications (36 total) for architect licensing exams. Martin and his partner, seeing heavy similarity across the 18+18, decided to build a shared reusable framework first, starting with the hardest vignette. One year and 45,000 lines of framework (plus 6,000 lines of app code) later, the framework didn't fit the next applications — "subtle frictions that just didn't work" — forcing a full rewrite. The second attempt built four vignettes *simultaneously* against a framework being extracted from all four at once; this also took a year but produced a framework (again ~45,000 lines) that genuinely fit, after which the remaining vignettes "started popping out... every few weeks" as originally hoped. Lesson stated directly in the text: "You can't make a reusable framework until you first make a usable framework. Reusable frameworks require that you build them in concert with several reusing applications."

## Key Takeaways
1. Abstract hardware/device control behind a real interface before a second device variant ever shows up — retrofitting isolation after the fact (SAC modem story) is far more expensive than designing it in up front.
2. A true plugin boundary requires flow-of-control and compile-time dependency to point in opposite directions — verify this explicitly rather than assuming any "modular-looking" boundary qualifies.
3. Don't build a reusable framework speculatively; extract it from at least one (ideally several concurrent) real, usable consuming applications.
4. Match architectural investment to problem scale — heavy layering that's appropriate for an enterprise system can sink a project that only needed a small tool (ROSE vs. its scrappy Wisconsin-built replacement).
5. Freezing incomprehensible business-critical code ("rigid" lockdown) is a symptom of insufficient clean-code discipline having been applied when it was written, not a durable strategy.
6. Geographically forked codebases under time pressure (SAC/Europe) tend to diverge faster than they can be reconciled — plan integration tooling and cadence before the fork happens, not after years of drift.
7. Point dependencies toward high-level policy, not merely with the flow of control — ROSE's failure to do this is cited as a contributing factor in its demise, reinforcing the core Dependency Rule from the rest of the book.

## Connects To
- **Ch 11 (OCP)**: the vectorization story is a hardware-era, pre-OO discovery of exactly the plugin/polymorphism mechanism OCP formalizes.
- **Ch 22 (Clean Architecture) / Dependency Rule**: ROSE's flow-of-control-direction dependencies are a direct, real-world counterexample to the Dependency Rule.
- **Ch 30-32 (Database/Web/Frameworks Are Details)**: the SAC modem-coupling disaster is the hardware-era ancestor of these chapters' "isolate details behind boundaries" argument.
- **Ch 12-14 (Component Principles)**: the ETS reuse story is a concrete, painful illustration of why the Common Reuse Principle warns against designing reusable components before real consumers exist.
