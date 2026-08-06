---
name: head-first-design-patterns
description: Apply the object-oriented design principles and patterns from Head First Design Patterns to design, refactoring, review, and teaching tasks. Use when a problem involves changing behavior, object creation, collaboration, composition, state, access, or extensibility.
---

# Head First Design Patterns

This skill turns Head First Design Patterns, 2nd edition, by Eric Freeman, Elisabeth Robson, Kathy Sierra, and Bert Bates into a practical design-pattern reference. It is optimized for reasoning about extensible, maintainable object-oriented software, especially Java-style designs.

## How to use this skill

Start with the design pressure, not the pattern name:

1. Identify what varies, who owns the decision, and what must remain stable.
2. Name the coupling or responsibility that makes the current design hard to change.
3. Choose the smallest pattern or refactoring that addresses that pressure.
4. Check consequences: indirection, object count, lifecycle, testing, performance, and team comprehension.
5. Explain the resulting collaboration in terms of roles and runtime messages.

Use the chapter files for focused study and the references for fast lookup:

- [Learning path and principles](chapters/intro-head-first-learning.md)
- [Chapter 1 — Strategy](chapters/ch01-strategy.md)
- [Chapter 2 — Observer](chapters/ch02-observer.md)
- [Chapter 3 — Decorator](chapters/ch03-decorator.md)
- [Chapter 4 — Factory](chapters/ch04-factory.md)
- [Chapter 5 — Singleton](chapters/ch05-singleton.md)
- [Chapter 6 — Command](chapters/ch06-command.md)
- [Chapter 7 — Adapter and Facade](chapters/ch07-adapter-facade.md)
- [Chapter 8 — Template Method](chapters/ch08-template-method.md)
- [Chapter 9 — Iterator and Composite](chapters/ch09-iterator-composite.md)
- [Chapter 10 — State](chapters/ch10-state.md)
- [Chapter 11 — Proxy](chapters/ch11-proxy.md)
- [Chapter 12 — Compound Patterns](chapters/ch12-compound-patterns.md)
- [Chapter 13 — Patterns in the Real World](chapters/ch13-real-world-patterns.md)
- [Chapter 14 — Leftover Patterns](chapters/ch14-leftover-patterns.md)
- [Pattern catalog](references/pattern-catalog.md)
- [Pattern comparison matrix](references/comparison-matrix.md)
- [Java design checklist](references/java-design-checklist.md)
- [Glossary](references/glossary.md)
- [Source map](references/source-map.md)

## Operating principles

### Encapsulate what varies

Find the behavior that changes, extract it behind an abstraction, and keep stable code independent of its concrete implementations. This is the central move behind Strategy, State, Factory, Command, and many of the structural patterns.

### Program to an interface

Depend on a stable supertype or capability contract rather than a concrete implementation. The goal is to make clients work with a family of objects and to localize construction and substitution decisions.

### Favor composition over inheritance

Compose objects at runtime when behavior should vary independently or be combined. Use inheritance when a true shared algorithm skeleton or subtype relationship is the better fit, as with Template Method.

### Strive for loosely coupled designs

The communicating objects should know as little as practical about one another. Observer, Mediator, Facade, Adapter, and Proxy each reduce a different kind of coupling.

### Classes should be open for extension but closed for modification

When a requirement repeatedly causes edits to stable code, look for a polymorphic extension point. Do not treat the principle as a ban on all modification; use it to control change hotspots.

### Depend on abstractions

High-level policy and low-level details should meet through abstractions. Factories and dependency injection help keep concrete construction out of policy code.

### Use the Principle of Least Knowledge

An object should interact with only its close friends. Avoid chaining through strangers, and use Facade or a clearer collaboration boundary when a subsystem’s internal relationships leak outward.

### Let each class have one reason to change

Separate responsibilities that change for different reasons. Iterator separates traversal; Command separates request invocation; MVC separates model, presentation, and input concerns.

## Pattern selection guide

| Design pressure | First patterns to inspect | Diagnostic question |
|---|---|---|
| Several algorithms vary independently | Strategy, Template Method | Is the whole algorithm replaceable, or only a few steps? |
| Many objects need synchronized updates | Observer, Mediator | Should dependents subscribe, or should a coordinator mediate? |
| Add behavior without editing a class | Decorator, Visitor | Is the extension per object, or an operation across a stable structure? |
| Concrete construction spreads through clients | Factory Method, Abstract Factory, Builder, Prototype | Are you varying one product, a product family, construction steps, or copying? |
| Exactly one shared service is genuinely required | Singleton | Is uniqueness a domain constraint, or merely a convenience for global access? |
| Requests need undo, queueing, or logging | Command, Memento | Should the action be an object, and where will prior state live? |
| Interfaces do not match | Adapter | Which existing interface does the client expect? |
| A subsystem is too complex for clients | Facade | What smaller use-case interface can hide orchestration? |
| A sequence is stable but steps vary | Template Method | Which steps are primitive operations and which are hooks? |
| Traversal leaks collection representation | Iterator | Can every aggregate expose a common traversal protocol? |
| An object changes behavior across lifecycle phases | State | What are the states, events, guards, and transitions? |
| Access needs remoting, laziness, authorization, or caching | Proxy | What access policy belongs at the boundary? |
| Individual objects and trees should be uniform | Composite | Are leaves and composites part of one recursive abstraction? |

## Reasoning rules

- Prefer a direct implementation until a real variation or coupling pressure appears.
- State the force before proposing a pattern.
- Separate pattern intent from class-diagram similarity. Adapter, Decorator, and Proxy can all wrap an object but solve different problems.
- Keep creation decisions at a boundary. A client that constructs every concrete collaborator is often coupled to change.
- Make lifecycle, thread-safety, error, and ownership rules explicit; a pattern does not supply them automatically.
- Review pattern consequences as carefully as benefits.
- If the design becomes harder to explain than the problem warrants, simplify or refactor the pattern away.

## Response format for design questions

When applying this skill to a code or architecture question, structure the answer around:

1. Current pressure and the likely change hotspot.
2. Relevant principle or pattern, including why it fits.
3. Roles and collaboration flow.
4. Minimal implementation sketch or refactoring sequence.
5. Consequences, alternatives, and tests.

Do not recommend a pattern solely because it is in this catalog. A good answer may conclude that a simpler design, dependency injection, a function, or a small refactoring is preferable.

## Source and scope

The source is the user-provided PDF:

Head First Design Patterns: Building Extensible and Maintainable Object-Oriented Software, 2nd edition, O’Reilly Media, 2021 copyright page, source filename dated 2020.

The generated notes preserve the book’s major teaching examples and definitions in condensed form. They are a study and application aid, not a replacement for the source text.

