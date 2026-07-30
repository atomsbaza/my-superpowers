# Chapter 18: Iterator Pattern

## Core Idea
Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

## Frameworks Introduced
- **Iterator**: Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.
  - When to use: When you need to traverse different kinds of collection objects (arrays, linked lists, and so on) in a standard, uniform way without the client needing to know each collection's internal structure.
  - How: An `Aggregate` interface (e.g., `ISubjects`) exposes a `CreateIterator()` factory method; a common `IIterator` interface (`First()`, `Next()`, `IsDone()`, `CurrentItem()`) is implemented differently by each concrete iterator (e.g., `ScienceIterator` over a `LinkedList<string>`, `ArtsIterator` over a `string[]`) so client code can traverse any of them identically.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation."

**Also Known As**: Cursor

**Applicability** — GoF says use this pattern to:
- Access an aggregate object's contents without exposing its internal representation.
- Support multiple traversals of aggregate objects pending at once.
- Provide a uniform interface for traversing different aggregate structures (polymorphic iteration).

**Participants**:
- **Iterator** — defines an interface for accessing and traversing elements.
- **ConcreteIterator** — implements the Iterator interface and tracks the current position in the traversal.
- **Aggregate** — defines an interface for creating an Iterator object.
- **ConcreteAggregate** — implements the iterator-creation interface to return an instance of the proper ConcreteIterator.

**Consequences**:
1. Supports variations in traversal — swapping in a different iterator (or Iterator subclass) changes how a complex aggregate (e.g., a parse tree, inorder vs. preorder) is walked, without touching the aggregate.
2. Simplifies the Aggregate interface — traversal operations live on the Iterator, so Aggregate doesn't need its own.
3. More than one traversal can be pending on an aggregate at once, since each iterator tracks its own state independently.

**Implementation notes**:
- **External vs. internal iterators**: an *external* iterator is driven by the client (calls `Next`/`IsDone` itself) and is more flexible — e.g., you can compare two collections in lockstep — while an *internal* iterator controls its own traversal and applies a client-supplied operation to each element; internal iterators are easier to use but weaker in languages without closures.
- **Who defines the traversal algorithm**: putting it in the iterator (rather than the aggregate) makes it easy to reuse across different aggregates, but the iterator may then need privileged access to the aggregate's internals, which can compromise encapsulation.
- **Robust iterators**: traversal state can be corrupted by concurrent insertion/removal; a robust iterator, typically by registering itself with the aggregate, guarantees insertions/removals don't interfere with an in-progress traversal without requiring a defensive copy.
- Iterating recursive/Composite structures often favors an internal iterator (it can recurse and use the call stack to store the path implicitly) over an external one (which must explicitly store a path through the structure); a **NullIterator**, whose `IsDone` is always true, simplifies traversing leaf nodes uniformly.

**Known Uses (1994-era)**: The Booch components' bounded/unbounded Queue classes; Smalltalk's collection classes (`do:`, an internal iterator taking a block) and its `ReadStream`-style external iterators; ET++ container classes (polymorphic iterators plus a cleanup Proxy); Unidraw's cursor-based iterators; Borland ObjectWindows 2.0 (a uniform iterator hierarchy overloading `operator++`).

**Related Patterns (per GoF)**: Composite (163) — iterators are often applied to recursive Composite structures. Factory Method (107) — polymorphic iterators rely on a factory method (e.g., `CreateIterator`) to instantiate the right ConcreteIterator. Memento (283) — often used with Iterator so an iterator can capture and internally store a snapshot of traversal state.

## Key Concepts
- **Aggregate**: An object (or interface) that defines how to create an Iterator object for a given collection; the term and naming convention are adopted directly from the GoF.
- **Iterator interface**: The common contract (`First()`, `Next()`, `IsDone()`, `CurrentItem()`) that every concrete iterator implements, regardless of the underlying data structure.
- **Concrete iterator**: A class implementing the iterator interface for one specific collection type (e.g., `ScienceIterator` wraps a `LinkedList<string>`; `ArtsIterator` wraps a `string[]`).
- **Uniform traversal**: The client (e.g., an administrative department merging two companies' employee records) can call the same methods regardless of whether data lives in a linked list or an array.
- **Built-in language iterators**: C# has native iterator support (introduced in Visual Studio 2005) via `foreach`; Java has `java.util.Iterator`. The GoF-style hand-rolled Iterator is often superseded by these built-ins.
- **Collection vs array**: Collections (e.g., `LinkedList<T>`, `List<T>`, `Dictionary<TKey,TValue>`) can grow/shrink dynamically and support keyed lookup, unlike fixed-size arrays.

## Mental Models
- Real-life analogy from the book: Company A stores employee records in a linked list, Company B in an array; when the companies merge, Iterator lets both be traversed through one common interface without rewriting any code.
- Computer-world analogy: in a college, the arts department stores student records in an array while the science department uses a linked list; the administrative office doesn't care about the underlying structure — it just wants uniform access to the data.
- Think of Iterator as "hiding the container's internals behind a walk-forward cursor" — `IsDone()` + `Next()` let you drive any collection type with the same loop shape.
- Use Iterator with Composite when traversing tree-like structures (e.g., traversing nodes of a tree), and note that C#'s `foreach` is itself a built-in consumer of iterators — the book's own Visitor+Composite+Iterator combination example (Chapter 13) uses `foreach` this way.

## Anti-patterns
- **Allowing mutation of the underlying collection during traversal**: The book flags this as a key challenge — accidental modification during iteration must be guarded against.
- **Taking a full backup of the collection before every traversal "just to be safe"**: Called out explicitly as a costly operation, not a good general solution to concurrent-modification concerns.
- **Reducing the example to only one data structure type**: Demonstrating Iterator with just one collection (only linked list, or only array) hides the pattern's real value, which is uniform access across *different* underlying structures.

## Code Examples
```csharp
// ISubjects.cs
using System;
using IteratorPattern.Iterator;
namespace IteratorPattern.Aggregate
{
    public interface ISubjects
    {
        IIterator CreateIterator();
    }
}
// Science.cs
using System;
using IteratorPattern.Iterator;
using System.Collections.Generic;//For Linked List
namespace IteratorPattern.Aggregate
{
    public class Science:ISubjects
    {
        private LinkedList<string> Subjects;
        public Science()
        {
            Subjects = new LinkedList<string>();
            Subjects.AddFirst("Maths");
            Subjects.AddFirst("Comp. Sc.");
            Subjects.AddFirst("Physics");
        }
        public IIterator CreateIterator()
        {
            return new ScienceIterator(Subjects);
        }
    }
}
//Arts.cs
using System;
using IteratorPattern.Iterator;
namespace IteratorPattern.Aggregate
{
    public class Arts:ISubjects
    {
        private string[] Subjects;
        public Arts() { Subjects = new[] {"Bengali", "English"}; }
        public IIterator CreateIterator() { return new ArtsIterator(Subjects); }
    }
}
using System;
namespace IteratorPattern.Iterator
{
    public interface IIterator
    {
        void First();//Reset to first element
        string Next();//Get next element
        bool IsDone();//End of collection check
        string CurrentItem();//Retrieve Current Item
    }
}
```
- **What it demonstrates**: `ISubjects.CreateIterator()` is the Aggregate factory method; `IIterator` is the common traversal contract that `ScienceIterator` (backed by `LinkedList<string>`) and `ArtsIterator` (backed by `string[]`) each implement independently.

## Reference Tables
| Data structure | Iterator class | Backing storage |
|---|---|---|
| Science subjects | `ScienceIterator` | `LinkedList<string>` |
| Arts subjects | `ArtsIterator` | `string[]` |

## Worked Example
`Science` and `Arts` both implement `ISubjects`, storing subjects in a `LinkedList<string>` and a `string[]` respectively, and each returns its own concrete iterator from `CreateIterator()`. `Program.Main` creates a `Science` and an `Arts` instance, obtains an `IIterator` from each, and passes both to a shared `Print(IIterator iterator)` method that loops `while (!iterator.IsDone()) { Console.WriteLine(iterator.Next()); }` — the same print logic drives both a linked-list-backed and an array-backed collection without any type-specific branching. Output: Science prints "Physics / Comp. Sc. / Maths" (because `AddFirst` builds the list in reverse insertion order) and Arts prints "Bengali / English".

## Key Takeaways
1. Iterator's core value is letting client code traverse fundamentally different underlying data structures (linked list vs array) through one uniform interface.
2. Guard against mutating a collection mid-traversal; taking a full backup as a defense is explicitly called out as too costly to be a good general solution.
3. C# already provides built-in iterator support via `foreach` (since VS 2005) — hand-rolling `IIterator` is mainly instructive; production code typically relies on `IEnumerable<T>`/`IEnumerator<T>`.
4. Iterator pairs naturally with Composite for traversing tree-like structures, and with Visitor in combined scenarios (the book's Chapter 13 shows Visitor + Composite + Iterator together via `foreach`).
5. Demonstrating the pattern with at least two structurally different collections is what reveals its actual power — a single-collection example undersells the point.
6. This 2018-era C# code predates modern idioms; the Iterator intent — uniform sequential access without exposing internal representation — still applies, though modern code would typically implement `IEnumerable<T>`/`IEnumerator<T>` or use iterator (`yield return`) methods rather than a hand-rolled `IIterator` interface.

## Connects To
- **Ch 13 (Visitor / Composite, referenced in-book)**: The book's modified Visitor illustration combines Visitor, Composite, and Iterator patterns together, using C#'s `foreach` to consume an iterator from client code.
- **GoF 1994 catalog**: Iterator is one of the original 23 GoF behavioral patterns; C#'s built-in `foreach`/`IEnumerable<T>` is a language-level realization of this same pattern.
- **GoF 1994 canonical entry**: GoF's external-vs-internal iterator distinction (client-driven vs. self-driven traversal) and its discussion of robust iterators under concurrent mutation are canonical framing this chapter's `foreach`-centric treatment doesn't cover.
