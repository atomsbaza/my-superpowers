# Chapter 13: Patterns in the Real World

## Core Idea

A pattern is a solution to a problem in a context. The problem describes the recurring design pressure, the context explains when it appears, and the solution describes a reusable structure and collaboration. Patterns are communication tools and practical design guidance, not rigid recipes.

## Frameworks Introduced

- **Pattern statement**:
  - Context: the situation in which the forces arise.
  - Problem: the recurring goal or difficulty.
  - Forces: competing goals and constraints that shape the trade-off.
  - Solution: a proven arrangement of responsibilities and collaborations.
- **Pattern catalog entry**: name, intent, motivation, applicability, structure, participants, collaborations, implementation, sample code, known uses, related patterns, and consequences.
- **Rule of Three**: a design is more plausibly a pattern when it has been applied in at least three real-world situations.
- **Pattern categories**:
  - Creational patterns address object creation.
  - Behavioral patterns address communication and responsibility.
  - Structural patterns address composition and relationships.
  - Class patterns use inheritance; object patterns use composition and collaboration.
- **Anti-pattern**: a commonly chosen path from a problem to a bad solution. It explains why the bad solution is attractive, why it fails, and what alternatives can improve it.

## Key Concepts

- **Intent**: the short answer to what the pattern accomplishes.
- **Applicability**: conditions that indicate the pattern may fit.
- **Forces**: tensions such as flexibility versus simplicity, reuse versus coupling, or speed versus consistency.
- **Consequences**: benefits and liabilities that follow from adopting the pattern.
- **Known uses**: evidence that the structure appears in real systems.
- **Pattern vocabulary**: shared names that make design discussions more precise.
- **KISS**: keep the design as simple as the current requirements permit.
- **Refactoring to patterns**: introduce a pattern in response to an observed design pressure, then remove it if the pressure disappears.
- **Pattern fever**: forcing patterns into code because they are fashionable or familiar.

## Mental Models

- A pattern is a map, not a destination. It tells you how a recurring problem has been navigated, but context determines whether the route is worthwhile.
- Forces are the reason a pattern exists. If there is no meaningful tension, the extra abstraction is likely ceremony.
- Pattern names improve team bandwidth: “use an Adapter” communicates a compatibility boundary faster than a paragraph of implementation detail.
- Every pattern has consequences. A flexible extension point may add indirection, classes, runtime wiring, or debugging cost.
- Start with the simplest design that works, watch for a recurring pressure, then refactor toward the pattern.

## Anti-patterns

- **Pattern fever**: using a Factory, Singleton, or Strategy where a direct constructor or function is clearer.
- **Overengineering**: designing for hypothetical variation that has no credible requirement.
- **Cargo-cult pattern**: copying a diagram without understanding its forces or consequences.
- **Pattern name as proof**: arguing that a design is good merely because it can be labeled with a pattern.
- **Ignoring local context**: applying a pattern whose trade-offs do not fit the language, team, scale, or operational constraints.

## Code Examples

~~~java
public final class ReportExporter {
    private final ExportStrategy strategy;

    public ReportExporter(ExportStrategy strategy) {
        this.strategy = strategy;
    }

    public byte[] export(Report report) {
        return strategy.export(report);
    }
}
~~~

- The pattern label is less important than the force being addressed: export formats vary independently from the caller. If there are only one or two stable formats and no expected variation, a direct implementation may be the better design.

## Reference Tables

| Pattern category | Main question | Examples from this book |
|---|---|---|
| Creational | How should objects be created? | Factory Method, Abstract Factory, Singleton |
| Behavioral | How should objects communicate or vary behavior? | Strategy, Observer, Command, Template Method, Iterator, State |
| Structural | How should objects be composed or wrapped? | Decorator, Adapter, Facade, Composite, Proxy |

| Good pattern use | Warning sign |
|---|---|
| Responds to a concrete recurring pressure | Solves a hypothetical future problem |
| Makes a change easier to localize | Adds indirection without reducing coupling |
| Has understood consequences | Copies a canonical diagram mechanically |
| Improves shared vocabulary | Uses a pattern name to avoid explaining trade-offs |

## Worked Example

Suppose a team adds multiple report export formats. At first, one conditional is simple. As formats gain independent validation, configuration, and tests, the conditional becomes a change hotspot. The team can extract an ExportStrategy and select it through composition. The pattern is justified by the force of independent algorithm variation. If the product later supports only one format, the abstraction should be reconsidered rather than preserved for its own sake.

## Key Takeaways

1. State context, problem, forces, solution, and consequences—not just a class diagram.
2. Learn patterns by recognizing the design pressure they address.
3. Use Rule of Three and known uses as evidence, not as a substitute for judgment.
4. Prefer the simplest design that handles current forces.
5. Refactor toward patterns when repeated changes reveal a stable structure.
6. Learn anti-patterns so attractive but costly solutions become easier to spot.

## Connects To

- **Chapter 1 — Strategy**: pattern thinking starts by isolating what varies.
- **Chapter 12 — Compound Patterns**: compound designs require an explicit account of each pattern’s role.
- **Appendix — Leftover Patterns**: pattern categories provide a map for exploring beyond the main examples.

