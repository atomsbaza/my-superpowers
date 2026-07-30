# Chapter 5: Abstract Factory Pattern

## Core Idea
Provide an interface for creating families of related or dependent objects without specifying their concrete classes — a "factory of factories."

## Frameworks Introduced
- **Abstract Factory**: Provide an interface for creating families of related or dependent objects without specifying their concrete classes (GoF).
  - When to use: When you need to create related products that must vary together as a family (e.g., wild-dog + wild-tiger vs. pet-dog + pet-tiger) and want to swap the whole family's concrete implementation at runtime without touching client code.
  - How: Define an abstract factory interface with one creation method per product type in the family; each concrete factory implements all of those methods to produce one consistent family of concrete products.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

**Also Known As**: Kit

**Applicability** — GoF says use this pattern when:
- A system should be independent of how its products are created, composed, and represented.
- A system should be configured with one of multiple families of products.
- A family of related product objects is designed to be used together, and you need to enforce this constraint.
- You want to provide a class library of products and reveal just their interfaces, not their implementations.

**Participants**:
- **AbstractFactory** (`WidgetFactory`) — declares an interface for operations that create abstract product objects.
- **ConcreteFactory** (`MotifWidgetFactory`, `PMWidgetFactory`) — implements the operations to create concrete product objects.
- **AbstractProduct** (`Window`, `ScrollBar`) — declares an interface for a type of product object.
- **ConcreteProduct** (`MotifWindow`, `MotifScrollBar`) — defines a product object created by the corresponding concrete factory, implementing `AbstractProduct`.
- **Client** — uses only interfaces declared by `AbstractFactory` and `AbstractProduct`.

**Consequences**:
1. Isolates concrete classes — clients manipulate instances only through abstract interfaces; product class names never appear in client code.
2. Makes exchanging product families easy — a concrete factory class appears only once (where it's instantiated), so switching the whole product family means switching one factory object.
3. Promotes consistency among products — since AbstractFactory guarantees an application uses objects from only one family at a time.
4. Supporting new kinds of products is difficult — extending the `AbstractFactory` interface to add a new product requires changing it and every subclass.

**Implementation notes**: A ConcreteFactory is typically implemented as a Singleton, since an app usually needs only one instance per product family. Concrete factories are most commonly implemented via a factory method per product; when many product families are possible, GoF suggests implementing the concrete factory with the Prototype pattern instead — initialized with one prototypical instance per product, cloning rather than subclassing to add a new family. A more flexible but less type-safe alternative parameterizes a single "Make" operation with a kind-identifier rather than declaring one method per product type.

**Known Uses (1994-era)**: InterViews uses the "Kit" suffix for its `WidgetKit`, `DialogKit`, and `LayoutKit` abstract factories (the last generating different composition objects for portrait vs. landscape layout). ET++ uses Abstract Factory (its `WindowSystem` abstract class) to achieve portability across X Windows and SunView.

**Related Patterns (per GoF)**: AbstractFactory classes are often implemented with factory methods (Factory Method), but can also be implemented using Prototype.

## Key Concepts
- **Abstract Factory**: `IAnimalFactory`, declaring `GetDog()` and `GetTiger()` without specifying which concrete dog/tiger type they return.
- **Concrete Factory**: `WildAnimalFactory` and `PetAnimalFactory`, each implementing both methods to produce a consistent family — wild animals or pet animals respectively.
- **Abstract Product**: `IDog` and `ITiger`, the interfaces each family of concrete products must implement.
- **Concrete Product**: `WildDog`, `WildTiger`, `PetDog`, `PetTiger` — the actual objects returned by the concrete factories.
- **Family of related objects**: The core distinguishing idea — a concrete factory produces multiple product types (dog *and* tiger) that are meant to be used together and share a common theme (wild vs. pet).
- **Factory of factories**: The chapter's shorthand description of Abstract Factory — it encapsulates a group of individual (Factory Method-style) factories under one umbrella interface.
- **Program to an interface, not an implementation**: The design principle the chapter cites as the reason clients depend only on `IAnimalFactory`/`IDog`/`ITiger`, never on concrete classes.

## Mental Models
- The book's real-life analogy: decorating a room with either wooden or steel tables — visiting a carpenter (wood factory) or a metal shop (steel factory); "based on demand, you decide what kind of factory you need."
- The computer-world framing: ADO.NET already applies a similar concept for establishing database connections, swapping the whole connection family based on which provider is configured.
- Build directly on Factory Method's mental model: where Factory Method had one factory hierarchy producing one product type (dog *or* tiger), Abstract Factory adds a second axis (wild *or* pet) so each concrete factory produces a *coordinated pair* of products from the same family.
- Think of "factory of factories" as: instead of independently choosing a dog-factory and a tiger-factory, you choose *one* factory (Wild or Pet) that guarantees the dog and tiger it hands you belong to the same consistent family.

## Anti-patterns
- **Assuming changes to the abstract factory are cheap**: the Q&A warns that any change to the abstract factory interface forces you to propagate that change to every concrete factory — a real maintenance cost of the "program to an interface" discipline.
- **Underestimating architectural complexity**: the chapter notes this pattern can result in unnecessary complexity and extra work, and that debugging becomes tougher in some cases — it's not a free abstraction.
- **Conflating Abstract Factory with Simple Factory or Factory Method without a clear distinguishing test**: the Q&A gives a concrete way to tell them apart (see Reference Table below); confusing the three leads to over- or under-engineering the creation logic.

## Code Examples
```csharp
using System;
namespace AbstractFactoryPattern
{
    public interface IDog
    {
        void Speak();
        void Action();
    }
    public interface ITiger
    {
        void Speak();
        void Action();
    }
    #region Wild Animal collections
    class WildDog : IDog
    {
        public void Speak()
        {
            Console.WriteLine("Wild Dog says: Bow-Wow.");
        }
        public void Action()
        {
            Console.WriteLine("Wild Dogs prefer to roam freely in jungles.\n");
        }
    }
    class WildTiger : ITiger
    {
        public void Speak()
        {
            Console.WriteLine("Wild Tiger says: Halum.");
        }
        public void Action()
        {
            Console.WriteLine("Wild Tigers prefer hunting in jungles.\n");
        }
    }
    #endregion
    #region Pet Animal collections
    class PetDog : IDog
    {
        public void Speak()
        {
            Console.WriteLine("Pet Dog says: Bow-Wow.");
        }
        public void Action()
        {
            Console.WriteLine("Pet Dogs prefer to stay at home.\n");
        }
    }
    class PetTiger : ITiger
    {
        public void Speak()
        {
            Console.WriteLine("Pet Tiger says: Halum.");
        }
        public void Action()
        {
            Console.WriteLine("Pet Tigers play in an animal circus.\n");
        }
    }
    #endregion
    //Abstract Factory
    public interface IAnimalFactory
    {
        IDog GetDog();
        ITiger GetTiger();
    }
    //Concrete Factory-Wild Animal Factory
    public class WildAnimalFactory : IAnimalFactory
    {
        public IDog GetDog()
        {
            return new WildDog();
        }
        public ITiger GetTiger()
        {
            return new WildTiger();
        }
    }
    //Concrete Factory-Pet Animal Factory
    public class PetAnimalFactory : IAnimalFactory
    {
        public IDog GetDog()
        {
            return new PetDog();
        }
        public ITiger GetTiger()
        {
            return new PetTiger();
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Abstract Factory Pattern Demo***\n");
            //Making a wild dog through WildAnimalFactory
            IAnimalFactory wildAnimalFactory = new WildAnimalFactory();
            IDog wildDog = wildAnimalFactory.GetDog();
            wildDog.Speak();
            wildDog.Action();
            //Making a wild tiger through WildAnimalFactory
            ITiger wildTiger = wildAnimalFactory.GetTiger();
            wildTiger.Speak();
            wildTiger.Action();
            Console.WriteLine("******************");
            //Making a pet dog through PetAnimalFactory
            IAnimalFactory petAnimalFactory = new PetAnimalFactory();
            IDog petDog = petAnimalFactory.GetDog();
            petDog.Speak();
            petDog.Action();
            //Making a pet tiger through PetAnimalFactory
            ITiger petTiger = petAnimalFactory.GetTiger();
            petTiger.Speak();
            petTiger.Action();
            Console.ReadLine();
        }
    }
}
```
- **What it demonstrates**: One abstract factory (`IAnimalFactory`) with two concrete factories (`WildAnimalFactory`, `PetAnimalFactory`), each producing a *consistent pair* of related products (`IDog` + `ITiger`) for its theme, without the client ever referencing `WildDog`, `PetTiger`, etc. directly.

## Reference Tables
| Pattern | Client code shape | Distinguishing trait |
|---|---|---|
| Simple Factory (book Ch. 24, non-GoF) | `simpleFactory.CreateAnimal()` via one factory class with internal conditional logic | One factory, one product type, decision logic lives inside the factory method itself |
| Factory Method (Ch. 4) | `tigerFactory.CreateAnimal()` / `dogFactory.CreateAnimal()` — one factory subclass per product | One factory hierarchy, one product per concrete factory, subclassing replaces conditionals |
| Abstract Factory (this chapter) | `wildAnimalFactory.GetDog()` and `wildAnimalFactory.GetTiger()` from the *same* factory instance | One factory produces a *family* of related products (multiple types) that must vary together |

Participant summary from the chapter:
- `IAnimalFactory`: Abstract factory.
- `WildAnimalFactory`: Concrete factory — creates wild dogs and wild tigers.
- `PetAnimalFactory`: Concrete factory — creates pet dogs and pet tigers.
- `ITiger` and `IDog`: Abstract products.
- `PetTiger`, `PetDog`, `WildTiger`, `WildDog`: Concrete products.

## Worked Example
`Program.Main` first creates a `WildAnimalFactory`, gets a dog and a tiger from it, and calls `Speak()`/`Action()` on each — both come out "wild" in behavior. It then creates a `PetAnimalFactory` and repeats the same two calls, getting "pet" behavior instead. Output:
```
***Abstract Factory Pattern Demo***
Wild Dog says: Bow-Wow.
Wild Dogs prefer to roam freely in jungles.
Wild Tiger says: Halum.
Wild Tigers prefer hunting in jungles.
******************
Pet Dog says: Bow-Wow.
Pet Dogs prefer to stay at home.
Pet Tiger says: Halum.
Pet Tigers play in an animal circus.
```
The key observation: switching from `wildAnimalFactory` to `petAnimalFactory` is the *only* code change needed to switch the entire family of products (both the dog and the tiger) from wild to pet — the client never names `WildDog`, `PetDog`, `WildTiger`, or `PetTiger` directly, only `IAnimalFactory`, `IDog`, and `ITiger`.

## Key Takeaways
1. Abstract Factory is "a factory of factories": it groups multiple related creation methods (one per product type in the family) behind a single abstract factory interface.
2. Swapping the concrete factory (e.g., `WildAnimalFactory` → `PetAnimalFactory`) swaps the entire family of products consistently, without touching client code that consumes `IAnimalFactory`/`IDog`/`ITiger`.
3. This pattern trades simplicity for flexibility: the chapter explicitly warns of added architectural complexity and harder debugging as real costs.
4. Any change to the abstract factory interface must be propagated to every concrete factory — a maintenance cost worth weighing before adopting the pattern.
5. Distinguish the three factory-family patterns by client code shape: Simple Factory conditionals in one class, Factory Method's one-subclass-per-product, and Abstract Factory's one-instance-produces-a-family.
6. Abstract Factory tends to favor object composition (a factory instance handing out related objects), while Factory Method tends to favor inheritance (subclasses overriding the creation method) — though the chapter notes both approaches can blend in practice.
7. This code targets pre-modern C# (circa C# 6/7, .NET Framework era, 2018); the Abstract Factory intent and family-of-products reasoning still apply, but idiomatic C# today might lean on DI container registration (e.g., named/keyed services) instead of hand-rolled concrete factory classes.

## Connects To
- **Ch 4**: Abstract Factory is presented as a direct extension of the Factory Method example — the same `IAnimal`/`Dog`/`Tiger`-style products, now organized into wild/pet families behind one factory interface per family.
- **Ch 3**: The abstract-class-vs-interface design discussion from the Builder chapter's Q&A (MSDN's versioning/shared-behavior guidance) is the same reasoning underlying why `IAnimalFactory` here is an interface rather than an abstract class.
- **GoF 1994 catalog**: Abstract Factory is one of the five Creational patterns in the original Gang of Four catalog, and the chapter positions it as the most complex/flexible of the "factory family" — Simple Factory, Factory Method, Abstract Factory — that this book's early chapters build up in sequence.
- **GoF 1994 canonical entry**: GoF's "Also Known As: Kit" and its recommendation to implement a ConcreteFactory as a Singleton (an explicit Related-Patterns-style cross-reference to Ch 1) are both missing from this chapter's `IAnimalFactory` treatment.
