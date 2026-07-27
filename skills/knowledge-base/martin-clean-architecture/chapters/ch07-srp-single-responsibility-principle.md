# Chapter 7: SRP: The Single Responsibility Principle

## Core Idea
The SRP is not "do one thing" — it is "a module should be responsible to one, and only one, actor," where an actor is a group of people who require a particular kind of change; the point is to separate code that different actors depend on.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: "A module should be responsible to one, and only one, actor." (Earlier equivalent formulations: "A module should have one, and only one, reason to change"; "A module should be responsible to one, and only one, user or stakeholder.")
  - When to use: Whenever a class or source file contains methods serving more than one business actor/stakeholder group.
  - How: Identify which actor(s) each method/field serves; if more than one actor is represented, split the module along actor lines so each resulting module answers to exactly one actor.
- **Function-level single-thing principle** (distinct from SRP): "A function should do one, and only one, thing." This is a low-level refactoring principle (breaking large functions into smaller ones), not one of the SOLID principles — do not conflate it with SRP.

## Key Concepts
- **Actor**: A group of one or more people who require the same kind of change to a system — the true "reason to change" behind SRP, not an individual user.
- **Module**: The simplest definition is a source file; more generally, a cohesive set of functions and data structures.
- **Cohesion**: The force that binds together code responsible to a single actor; it is what SRP is fundamentally about.
- **Accidental duplication**: Two actors' code appears to share logic by coincidence; extracting a "shared" helper couples the actors even though their needs will diverge.
- **Facade pattern (SRP solution)**: A thin class that only instantiates and delegates to the separated, single-responsibility classes, so callers don't have to manage multiple objects.
- **Scope**: The boundary of a class containing a family of private methods for one responsibility — outside that scope, nobody knows the private members exist.

## Mental Models
- Think of a class with multiple unrelated methods as a shared meeting room booked by three different departments — inevitably their schedules collide (merge conflicts) and their furniture gets rearranged by mistake (accidental coupling).
- Use "who signs off on a change to this method?" as the diagnostic question — if the answer differs across methods in the same class, the class violates SRP.
- SRP recurs fractally: at the component level it becomes the Common Closure Principle; at the architecture level it becomes the Axis of Change that drives Architectural Boundaries.

## Anti-patterns
- **Accidental duplication (shared algorithm across actors)**: When two actors' methods call a common private helper (e.g., `regularHours()` used by both `calculatePay()` for the CFO and `reportHours()` for the COO), a change intended for one actor silently corrupts behavior for the other, because the coupling isn't visible in either method's signature.
- **Merge risk from multi-actor files**: Files containing methods for multiple actors attract concurrent edits from unrelated teams (e.g., DBAs changing schema, HR changing report format), increasing merge collisions and cross-team risk.
- **"One class, one function" over-literalism**: Misreading SRP as requiring every class to contain exactly one method; in practice each separated responsibility class may still need many private helper methods — SRP is about actor-cohesion, not method count.

## Code Examples
<!-- omit — no fenced code in this chapter, only figure-based class diagrams -->

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
The `Employee` class in a payroll app has three methods: `calculatePay()` (specified by Accounting/CFO), `reportHours()` (specified by HR/COO), and `save()` (specified by DBAs/CTO) — three actors in one module, violating SRP. Developers, avoiding duplication, extract a shared `regularHours()` helper called by both `calculatePay()` and `reportHours()`. When the CFO's team tweaks non-overtime hour calculation for pay purposes, `reportHours()`'s output silently breaks for the COO's HR reports — the two actors were invisibly coupled through the shared function.

**Solutions (each moves responsibilities into separate classes):**
1. Split into three classes (`PayCalculator`, `HourReporter`, `EmployeeSaver`) sharing only a plain `EmployeeData` struct with no methods; the classes don't know about each other, eliminating accidental duplication.
2. Add an `EmployeeFacade` that merely instantiates and delegates to the three classes, so callers don't juggle three objects.
3. Alternatively, keep the most important method in the original `Employee` class and use it as a Facade for the lesser responsibilities, if the team prefers business rules to stay close to the data.

## Key Takeaways
1. Never equate SRP with "one method per class" — it's about one actor per module.
2. Before extracting a "shared" helper to avoid duplication, check whether the callers actually serve the same actor; if not, the duplication is accidental, not real, and should stay separate.
3. Treat unexpected merge conflicts in a file as a diagnostic signal that the file may be serving multiple actors and should be split.
4. Use Facade classes to keep the ergonomics of a single entry point after splitting responsibilities across classes.
5. Remember SRP reappears as the Common Closure Principle (components) and the Axis of Change (architecture) — the same actor-separation logic scales up.

## Connects To
- **Ch 12-14 (Component Principles)**: SRP generalizes to the Common Closure Principle when grouping classes into components.
- **Ch 8 (OCP)**: Separating actor-specific responsibilities is a prerequisite for organizing dependencies so changes don't propagate (OCP).
- **Architectural Boundaries**: The "Axis of Change" concept used later to justify architectural boundaries is SRP applied at the system level.
