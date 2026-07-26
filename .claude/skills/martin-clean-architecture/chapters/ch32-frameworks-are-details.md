# Chapter 32: Frameworks Are Details

## Core Idea
Frameworks are written by authors to solve their own problems, not yours, and the relationship is asymmetrically risky — you commit fully to the framework while it commits nothing to you — so treat frameworks as plugin details kept at arm's length from your business objects, never married into your inner circles.

## Frameworks Introduced
- **Asymmetric Marriage**: the one-directional commitment relationship between a developer and a framework author — you take on all the risk and burden of coupling; the author takes on none.
  - When to use: evaluating any decision to adopt a framework, especially one that asks you to derive business classes from its base classes.
  - How: recognize that framework docs pushing "derive your Entities from our base class" / "sprinkle our annotations everywhere" are asking you to marry the framework — resist by design.
- **Don't Marry the Framework**: keep frameworks in the outer circles as plugins to your core, never coupled into Entities/business objects.
  - When to use: integrating any third-party framework (DI containers, ORMs, web frameworks).
  - How: derive proxies/wrapper classes instead of deriving business objects directly from framework base classes; confine framework-aware code (e.g., `@Autowired` annotations) to the Main/composition-root component, which is allowed to be the "dirtiest, lowest-level component."

## Key Concepts
- **Framework author's motive**: authors solve their own and their peers' problems, not yours — overlap with your needs is coincidental, not guaranteed.
- **Coupling risk**: frameworks tend to violate the Dependency Rule by design, asking you to inherit their code into your innermost Entities.
- **Framework outgrowth**: a framework helpful for early features may fight you as the product matures and needs diverge from what the framework was built for.
- **Unwanted evolution**: framework upgrades can remove or change features you depended on, forcing unwanted migration work.
- **Necessary marriages**: some frameworks (e.g., STL in C++, the standard library in Java) are unavoidable and effectively mandatory — but this should still be a conscious, deliberate decision, not a reflex.

## Mental Models
- Think of framework adoption as a **marriage proposal**: read the fine print before saying "I do," because divorce (migrating away) is expensive and the author bears none of that cost.
- Use **"date it before you marry it"**: prototype/experiment with a framework behind a boundary before committing your core architecture to it.
- Think of **Main as the licensed coupling zone**: it's fine for the composition root to know about and wire up the framework (e.g., Spring); it is not fine for business logic to know the framework exists.

## Anti-patterns
- **Deriving Entities/business objects directly from framework base classes**: locks the framework into your innermost circle permanently — "the wedding ring is on your finger."
- **Sprinkling framework annotations throughout business objects** (e.g., `@Autowired` on domain classes): couples core logic to a specific DI framework's mechanics instead of confining that knowledge to Main.
- **Assuming framework popularity or free availability implies safety**: free and well-intentioned does not mean low-risk; the risk is structural (asymmetric commitment), not about the author's motives.

## Code Examples
```text
Bad:  Business objects annotated with @Autowired, extending framework base classes.
Good: Main wires dependencies via Spring; business objects have zero Spring imports;
      framework integration happens through proxy/adapter classes that are plugins
      to the business rules, following the Dependency Rule.
```
- **What it demonstrates**: the correct placement of framework coupling — confined to Main / outer-circle adapters, never in Entities or use cases.

## Worked Example
Martin uses Spring (a Java DI framework) as the running example. The naive approach sprinkles `@autowired` annotations throughout business objects, coupling them directly to Spring's mechanics. The recommended approach: let Spring auto-wire dependencies, but only within the Main component — the lowest-level, "dirtiest" part of the system that is expected to know about frameworks and wiring. Business objects remain framework-ignorant. If the framework insists you derive business objects from its base classes, the answer is "say no" — write proxy classes instead, and keep those proxies in plugin components that depend on (not are depended upon by) the business rules.

## Key Takeaways
1. Never derive Entities or use-case classes from framework base classes — write proxies/adapters instead.
2. Confine framework-specific code (annotations, imports, configuration) to Main or a thin outer-circle wiring layer.
3. Treat framework adoption as a long-term commitment decision to be made deliberately, not a reflexive "just import it."
4. Distinguish frameworks you can reasonably decouple from (web/DI/ORM frameworks) from those you effectively must marry (language standard libraries) — but make even the latter a conscious choice.
5. A framework helping you ship early features can become an obstacle as your product outgrows its assumptions — plan the exit path before you need it.

## Connects To
- **Ch 30/31**: Same "keep details out of the core" logic applied to databases and the web — frameworks are the third leg of this triad.
- **Dependency Rule (Ch 22)**: frameworks that force inward dependencies directly violate it; proxies restore compliance.
