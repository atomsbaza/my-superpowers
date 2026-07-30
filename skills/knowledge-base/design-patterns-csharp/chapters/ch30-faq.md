# Chapter 30: FAQ

## Core Idea
This chapter is a cross-cutting roundup of the book's most useful pattern-vs-pattern distinctions, gathered so a reader can quickly compare patterns that are structurally or conceptually similar without re-reading every chapter's individual Q&A section.

## Frameworks Introduced
- **Pattern-comparison-by-intent**: When two patterns look alike (similar UML or similar mechanism), resolve the ambiguity by comparing their stated intent and category (creational/structural/behavioral) rather than their diagrams.
  - When to use: Any time you're deciding between two patterns that could both structurally solve a problem (e.g., Builder vs. Strategy, Chain of Responsibility vs. Decorator).
  - How: Ask what each pattern is *for* first (construction vs. algorithm selection, access control vs. responsibility addition), then let that answer — not the class diagram — drive the choice.

## Key Concepts
- **Class patterns vs. object patterns (GoF classification)**: Class patterns rely on static, compile-time inheritance relationships; object patterns rely on dynamic, runtime object composition/relationships.
- **Creational / Structural / Behavioral**: The GoF's three top-level categories — instantiation concerns, composition-into-larger-structures concerns, and algorithm/responsibility/communication concerns, respectively.
- **GoF's 23 patterns**: The foundational catalog from *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides, 1994) — 5 creational, 7 structural, 11 behavioral.
- **Christopher Alexander's original pattern concept**: Patterns originated in building architecture, not software — Alexander described a recurring problem and a reusable core solution "without ever doing it the same way twice," a definition the GoF explicitly ported to object-oriented design.

## Mental Models
- Use "focus on intent first" as the tie-breaker whenever two patterns share a UML shape — the chapter repeatedly resolves lookalikes (Builder/Strategy, Chain of Responsibility/Decorator) this way rather than by structure.
- Treat GoF's two-axis classification (purpose: creational/structural/behavioral; scope: class vs. object) as a grid, not a single list — a pattern's position on both axes explains why it resembles some patterns and not others.
- Think of design patterns as a shared vocabulary/template layer, not language-specific tools — the underlying ideas transfer across languages, though a given language's features (e.g., C#'s native iterators) may make some patterns unnecessary to hand-implement.

## Anti-patterns
Not applicable — this is a Q&A/reference chapter; anti-patterns are covered in Chapter 28.

## Code Examples
No significant code examples in this chapter — it is a pure Q&A digest.

## Reference Tables
| | Class Patterns | Object Patterns |
|---|---|---|
| Creational | Can defer object creation to subclasses | Can defer object creation to another object |
| Structural | Focuses on composition of classes (primarily via inheritance) | Focuses on different ways of composing objects |
| Behavioral | Describes algorithms and execution flows | Describes how different objects work together to complete a task |

GoF's 23-pattern catalog by category (from the chapter's appendix material):
- **Creational (5)**: Singleton, Prototype, Factory Method, Builder, Abstract Factory
- **Structural (7)**: Proxy, Flyweight, Composite, Bridge, Facade, Decorator, Adapter
- **Behavioral (11)**: Observer, Strategy, Template Method, Command, Iterator, Memento, State, Mediator, Chain of Responsibility, Visitor, Interpreter

## Worked Example
A compact digest of the chapter's most broadly useful pattern-vs-pattern Q&As:

1. **Command vs. Memento** — Command stores every action (with undo/redo per action); Memento saves state only on request and has no undo/redo concept.
2. **Facade vs. Builder** — Facade makes an existing complex subsystem easier to use (abstracts details away); Builder separates the construction process from the object's representation, letting the same construction steps produce different representations.
3. **Builder vs. Strategy** — Despite similar-looking UML, Builder is creational (same construction process, multiple product types) while Strategy is behavioral (choose an algorithm at runtime); intent, not diagram shape, is the correct discriminator.
4. **Chain of Responsibility vs. Observer** — In Observer, all registered subscribers are notified in parallel; in Chain of Responsibility, a request may be handled early by any link and need not reach every member of the chain.
5. **Chain of Responsibility vs. Decorator** — Structurally similar, but at a given moment only one class handles the request in Chain of Responsibility, whereas in Decorator every wrapping class participates in handling it; Decorator is specifically about adding/removing responsibilities at runtime.
6. **Mediator vs. Observer (per the GoF)** — "These are competing patterns. Observer distributes communication by introducing observer and subject objects, whereas a mediator object encapsulates the communication between other objects." Reusable observers/subjects are typically easier to build than reusable mediators, but Mediator gives stronger control over the flow of communication.
7. **Singleton vs. static class** — Singleton supports object creation semantics (so inheritance/polymorphism apply) and is generally considered easier to mock in unit tests; a static class cannot be instantiated or subclassed.
8. **Proxy vs. Adapter** — Proxies expose the *same* interface as their subject; Adapters expose a *different* interface to bridge otherwise-incompatible objects.
9. **Proxy vs. Decorator** — Some proxy variants (e.g., protection proxies) can resemble decorators structurally, but Decorator's purpose is adding responsibilities while Proxy's purpose is controlling access to an object.
10. **Simple Factory vs. Factory Method vs. Abstract Factory** — All three encapsulate object creation and promote coding to an abstraction/interface rather than a concrete class, reducing dependency on concrete types; they differ in mechanism and scope (see Chapter 5's Q&A for the detailed breakdown).

## Key Takeaways
1. When two patterns share structure or UML shape, resolve the choice by comparing stated intent and GoF category (creational/structural/behavioral, class/object), not by diagram similarity.
2. Observer and Mediator are explicitly framed by the GoF as "competing" patterns for decoupling communication — Observer favors reusability of individual parts, Mediator favors centralized control over the flow.
3. Singleton and Factory Method both control object creation but for opposite goals: Singleton restricts you to exactly one instance; Factory Method exists to produce as many (non-unique) instances as needed.
4. Proxy, Adapter, and Decorator are frequently confused because they can share implementation shape, but each has a distinct primary purpose: same-interface access control (Proxy), interface translation (Adapter), and runtime responsibility addition (Decorator).
5. This chapter's discussions and comparisons are pattern-intent level, not code-level, so they remain fully applicable to modern C#; where earlier chapters' code samples used pre-modern idiom (WinForms, manual dispose, no `IEnumerable`/`yield`-based iterators), this FAQ's comparisons are unaffected by that vintage.

## Connects To
- **Ch 5 (Factory Method) / Simple Factory / Abstract Factory**: This chapter's Q&A 15-17 explicitly point back to Chapter 5 for the detailed similarities/differences discussion among the three factory-style patterns.
- **Ch 21 (Mediator) and Observer pattern chapters**: Q&A 9 directly cross-references the two-workers-and-a-boss example from the Mediator chapter to illustrate why Mediator's two-way control differs from Observer's distributed notification.
- **Appendix A (GoF catalog overview)**: The class-vs-object-patterns table and the 23-pattern category breakdown reproduced here originate in the book's closing appendix summarizing the full GoF catalog and its historical origin in Christopher Alexander's architectural pattern language.
