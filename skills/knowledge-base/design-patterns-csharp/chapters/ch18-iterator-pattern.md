# Chapter 18: Iterator Pattern

## Core Idea
Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

## Frameworks Introduced
- **Iterator**: Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.
  - When to use: When you need to traverse different kinds of collection objects (arrays, linked lists, and so on) in a standard, uniform way without the client needing to know each collection's internal structure.
  - How: An `Aggregate` interface (e.g., `ISubjects`) exposes a `CreateIterator()` factory method; a common `IIterator` interface (`First()`, `Next()`, `IsDone()`, `CurrentItem()`) is implemented differently by each concrete iterator (e.g., `ScienceIterator` over a `LinkedList<string>`, `ArtsIterator` over a `string[]`) so client code can traverse any of them identically.

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
