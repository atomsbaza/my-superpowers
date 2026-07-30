# Chapter 15: Strategy (Policy) Pattern

## Core Idea
Define a family of algorithms, encapsulate each one, and make them interchangeable, so the algorithm can vary independently from the clients that use it.

## Frameworks Introduced
- **Strategy (also called Policy)**: Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.
  - When to use: You need to select an algorithm's behavior dynamically at runtime, and hard-wiring the choice via inheritance would create the kind of interface bloat and rigid deadlocks described in the Q&A below.
  - How: A `Context` class holds a reference to a `IChoice` (strategy) object and delegates the actual behavior to it via a setter (`SetChoice`); client code swaps which concrete strategy (`FirstChoice`, `SecondChoice`) the context holds, changing behavior without changing the context's own code.

## Key Concepts
- **Context**: The class that holds a reference to the current strategy and delegates work to it (`Context`, holding an `IChoice`).
- **Strategy interface**: The common contract implemented by every interchangeable algorithm (`IChoice.MyChoice()`).
- **Concrete strategy**: A specific algorithm implementation (`FirstChoice`, `SecondChoice`).
- **Runtime algorithm selection**: The defining trait of Strategy — the concrete strategy bound to the context is chosen and can be changed while the program runs, not fixed at compile time.
- **Setter-based delegation over constructor injection**: The book deliberately uses `SetChoice(IChoice choice)` as a method rather than a constructor parameter specifically so the "choice behavior" can be swapped on the fly, mid-lifecycle.
- **Strategy vs. plain inheritance**: Using inheritance to vary behavior instead of Strategy forces every subclass to implement every method in the shared interface, and any special-case method (e.g. `MySpecialChoice`) either breaks classes that shouldn't have it or forces an abstract-class workaround that can't be instantiated directly — this is the specific failure mode Strategy avoids.

## Mental Models
- Think of a soccer match: if Team A is leading late in the game, it switches to a defensive strategy, while Team B switches to an all-out attacking strategy — same team (context), different algorithm (strategy) chosen based on runtime conditions.
- Computer-world framing: a backup memory slot that gets used only if the primary memory is full — the "which storage strategy to use" decision is made dynamically based on runtime state rather than fixed at compile time.
- Use Strategy whenever you notice a class growing multiple `if`/`else` branches to pick between algorithm variants — that branching logic is exactly what should move into separate strategy classes behind a shared interface.

## Anti-patterns
- **Using inheritance to express "a class may or may not have a special behavior"**: Forces a choice between violating a constraint (implementing a method a class shouldn't have) or breaking the type system (needing an abstract class that can't be instantiated) — illustrated directly in Q&A #1 with `MySpecialChoice()`.
- **Splitting special behavior into a second interface (`ISpecialChoice`) as a workaround**: Technically works but scales poorly — if the special behavior's implementation changes later, every class implementing that secondary interface needs to be tracked down and updated individually (Q&A #2).

## Code Examples
```csharp
// IChoice.cs
public interface IChoice
{
    void MyChoice();
}

// FirstChoice.cs
public class FirstChoice:IChoice
{
    public void MyChoice() { Console.WriteLine("Traveling to Japan"); }
}

// SecondChoice.cs
public class SecondChoice:IChoice
{
    public void MyChoice() { Console.WriteLine("Traveling to India"); }
}

// Context.cs
public class Context
{
    IChoice choice;
    /*It's our choice. We prefer to use a setter method instead of using a
    constructor. We can call this method whenever we want to change the
    "choice behavior" on the fly*/
    public void SetChoice(IChoice choice)
    {
        this.choice = choice;
    }

    /* This method will help us to delegate the particular object's
    choice behavior/characteristic*/
    public void ShowChoice()
    {
        choice.SetChoice();
    }
}
```
- **What it demonstrates**: `Context` never implements travel logic itself — it holds whatever `IChoice` was last set via `SetChoice` and delegates to it in `ShowChoice`, so swapping `FirstChoice` for `SecondChoice` at runtime changes behavior without touching `Context`.

## Reference Tables
None in this chapter.

## Worked Example
`Program.Main` loops twice, reading a user choice ("1" or "2") each iteration. For "1" it constructs `new FirstChoice()`, for anything else `new SecondChoice()`; either way it calls `cxt.SetChoice(ic)` then `cxt.ShowChoice()`. Output confirms the same `Context` instance prints "Traveling to India" when choice 2 is picked and "Traveling to Japan" when choice 1 is picked — the algorithm executed depends purely on which strategy object was last assigned, not on any change to `Context`'s own code.

The Q&A section extends this with a variant (Q&A #3): renaming `MyChoice()` to `SetChoice()` and adding constructor side effects (e.g. `FirstChoice()`'s constructor prints "I do not want to travel", `SecondChoice()`'s prints "I am arranging money to travel"), showing that default behaviors bound at construction time can still be overridden dynamically through the strategy's own method.

## Key Takeaways
1. Strategy's defining feature is that the algorithm is chosen and can be swapped at runtime — if the choice is truly fixed at compile time, plain polymorphism may suffice instead.
2. Preferring a setter (`SetChoice`) over constructor injection for the strategy reference is a deliberate choice to allow behavior changes mid-lifecycle, not an accidental style choice.
3. When a class hierarchy needs an occasional "special" behavior that not every member should have, forcing it into a shared interface (via inheritance) creates a deadlock between violating a constraint and breaking instantiability — Strategy sidesteps this by keeping algorithms as separate, optional, swappable objects.
4. The added `Context` object is itself a cost (more objects in the application) — Strategy trades a small amount of structural overhead for the ability to vary algorithms independently of client code.
5. Users of a Strategy-based system must understand that behavior can vary by strategy — silently swapping strategies without documentation can surprise callers who expect one fixed behavior.
6. This example predates modern C# (2018-era): it uses interface-per-algorithm with manual `if`/`else` string comparison for user input and no switch expressions, delegates, or `Func<T>`-based strategy injection — the pattern's runtime-swap intent carries over directly to modern idiom, where a `Func<T>` or lambda is sometimes used in place of a full interface hierarchy for lightweight cases (see modern-csharp-notes.md).

## Connects To
- **Ch 16 (Template Method)**: Both patterns vary an algorithm, but Template Method fixes the algorithm's skeleton in a base class and lets subclasses override specific steps, while Strategy delegates the entire algorithm to a swappable, composed object — a common point of confusion the book addresses across both chapters.
- **Ch 3 (Builder, referenced in Q&A #4)**: The book points back to its Builder-pattern Q&A for a fuller discussion of when to prefer an abstract class over an interface for the strategy contract.
- **GoF 1994 catalog**: Strategy is one of the original eleven Behavioral patterns and is frequently implemented in modern languages using first-class functions/delegates instead of a full class hierarchy.
