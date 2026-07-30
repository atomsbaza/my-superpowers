# Cheatsheet

## Decision Rules

- **Before reaching for any GoF pattern**: ask "does modern C#/.NET already give me this for free?" (records, pattern matching, DI container, `IEnumerable`/LINQ, ASP.NET Core middleware). 2025/26 practitioner consensus: blindly applying all 23 patterns is worse than not using them. (modern-csharp-notes.md)
- **When you need exactly one instance of something**: use `services.AddSingleton<T>()` in your DI container, not a hand-written Singleton class with a static accessor — the container already owns lifetime/creation/disposal safely. (Ch1)
- **When creation logic is itself a business rule** (e.g., picking a notification channel by user attributes): a small Factory (often a `switch` expression) is still justified. **When creation logic is just object wiring**: let the DI container do it — don't write a factory class. (Ch4, Ch5, Ch24)
- **When you need to add behavior to an object without changing its interface**: Decorator (adds responsibility) vs. Proxy (controls access) vs. Adapter (converts interface) — all three "wrap and delegate," but the *intent* differs. If you're translating a mismatched interface, it's Adapter. If you're gating/controlling access, it's Proxy. If you're layering an orthogonal concern (caching, logging, retry), it's Decorator. (Ch6, Ch7, Ch8)
- **When behavior must vary at runtime and you're tempted to write a long `if`/`switch` chain**: Strategy. In modern C#, prefer injecting `IEnumerable<IStrategy>` via DI or expressing the choice as a pattern-matching `switch` expression over writing a rigid class hierarchy. (Ch15)
- **When several classes share the same algorithm shape but differ in specific steps**: Template Method (inheritance-based) is the classic answer, but modern C# increasingly prefers composition — inject `Func<>`/`Action<>` delegates into a pipeline instead of subclassing a base class. Reach for composition first; use Template Method only in framework-level code where strict execution order must be enforced. (Ch16)
- **When you need undo/redo or auditable actions**: Command (the action itself as an object) pairs with Memento (state snapshots for restoring). In 2025/26 practice, Commands are typically `record` types dispatched through a mediator library. (Ch17, Ch19)
- **When many objects need to talk to each other**: don't let them reference each other directly — introduce a Mediator. As of 2025/26 this is usually a library (MediatR) rather than a hand-rolled mediator class, with pipeline behaviors handling cross-cutting concerns. (Ch21)
- **When a request should be handled by one of several possible handlers, chosen dynamically**: Chain of Responsibility. In ASP.NET Core, this is just middleware — don't hand-roll a linked-list-of-handlers unless you're outside a pipeline-based framework. (Ch22)
- **When "no object" is a legitimate, expected outcome**: return a Null Object instead of `null`, but don't let it silently mask a genuine missing-data bug — make sure "no object" really is a valid domain state before reaching for this. (Ch25)

## Decision Tree: Proxy vs. Decorator vs. Adapter (the three "wrap and delegate" patterns)

1. Does the wrapper need to present a **different interface** than the wrapped object (translating between an existing class and what the client expects)?
   - Yes → **Adapter**.
   - No (same interface as the wrapped object) → continue.
2. Is the wrapper's purpose to **control or gate access** to the wrapped object (lazy loading, authorization, caching as a stand-in, remote-call indirection)?
   - Yes → **Proxy**.
   - No → continue.
3. Is the wrapper's purpose to **add an orthogonal responsibility** (logging, additional caching-as-cross-cutting-concern, retry) that could be layered/stacked with other similar wrappers?
   - Yes → **Decorator**.
(Ch6, Ch7, Ch8, Ch9 Q&A)

## Decision Tree: Factory Method vs. Abstract Factory vs. Simple Factory

1. Are you creating **one product**, and does the choice of concrete type matter enough to warrant a subclass hierarchy?
   - Yes → **Factory Method** (subclasses override a creator method).
2. Are you creating a **family of related products** that must be used together consistently (e.g., a themed UI toolkit)?
   - Yes → **Abstract Factory** (one interface, one creation method per product in the family).
3. Do you just need **centralized creation logic based on a simple input condition**, without a subclass hierarchy?
   - Yes → **Simple Factory** (not in the original GoF catalog — a single method/`switch` expression is enough; don't over-engineer this into Factory Method or Abstract Factory if the choice is just an `if`/`switch`).
(Ch4, Ch5, Ch24)

## Trade-off Matrix: GoF Pattern Status in Modern C# (2025/26)

| Category | Still hand-written mostly as-shown | Now usually record/delegate-based | Now usually framework/library-provided |
|---|---|---|---|
| Creational | Builder, Prototype | Simple Factory (switch expressions) | Singleton (DI container), Factory Method/Abstract Factory (DI) |
| Structural | Composite, Bridge, Flyweight | — | Proxy (HTTP clients/resilience libs), Adapter (still hand-written but at integration edges only) |
| Behavioral | State, Null Object, Memento (as records) | Strategy, Command | Observer (events/message brokers), Iterator (`IEnumerable`/LINQ), Chain of Responsibility (middleware), Mediator (MediatR) |
(modern-csharp-notes.md — full detail per pattern)

## Thresholds & Defaults

- **A Facade that has grown to coordinate more than a handful of subsystem calls** is trending toward a God-class anti-pattern — keep Facades thin and delegating, not doing real work themselves. (Ch9, Ch28)
- **Adding a new element type to a Visitor-based hierarchy** requires updating every Visitor implementation — if element types change more often than operations, prefer pattern matching over Visitor. (Ch13)
- **A Chain of Responsibility longer than a few handlers** becomes hard to trace manually — prefer a framework-provided pipeline (ASP.NET Core middleware) over a hand-built chain once it grows. (Ch22)

## Tells & Smells

- **A class with a private constructor and a static `Instance` property, accessed from many unrelated places** → classic hand-rolled Singleton; in 2025/26 this is usually better expressed as a DI-registered singleton service. (Ch1)
- **A base class with an abstract method meant to be overridden, and a fixed algorithm method calling it** → Template Method; check whether composition (injected delegates) would be more flexible before extending this hierarchy further. (Ch16)
- **Deeply nested `if`/`switch` blocks selecting behavior based on a type/category field** → Strategy pattern opportunity (or, in modern C#, a pattern-matching `switch` expression directly). (Ch15, Ch24)
- **A repository class whose methods just forward to `DbContext` calls with no added logic** → Repository anti-pattern; EF Core's `DbContext` already provides the abstraction — only keep a repository if it protects invariants or coordinates complex persistence. (modern-csharp-notes.md)
- **Manual subscriber-list management (`Attach`/`Detach`/`Notify`) written by hand in application code** → reinventing what C# `event`/`delegate` (or a message bus) already provides — a red flag in 2025/26 code review. (Ch14)
- **A class doing "everything" for a feature — data access, validation, business rules, and presentation formatting all in one place** → God class anti-pattern; look for where a Facade, Mediator, or clearer layering should have split responsibilities. (Ch28)

## GoF Pattern Classification (Purpose × Scope)

All 23 patterns, GoF's Table 1.1 (Section 1.5). Note **Adapter is the only pattern that spans both scopes** — a class-scope version (via inheritance) and an object-scope version (via composition).

| Scope | Creational | Structural | Behavioral |
|---|---|---|---|
| **Class** | Factory Method | Adapter (class) | Interpreter, Template Method |
| **Object** | Abstract Factory, Builder, Prototype, Singleton | Adapter (object), Bridge, Composite, Decorator, Facade, Flyweight, Proxy | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Visitor |

(ch31-gof-introduction.md)

## GoF's Own Pattern-Selection Procedure

GoF's actual recommended steps for choosing a pattern (Section 1.7, "How to Select a Design Pattern"):

1. **Consider how design patterns solve design problems** — start from the "cause of redesign" you're facing (e.g., algorithmic dependencies, tight coupling to a concrete class) and note which patterns are documented as addressing that specific cause.
2. **Scan each candidate's Intent section** — the one- or two-sentence Intent is often enough to rule a pattern in or out for your specific problem.
3. **Study how patterns interrelate** — several patterns are commonly used together or are natural alternatives to each other; understanding the relationships (see each chapter's Related Patterns / Connects To) prevents picking one in isolation when a pair is the better fit.
4. **Study patterns of like purpose** — compare all patterns within the same Creational/Structural/Behavioral group side by side, since the right answer is often "which one of these three" rather than "is it this pattern at all."
5. **Examine a cause of redesign** — use the "aspects that vary" framing (Table 1.2) as the prescriptive counterpart to step 1's diagnostic framing: if you already know what needs to vary, find the pattern whose row names exactly that aspect.
6. **Consider what should be variable in your design** — the general design-for-change question underlying the whole exercise: identify the concept most likely to change, and let that drive which pattern (if any) is worth the added indirection.

(ch31-gof-introduction.md)
