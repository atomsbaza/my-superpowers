# Chapter 31: GoF Introduction — What Is a Design Pattern?

## Core Idea
A design pattern names, abstracts, and identifies the key aspects of a recurring communicating-object structure that solves a general design problem in a particular context — GoF's own adaptation of Christopher Alexander's definition of a pattern in architecture.

## Frameworks Introduced
- **The four essential elements of a pattern**: pattern name, problem, solution, consequences.
  - When to use: whenever documenting or evaluating any reusable design so it can be taught, compared, and applied consistently.
  - How: name the design to build a shared vocabulary; state the problem (when to apply it, including any preconditions); describe the solution as an abstract template of elements, relationships, responsibilities, and collaborations (not a concrete implementation); enumerate the consequences — the results and trade-offs, particularly impact on flexibility, extensibility, portability, space, and time.
- **Purpose × Scope classification (Section 1.5)**: organize the 23-pattern catalog along two independent axes so related patterns can be found and compared.
  - When to use: when selecting a pattern, or when trying to understand how one pattern relates to a family of others.
  - How: classify by *purpose* — what the pattern does (Creational / Structural / Behavioral) — and by *scope* — whether it applies to classes (static, fixed at compile-time via inheritance) or objects (dynamic, changeable at run-time). See Reference Tables below.
- **"Program to an interface, not an implementation"**: don't declare variables as instances of particular concrete classes; commit only to an interface defined by an abstract class.
  - When to use: any time client code needs to remain unaware of the concrete types or classes of the objects it collaborates with.
  - How: define an abstract class establishing the common interface; have concrete subclasses implement it; instantiate concrete classes only through creational patterns (Abstract Factory, Builder, Factory Method, Prototype, Singleton) so the rest of the system stays written in terms of interfaces.
- **"Favor object composition over class inheritance"**: assemble behavior at run-time from black-box objects rather than baking it into a compile-time class hierarchy.
  - When to use: whenever inheritance would expose subclasses to a parent's implementation details ("inheritance breaks encapsulation") or would need to change behavior after compile-time.
  - How: give the composed objects well-defined interfaces (black-box reuse) instead of exposing internals (white-box reuse via inheritance); accept the cost of more objects and behavior determined by run-time interrelationships rather than by one class.

## Key Concepts
- **White-box reuse**: reuse via class inheritance; the internals of the parent class are visible to and can be relied upon by the subclass.
- **Black-box reuse**: reuse via object composition; no internal details of the composed objects are visible, only their interfaces.
- **Delegation**: a receiving object forwards (delegates) an operation to a delegate object, passing itself along so the delegate can refer back to the original receiver — an extreme, maximally flexible form of composition that can replace inheritance entirely (e.g., State, Strategy, Visitor all depend on it).
- **Aggregation vs. acquaintance**: aggregation means one object owns/is responsible for another with identical lifetimes (diamond-arrow in GoF's notation); acquaintance ("association"/"using") means an object merely knows of and can request operations on another, with no ownership and much looser, more transient coupling (plain arrow).
- **Class inheritance vs. interface inheritance (subtyping)**: class inheritance defines an object's implementation in terms of another's (code/representation sharing, fixed at compile-time); interface inheritance describes when one object can be substituted for another (subtyping) — languages like C++/Eiffel conflate the two, but design patterns often depend on keeping them conceptually distinct.
- **Framework vs. toolkit vs. design pattern**: a toolkit is a library of reusable classes providing general-purpose functionality without imposing an application architecture (code reuse, "you call it"); a framework is a reusable design for a specific class of applications that dictates the architecture and calls your code (design reuse, "it calls you" — inversion of control); a design pattern is more abstract than either — it's never embodied directly in executable code, is a smaller architectural element than a framework, and is less domain-specific.
- **Dynamic binding / polymorphism**: the run-time association of a request to an object and one of its operations, letting a client substitute objects with identical interfaces for each other without knowing their concrete types — the mechanism that makes "program to an interface" actually work.
- **Parameterized types (generics/templates)**: a third axis (alongside inheritance and composition) for varying behavior, by supplying an unspecified type as a parameter at the point of use; unlike composition, the bound type can't change at run-time.

## Mental Models
- Use the Purpose × Scope table as a map, not a rulebook: when you know *what kind of variation* you need (object creation vs. structure vs. interaction) and *when* it needs to vary (compile-time class relationships vs. run-time object relationships), you've already narrowed 23 patterns down to a small cell.
- Think of "causes of redesign" as the diagnostic entry point and "aspects that vary" (Table 1.2) as the prescriptive entry point to the same catalog — one starts from the pain, the other from the design goal; GoF explicitly recommend trying both.
- Treat framework, toolkit, and pattern as three different levels of reuse granularity on the same spectrum: toolkit reuses code, pattern reuses a documented design idea (never runnable on its own), framework reuses an entire runnable architecture built from several patterns.
- A pattern is "a solution to a problem in a context," not a ready-made component — it must always be re-implemented and adapted each time it's applied, unlike a class from a toolkit that you just instantiate.

## Anti-patterns
- **Modeling classes strictly on real-world nouns**: strict fidelity to the analysis model's real-world objects produces a system that reflects today's domain but resists tomorrow's changes; flexible abstractions (e.g., Composite's uniform treatment of objects, Strategy's algorithm-as-object) often have no physical counterpart and are discovered later, not during initial analysis.
- **Hard-coding object creation with explicit constructor calls to concrete classes**: commits the codebase to a specific implementation everywhere that class is instantiated, complicating any future change of concrete type — this is exactly what the creational patterns exist to avoid.
- **Applying a design pattern indiscriminately**: patterns often introduce extra indirection that adds design complexity and can cost performance; a pattern should be applied only when the flexibility it buys is actually needed — read a pattern's Consequences section to judge this before applying it.
- **Confusing class inheritance with interface inheritance**: because most languages (C++, Eiffel) don't force the distinction, it's easy to inherit implementation you didn't want merely to get the interface (or vice versa), silently coupling a subclass to a parent's internals it should never have depended on.

## Code Examples
```cpp
// MonoGlyph-style delegation illustrating "favor composition, program to an interface":
// Window delegates to Rectangle instead of inheriting from it.
class Window {
public:
    double Area() { return _rectangle->Area(); }  // delegates, doesn't inherit
private:
    Rectangle* _rectangle;   // "has a" Rectangle, not "is a" Rectangle
};
// Swapping _rectangle for a Circle instance at run-time (given a compatible
// interface) changes Window's shape without touching Window's own code —
// this is exactly the flexibility class inheritance cannot offer, since
// inheritance is resolved at compile-time.
```
- **What it demonstrates**: object composition plus delegation lets a run-time substitution ("become circular instead of rectangular") happen without recompiling or subclassing — the concrete illustration behind "favor object composition over class inheritance."

## Reference Tables

**Table 1.1 — Design pattern space (Purpose × Scope), reproduced from Section 1.5:**

|       |        | Creational (Purpose)                                                 | Structural (Purpose)                                                                                            | Behavioral (Purpose)                                                                                                                              |
|-------|--------|------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Class (Scope)  | | Factory Method                                                          | Adapter (class)                                                                                                    | Interpreter, Template Method                                                                                                                           |
| Object (Scope) | | Abstract Factory, Builder, Prototype, Singleton                        | Adapter (object), Bridge, Composite, Decorator, Facade, Flyweight, Proxy                                            | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Visitor                                                     |

**Table 1.2 — Design aspects that design patterns let you vary, reproduced from Section 1.7:**

| Purpose    | Pattern                    | Aspect(s) That Can Vary                                                                     |
|------------|-----------------------------|-----------------------------------------------------------------------------------------------|
| Creational | Abstract Factory            | families of product objects                                                                  |
| Creational | Builder                     | how a composite object gets created                                                          |
| Creational | Factory Method               | subclass of object that is instantiated                                                      |
| Creational | Prototype                   | class of object that is instantiated                                                          |
| Creational | Singleton                   | the sole instance of a class                                                                  |
| Structural | Adapter                     | interface to an object                                                                        |
| Structural | Bridge                      | implementation of an object                                                                    |
| Structural | Composite                   | structure and composition of an object                                                        |
| Structural | Decorator                   | responsibilities of an object without subclassing                                              |
| Structural | Facade                      | interface to a subsystem                                                                       |
| Structural | Flyweight                   | storage costs of objects                                                                       |
| Structural | Proxy                       | how an object is accessed; its location                                                        |
| Behavioral | Chain of Responsibility      | object that can fulfill a request                                                              |
| Behavioral | Command                     | when and how a request is fulfilled                                                            |
| Behavioral | Interpreter                 | grammar and interpretation of a language                                                        |
| Behavioral | Iterator                    | how an aggregate's elements are accessed, traversed                                             |
| Behavioral | Mediator                    | how and which objects interact with each other                                                 |
| Behavioral | Memento                     | what private information is stored outside an object, and when                                 |
| Behavioral | Observer                    | number of objects that depend on another object; how the dependent objects stay up to date       |
| Behavioral | State                       | states of an object                                                                             |
| Behavioral | Strategy                    | an algorithm                                                                                    |
| Behavioral | Template Method              | steps of an algorithm                                                                           |
| Behavioral | Visitor                     | operations that can be applied to object(s) without changing their class(es)                    |

## Worked Example
GoF's own **"How to Select a Design Pattern"** (Section 1.7), applied to a concrete choice — suppose you're designing a text-compositing feature and need to decide which pattern handles "let the linebreaking algorithm vary":

1. **Consider how design patterns solve design problems (Section 1.6)** — the problem is "algorithmic dependencies": objects depending directly on an algorithm must change whenever that algorithm changes. GoF list Builder, Iterator, Strategy, Template Method, Visitor as the patterns that address exactly this cause of redesign.
2. **Scan Intent sections** — of that shortlist, Strategy's intent ("define a family of algorithms, encapsulate each one, make them interchangeable") matches "swap linebreaking algorithms" precisely; Builder's intent (construct a complex object step by step) and Visitor's (add operations without changing element classes) don't fit this specific problem.
3. **Use Table 1.1** to confirm Strategy's placement — Behavioral, Object scope — meaning the variation is resolved at run-time via object collaboration, not at compile-time via class hierarchy. That matches the requirement to potentially change algorithms without recompiling.
4. **Consider what should be variable (Table 1.2)** — Strategy's row says explicitly "an algorithm" varies; this is the aspect we want to change without redesign, confirming the match from the opposite direction.
5. **Having selected Strategy**, apply GoF's **"How to Use a Design Pattern"** (Section 1.8): read the pattern once for Applicability/Consequences to confirm fit → study Structure/Participants/Collaborations → study Sample Code → choose application-specific names for participants (e.g., `Compositor` instead of the generic `Strategy`, `Composition` instead of `Context`) → define the classes and their interfaces → define application-specific operation names (e.g., `Compose` instead of a generic `Execute`) → implement the operations.

This exact reasoning chain — problem → intent scan → classification confirmation → aspect-that-varies confirmation → naming/implementation — is what GoF's Chapter 2 case study (ch32) performs in miniature for each of Lexi's seven design problems.

## Key Takeaways
1. A pattern always has four parts — name, problem, solution, consequences — and skipping the consequences discussion (the part people most often omit) is what turns pattern-application into cargo-culting.
2. The Purpose × Scope table is a navigation tool, not a taxonomy to memorize; use it alongside "causes of redesign" and "aspects that vary" as three independent entry points into the same 23-pattern catalog.
3. "Program to an interface, not an implementation" and "favor object composition over class inheritance" are GoF's two foundational principles — nearly every pattern in the catalog is an instance of applying one or both.
4. Delegation is the mechanism that lets composition match inheritance's power for code reuse — several patterns (State, Strategy, Visitor) depend on it explicitly, and understanding it is a prerequisite for understanding why those patterns are shaped the way they are.
5. Patterns are more abstract than frameworks and smaller than frameworks — never confuse "the app uses a framework" with "the app implements a pattern"; a mature framework typically incorporates several patterns.
6. Design patterns should only be applied when their added indirection is actually justified by a real, anticipated need for flexibility — over-application is explicitly called out as a misuse in Section 1.8.

## Connects To
- **Ch 15 (Strategy)**: GoF's own worked example of encapsulating an algorithm as an object (View/Controller substitution in MVC, Section 1.2) is the same mechanism the C# book's `Context`/`IChoice` example demonstrates — runtime algorithm substitution via delegation.
- **Ch 05 (Abstract Factory), Ch 07 (Decorator), Ch 11 (Composite), Ch 12 (Bridge), Ch 13 (Visitor), Ch 17 (Command), Ch 18 (Iterator)**: every pattern named in the Section 1.5 classification table and the "causes of redesign" list has a dedicated chapter earlier in this skill covering its C# implementation — this chapter is the conceptual scaffolding those chapters' concrete code sits inside.
- **Ch 32 (GoF Case Study — Lexi)**: applies the exact selection/usage procedure described here to seven concrete design problems, culminating in eight of the patterns referenced in this chapter's tables.
- **SOLID principles (external)**: "program to an interface, not an implementation" is a direct precursor to the Dependency Inversion Principle; "favor composition over inheritance" underlies the modern preference for composition-based DI containers over deep class hierarchies.
