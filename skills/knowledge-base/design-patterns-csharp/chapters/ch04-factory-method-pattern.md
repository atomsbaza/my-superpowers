# Chapter 4: Factory Method Pattern

## Core Idea
Define an interface for creating an object, but let subclasses decide which class to instantiate — the Factory Method pattern lets a class defer instantiation to subclasses.

## Frameworks Introduced
- **Factory Method**: Define an interface for creating an object, but let subclasses decide which class to instantiate. The Factory Method pattern lets a class defer instantiation to subclasses (GoF).
  - When to use: When client code needs to create objects of a family without hardcoding `if-else`/`switch` logic that picks the concrete type — e.g., choosing between `SqlConnection` and `OracleConnection` — so new types can be added without modifying existing code.
  - How: Declare an abstract `CreateAnimal()`-style method on an abstract creator class; each concrete creator subclass overrides it to instantiate its own specific product type, keeping the "varying" creation logic isolated in the subclasses.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.

**Also Known As**: Virtual Constructor

**Applicability** — GoF says use this pattern when:
- A class can't anticipate the class of objects it must create.
- A class wants its subclasses to specify the objects it creates.
- Classes delegate responsibility to one of several helper subclasses, and you want to localize the knowledge of which helper subclass is the delegate.

**Participants**:
- **Product** (`Document`) — defines the interface of objects the factory method creates.
- **ConcreteProduct** (`MyDocument`) — implements the `Product` interface.
- **Creator** (`Application`) — declares the factory method (which may have a default implementation returning a default `ConcreteProduct`) and may call it internally.
- **ConcreteCreator** (`MyApplication`) — overrides the factory method to return an instance of a `ConcreteProduct`.

**Consequences**:
1. Eliminates the need to bind application-specific classes into code — client code only deals with the `Product` interface.
2. A potential disadvantage: clients may have to subclass `Creator` just to create a particular `ConcreteProduct`.
3. Provides hooks for subclasses — a non-abstract factory method with a reasonable default implementation still lets subclasses override it to return an extended product.
4. Connects parallel class hierarchies — when a class delegates responsibilities to a separate class (e.g., `Figure` to `Manipulator`), a factory method (`CreateManipulator`) localizes the knowledge of which classes in the two parallel hierarchies belong together.

**Implementation notes**: Two major varieties — an abstract `Creator` with no default implementation (forces subclasses to define one) versus a concrete `Creator` with a default implementation (used mainly for flexibility). A **parameterized factory method** takes an identifier and creates one of several product kinds from one method, and can be selectively overridden (delegating unhandled identifiers back to the parent's implementation). In C++, avoid calling factory methods from the `Creator`'s constructor — the `ConcreteCreator`'s override isn't available yet; use lazy initialization via an accessor instead. A template-based `Creator` subclass parameterized by the product class can avoid subclassing entirely.

**Known Uses (1994-era)**: Pervasive in MacApp and ET++ (the Document/Application example) and in Unidraw (the Manipulator example). Smalltalk-80 MVC's `View` uses `defaultControllerClass` as its real factory method (not `defaultController`, which merely calls it). `Behavior`'s `parserClass` lets a class supply a customized source-code parser (e.g., `SQLParser`). Orbix (IONA Technologies' ORB system) uses Factory Method to generate the appropriate proxy type for a remote object reference.

**Related Patterns (per GoF)**: Abstract Factory is often implemented with factory methods. Factory methods are usually called within Template Methods. Prototype doesn't require subclassing `Creator` but often needs an `Initialize` operation on the product that Factory Method doesn't require.

## Key Concepts
- **Creator (abstract)**: `IAnimalFactory`, an abstract class declaring the abstract factory method `CreateAnimal()` that subclasses must implement.
- **ConcreteCreator**: `DogFactory` and `TigerFactory`, each overriding `CreateAnimal()` to instantiate its own specific product (`Dog` or `Tiger`).
- **Product (abstract)**: `IAnimal`, the interface both concrete products implement (`Speak()`, `Action()`).
- **ConcreteProduct**: `Dog` and `Tiger`, the concrete implementations of `IAnimal`.
- **Two parallel hierarchies**: The chapter's Q&A observation that creators (`IAnimalFactory` → `DogFactory`/`TigerFactory`) and products (`IAnimal` → `Dog`/`Tiger`) form two separate class hierarchies that mirror each other.
- **Template-style factory method (`MakeAnimal()`)**: The "Modified Implementation" adds a concrete method in the abstract creator that calls the abstract `CreateAnimal()` internally and then enforces additional behavior (`Speak()`, `Action()`) that subclasses cannot skip — a lightweight Template Method layered on top of Factory Method.
- **Simple Factory pattern**: A related but distinct, non-GoF pattern (covered in the book's Chapter 24) that uses a single factory class with conditional logic instead of a subclass hierarchy; referenced repeatedly here as the pattern this chapter builds upon and differentiates from.

## Mental Models
- The book's real-life analogy: a chef in a restaurant varies the taste of dishes based on customer input — the "recipe" (creation contract) is fixed, but which "chef" (concrete creator) handles it determines the final dish (product).
- The computer-world framing: choosing between `SqlConnection` and `OracleConnection` per database user — Factory Method avoids repeating `if-else`/`switch` blocks scattered through the codebase by pushing that decision into dedicated creator subclasses.
- Think of the abstract creator as a contract that says "I will produce *some* `IAnimal`, but I don't know which one — that's my subclass's job" — this is the literal meaning of "defer instantiation to subclasses."
- Distinguish Simple Factory ("one-time deal," not closed for modification — every new product means editing the factory's conditional logic) from Factory Method ("closed for modification, open for extension" — every new product means adding a new subclass, not editing existing code).

## Anti-patterns
- **Treating Factory Method as identical to Simple Factory**: the chapter's Q&A stresses that while the subclasses can look similar, Simple Factory requires editing an `if-else`/`switch` block in one factory class for every new product, whereas Factory Method requires only adding a new subclass — the former violates open/closed, the latter honors it.
- **Marking the factory method abstract when there's no subclass hierarchy**: the Q&A clarifies you should not always mark the factory method `abstract`; if the creator has no subclasses, a default (non-abstract) factory method is appropriate.
- **Ignoring performance cost at scale**: the Q&A notes that if the system must support many different product types, the overall performance can be affected — Factory Method isn't free of cost as the hierarchy grows.

## Code Examples
```csharp
using System;
namespace FactoryMethodPattern
{
    public interface IAnimal
    {
        void Speak();
        void Action();
    }
    public class Dog : IAnimal
    {
        public void Speak()
        {
            Console.WriteLine("Dog says: Bow-Wow.");
        }
        public void Action()
        {
            Console.WriteLine("Dogs prefer barking...\n");
        }
    }
    public class Tiger : IAnimal
    {
        public void Speak()
        {
            Console.WriteLine("Tiger says: Halum.");
        }
        public void Action()
        {
            Console.WriteLine("Tigers prefer hunting...\n");
        }
    }
    public abstract class IAnimalFactory
    {
        //Remember the GoF definition which says "....Factory method lets a class
        //defer instantiation to subclasses." Following method will create a Tiger
        //or Dog But at this point it does not know whether it will get a Dog or a
        //Tiger. It will be decided by the subclasses i.e.DogFactory or TigerFactory.
        //So, the following method is acting like a factory (of creation).
        public abstract IAnimal CreateAnimal();
    }
    public class DogFactory : IAnimalFactory
    {
        public override IAnimal CreateAnimal()
        {
            //Creating a Dog
            return new Dog();
        }
    }
    public class TigerFactory : IAnimalFactory
    {
        public override IAnimal CreateAnimal()
        {
            //Creating a Tiger
            return new Tiger();
        }
    }
    class Client
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Factory Pattern Demo***\n");
            // Creating a Tiger Factory
            IAnimalFactory tigerFactory =new TigerFactory();
            // Creating a tiger using the Factory Method
            IAnimal aTiger = tigerFactory.CreateAnimal();
            aTiger.Speak();
            aTiger.Action();
            // Creating a DogFactory
            IAnimalFactory dogFactory = new DogFactory();
            // Creating a dog using the Factory Method
            IAnimal aDog = dogFactory.CreateAnimal();
            aDog.Speak();
            aDog.Action();
            Console.ReadKey();
        }
    }
}
```
- **What it demonstrates**: An abstract `CreateAnimal()` factory method deferred to `DogFactory`/`TigerFactory`, so the client works only against `IAnimalFactory`/`IAnimal` abstractions while each concrete factory decides the concrete product type.

```csharp
//Modifying the IAnimalFactory class.
public abstract class IAnimalFactory
{
    public IAnimal MakeAnimal()
    {
        Console.WriteLine("\n IAnimalFactory.MakeAnimal()-You cannot ignore parent rules.");
        /* At this point, it doesn't know whether it will get a Dog or a
        Tiger. It will be decided by the subclasses i.e.DogFactory or
        TigerFactory. But it knows that it will Speak and it will have
        a preferred way of Action. */
        IAnimal animal = CreateAnimal();
        animal.Speak();
        animal.Action();
        return animal;
    }
    //So, the following method is acting like a factory
    //(of creation).
    public abstract IAnimal CreateAnimal();
}
```
- **What it demonstrates**: A concrete `MakeAnimal()` method in the abstract creator enforces a mandatory sequence (create, then always `Speak()` and `Action()`) around the still-abstract `CreateAnimal()`, so subclasses cannot skip the parent's imposed rules — a small Template Method layered onto Factory Method.

## Reference Tables
| Aspect | Simple Factory (Ch. 24, non-GoF) | Factory Method (this chapter) |
|---|---|---|
| Structure | One factory class with conditional (`if-else`/`switch`) creation logic | Abstract creator + one concrete creator subclass per product |
| Adding a new product | Edit the existing factory class | Add a new concrete creator subclass, no existing code changes |
| Open/closed principle | Violated — factory class must be modified | Honored — "closed for modification, open for extension" |
| Client awareness | Client unaware of concrete product creation logic | Client depends on abstract creator/product only |

## Worked Example
`Client.Main` creates a `TigerFactory`, calls `CreateAnimal()` to get an `IAnimal` (a `Tiger`), then calls `Speak()` and `Action()` on it; it repeats the same for `DogFactory`/`Dog`. Output:
```
***Factory Pattern Demo***
Tiger says: Halum.
Tigers prefer hunting...
Dog says: Bow-Wow.
Dogs prefer barking...
```
The "Modified Implementation" replaces direct `CreateAnimal()` + manual `Speak()`/`Action()` calls with a single `MakeAnimal()` call per factory, which internally still calls the subclass's `CreateAnimal()` but now *always* invokes `Speak()` and `Action()` as an enforced parent-class rule. Output becomes:
```
***Beautification to Factory Pattern Demo***
 IAnimalFactory.MakeAnimal()-You cannot ignore parent rules.
Tiger says: Halum.
Tigers prefer hunting...
 IAnimalFactory.MakeAnimal()-You cannot ignore parent rules.
Dog says: Bow-Wow.
Dogs prefer barking...
```
The repeated warning line demonstrates that neither `DogFactory` nor `TigerFactory` can bypass the base class's imposed sequence, even though they still control *which* concrete animal gets created.

## Key Takeaways
1. Factory Method defers the decision of "which concrete class to instantiate" to subclasses, while the client only ever depends on the abstract creator and abstract product.
2. It honors the open/closed principle: adding a new product (e.g., `Lion`, `Bear`) means adding a new concrete creator subclass, not modifying existing factory code — unlike Simple Factory's conditional logic.
3. The pattern naturally produces two parallel class hierarchies — one for creators, one for products — that evolve in lockstep.
4. An abstract creator can still hold concrete, non-abstract methods (like `MakeAnimal()`) that enforce shared behavior around the abstract factory method, blending in Template Method characteristics.
5. The factory method need not always be `abstract` — a default implementation is appropriate when the creator has no subclasses.
6. Factory Method's cost grows with the number of product types it must support, potentially affecting performance in large hierarchies.
7. This code targets pre-modern C# (circa C# 6/7, .NET Framework era, 2018); the Factory Method intent and creator/product hierarchy reasoning still apply, but idiomatic C# today might use generic factories, dependency injection containers, or `Func<IAnimal>` delegates for lighter-weight variants.

## Connects To
- **Ch 5**: Abstract Factory directly extends this chapter's `IAnimalFactory`/`Dog`/`Tiger` example by adding a second axis of variation (wild vs. pet), turning single-product factories into "factories of families of related products."
- **Simple Factory (book Chapter 24, non-GoF)**: repeatedly used as the comparison baseline throughout this chapter's Q&A to clarify what Factory Method adds — subclass-based extensibility instead of conditional-logic-based creation.
- **GoF 1994 catalog**: Factory Method is one of the five Creational patterns in the original Gang of Four catalog, and is frequently confused with the non-GoF Simple Factory idiom this book treats as a separate, simpler precursor.
- **GoF 1994 canonical entry**: GoF's "Also Known As: Virtual Constructor" and its Related-Patterns link to Template Method ("factory methods are usually called within Template Methods") are both absent from this chapter's treatment, which frames the pattern purely through the `IAnimalFactory` subclass-selection example.
