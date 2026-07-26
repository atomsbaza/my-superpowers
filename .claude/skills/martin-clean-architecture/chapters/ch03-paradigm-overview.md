# Chapter 3: Paradigm Overview

## Core Idea
There are exactly three programming paradigms — structured, object-oriented, and functional — and each one *removes* a capability from the programmer (direct jumps, indirect jumps, and assignment respectively) rather than adding new power; together they map directly onto the three core concerns of architecture.

## Frameworks Introduced
- **The Three Paradigms as Disciplines of Removal**: Structured programming imposes discipline on direct transfer of control; object-oriented programming imposes discipline on indirect transfer of control; functional programming imposes discipline on assignment.
  - When to use: As the mental map for why each paradigm exists and what architectural concern it serves.
  - How: Map each paradigm to its architectural use — structured programming → algorithmic foundation of modules; OO → mechanism (polymorphism) for crossing architectural boundaries; functional → discipline on the location of and access to data.
- **Paradigms-to-architecture-concerns mapping**: Function, separation of components, and data management are architecture's three big concerns, and each aligns with one paradigm.
  - When to use: When deciding which paradigm-derived discipline addresses which architectural problem.
  - How: Use polymorphism (OO) to define and cross component boundaries; use functional discipline to control where and how mutable data is accessed; use structured decomposition for provable, falsifiable module-level logic.

## Key Concepts
- **Structured programming**: Discovered by Dijkstra (1968); replaces unrestrained `goto` with `if/then/else` and `do/while/until`.
- **Object-oriented programming**: Discovered by Dahl and Nygaard (1966); arose from moving the function call stack frame to the heap, enabling classes, instance variables, methods, and polymorphism via disciplined function pointers.
- **Functional programming**: Rooted in Alonzo Church's 1936 λ-calculus, predating computer programming itself; foundational notion is immutability — functional languages effectively have no (or heavily disciplined) assignment.
- **Negative paradigms**: Each paradigm tells programmers what *not* to do rather than adding new capability — they remove `goto`, function pointers used dangerously, and unrestrained assignment.
- **Closure of paradigm discovery**: All three were discovered within a single decade (1958–1968); no new negative paradigm has emerged since, and the author argues none is likely (nothing further to "take away").

## Mental Models
- Think of each paradigm as a **constraint layer**, not a feature layer — evaluate any new "paradigm" claim by asking "what capability does it remove," not "what does it add."
- Use the **three-paradigm-to-three-concerns mapping** as a checklist when designing architecture: have you disciplined your control flow (structured), your component boundaries (OO/polymorphism), and your data mutation (functional)?

## Anti-patterns
- **Treating OO purely as "the paradigm with encapsulation/inheritance/polymorphism-as-buzzwords"**: Chapter 3 sets up that OO's architectural value is specifically about disciplined indirect control transfer (detailed in Ch 5), not the buzzword triad.
- **Expecting a "fourth paradigm" to unlock new power**: The chapter's historical argument (all three discovered in one decade, all subtractive) implies skepticism toward claims of paradigm-level breakthroughs going forward.

## Worked Example
No extended narrative example in this short overview chapter — it is a compact historical/conceptual bridge. The clearest illustrative device is the summary triad itself: "Structured programming imposes discipline on direct transfer of control. Object-oriented programming imposes discipline on indirect transfer of control. Functional programming imposes discipline upon assignment." Martin then walks this back to architecture directly: polymorphism (OO) is the mechanism for crossing architectural boundaries; functional programming disciplines the location of and access to data; structured programming is the algorithmic foundation of modules — matching the three big architectural concerns of function, component separation, and data management.

## Key Takeaways
1. Learn each paradigm as "what it forbids," not "what it adds" — this reframing clarifies why disciplined code is more valuable than clever code.
2. Map any architecture decision to one of the three concerns (function / component separation / data management) and check which paradigm's discipline should govern it.
3. Don't wait for a "next paradigm" to solve an architecture problem — the toolset (structured, OO, functional) is considered essentially complete.

## Connects To
- **Ch 4**: Deep dive on structured programming — falsifiability, proof, and why it underlies testable modules.
- **Ch 5**: Deep dive on OO — reveals polymorphism as the true architectural payload (dependency inversion), not encapsulation/inheritance.
- **Ch 6**: Deep dive on functional programming — immutability's direct implications for concurrency-safe architecture.
