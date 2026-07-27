# Chapter 19: Policy and Level

## Core Idea
Software is statements of policy; good architecture groups policies that change for the same reasons together and orders source-code dependencies by *level* (distance from inputs/outputs), not by data flow — low-level components depend on high-level ones, never the reverse.

## Frameworks Introduced
- **Level (as a design dimension)**: "the distance from the inputs and outputs." The farther a policy sits from I/O, the higher its level; I/O-handling policy is always lowest-level.
  - When to use: whenever deciding which component should depend on which.
  - How: identify which policy is closer to raw inputs/outputs (lower level) vs. which is a general/abstract computation independent of any specific I/O device (higher level); make the low-level one depend on the high-level one, inverting the naive data-flow direction if necessary.
- **Source code dependency decoupled from data flow, coupled to level**: data can flow in one direction while compile-time (import/using/require) dependencies point in a different, level-based direction.
  - When to use: any pipeline where data physically flows through low-level I/O into a high-level transform and back out.
  - How: introduce interfaces at the boundary (e.g., CharWriter/CharReader) owned by the high-level module, so low-level I/O classes implement interfaces defined by the high-level policy (Dependency Inversion Principle).

## Key Concepts
- **Policy**: a rule describing how inputs are transformed into outputs; the fundamental substance of any program.
- **Level**: distance of a policy from the system's inputs and outputs; higher level = farther from I/O.
- **Directed acyclic graph (of components)**: the target shape for a well-factored architecture, nodes = same-level policy groups, edges = dependencies between levels.
- **Central Transform**: term (from Meilir Page-Jones) for the highest-level component in a data-flow diagram — farthest from both inputs and outputs.
- **Plugin architecture**: lower-level components (I/O, frameworks) should plug into higher-level components, not the reverse.

## Mental Models
- Use "distance from I/O" as level, not "how important the code looks" — a component that reads keystrokes is always low-level no matter how complex its logic.
- Think of dependency direction as independent of data-flow direction: data can flow from a low-level reader, through a high-level transform, to a low-level writer, while all source dependencies point inward toward the transform.
- Treat frequent/urgent-but-trivial changes (I/O, formatting) as the domain of low-level components; treat rare/substantive changes as the domain of high-level components — this predicts which side should be insulated from which.

## Anti-patterns
- **Letting a high-level function call low-level I/O functions directly** (e.g., `encrypt()` calling `readChar()`/`writeChar()` directly): binds the important policy to volatile low-level details, so I/O churn destabilizes the core logic.
- **Grouping policies by data-flow adjacency instead of by rate/reason of change**: violates SRP/CCP — policies that change for different reasons end up entangled in one component.

## Code Examples
```
function encrypt() {
  while(true)
    writeChar(translate(readChar()));
}
```
- **What it demonstrates**: an *incorrect* architecture — the high-level `encrypt` policy directly depends on low-level `readChar`/`writeChar`, coupling the important algorithm to volatile I/O details. The fix is to define `CharReader`/`CharWriter` interfaces owned by the high-level `Encrypt` class, with `ConsoleReader`/`ConsoleWriter` as low-level implementations depending inward on those interfaces.

## Worked Example
A simple encryption program reads characters from an input device, translates them via a table, and writes them to an output device.
- Data flow (curved arrows): input device → read → translate → write → output device.
- Naive/incorrect design: `encrypt()` directly calls `readChar()` and `writeChar()` — source dependencies follow data flow, so the high-level Translate policy depends on low-level I/O.
- Correct design (Fig 19.2): an `Encrypt` class sits inside a boundary with `CharWriter`/`CharReader` interfaces; `ConsoleReader`/`ConsoleWriter` classes (low-level, close to I/O) implement those interfaces from outside. All dependencies crossing the boundary point inward toward `Encrypt`.
- Result (Fig 19.3, component view): the `IODevices` component depends on the `Encryption` component; `Encryption` knows nothing of `IODevices` — I/O is a plugin to the encryption policy, so changing the I/O device (or swapping console for file) has zero impact on the encryption algorithm.

## Key Takeaways
1. Rank components by level (distance from I/O), not by where they sit in the data-flow pipeline.
2. Force low-level, frequently-changing components (I/O, formatting, devices) to depend on high-level, rarely-changing policy — invert the dependency with interfaces owned by the high-level side when data flow would naturally point the wrong way.
3. Treat lower-level components as plugins to higher-level ones; this is a direct architectural application of SRP, OCP, CCP, DIP, SDP, and SAP working together.

## Connects To
- **Ch 20 (Business Rules)**: level thinking directly motivates why Entities (highest-level Critical Business Rules) must not depend on use cases or I/O.
- **Ch 22 (The Clean Architecture)**: the concentric-circle Dependency Rule is level-and-policy thinking generalized into a full layered architecture.
- **Dependency Inversion Principle**: the mechanism (interfaces owned by the high-level side) used here to make dependencies point opposite to data flow.
