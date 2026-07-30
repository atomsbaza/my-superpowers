# Chapter 12: Bridge Pattern

## Core Idea
Decouple an abstraction from its implementation so that the two can vary independently, by introducing a bridge interface between an abstract class hierarchy and an implementor class hierarchy.

## Frameworks Introduced
- **Bridge**: Decouple an abstraction from its implementation so that the two can vary independently.
  - When to use: You have (or anticipate) two hierarchies that both need to grow — e.g., different products and different states/behaviors — and hard-wiring them together via subclassing would cause a combinatorial explosion of classes.
  - How: An abstract class (`Abstraction`, e.g. `ElectronicGoods`) holds a reference to an `Implementor` interface (e.g. `IState`) rather than implementing behavior itself. Concrete subclasses of the abstraction (`RefinedAbstraction`, e.g. `Television`, `VCD`) delegate the actual work to whatever concrete implementor (`ConcreteImplementor`, e.g. `OnState`, `OffState`) is currently assigned, and that assignment can change at runtime.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Decouple an abstraction from its implementation so that the two can vary independently."

**Also Known As**: Handle/Body

**Applicability** — GoF says use this pattern when:
- You want to avoid a permanent binding between an abstraction and its implementation, e.g., when the implementation must be selected or switched at run-time.
- Both the abstractions and their implementations should be extensible by subclassing independently.
- Changes in the implementation of an abstraction should have no impact on clients — their code shouldn't need recompiling.
- (C++) You want to hide an abstraction's implementation completely from clients.
- You have a proliferation of classes (Rumbaugh's "nested generalizations"), indicating the need to split an object into two parts.
- You want to share an implementation among multiple objects (perhaps via reference counting), hidden from the client.

**Participants**:
- **Abstraction** (`Window`) — defines the abstraction's interface and maintains a reference to an `Implementor`.
- **RefinedAbstraction** (`IconWindow`) — extends the interface defined by Abstraction.
- **Implementor** (`WindowImp`) — defines the interface for implementation classes; need not correspond exactly to Abstraction's interface — typically it exposes only primitive operations, while Abstraction builds higher-level operations on top of them.
- **ConcreteImplementor** (`XWindowImp`, `PMWindowImp`) — implements the Implementor interface with a concrete, platform-specific implementation.

**Consequences**:
1. Decoupling interface and implementation — the implementation isn't bound permanently; it's configurable, even changeable, at run-time; eliminates compile-time dependencies, essential for binary compatibility across library versions.
2. Improved extensibility — Abstraction and Implementor hierarchies extend independently.
3. Hiding implementation details from clients — including details like implementor sharing and reference counting.

**Implementation notes**: With only one Implementor, an abstract Implementor class is a degenerate but still useful case — Carolan's "Cheshire Cat" — because clients only need relinking, not recompiling, when the implementation changes; the Implementor's class interface can live in a private C++ header hidden from clients. Deciding which ConcreteImplementor to instantiate can be done in Abstraction's constructor (parameterized by e.g. collection size), chosen as a default and switched later based on usage, or delegated entirely to an Abstract Factory that encapsulates the platform-specifics. Multiple inheritance (public from Abstraction, private from a ConcreteImplementor) can combine an interface with an implementation in C++, but this is static and therefore not a true Bridge — it binds the implementation permanently.

**Known Uses (1994-era)**: ET++'s Window/WindowPort (WindowPort keeps a back-reference to Window to notify it of platform events); libg++'s Set/LinkedSet/HashSet over LinkedList/HashTable (a degenerate bridge with no abstract Implementor); NeXT AppKit's NXImage/NXImageRep bridge for display-device-appropriate image rendering, notably capable of holding more than one NXImageRep implementation at once.

**Related Patterns (per GoF)**: An Abstract Factory can create and configure a particular Bridge. Adapter is geared toward making unrelated, already-designed classes work together after the fact; Bridge is used up-front in a design to let abstractions and implementations vary independently — same wrap-and-forward structure, opposite point in the lifecycle.

## Key Concepts
- **Abstraction**: The abstract class that defines the client-facing interface and holds a reference to an `Implementor` (`ElectronicGoods`).
- **RefinedAbstraction**: A concrete subclass of the abstraction that extends its interface (`Television`, `VCD`).
- **Implementor**: The interface for implementation classes, kept deliberately separate from the abstraction's own interface (`IState`).
- **ConcreteImplementor**: A concrete class implementing the `Implementor` interface (`OnState`, `OffState`).
- **Handle/Body pattern**: An alternate name for Bridge, emphasizing that the abstraction is a "handle" delegating to an implementation "body."
- **Composition over inheritance**: The abstraction holds the implementor by composition (a field), not by inheriting from it — this is exactly what lets the two hierarchies vary independently.
- **Bridge vs. Adapter**: Bridge is designed up front to let two hierarchies evolve independently; Adapter is applied after the fact to reconcile incompatible interfaces. They are easy to confuse but solve different problems.

## Mental Models
- Think of a software company's marketing team acting as a bridge between customers and the development team: changes in customer strategy shouldn't force changes in how development works, and vice versa, because the marketing team absorbs and translates between the two sides.
- GUI frameworks are the canonical computer-world case: a window abstraction (cross-platform) is bridged to a platform-specific window implementation (Linux, macOS) so the same abstraction code runs against different back ends.
- Use Bridge when two designs both look plausible up front — a single tightly coupled hierarchy (simple now, unmaintainable later) vs. a bridged design (slightly more structure now, cheap to extend later) — and you know new items on *either* side (new electronics like AC/DVD, new states like Sleep/Mute) are coming.

## Anti-patterns
- **Reaching for subclassing when both hierarchies need to grow**: Ties the implementation to the abstraction at compile time; the book contrasts "Approach 1" and "Approach 2" designs that look fine initially but become unmaintainable once new electronics or new states are added, because each new item across either hierarchy multiplies subclasses.
- **Confusing Bridge with Adapter**: They are structurally similar (both wrap another interface) but Adapter's sole purpose is reconciling incompatible interfaces, not letting two hierarchies vary independently.

## Code Examples
```csharp
//Implementor
public interface IState
{
    void MoveState();
}

//ConcreteImplementor-1
public class OnState : IState
{
    public void MoveState() { Console.Write("On State"); }
}

//ConcreteImplementor-2
public class OffState : IState
{
    public void MoveState() { Console.Write("Off State"); }
}

//Abstraction
public abstract class ElectronicGoods
{
    //Composition - implementor
    protected IState state;

    public IState State
    {
        get { return state; }
        set { state = value; }
    }

    abstract public void MoveToCurrentState();
}

//Refined Abstraction
public class Television : ElectronicGoods
{
    public override void MoveToCurrentState()
    {
        Console.Write("\n Television is functioning at : ");
        state.MoveState();
    }
}

public class VCD : ElectronicGoods
{
    public override void MoveToCurrentState()
    {
        Console.Write("\n VCD is functioning at : ");
        state.MoveState();
    }
}
```
- **What it demonstrates**: `ElectronicGoods` (abstraction) never implements state behavior itself — it composes an `IState` (implementor) and delegates, so new electronics and new states can each be added independently without touching the other hierarchy.

## Reference Tables
None in this chapter.

## Worked Example
The demo creates a `Television` and assigns it `IState presentState = new OnState()` via the `State` property, then calls `eItem.MoveToCurrentState()`, which prints "Television is functioning at : On State". It then swaps `presentState` to `new OffState()` and calls `MoveToCurrentState()` again, printing "Off State" — same `Television` object, different behavior, assigned at runtime. It repeats this with a `VCD` object using the same two `IState` implementors, showing that the state implementations are shared across both electronics types without either hierarchy needing to know about the other's concrete classes.

## Key Takeaways
1. Bridge is warranted specifically when *two* hierarchies both need independent extensibility — if only one side will ever grow, plain subclassing may be enough.
2. The abstraction holds the implementor as a field (composition) rather than inheriting from it; this indirection is the entire mechanism that decouples the two hierarchies.
3. Bridge and Adapter look similar in structure but differ in intent: Bridge is a design-time decision for future flexibility, Adapter is a retrofit for interface incompatibility.
4. The book's commented-out constructor code shows both a constructor-injection style and a property-setter style for wiring the implementor — either is valid; pick based on whether you need to change the implementor after construction.
5. This example predates modern C# (2018-era): the state assignment uses simple properties and abstract methods with no generics, no records, and no primary constructors — the pattern's structural intent carries over unchanged to modern idiom (see modern-csharp-notes.md).

## Connects To
- **Ch 22 (State, referenced in Q&A)**: The book explicitly warns that Bridge's use of interchangeable "state" objects can look like the State pattern, but Bridge's intent is decoupling two hierarchies while State's intent is behavior change based on internal object state.
- **GoF 1994 catalog**: Bridge is one of the seven original Structural patterns; it is frequently paired conceptually with Adapter because both wrap an interface, though for different reasons.
- **GoF 1994 canonical entry**: GoF's discussion of structural patterns sharpens the Bridge-vs-Adapter distinction beyond "structurally similar" — Adapter resolves an *unforeseen* incompatibility discovered after two classes already exist, while Bridge is chosen *up front* because the designer already knows an abstraction will need multiple, independently evolving implementations; this is a lifecycle distinction, not a quality judgment on either pattern.
