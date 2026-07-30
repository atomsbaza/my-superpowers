# Chapter 1: Singleton Pattern

## Core Idea
Ensure a class has only one instance, and provide a global point of access to it.

## Frameworks Introduced
- **Singleton**: Ensure a class has only one instance, and provide a global point of access to it (GoF).
  - When to use: You need exactly one instance of a class shared across the system — e.g., a centralized file system or resource manager — and creating extra instances would be wasteful or incorrect.
  - How: Make the constructor private so callers cannot use `new`, hold a single instance in a `private static readonly` field, and expose it through a `public static` property/accessor that returns the existing instance.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: Ensure a class only has one instance, and provide a global point of access to it.

**Applicability** — GoF says use this pattern when:
- There must be exactly one instance of a class, and it must be accessible to clients from a well-known access point.
- The sole instance should be extensible by subclassing, and clients should be able to use an extended instance without modifying their code.

**Participants**:
- **Singleton** (no example class given — the pattern is presented generically) — defines an `Instance` operation (a class/static operation) that lets clients access its unique instance, and may be responsible for creating its own unique instance.

**Consequences**:
1. Controlled access to sole instance — the class encapsulates its sole instance and controls how and when clients access it.
2. Reduced name space — an improvement over global variables, which pollute the name space.
3. Permits refinement of operations and representation — the Singleton class may be subclassed, letting an app configure itself with an instance of an extended class at run-time.
4. Permits a variable number of instances — it's easy to change your mind later and allow more than one instance; only the access operation needs to change.
5. More flexible than class operations — static member functions in C++ are never virtual, so subclasses can't override them polymorphically the way an `Instance` operation can be overridden.

**Implementation notes**: Hide the creation operation behind a static accessor with lazy initialization. GoF explicitly warns against relying on a global/static object with automatic initialization instead of an accessor, for three C++-specific reasons: you can't guarantee only one static instance is ever declared, you may lack the data needed to construct it at static-init time, and C++ doesn't define construction order for globals across translation units — so dependent singletons can break. For run-time-selectable subclasses, GoF proposes a registry-of-singletons keyed by name (looked up via an environment variable) rather than hard-coding the concrete subclass in `Instance`.

**Known Uses (1994-era)**: Smalltalk-80's `ChangeSet current`, and the class/metaclass relationship (every metaclass has exactly one instance — its class). The InterViews toolkit uses Singleton for its unique `Session` and `WidgetKit` instances; `WidgetKit::instance()` picks the concrete look-and-feel subclass based on an environment variable `Session` defines.

**Related Patterns (per GoF)**: Many patterns can be implemented using Singleton — see Abstract Factory, Builder, and Prototype, all of which may use a single "factory object" that is itself a Singleton.

## Key Concepts
- **Static initialization**: The approach used in the chapter's main example — the CLR creates the instance the first time any static member of the class is referenced.
- **Lazy instantiation**: Instantiation is deferred until the `Instance` property is actually invoked, rather than happening eagerly at program start.
- **`sealed` keyword**: Prevents derivation of the Singleton class, guarding against a nested subclass being used to sneak around the private constructor.
- **`readonly` keyword**: Ensures the instance field is assigned only once, during static initialization.
- **Double-checked locking**: An alternative implementation that checks `instance == null` both outside and inside a `lock` block, avoiding the cost of locking on every access while still being thread-safe.
- **`volatile` keyword**: Marks a field as subject to concurrent modification, disabling compiler optimizations that assume single-threaded access so all threads see the most up-to-date value.
- **Naive (unsynchronized) lazy singleton**: A simple null-check-then-create pattern that works in single-threaded code but can produce multiple instances under concurrent access.

## Mental Models
- Think of the Singleton as "your team's one and only captain" — the real-life analogy the chapter opens with: a team must have exactly one captain to represent it in a coin toss, and if none exists, one must be elected before proceeding.
- Use static initialization when you want the simplest correct implementation and don't need fine control over exactly when the instance is created — the CLR guarantees safety at the cost of the instance being created as soon as any static member is touched.
- Use double-checked locking only when you specifically need lazy, on-demand creation in a multithreaded environment and are willing to accept the cost of a locking mechanism.
- Treat the private constructor plus `sealed` as a pair: the private constructor stops `new Singleton()` from outside, and `sealed` stops someone from wrapping that private constructor's access inside a nested derived class that could still call it (e.g., `public class NestedDerived : Singleton {}` nested inside `Singleton` itself).

## Anti-patterns
- **Naive null-check singleton in concurrent code**: `if (instance == null) instance = new Singleton();` without locking lets two or more threads simultaneously see `instance == null` and each create their own instance, breaking the "only one instance" guarantee.
- **Relying on static fields without realizing they trigger instantiation**: Referencing any static member of the Singleton class (even an unrelated one like `MyInt`) causes the CLR to run the static initializer and construct the singleton — this gives you less control over exactly when instantiation happens, even though it's usually tolerable since it's a one-time cost.
- **Omitting `sealed` on a class with only a private constructor**: leaves a loophole open — a nested class derived from the Singleton can still be instantiated multiple times via its own constructor, defeating the pattern's guarantee.

## Code Examples
```csharp
using System;
namespace SingletonPatternEx
{
    public sealed class Singleton
    {
        private static readonly Singleton instance=new Singleton();
        private int numberOfInstances = 0;
        //Private constructor is used to prevent
        //creation of instances with 'new' keyword outside this class
        private Singleton()
        {
            Console.WriteLine("Instantiating inside the private constructor.");
            numberOfInstances++;
            Console.WriteLine("Number of instances ={0}", numberOfInstances);
        }
        public static Singleton Instance
        {
            get
            {
                Console.WriteLine("We already have an instance now.Use it.");
                return instance;
            }
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Singleton Pattern Demo***\n");
            Console.WriteLine("Trying to create instance s1.");
            Singleton s1 = Singleton.Instance;
            Console.WriteLine("Trying to create instance s2.");
            Singleton s2 = Singleton.Instance;
            if (s1 == s2)
            {
                Console.WriteLine("Only one instance exists.");
            }
            else
            {
                Console.WriteLine("Different instances exist.");
            }
            Console.Read();
        }
    }
}
```
- **What it demonstrates**: A private constructor plus a `sealed`, `readonly` static instance gives every caller of `Singleton.Instance` the same object, proven by reference-equality check (`s1 == s2`).

```csharp
//Double checked locking
using System;
public sealed class Singleton
{
    //We are using volatile to ensure that
    //assignment to the instance variable finishes before it's
    //access.
    private static volatile Singleton instance;
    private static object lockObject = new Object();
    private Singleton() { }
    public static Singleton Instance
    {
        get
        {
            if (instance == null)
            {
                lock (lockObject)
                {
                    if (instance == null)
                        instance = new Singleton();
                }
            }
            return instance;
        }
    }
}
```
- **What it demonstrates**: Thread-safe lazy instantiation — the outer null check avoids locking on every access, the lock protects the actual creation, and the inner null check prevents a second thread (that was waiting on the lock) from creating a duplicate instance.

## Reference Tables
| Approach | Thread-safe | Lazy | Cost |
|---|---|---|---|
| Static initialization (main example) | Yes (CLR guarantees it) | No — created on first static member access | Cheap, one-time |
| Naive null-check | No | Yes | Cheap but broken under concurrency |
| Double-checked locking | Yes | Yes | Locking overhead, but only on the first access |

## Worked Example
Running the main demo prints `***Singleton Pattern Demo***`, then on the first call to `Singleton.Instance` (assigned to `s1`) the private constructor fires exactly once, printing "Instantiating inside the private constructor." and "Number of instances =1", followed by "We already have an instance now.Use it." The second call (assigned to `s2`) skips construction entirely and just prints "We already have an instance now.Use it." again. Because `s1 == s2` is true, the program prints "Only one instance exists." A separate "Challenges" walkthrough shows that merely referencing an unrelated static field `Singleton.MyInt` from `Main()` — without ever touching `Instance` — still triggers "Number of instances =1" before printing `25`, proving static initialization runs on any static member access, not just `Instance`.

## Key Takeaways
1. A private constructor combined with a `static readonly` instance field is the simplest correct Singleton in C#, relying on CLR-guaranteed static initialization semantics.
2. `sealed` closes a subtle loophole: without it, a nested derived class can still be instantiated repeatedly even though the base constructor is private.
3. The naive null-check pattern is not thread-safe; double-checked locking with `volatile` is the standard fix when lazy, on-demand creation is required under concurrency.
4. Referencing any static member of a class — not just the singleton accessor — can trigger instantiation, so you have less fine-grained control over timing than you might expect; in practice this one-time cost is usually acceptable.
5. This code targets pre-modern C# (circa C# 6/7, .NET Framework era, 2018); the Singleton intent and thread-safety reasoning still apply, but idiomatic implementation today might lean on `Lazy<T>` instead of manual double-checked locking.

## Connects To
- **Ch 3**: Both Singleton and Builder care about controlling object construction, but Singleton restricts cardinality (exactly one) while Builder controls how a complex object's parts are assembled.
- **GoF 1994 catalog**: Singleton is one of the five Creational patterns in the original Gang of Four catalog; this chapter's static-initialization and double-checked-locking variants are C#-specific implementation strategies for that same intent.
- **GoF 1994 canonical entry**: GoF's registry-of-singletons technique — looking up the concrete subclass to instantiate by name at run-time via an environment variable — is a subclass-selection strategy this chapter never discusses, since its `sealed` static-instance approach forecloses subclassing entirely.
