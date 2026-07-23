# Chapter 17: Smells and Heuristics

## Core Idea
This chapter is Martin's comprehensive catalog of code smells and heuristics — built by walking through real refactorings and writing down, for each change, *why* it was made. It is organized into six lettered categories (Comments, Environment, Functions, General, Names, Tests) plus a bonus Java-specific set, each entry numbered (C1, E1, F1, G1, N1, T1, J1...) and meant to be read once top-to-bottom, then used forever after as a reference/checklist.

## Frameworks Introduced
- **The Smells & Heuristics Catalog**: a categorized, numbered checklist of ~91 code smells and heuristics distilled from Martin Fowler's *Refactoring* plus Martin's own field experience.
  - When to use: as a code-review or self-review checklist, either scanning top-to-bottom during a dedicated review pass, or looked up by ID when a specific smell is suspected.
  - How: read a module, and for each category (comments, build/test setup, function shape, general design, naming, tests) check the code against the relevant entries; each entry names the smell, explains why it hurts, and often shows a before/after code snippet.

## Key Concepts
- **Comments (C)**: smells related to comment quality and appropriateness — comments should never substitute for clean code and should not hold information better tracked elsewhere.
- **Environment (E)**: smells in the build and test process itself — building and testing should each be a single, obvious step.
- **Functions (F)**: smells in function signatures and shape — arguments, outputs, flags, and dead functions.
- **General (G)**: the largest category (G1–G36) — cross-cutting design smells about abstraction levels, duplication, coupling, naming of intent, and structure.
- **Names (N)**: smells in naming — descriptiveness, abstraction level, standard nomenclature, ambiguity, scope-appropriate length, encodings, and side-effect honesty.
- **Tests (T)**: smells in test suite quality — coverage, boundary testing, speed, and the diagnostic value of test patterns.

## Mental Models
- **The checklist as a trained nose** — this chapter isn't a rulebook to apply mechanically; it's an attempt to externalize the "smell" a disciplined programmer develops after years of refactoring, so a less experienced reader can borrow that nose.
- **One switch rule (G23)** — polymorphism should replace repeated switch/case or if/else chains; at most one switch statement should exist for a given type of selection, and its cases should produce polymorphic objects that eliminate the need for other switches on the same type.
- **Physical vs. logical dependency (G22)** — a dependency should be explicit (an argument, a call) rather than an unstated assumption baked into a magic constant or hardcoded behavior.
- **Levels of abstraction must not mix (G6, G34, N2)** — the recurring theme across categories: base classes shouldn't know about derivatives, functions should sit exactly one level below their own name, and names should reflect the abstraction level of their scope, not implementation detail.
- **The chapter as synthesis** — nearly every entry cross-references earlier chapters (Ch2 Names, Ch3 Functions, Ch4 Comments, Ch6 Objects/Data, Ch9 Tests), making this the condensed, searchable index of the whole book's principles.

## Anti-patterns
- **G5: Duplication** — the single most important rule in the list; every duplication is a missed abstraction opportunity (DRY, "Once and only once").
- **G6: Code at Wrong Level of Abstraction** — higher-level and lower-level concepts mixed in the same class/module instead of being cleanly separated.
- **G23: Prefer Polymorphism to If/Else or Switch/Case** — switch statements are the brute-force default, not usually the right solution; polymorphism should replace repeated conditionals on type.
- **G28: Encapsulate Conditionals** — extract boolean logic into a well-named function (`shouldBeDeleted(timer)`) instead of inlining it in an `if`.
- **G34: Functions Should Descend Only One Level of Abstraction** — the hardest heuristic to apply; humans are too good at seamlessly mixing abstraction levels within one function.
- **G14: Feature Envy** — a method that reaches into another object's accessors/mutators more than its own data envies that object's scope.
- **G15: Selector Arguments** — a trailing boolean/enum flag argument secretly packs multiple behaviors into one function; split into separate functions instead.
- **G17: Misplaced Responsibility** — code lives where it's convenient to write rather than where a reader would naturally expect to find it (principle of least surprise).
- **G22: Make Logical Dependencies Physical** — a dependent module silently assumes facts about another module instead of explicitly querying for them.
- **G25: Replace Magic Numbers with Named Constants** — raw, unexplained numeric or string literals should be hidden behind well-named constants.
- **G29: Avoid Negative Conditionals** — `if (buffer.shouldCompact())` reads easier than `if (!buffer.shouldNotCompact())`.
- **G30: Functions Should Do One Thing** — a function with multiple sequential sections (loop, check, act) should be decomposed into smaller single-purpose functions.
- **G36: Avoid Transitive Navigation** — chains like `a.getB().getC().doSomething()` (Law of Demeter violation) leak the object graph and make architecture rigid.
- **N1: Choose Descriptive Names** — names are 90% of what makes software readable; poorly chosen names (`x`, `q`, `z`) obscure even simple algorithms.
- **N7: Names Should Describe Side-Effects** — a getter that also lazily creates its return value (`getOos()`) should be named to reveal that, e.g. `createOrReturnOos()`.
- **F1: Too Many Arguments** — zero args is best, then one, two, three; more than three should be avoided with prejudice.
- **F3: Flag Arguments** — a boolean argument is a loud declaration that the function does more than one thing.
- **C3: Redundant Comment** — a comment that merely restates what the code already says plainly (`i++; // increment i`).
- **C5: Commented-Out Code** — dead, commented-out code rots and confuses; delete it, trust source control to remember it.
- **T9: Tests Should Be Fast** — a slow test is a test that eventually gets skipped or dropped.

## Code Examples
(omit — this chapter is mostly a checklist, not code-heavy)

## Reference Tables
| ID | Smell/Heuristic | Category |
|----|------------------|----------|
| C1 | Inappropriate Information | Comments |
| C2 | Obsolete Comment | Comments |
| C3 | Redundant Comment | Comments |
| C4 | Poorly Written Comment | Comments |
| C5 | Commented-Out Code | Comments |
| E1 | Build Requires More Than One Step | Environment |
| E2 | Tests Require More Than One Step | Environment |
| F1 | Too Many Arguments | Functions |
| F2 | Output Arguments | Functions |
| F3 | Flag Arguments | Functions |
| F4 | Dead Function | Functions |
| G1 | Multiple Languages in One Source File | General |
| G2 | Obvious Behavior Is Unimplemented | General |
| G3 | Incorrect Behavior at the Boundaries | General |
| G4 | Overridden Safeties | General |
| G5 | Duplication | General |
| G6 | Code at Wrong Level of Abstraction | General |
| G7 | Base Classes Depending on Their Derivatives | General |
| G8 | Too Much Information | General |
| G9 | Dead Code | General |
| G10 | Vertical Separation | General |
| G11 | Inconsistency | General |
| G12 | Clutter | General |
| G13 | Artificial Coupling | General |
| G14 | Feature Envy | General |
| G15 | Selector Arguments | General |
| G16 | Obscured Intent | General |
| G17 | Misplaced Responsibility | General |
| G18 | Inappropriate Static | General |
| G19 | Use Explanatory Variables | General |
| G20 | Function Names Should Say What They Do | General |
| G21 | Understand the Algorithm | General |
| G22 | Make Logical Dependencies Physical | General |
| G23 | Prefer Polymorphism to If/Else or Switch/Case | General |
| G24 | Follow Standard Conventions | General |
| G25 | Replace Magic Numbers with Named Constants | General |
| G26 | Be Precise | General |
| G27 | Structure over Convention | General |
| G28 | Encapsulate Conditionals | General |
| G29 | Avoid Negative Conditionals | General |
| G30 | Functions Should Do One Thing | General |
| G31 | Hidden Temporal Couplings | General |
| G32 | Don't Be Arbitrary | General |
| G33 | Encapsulate Boundary Conditions | General |
| G34 | Functions Should Descend Only One Level of Abstraction | General |
| G35 | Keep Configurable Data at High Levels | General |
| G36 | Avoid Transitive Navigation | General |
| J1 | Avoid Long Import Lists by Using Wildcards | Java (bonus) |
| J2 | Don't Inherit Constants | Java (bonus) |
| J3 | Constants versus Enums | Java (bonus) |
| N1 | Choose Descriptive Names | Names |
| N2 | Choose Names at the Appropriate Level of Abstraction | Names |
| N3 | Use Standard Nomenclature Where Possible | Names |
| N4 | Unambiguous Names | Names |
| N5 | Use Long Names for Long Scopes | Names |
| N6 | Avoid Encodings | Names |
| N7 | Names Should Describe Side-Effects | Names |
| T1 | Insufficient Tests | Tests |
| T2 | Use a Coverage Tool! | Tests |
| T3 | Don't Skip Trivial Tests | Tests |
| T4 | An Ignored Test Is a Question about an Ambiguity | Tests |
| T5 | Test Boundary Conditions | Tests |
| T6 | Exhaustively Test Near Bugs | Tests |
| T7 | Patterns of Failure Are Revealing | Tests |
| T8 | Test Coverage Patterns Can Be Revealing | Tests |
| T9 | Tests Should Be Fast | Tests |

## Worked Example
(omit — this chapter has no single running example, it's a checklist)

## Key Takeaways
1. Treat this catalog as a living review checklist, not a one-time read — scan code against the relevant category (C/E/F/G/N/T) during every review pass.
2. Duplication (G5) is the highest-priority smell to hunt for; nearly every design pattern exists to eliminate some form of it.
3. When in doubt about where responsibility, a constant, or a piece of logic belongs, apply the Principle of Least Surprise (G2, G17) — put it where a reader would naturally look.
4. Prefer polymorphism over conditional chains (G23) and encapsulate any boolean logic complex enough to need a name (G28).
5. Function- and name-level smells (F1–F4, N1–N7) are the fastest, cheapest wins — fix argument counts, flag arguments, and vague names before chasing deeper architectural smells.
6. Test-suite health (T1–T9) is itself subject to smells: insufficient coverage, skipped trivial tests, and slow tests all erode the safety net that makes the rest of the catalog safe to apply.
7. Use this chapter as the fast index back into Chapters 1–16 — each entry names the specific principle to re-read in full when a smell needs deeper justification.

## Connects To
- **Ch 1–16**: this chapter is the summary/synthesis of the entire first (Clean Code) book — Ch2 Meaningful Names underlies category N, Ch3 Functions underlies category F and several G entries (G30, G34), Ch4 Comments underlies category C, Ch6 Objects and Data Structures underlies G7/G8, Ch9 Unit Tests underlies category T, and Ch17 as a whole is explicitly built by refactoring real code and recording the reasoning chapter-by-chapter.
- **Martin Fowler's *Refactoring*** — the direct source of many smells (explicitly cited, e.g. G14 Feature Envy) and the origin of the "code smell" vocabulary this chapter extends.
- **Law of Demeter / "Writing Shy Code"** (Pragmatic Programmers) — underlies G36 Avoid Transitive Navigation.
- **Ch 18–32 (The Clean Coder)**: this catalog is the technical-craft counterpart to that book's professionalism/discipline heuristics — Clean Code answers "what does bad code look like," The Clean Coder answers "what professional habits prevent it."
