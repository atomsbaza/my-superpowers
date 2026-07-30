# Chapter 24: Simple Factory Pattern

## Core Idea
Create an object without exposing the instantiation logic to the client. Unlike every other pattern in this book, Simple Factory is explicitly **not** one of the original 23 Gang of Four patterns — the book covers it in Part II ("Additional Design Patterns") as a common, practical idiom that Factory Method and Abstract Factory are themselves considered to have originated from.

## Frameworks Introduced
- **Simple Factory**: Create an object without exposing the instantiation logic to the client (not a GoF pattern; a common practical idiom).
  - When to use: You want to separate the part of your code that varies (which concrete object to create) from the part that doesn't (what the client does with the object), without yet needing subclass-deferred creation.
  - How: A factory class (optionally behind an abstract class or interface) centralizes a switch/if-based creation method that the client calls instead of using `new` directly.

## Key Concepts
- **Factory**: An object whose job is to create other objects, abstracting the instantiation process away from the objects' consumers.
- **`ISimpleFactory` (abstract class)**: Declares the `CreateAnimal()` contract; not strictly required, but recommended so future factory variants can be swapped in via polymorphism.
- **Centralized creation logic**: All `if`/`switch` branching over which concrete type to instantiate lives inside `SimpleFactory.CreateAnimal()`, not scattered through client code.
- **Varying vs. non-varying code**: The chapter explicitly marks the creation call as "the code region that will vary" versus the following `Speak()`/`Action()` calls as "the codes that do not change frequently" — a direct illustration of separating what changes from what doesn't.
- **Open/closed principle violation**: Adding or removing a supported type requires modifying `CreateAnimal()` directly, which the Q&A flags as a violation of the open/closed half of SOLID.
- **Not a GoF pattern**: The Simple Factory pattern is explicitly called out as not part of the original Gang of Four catalog; it is considered the conceptual seed that Factory Method and Abstract Factory (both true GoF patterns) build on.

## Mental Models
- Think of a South Indian restaurant: you place an order for biryani and specify "more spice" or "less spice"; the chef (the factory) decides how to prepare the dish based on your choice, and you never see or control the actual cooking steps.
- Use Simple Factory when you have a small, closed set of related types and want to hide `new` calls behind one method — it is the simplest way to keep object-creation code out of client logic.
- Think of `#region` markers in the client (`The code region that will vary` vs. `The codes that do not change frequently`) as a literal illustration of the separation-of-concerns goal: only the factory call varies with user choice; everything downstream (`Speak()`, `Action()`) is stable.
- Treat Simple Factory as a stepping stone, not a destination: if you find yourself needing subclasses to decide which product to instantiate (rather than one factory class with a switch), that need signals you actually want Factory Method instead.

## Anti-patterns
- **Calling `new` directly in client code for each type**: puts branching logic and concrete-type knowledge in the client, defeating the goal of abstracting creation away from consumers and forcing every call site to change when new types are added.
- **Skipping the abstract class/interface (`ISimpleFactory`)**: works, but removes the ability to swap in a different factory implementation via polymorphism later without touching client code that depends on the concrete `SimpleFactory` type directly.
- **Adding new types by editing `CreateAnimal()`'s switch statement indefinitely**: technically necessary in Simple Factory (unlike Factory Method), but the chapter is explicit this violates the open/closed principle — every new supported type requires modifying existing, already-tested code.

## Code Examples
```csharp
public interface IAnimal
{
    void Speak();
    void Action();
}
public class Dog : IAnimal
{
    public void Speak() { Console.WriteLine("Dog says: Bow-Wow."); }
    public void Action() { Console.WriteLine("Dogs prefer barking..."); }
}
public class Tiger : IAnimal
{
    public void Speak() { Console.WriteLine("Tiger says: Halum."); }
    public void Action() { Console.WriteLine("Tigers prefer hunting..."); }
}
public abstract class ISimpleFactory
{
    public abstract IAnimal CreateAnimal();
}
public class SimpleFactory : ISimpleFactory
{
    public override IAnimal CreateAnimal()
    {
        IAnimal intendedAnimal=null;
        Console.WriteLine("Enter your choice(0 for Dog, 1 for Tiger)");
        string b1 = Console.ReadLine();
        int input;
        if (int.TryParse(b1, out input))
        {
            Console.WriteLine("You have entered {0}", input);
            switch (input)
            {
                case 0: intendedAnimal = new Dog(); break;
                case 1: intendedAnimal = new Tiger(); break;
                default:
                    Console.WriteLine("You must enter either 0 or 1");
                    throw new ApplicationException(String.Format(" Unknown Animal cannot be instantiated"));
            }
        }
        return intendedAnimal;
    }
}
```
- **What it demonstrates**: All type-selection logic (`switch` over user input) is centralized inside `SimpleFactory.CreateAnimal()`, behind the `ISimpleFactory` abstraction — the client never sees `new Dog()` or `new Tiger()` directly.

```csharp
class Client
{
    static void Main(string[] args)
    {
        IAnimal preferredType=null;
        ISimpleFactory simpleFactory = new SimpleFactory();
        #region The code region that will vary based on users preference
        preferredType = simpleFactory.CreateAnimal();
        #endregion
        #region The codes that do not change frequently
        preferredType.Speak();
        preferredType.Action();
        #endregion
    }
}
```
- **What it demonstrates**: The `#region` comments make explicit which part of the client is expected to vary (the factory call, driven by user choice) versus which part is stable regardless of which concrete type was created (`Speak()`/`Action()`).

## Reference Tables
| Aspect | Simple Factory | Factory Method (Ch 4) | Abstract Factory (Ch 5) |
|---|---|---|---|
| GoF pattern? | No | Yes | Yes |
| Who decides the concrete type | One factory class's `if`/`switch` | Subclasses, via overridden factory method | A family of factory objects, one per product family |
| Adding a new type | Modify the existing factory class (violates open/closed) | Add a new subclass (no existing code modified) | Add a new concrete factory + products |
| Book's own framing | "Simplest form" that Factory Method and Abstract Factory are assumed to originate from | Builds on Simple Factory's separation-of-concerns goal | Builds on both Simple Factory and Factory Method |

## Worked Example
A client asks the user to choose an animal (0 for Dog, 1 for Tiger) and delegates creation entirely to `simpleFactory.CreateAnimal()`. For input `0`, the factory parses the input, matches `case 0`, instantiates a `Dog`, and returns it; the client then calls `Speak()` ("Dog says: Bow-Wow.") and `Action()` ("Dogs prefer barking...") without knowing or caring that a `Dog` specifically was created. For input `1`, the same flow produces a `Tiger` ("Tiger says: Halum." / "Tigers prefer hunting..."). For an invalid input like `3`, the factory's `default` case prints an error and throws an `ApplicationException` ("Unknown Animal cannot be instantiated"), which surfaces to the caller as a runtime exception (shown in the book's Figure 24-4) rather than a silently `null` object.

## Key Takeaways
1. Simple Factory centralizes object-creation logic in one place, hiding `new` calls and any conditional type-selection from client code.
2. It is explicitly not one of the 23 GoF patterns — the book places it in Part II precisely because it is a common idiom, not a formal GoF-catalogued pattern, though Factory Method and Abstract Factory are described as having originated from its design goals.
3. Its main weakness is violating the open/closed principle: adding or removing a supported product type requires editing the factory's existing creation method directly.
4. Using an abstract class or interface (`ISimpleFactory`) instead of depending on the concrete `SimpleFactory` class is optional here but recommended, since it leaves room to swap factory implementations via polymorphism later.
5. This code targets pre-modern C# (2018, .NET Framework era) — the create-behind-an-abstraction intent still applies today, but idiomatic modern C# might express the type-selection switch via pattern matching (`input switch { 0 => new Dog(), ... }`) rather than a classic `switch` statement.

## Connects To
- **Ch 4 (Factory Method) / Ch 5 (Abstract Factory)**: The book cross-references this chapter repeatedly from both — it recommends readers understand Simple Factory first, since Factory Method defers instantiation to subclasses (which Simple Factory does not need to do) and Abstract Factory builds on both Simple Factory and Factory Method to create families of related objects.
- **SOLID / Open-Closed Principle**: The chapter's own Q&A ties the pattern's chief weakness directly to Robert C. Martin's open/closed principle — code should be open for extension but closed for modification, which a growing `switch` statement in `CreateAnimal()` violates.
