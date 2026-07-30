# Chapter 19: Memento Pattern

## Core Idea
Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later.

## Frameworks Introduced
- **Memento**: Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later.
  - When to use: When you need to save and later restore an object's internal state (e.g., supporting undo/rollback) without exposing that object's internal implementation details to the code that manages the saved states.
  - How: Three roles — `Originator` (owns the state, can produce a `Memento` snapshot and restore from one), `Memento` (an opaque, immutable-from-the-outside snapshot of the originator's state), and `Caretaker` (requests and holds mementos on the originator's behalf, but never inspects or modifies their contents).

## Key Concepts
- **Originator**: The object whose internal state is being saved/restored; only the originator that created a memento is allowed to access its contents.
- **Memento**: The snapshot object holding captured state; treated as opaque by the caretaker (caretaker cannot alter it).
- **Caretaker**: Requests a memento from the originator to save its current state, and later passes a memento back to the originator to restore that state — without ever violating the originator's encapsulation.
- **Opaque object**: A memento's defining property — external code (the caretaker) can hold it and pass it around but cannot read or mutate its internal state.
- **Restore point**: A saved memento representing one point-in-time snapshot; multiple restore points can be kept in a list-like collection (`IList<Memento>`).
- **State externalization without exposure**: The pattern's central tension — state must leave the originator (to be saved elsewhere) without becoming publicly accessible or mutable outside the originator.

## Mental Models
- Real-life analogy from the book: a turnstile as a simple finite state machine — locked, then unlocked after payment, then relocked after passage — illustrating discrete, restorable states.
- Computer-world analogy: a drawing application needing to revert to an older state (undo).
- Think of Memento as a "sealed envelope" system: the caretaker collects sealed envelopes (mementos) from the originator and hands them back on request, but can never open one to peek at or change its contents — only the originator that sealed it can read it back out.
- Use Memento (rather than plain public state) whenever restoring state matters more than raw simplicity, and encapsulation must be preserved — if you're tempted to make state public just to let the caretaker manage it directly, that breaks the pattern's core guarantee.

## Anti-patterns
- **Making the originator's state public so the caretaker can manage it directly**: Explicitly rejected in the Q&A — this breaks encapsulation, which is the pattern's foundational constraint ("Without violating encapsulation...").
- **Storing unlimited mementos without regard to cost**: More mementos require more storage and add burden to the caretaker, increasing maintenance cost and impacting performance.
- **Treating Memento as a full substitute for the Command pattern's undo**: The two solve related but different problems — Memento is unnecessary overhead for simple invertible operations that don't require storing prior state (e.g., undoing addition by subtracting).

## Code Examples
```csharp
using System;
namespace MementoPattern
{
    class Memento
    {
        private string state;
        public string State
        {
            get { return state; }
            set { state = value; }
        }
    }

    class Originator
    {
        private string state;
        Memento myMemento;
        public string State
        {
            get { return state; }
            set { state = value; Console.WriteLine("Current State : {0}", state); }
        }
        // Originator will supply the memento in respond to caretaker's request
        public Memento GetTheMemento()
        {
            //Creating a memento with the current state
            myMemento = new Memento();
            myMemento.State = state;
            return myMemento;
        }
        // Back to old state (Restore)
        public void RevertToState(Memento previousMemento)
        {
            Console.WriteLine("Restoring to previous state...");
            this.state = previousMemento.State;
            Console.WriteLine("Current State : {0}", state);
        }
    }
}
```
- **What it demonstrates**: `Originator.GetTheMemento()` packages current state into a `Memento`; `RevertToState()` restores state from a previously obtained `Memento` — the caretaker never touches `Memento.State` directly except to pass it back.

## Reference Tables
| Aspect | Memento Pattern | Command Pattern |
|---|---|---|
| What is stored | Only the state, saved on request | Every action performed, as a command object |
| Undo mechanism | Restore a previously captured state | Explicit undo/redo operation per command |
| Best fit | Operations expensive/complex to reverse computationally (e.g., paint operations) | Operations cheaply reversible via an inverse action (e.g., add → subtract) |

## Worked Example
The base demo has `Originator` set its `State` to "Initial state", then call `GetTheMemento()` to snapshot it. The state is then changed to "Intermediary state", and `RevertToState(mementoObject)` restores it back to "Initial state" — output shows the state transitions in order: Initial state → Intermediary state → Restoring to previous state... → Initial state.

The Q&A extension generalizes this to multiple restore points using `IList<Memento> savedStates`. The originator's state is set to "State-1", "State-2", "State-3" in turn, with a memento saved after each; "State-4" is set but never saved. The program lists the three available restore points, then rolls back through them in reverse order via a loop that calls `GetTheMemento()`/sets `mementoObject.State`/calls `RevertToState()`, printing "Current State : State-3", then "State-2", then "State-1" as it unwinds.

## Key Takeaways
1. Memento lets you restore an object's previous state without exposing its internals — the caretaker manages mementos but is structurally prevented from reading or modifying them.
2. Multiple restore points are naturally supported by holding a generic collection (`IList<Memento>` / `List<Memento>`) of mementos rather than just one.
3. Prefer generic collections (`List<T>`) over their non-generic counterparts (`ArrayList`) per general C# best practice, independent of the pattern itself.
4. The main costs are storage and maintenance: more mementos mean more memory, more caretaker bookkeeping, and measurable performance impact from the save operations themselves.
5. Memento and Command both support undo but for different situations: Command suits cheaply invertible operations (e.g., reverse an addition by subtracting); Memento suits cases where you must snapshot full state because reversal isn't a simple inverse operation (e.g., paint applications) — a single application can combine both.
6. In modern C# you might reach for serialization/deserialization (as the book itself notes as an alternative) instead of hand-rolled Memento classes; this 2018-era code predates such idiom shifts, but the pattern's intent — safe, encapsulated state snapshot and restore — still applies.

## Connects To
- **Ch 17 (Command)**: GoF treats these as related patterns for supporting undo; Command re-executes inverse actions, Memento restores captured state snapshots, and applications often combine both.
- **GoF 1994 catalog**: Memento is one of the original 23 GoF behavioral patterns; the book also flags serialization/deserialization as a practical alternative technique achieving similar state-capture goals in C#/Java.
