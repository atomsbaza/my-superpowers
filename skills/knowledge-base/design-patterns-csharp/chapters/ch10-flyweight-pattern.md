# Chapter 10: Flyweight Pattern

## Core Idea
Use sharing to support large numbers of fine-grained objects efficiently. A flyweight is a shared object usable in multiple contexts simultaneously, indistinguishable from an unshared instance, by separating shareable *intrinsic* state from context-dependent *extrinsic* state that the client supplies.

## Frameworks Introduced
- **Flyweight**: Use sharing to support large numbers of fine-grained objects efficiently, by making the object indistinguishable from a non-shared instance in each context.
  - When to use: You need many similar objects and creating a distinct instance for every one of them would be too memory-expensive, but the objects' core structure is the same across instances.
  - How: A factory (`RobotFactory`) keeps a `Dictionary` of already-created flyweight instances keyed by type; when a client requests a category it already has, the factory returns the existing shared instance instead of creating a new one; any per-instance data (color, in the modified example) is supplied by the client as extrinsic state.

## Key Concepts
- **Flyweight**: The shared object itself (`IRobot`/`SmallRobot`/`LargeRobot`, or `Robot` in the modified version) — acts independently in each context even though it's the same instance.
- **Intrinsic state**: Data stored inside the flyweight, independent of context, and therefore shareable (the robot's category — Small or Large).
- **Extrinsic state**: Data that varies by context and cannot be shared; the client must pass it to the flyweight when needed (the robot's color in the modified example).
- **FlyweightFactory**: `RobotFactory`, which maintains a `Dictionary<string, IRobot>` (`shapes`) keyed by robot type, returning an existing instance if present or creating and caching a new one otherwise.
- **ConcreteFlyweight**: A concrete implementation of the flyweight interface (`SmallRobot`, `LargeRobot` in the first version; a single parameterized `Robot` class in the modified version).
- **Sharing vs. non-sharing**: A flyweight interface does not require that every implementation be shareable — nonshareable flyweights with concrete objects as children are a valid variation.

## Mental Models
- Think of a pen: the pen body itself (without ink) is the flyweight with intrinsic state, and the ink refill you swap in is the extrinsic data — one pen body, many possible colors.
- Think of a company's business cards: the shared template (logo, address — intrinsic) is printed once conceptually, and each employee's name/title (extrinsic) is applied per card — you don't redesign the whole card layout per employee.
- Use Flyweight when a computer game (or similarly large-population system) needs many participants with the same core structure but varying appearance/state — store one shared structure per category and let each client instance supply its own variation, rather than storing full duplicate objects per participant.
- Flyweight can look like Singleton because both prevent duplicate object creation, but the goal differs: Singleton guarantees *at most one* object of a kind system-wide; Flyweight guarantees *reuse of a small set of shared templates* to represent many logical (heavy) objects cheaply (Q1).

## Anti-patterns
- **Unguarded lazy creation under multithreading**: Just as with Singleton, creating flyweights with `new` inside a factory method that isn't thread-safe can produce multiple unwanted instances of what's supposed to be a shared object under concurrent access — the same remedy class applies (Q2).
- **Treating extrinsic data as if it belonged in the flyweight**: Extrinsic data (like color here) is not shareable and must be passed in by the client at the point of use — baking it into the flyweight instance would break sharing across different contexts that want different extrinsic values.
- **Creating a fresh `Random` per call as a substitute for real randomness testing**: The modified demo's `getRandomColor()` instantiates `new Random()` on every call and uses `Thread.Sleep(1000)` purely to increase the odds of getting a different seed — the book's own workaround for `Random`'s time-based seeding, not a general design recommendation; it demonstrates the extrinsic-state variation, not a production randomness technique.

## Code Examples
```csharp
using System;
using System.Collections.Generic;//Dictionary is used here
namespace FlyweightPattern
{
    /// <summary>
    /// The 'Flyweight' interface
    /// </summary>
    interface IRobot
    {
        void Print();
    }

    /// <summary>
    /// A 'ConcreteFlyweight' class
    /// </summary>
    class SmallRobot : IRobot
    {
        public void Print()
        {
            Console.WriteLine("This is a small Robot");
        }
    }

    /// <summary>
    /// A 'ConcreteFlyweight' class
    /// </summary>
    class LargeRobot : IRobot
    {
        public void Print()
        {
            Console.WriteLine("I am a large Robot");
        }
    }

    /// <summary>
    /// The 'FlyweightFactory' class
    /// </summary>
    class RobotFactory
    {
        Dictionary<string, IRobot> shapes = new Dictionary<string, IRobot>();
        public int TotalObjectsCreated
        {
            get { return shapes.Count; }
        }

        public IRobot GetRobotFromFactory(string robotType)
        {
            IRobot robotCategory = null;
            if (shapes.ContainsKey(robotType))
            {
                robotCategory = shapes[robotType];
            }
            else
            {
                switch (robotType)
                {
                    case "Small":
                        robotCategory = new SmallRobot();
                        shapes.Add("Small", robotCategory);
                        break;
                    case "Large":
                        robotCategory = new LargeRobot();
                        shapes.Add("Large", robotCategory);
                        break;
                    default:
                        throw new Exception("Robot Factory can create only small and large robots");
                }
            }
            return robotCategory;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Flyweight Pattern Demo***\n");
            RobotFactory myfactory = new RobotFactory();
            IRobot shape = myfactory.GetRobotFromFactory("Small");
            shape.Print();
            /*Now we are trying to get the 2 more Small robots. Note that:
            now onwards we need not create additional small robots because
            we have already created one of this category*/
            for (int i = 0; i < 2; i++)
            {
                shape = myfactory.GetRobotFromFactory("Small");
                shape.Print();
            }
            int NumOfDistinctRobots = myfactory.TotalObjectsCreated;
            Console.WriteLine("\n Now, total numbers of distinct robot objects is = {0}\n", NumOfDistinctRobots);
            /*Here we are trying to get the 5 more Large robots. Note that:
            now onwards we need not create additional small robots because
            we have already created one of this category */
            for (int i = 0; i < 5; i++)
            {
                shape = myfactory.GetRobotFromFactory("Large");
                shape.Print();
            }
            NumOfDistinctRobots = myfactory.TotalObjectsCreated;
            Console.WriteLine("\n Distinct Robot objects created till now = {0}", NumOfDistinctRobots);
            Console.ReadKey();
        }
    }
}
```
- **What it demonstrates**: `RobotFactory.GetRobotFromFactory` checks its `shapes` dictionary before creating anything; requesting `"Small"` three times and `"Large"` five times still yields only 2 distinct objects total (`TotalObjectsCreated`), because every repeat request returns the same cached instance.

## Reference Tables
Singleton vs. Flyweight, from Q1 (the book states this as prose, not a printed table):

| Aspect | Singleton | Flyweight |
|---|---|---|
| Cardinality goal | At most one instance of the type, system-wide | A small set of shared template instances, reused across many logical objects |
| Motivation | Guarantee uniqueness of a single required object | Reduce memory for large numbers of similar, heavy objects |
| Client's data | N/A — one instance for everyone | Each client supplies its own extrinsic state (e.g., color) on top of the shared intrinsic template |

Intrinsic vs. extrinsic state (Q6-Q8):

| State type | Stored where | Shareable? | Example in chapter |
|---|---|---|---|
| Intrinsic | Inside the flyweight | Yes | Robot category (Small/Large) |
| Extrinsic | Held/passed by the client | No | Robot color |

## Worked Example
First version: `RobotFactory` caches `SmallRobot`/`LargeRobot` instances in `shapes`. The demo requests `"Small"` three times total and `"Large"` five times total; the output prints the small-robot message three times and the large-robot message five times, but `TotalObjectsCreated` reports only 1 after the small requests and 2 after the large requests — proving reuse rather than re-creation.

Modified version: to demonstrate extrinsic state, the book collapses `SmallRobot`/`LargeRobot` into a single `Robot` class parameterized by `robotType`, adding `SetColor`/`colorOfRobot`. `RobotFactory.GetRobotFromFactory` still checks its dictionary first, printing `"We do not have Small Robot at present.So we are creating a Small Robot now."` only the first time a category is requested. The demo loop requests `"Small"` three times and `"Large"` three times, calling `Thread.Sleep(1000)` and `shape.SetColor(getRandomColor())` before each `Print()` — `getRandomColor()` builds a fresh `Random`, checks `r.Next(100) % 2`, and returns `"red"` or `"green"`. Because color is extrinsic and set per call, the printed messages vary run to run (e.g., "This is a Small type robot with redcolor" then "...with greencolor"), while `TotalObjectsCreated()` still reports only 2 distinct underlying `Robot` objects — the category (intrinsic) is shared, the color (extrinsic) is not.

## Key Takeaways
1. Flyweight's core mechanism is a factory that caches and reuses instances by category, avoiding redundant heavy-object creation.
2. Separating intrinsic (shareable, stored in the flyweight) from extrinsic (per-context, supplied by the client) state is the crux of the pattern — get this split wrong and sharing breaks down.
3. Flyweight and Singleton both prevent unwanted duplication, but for different reasons: Singleton bounds a type to one instance; Flyweight bounds a type to a small reusable set of templates serving many logical objects.
4. As with Singleton, naive lazy creation in the factory is not automatically thread-safe — the same class of remedy applies under concurrency.
5. Configuring flyweights (extracting a shared template and wiring up extrinsic-state plumbing) is itself an added layer of complexity that can be tricky to debug, even though the payoff (memory savings) is real.
6. This example predates modern C# (2018-era, targeting C# 6/7): it uses classic `Dictionary`/`switch` code and no records, pattern matching, or expression-bodied members — the Flyweight intent still applies, but idiomatic modern C# would express some of this more tersely (see modern-csharp-notes.md).

## Connects To
- **Ch 1 (Singleton)**: Both patterns restrict object creation, but toward different goals — Singleton for uniqueness, Flyweight for shared reuse across many logical objects; the thread-safety pitfalls in lazy creation are shared between the two chapters.
- **Ch 9 (Facade)**: Not directly related in intent, but both patterns in this book use a "coordinator" class (`RobotFactory` here, `RobotFacade` in Ch 9) that clients call instead of managing details themselves — worth contrasting the very different reasons each coordinator exists.
- **GoF 1994 catalog**: Flyweight is one of the seven original Structural patterns.
