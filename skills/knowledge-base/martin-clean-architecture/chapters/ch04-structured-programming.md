# Chapter 4: Structured Programming

## Core Idea
Structured programming's real value is that it makes modules falsifiable (testable) by restricting control flow to sequence, selection, and iteration — software can never be proven correct, only shown to have resisted our best attempts to prove it incorrect, and structured decomposition is what makes that falsification tractable.

## Frameworks Introduced
- **Structured Programming (Dijkstra, 1968)**: "Structured programming imposes discipline on direct transfer of control."
  - When to use: At every level from smallest function to largest component, wherever you need a unit to be recursively decomposable and falsifiable.
  - How: Replace unrestrained `goto` with the three Böhm–Jacopini structures — sequence, selection (`if/then/else`), and iteration (`do/while`) — which allow recursive decomposition into provable/testable units.
- **Falsifiability over provability (the scientific method applied to code)**: Programs, like scientific theories, cannot be proven correct — only proven incorrect (falsified) by a failing test.
  - When to use: Whenever deciding how much confidence a passing test suite should give you, or justifying why testing (not formal proof) is the primary correctness mechanism in software.
  - How: Recursively decompose a system into small provable/functionally-decomposed units, then attempt to falsify each with tests; a unit that survives sufficient falsification attempts is "deemed correct enough."

## Key Concepts
- **Böhm–Jacopini theorem**: Any program can be constructed from just three control structures — sequence, selection, and iteration — proved two years before Dijkstra's structured programming discovery.
- **Provable decomposition**: Only modules built from sequence/selection/iteration (no unrestrained `goto`) can be recursively subdivided into units small enough to reason about or prove.
- **Functional decomposition**: Breaking a large-scale problem into high-level functions, each further decomposed into lower-level functions, all expressible in structured-programming control structures.
- **Falsifiability (science vs. mathematics)**: Mathematics proves provable statements true; science proves provable statements false (or fails to, and deems them true enough). Dijkstra: "Testing shows the presence, not the absence, of bugs."
- **Unprovable programs**: A program built with unrestrained `goto` cannot be deemed correct no matter how much testing is applied, because it resists the decomposition falsifiability depends on.

## Mental Models
- Think of **tests as falsification attempts**, not correctness proofs — a passing suite means "we failed to prove this wrong," which is the same epistemic status as a surviving scientific theory (e.g., F=ma).
- Use the **divide-and-conquer / recursive decomposition lens** for any module design: can this be broken into small enough falsifiable units? If a control-flow pattern blocks that decomposition (unrestrained jumps), it blocks testability too.
- At the architecture level, treat **modules, components, and services as the "structured programming" units of the macro world** — architects apply the same restrictive, falsifiability-oriented discipline at a much higher level.

## Anti-patterns
- **Unrestrained `goto` / uncontrolled direct transfer of control**: Prevents recursive decomposition into small provable/testable units, so no amount of testing can establish confidence in the module.
- **Believing tests can prove a program correct**: Category error — tests can only fail to prove it incorrect; treating "all green" as a correctness guarantee overstates what testing can deliver.
- **Chasing Dijkstra's original goal of formal mathematical proof for ordinary software**: Never materialized in practice ("the proofs never came") — not a productive target for most teams; falsifiability via testing is the workable substitute.

## Worked Example
Dijkstra's own path: as a programmer in the 1950s he wanted to apply mathematical proof to programs (a Euclidean hierarchy of postulates/theorems, like geometry). To make this work he needed every module decomposable into small provable units. He found that *some* uses of `goto` blocked this recursive decomposition, while other uses of `goto` were equivalent to simple `if/then/else` and `do/while` — and Böhm and Jacopini had already shown (2 years earlier) that sequence + selection + iteration alone suffice to build any program. Dijkstra proved sequential code correct by tracing inputs to outputs (enumeration), proved selection correct by enumerating each branch, and proved iteration correct via induction (base case + N→N+1 step). This became "Go To Statement Considered Harmful" (CACM, 1968), which triggered roughly a decade of controversy before goto-based programming effectively disappeared from mainstream languages. The formal-proof program itself never scaled to real software ("no formal proofs" ever materialized industry-wide) — but the falsifiability/testability benefit of restricted control flow survived and became the lasting value of structured programming.

## Key Takeaways
1. Treat tests as falsification, not proof — never claim "this is correct" from a green suite; claim "we failed to prove it incorrect."
2. Favor recursive functional decomposition into small units specifically because it makes each unit independently falsifiable.
3. Modern languages already enforce structured control flow (no unrestrained `goto`) — the discipline is now free; apply the same falsifiability mindset deliberately at the module/component/architecture level, where it is not automatically enforced.
4. Formal correctness proofs are not a practical target for ordinary software development — don't invest team effort chasing them.
5. A component that resists decomposition into small falsifiable units (spaghetti control flow, hidden jumps via exceptions/flags) undermines your ability to trust it no matter how much you test it.

## Connects To
- **Ch 3**: Structured programming is one of the three foundational paradigms; this chapter is the deep dive on "discipline on direct transfer of control."
- **Ch 5**: OO's polymorphism is framed as discipline on *indirect* transfer of control — the natural next step after structured programming's direct-control discipline.
- **TDD / testing practice**: Directly grounds why test-driven development is the practical, scalable descendant of Dijkstra's falsifiability idea.
