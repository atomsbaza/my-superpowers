# Chapter 28: Anti-patterns

## Core Idea
An anti-pattern is a commonly repeated approach that looks attractive at first but predictably causes problems over time; naming and cataloging them lets teams recognize the trap before paying its long-term cost.

## Frameworks Introduced
- **Anti-pattern (as a category)**: An established practice that identifies problems, rather than a solution — it alerts developers, managers, and architects to common mistakes and suggests an alternate (sometimes tougher-looking) solution that pays off in the long run.
  - When to use: Whenever an approach seems like a quick, attractive fix (e.g., to meet a deadline) — pause and check whether it matches a known anti-pattern before committing to it.
  - How: Recognize the symptom (inability to add features easily, rising maintenance cost, loss of OO benefits like inheritance/polymorphism), trace it to a named anti-pattern, and apply the catalog's suggested remedy or refactor.

## Key Concepts
- **Anti-pattern vs. design pattern**: Both encode reused experience, but a design pattern is a proven solution while an anti-pattern documents a proven trap — and, critically, a design pattern applied in the wrong context can itself turn into an anti-pattern.
- **Overuse of patterns**: Applying a pattern reflexively "at any cost," regardless of whether it actually fits the problem.
- **God class**: One oversized object accumulates many unrelated responsibilities/methods, commonly arising from a misapplied Mediator pattern.
- **Not invented here**: Refusing to use an available, suitable third-party library purely out of a preference to build everything internally.
- **Zero means null**: Overloading a special/sentinel value (0, -1, 999, or a placeholder date like 09/09/9999) to mean "null" or "no value," which breaks the moment a real, legitimate use of that value is needed.
- **Golden hammer**: Insisting a single familiar technology is always the right tool, even when a new problem calls for a different one, purely to avoid learning something new.
- **Refactoring**: Improving the internal design of existing code without changing its external behavior — the standard remedy once an anti-pattern is detected, producing more readable, adaptable, and maintainable code.

## Mental Models
- Treat "prevention is better than a cure" as the organizing motivation for the whole chapter — anti-patterns exist to let you avoid the mistake, not just diagnose it afterward.
- Use symptom-first diagnosis: global variables, code duplication, little/no code reuse, one dominant class, or a glut of parameterless methods are surface signals worth investigating even before you can name which anti-pattern is present.
- Recognize anti-patterns as arising from mindset, not just code shape — the chapter's example quotes ("we need to deliver ASAP," "I know design patterns very well," "more complicated code reflects my expertise") show the human motivations that produce them.

## Anti-patterns
- **Overuse of patterns**: Using a pattern because you can, not because the problem calls for it — inflates complexity without matching benefit.
- **God class**: A single class absorbing unrelated responsibilities, frequently the result of a Mediator pattern applied too broadly.
- **Not invented here**: Rebuilding an already-solved problem from scratch rather than adopting an available library, for organizational-ego reasons rather than technical ones.
- **Zero means null**: Repurposing a valid value (0, -1, 999, a sentinel date) as a null marker, which fails the moment that value is legitimately needed — the chapter's suggested remedy is an explicit Boolean flag to represent "is null" rather than overloading the value itself.
- **Golden hammer**: Forcing every new problem through one familiar technology to avoid learning something new, even when it's the wrong fit.

## Code Examples
No significant code examples in this chapter — it is a discussion/Q&A chapter, illustrated with hypothetical scenarios (e.g., a sentinel date or integer standing in for null) rather than runnable C#.

## Reference Tables
None in this chapter (the chapter references an external catalog — the C2 Anti-Patterns Catalog at wiki.c2.com — rather than reproducing a table).

## Worked Example
The chapter's central case is the "zero means null" anti-pattern walked through step by step: a developer, out of laziness or optimism, treats an ordinary value (0, -1, 999, or the date 09/09/9999) as a stand-in for "no value." This works until the application legitimately needs that exact value — at which point the sentinel collides with real data and the system can no longer distinguish "null" from "actually -1" (or "actually September 9, 9999"). The remedy offered is architectural, not clever: add an explicit Boolean field that means "this value is null," rather than overloading the domain value itself. The same reasoning pattern — a shortcut that looks fine until real data collides with the placeholder — is repeated for the golden hammer example (Mr. X forcing every new project through technology T to avoid learning something new), where the remedy is training/education rather than a data-modeling fix, showing that the correct fix for an anti-pattern depends on its root cause (technical vs. organizational/human).

## Key Takeaways
1. An anti-pattern is defined by a trajectory, not a snapshot: it looks attractive at the point of adoption and only reveals its cost over time, so evaluate approaches against their long-term maintenance trajectory, not just immediate convenience.
2. A design pattern and an anti-pattern are not different categories of thing — the same pattern (e.g., Mediator) becomes an anti-pattern (God class) purely by being applied in the wrong context.
3. Anti-pattern awareness is not developer-only; the chapter explicitly extends it to managers and technical architects, since causes like deadline pressure are organizational, not just technical.
4. Watch for the catalog of surface symptoms — global variables, duplication, near-zero reuse, a dominant God class, excessive parameterless methods — as leading indicators even before you've pinned down which named anti-pattern is present.
5. This chapter is discussion-only with no runnable code; the anti-pattern concepts (God class, golden hammer, zero-means-null, not-invented-here) are language-agnostic and apply unchanged to modern C# codebases.

## Connects To
- **Ch 21 (Mediator)**: The God class anti-pattern is explicitly tied back to an inappropriately broad Mediator implementation, giving a concrete pattern-to-anti-pattern failure mode.
- **Ch 27 (Criticisms of Design Patterns)**: This chapter is the direct continuation of Chapter 27's closing claim that misapplied patterns degrade into anti-patterns — Chapter 27 raises the idea, this chapter catalogs it.
- **Refactoring literature**: The chapter's definition of refactoring (improving design without changing external behavior) matches the mainstream refactoring literature (e.g., Fowler) and is the standard prescribed remedy once an anti-pattern is confirmed.
