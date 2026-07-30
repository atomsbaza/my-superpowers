# Chapter 7: Decorator Pattern

## Core Idea
Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality — classes stay closed for modification but open for extension.

## Frameworks Introduced
- **Decorator**: Attach additional responsibilities to an object dynamically; a flexible alternative to subclassing for extending functionality.
  - When to use: You want to add functionality to a specific object instance (not the whole class), possibly combined in different ways, without touching the existing/underlying class.
  - How: Wrap a `Component` in an `AbstractDecorator` that also implements `Component`, holds a reference to the wrapped component, and delegates to it — then override the method in concrete decorators to run extra behavior before or after delegating.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality."

**Also Known As**: Wrapper

**Applicability** — GoF says use this pattern when:
- You want to add responsibilities to individual objects dynamically and transparently, without affecting other objects.
- The responsibilities need to be withdrawable later.
- Extension by subclassing is impractical — too many independent extensions would cause a subclass explosion, or the class definition is unavailable for subclassing.

**Participants**:
- **Component** (`VisualComponent`) — defines the interface for objects that can have responsibilities added dynamically.
- **ConcreteComponent** (`TextView`) — the object additional responsibilities can be attached to.
- **Decorator** — maintains a reference to a Component and defines an interface conforming to Component's.
- **ConcreteDecorator** (`BorderDecorator`, `ScrollDecorator`) — adds the actual responsibilities to the component.

**Consequences**:
1. More flexibility than static inheritance — responsibilities attach/detach at run time rather than requiring a new class per combination (e.g. `BorderedScrollableTextView`); decorators also make it trivial to add the same property twice (e.g. a double border), which is error-prone with inheritance.
2. Avoids feature-laden classes high in the hierarchy — a pay-as-you-go model where a simple base class gains functionality incrementally, so an application doesn't pay for features it doesn't use.
3. A decorator and its component aren't object-identical — a decorated component isn't identical to the wrapped one, so code shouldn't rely on object identity through a decorator.
4. Lots of little objects — systems built from many similar-looking decorator objects, differing only in interconnection, are easy to customize but harder to learn and debug.

**Implementation notes**: ConcreteDecorator classes must share a common ancestor for interface conformance (in C++). The abstract Decorator class can be omitted when only one responsibility is ever added. Keep the Component class lightweight (interface-focused, not data-heavy) so decorators stay cheap enough to use in quantity. GoF contrasts "changing the skin" (Decorator) with "changing the guts" (Strategy) — Strategy suits cases where Component is intrinsically heavyweight, making Decorator too costly.

**Known Uses (1994-era)**: InterViews and ET++ UI toolkits (graphical embellishments on widgets); ObjectWorks\Smalltalk class library; InterViews' `DebuggingGlyph` (traces layout requests) and ParcPlace Smalltalk's `PassivityWrapper` (enables/disables interaction); ET++'s streaming classes (`CompressingStream`, `ASCII7Stream` decorating a `FileStream`); MacApp 3.0 and Bedrock (adorner/behavior objects on heavyweight "view" components, as an alternative Strategy-based approach).

**Related Patterns (per GoF)**: Adapter — changes an object's interface entirely, whereas Decorator only changes responsibilities, keeping the interface intact. Composite — structurally similar (both use recursive composition), but Composite's focus is uniform treatment/representation of many objects, while Decorator's is embellishment without subclassing; a composite can be a Decorator's ConcreteComponent, and a decorator can be a Composite's Leaf. Strategy — lets you change an object's "guts" (behavior delegated to a swappable strategy object) versus Decorator's "skin" (wrapping from the outside).

## Key Concepts
- **Component**: The abstract base type both the plain object and every decorator implement, so they're interchangeable to the client.
- **ConcreteComponent**: The original, unmodified object whose core behavior stays untouched.
- **AbstractDecorator**: Implements `Component`, holds a `Component` reference (`com`), and delegates the call to it — it is abstract even though it declares no abstract method, because it's not meant to be instantiated directly.
- **ConcreteDecorator**: Adds specific new behavior around the delegated call (e.g., `ConcreteDecoratorEx1` adds a floor, `ConcreteDecoratorEx2` paints the house).
- **Object composition over inheritance**: Decorators wrap objects at runtime rather than creating new subclasses at compile time — this is what makes the binding dynamic instead of static.
- **Open/closed principle**: The class this pattern is built around — closed for modification, open for extension — is the design principle Decorator exists to satisfy.
- **Chaining decorators**: A decorator can wrap another decorator (not just a plain component), letting responsibilities stack incrementally.

## Mental Models
- Think of building a second floor on top of an existing single-story house: you don't touch the ground floor's architecture, you add on top of it — and you could even paint the whole thing afterward as a further addition, without redoing earlier work.
- Use Decorator when you'd otherwise reach for multiple subclasses just to combine features (e.g., "add a floor" + "paint" + "add a floor and paint") — inheritance forces you to either explode into many subclasses or hit multiple-inheritance limits (the "diamond effect"), which C# does not support for classes.
- .NET's and Java's I/O stream implementations are real-world Decorator usage — wrapping a base stream with layers like buffering or encryption without modifying the base stream class.

## Anti-patterns
- **Reaching for inheritance to combine independent responsibilities**: If you need "floor + paint + extra feature," subclassing forces either a combinatorial explosion of subclasses or a diamond-shaped multiple-inheritance need that C# classes cannot express (Q3).
- **Creating too many decorators**: Even though each decorator is simple, stacking many of them makes the system hard to maintain and debug — the flexibility becomes its own confusion if left unchecked (Q5).
- **Making a decorator apply itself to itself**: `decorator2.SetTheComponent(decorator2)` (a typo'd variant discussed in Q8) creates infinite self-delegation and throws `StackOverflowException` at runtime — a reminder that a decorator's wrapped component must never be the decorator itself.

## Code Examples
```csharp
using System;
namespace DecoratorPattern
{
    abstract class Component
    {
        public abstract void MakeHouse();
    }

    class ConcreteComponent : Component
    {
        public override void MakeHouse()
        {
            Console.WriteLine("Original House is complete. It is closed for modification.");
        }
    }

    abstract class AbstractDecorator : Component
    {
        protected Component com;

        public void SetTheComponent(Component c)
        {
            com = c;
        }

        public override void MakeHouse()
        {
            if (com != null)
            {
                com.MakeHouse();//Delegating the task
            }
        }
    }

    class ConcreteDecoratorEx1 : AbstractDecorator
    {
        public override void MakeHouse()
        {
            base.MakeHouse();
            Console.WriteLine("***Using a decorator***");
            //Decorating now.
            AddFloor();
            //You can put additional stuff as per your needs.
        }
        private void AddFloor()
        {
            Console.WriteLine("I am making an additional floor on top of it.");
        }
    }

    class ConcreteDecoratorEx2 : AbstractDecorator
    {
        public override void MakeHouse()
        {
            Console.WriteLine("");
            base.MakeHouse();
            Console.WriteLine("***Using another decorator***");
            //Decorating now.
            PaintTheHouse();
            //You can add additional stuffs as per your need
        }
        private void PaintTheHouse()
        {
            Console.WriteLine("Now I am painting the house.");
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Decorator pattern Demo***\n");
            ConcreteComponent cc = new ConcreteComponent();
            ConcreteDecoratorEx1 decorator1 = new ConcreteDecoratorEx1();
            decorator1.SetTheComponent(cc);
            decorator1.MakeHouse();

            ConcreteDecoratorEx2 decorator2 = new ConcreteDecoratorEx2();
            //Adding results from decorator1
            decorator2.SetTheComponent(decorator1);
            decorator2.MakeHouse();
            Console.ReadKey();
        }
    }
}
```
- **What it demonstrates**: `AbstractDecorator` implements the same `Component` type it wraps, so `ConcreteDecoratorEx2` can wrap `decorator1` (itself a decorator) exactly as easily as it could wrap a plain `ConcreteComponent`, letting responsibilities stack.

## Reference Tables
Decorator vs. inheritance, synthesized from the Q&A session (not printed as a table in the book):

| Aspect | Decorator | Inheritance |
|---|---|---|
| Binding | Dynamic (runtime composition) | Static (compile-time) |
| Adding a responsibility | Attach/detach a decorator object | Create a new subclass |
| Combining responsibilities | Wrap decorators around decorators | Risk of multiple-inheritance/"diamond" problems |
| Existing code impact | Untouched — new bugs can't be introduced there | New subclasses can proliferate, increasing complexity |

## Worked Example
Running the demo: `decorator1` wraps `cc` (the plain `ConcreteComponent`) and calling `decorator1.MakeHouse()` prints "Original House is complete..." (delegated) followed by "***Using a decorator***" and "I am making an additional floor on top of it." Then `decorator2` wraps `decorator1` (not `cc` directly) — calling `decorator2.MakeHouse()` re-runs the entire `decorator1.MakeHouse()` chain (house + floor messages again) and then prints "***Using another decorator***" and "Now I am painting the house." The output shows the floor-adding sequence appearing twice: once standalone, once as part of the painted-and-floored composition — because `decorator2` delegates through `decorator1`, which delegates through `cc`. The Q&A session also shows this same result is achievable by declaring the decorator variables as `AbstractDecorator` instead of their concrete types (polymorphism), proving the client only ever needs to depend on the abstract type.

## Key Takeaways
1. Composition (wrap-and-delegate) gives you dynamic behavior that inheritance's compile-time binding cannot.
2. A decorator can wrap either a plain component or another decorator — this is what allows responsibilities to stack incrementally rather than requiring a subclass per combination.
3. An abstract class needs no abstract methods to be legitimately abstract in C# — `AbstractDecorator` is abstract purely to prevent direct instantiation and signal "instantiate a concrete decorator instead."
4. Decorator pairs naturally with the single responsibility principle: each decorator should add exactly one responsibility, keeping them composable and easy to reason about.
5. Don't over-decorate: many stacked decorators can become as hard to maintain as the deep subclass hierarchies they were meant to replace.
6. This example predates modern C# (2018-era, targeting C# 6/7): it uses classic virtual/override chains and no records, primary constructors, or pattern matching — the Decorator intent still applies, but idiomatic modern C# would express some of this more tersely (see modern-csharp-notes.md).

## Connects To
- **Ch 6 (Proxy)**: Proxy and Decorator share the same wrap-and-implement-the-same-interface shape, which is why they're often confused. The distinguishing intent: Proxy controls *access* to the wrapped object; Decorator adds *responsibilities* to it. Adapter (Ch 8) differs from both by changing the interface itself rather than preserving it.
- **Ch 8 (Adapter)**: Where Decorator keeps the same interface and adds behavior, Adapter changes the interface to make two otherwise-incompatible types work together.
- **GoF 1994 catalog**: Decorator is one of the seven original Structural patterns.
- **GoF 1994 canonical entry**: GoF's "Composite versus Decorator versus Proxy" discussion adds a structural reason beyond "adds responsibilities vs. controls access": Decorator's open-endedness (an object's total functionality can't conveniently be determined at compile time) is *why* recursive composition is essential to it, whereas Proxy's proxy-subject relationship is a single, static relationship expressible without recursion — the two patterns only look alike superficially because both keep a reference and forward requests.
