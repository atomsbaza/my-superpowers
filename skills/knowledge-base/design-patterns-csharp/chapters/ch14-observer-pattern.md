# Chapter 14: Observer Pattern

## Core Idea
Define a one-to-many dependency between objects so that when one object (the subject) changes state, all its dependents (observers) are notified and updated automatically.

## Frameworks Introduced
- **Observer**: Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.
  - When to use: Multiple objects need to react whenever a single subject's state changes, and you want the subject and its observers to stay loosely coupled — neither needs deep knowledge of the other's implementation.
  - How: Observers implement a common `IObserver.Update(...)` method and register themselves with a `Subject` (via `Register`/`Unregister`); whenever the subject's tracked state changes, it loops over its registered observers and calls `Update` on each, i.e. `NotifyRegisteredUsers`.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically."

**Also Known As**: Dependents, Publish-Subscribe

**Applicability** — GoF says use this pattern when:
- An abstraction has two aspects, one dependent on the other, and encapsulating them in separate objects lets you vary and reuse each independently.
- A change to one object requires changing others, and you don't know how many objects need to be changed.
- An object should notify other objects without making assumptions about who those objects are (i.e., you want to avoid tight coupling).

**Participants**:
- **Subject** — knows its observers (any number may observe it) and provides an interface for attaching/detaching them.
- **Observer** — defines an updating interface for objects that should be notified of changes in a subject.
- **ConcreteSubject** (e.g., ClockTimer) — stores state of interest to ConcreteObserver objects and sends notification when that state changes.
- **ConcreteObserver** (e.g., DigitalClock, AnalogClock) — maintains a reference to a ConcreteSubject, stores state that should stay consistent with the subject's, and implements Update to reconcile it.

**Consequences**:
1. Abstract coupling between Subject and Observer — the subject only knows a list of objects conforming to a simple Observer interface, so subjects and observers can belong to different layers of abstraction.
2. Support for broadcast communication — a notification needn't specify its receiver; any number of observers can subscribe or unsubscribe at any time.
3. Unexpected updates — because observers don't know about each other, an innocuous subject change can cascade into costly updates, and poorly defined dependency criteria cause spurious, hard-to-track updates. The minimal update protocol also gives observers no detail on *what* changed, forcing them to deduce it.

**Implementation notes**:
- **Push vs. pull update models**: push has the subject send observers detailed change data (assumes it knows observer needs, hurting reusability); pull sends a bare notification and lets observers query for what they need (more decoupled, but observers must work harder to discover the change).
- **Who triggers Notify**: either state-setting operations on Subject call it automatically (simple for clients but can cause redundant consecutive updates), or clients call it explicitly after a batch of changes (more efficient but error-prone if forgotten).
- **Dangling references**: deleting a subject must notify observers first so they can reset their reference, rather than leaving stale pointers.
- **Self-consistency before notification**: Subject state must be fully consistent before Notify fires (observers query the subject during their own update); GoF recommends calling Notify last inside a Template Method to guarantee subclass state is settled first.
- **ChangeManager**: for complex subject/observer graphs, a separate ChangeManager object maps subjects to observers, defines the update strategy, and batches updates so observers aren't notified redundantly when several interdependent subjects change together.

**Known Uses (1994-era)**: Smalltalk MVC (Model plays Subject, View is the observer base class); ET++ and the THINK class library, which put Subject/Observer interfaces in the root class; Interviews, the Andrew Toolkit, and Unidraw UI toolkits.

**Related Patterns (per GoF)**: Mediator (273) — a ChangeManager that encapsulates complex update semantics is itself an instance of Mediator, acting as intermediary between subjects and observers. Singleton (127) — the (usually single, globally known) ChangeManager is a natural candidate for Singleton.

## Key Concepts
- **Subject**: The object being watched, which maintains the list of registered observers and triggers notification when its state changes (`Subject` implementing `ISubject`).
- **Observer**: An object that wants to be notified of subject changes (`IObserver`, implemented by `ObserverType1`, `ObserverType2`).
- **Register / Unregister**: The subscribe/unsubscribe operations that let observers join or leave the notification list at runtime.
- **Publisher-Subscriber model**: An alternate name for this pattern, emphasizing the one-to-many broadcast relationship.
- **Lapsed listener problem**: A named risk where observers that unregister-forget or never unregister cause memory leaks, since the subject's reference list can keep observers alive longer than intended.
- **One-to-many notification vs. Chain of Responsibility**: In Observer, all registered observers are notified in parallel/at once; in Chain of Responsibility, objects are notified one at a time in sequence until one handles the request fully.

## Mental Models
- Think of a celebrity with many social-media followers: followers (observers) subscribe to get updates, and can unsubscribe when they lose interest, all without the celebrity (subject) needing to know anything specific about each follower beyond "notify them."
- Computer-world framing: a UI observing a database — when the database changes, the UI needs to be notified so it can refresh, keeping the UI and the data layer decoupled.
- Use Observer when you want to add or remove interested parties dynamically at runtime without changing the subject's code — the registration list, not the subject's logic, is what changes.

## Anti-patterns
- **Forgetting to unregister long-lived subscribers**: The lapsed listener problem — the subject's reference to an observer can keep it alive indefinitely, and a garbage collector alone won't reliably clean this up in event-heavy C# code.
- **Assuming Observer replaces Chain of Responsibility, or vice versa**: They look similar (both fan out notifications across multiple objects) but Observer broadcasts to all registered parties at once, while Chain of Responsibility passes a single request sequentially until something handles it.

## Code Examples
```csharp
interface IObserver
{
    void Update(int i);
}

class ObserverType1 : IObserver
{
    string nameOfObserver;
    public ObserverType1(String name) { this.nameOfObserver = name; }
    public void Update(int i)
    {
        Console.WriteLine("{0} has received an alert: Someone has updated myValue in Subject to: {1}", nameOfObserver,i);
    }
}

interface ISubject
{
    void Register(IObserver o);
    void Unregister(IObserver o);
    void NotifyRegisteredUsers(int i);
}

class Subject:ISubject
{
    List<IObserver> observerList = new List<IObserver>();
    private int flag;
    public int Flag
    {
        get { return flag; }
        set
        {
            flag = value;
            //Flag value changed. So notify observer/s.
            NotifyRegisteredUsers(flag);
        }
    }

    public void Register(IObserver anObserver) { observerList.Add(anObserver); }
    public void Unregister(IObserver anObserver) { observerList.Remove(anObserver); }

    public void NotifyRegisteredUsers(int i)
    {
        foreach (IObserver observer in observerList)
        {
            observer.Update(i);
        }
    }
}
```
- **What it demonstrates**: Setting the `Flag` property on `Subject` automatically fans out `Update` calls to every currently-registered `IObserver`, with registration/unregistration controlling membership independently of the notification logic itself.

## Reference Tables
None in this chapter (the Observer-vs-Chain-of-Responsibility comparison in Q&A #4 is a diagram-based distinction, not a table).

## Worked Example
Three observers are created: `myObserver1` ("Roy", `ObserverType1`), `myObserver2` ("Kevin", `ObserverType1`), and `myObserver3` ("Bose", `ObserverType2`). All three register with a `Subject`. Setting `subject.Flag = 5` notifies all three. Roy then unregisters; setting `subject.Flag = 50` notifies only Kevin and Bose (Roy gets nothing). Roy re-registers, and setting `subject.Flag = 100` notifies all three again, including Roy. The output trace confirms exactly this pattern of who receives which notification, demonstrating dynamic add/remove of observers at runtime.

## Key Takeaways
1. The subject only needs to know observers through the shared `IObserver` interface — it never needs to know concrete observer types, keeping the two sides loosely coupled.
2. Observers can register and unregister at runtime, and the subject's notification logic doesn't change to accommodate this — membership and notification are cleanly separated concerns.
3. Memory leaks (the lapsed listener problem) are the primary real-world risk with this pattern in C#, especially with long-lived event subscriptions; forgetting to unregister is the most common cause.
4. C# has built-in support for this pattern via language-level events and the generic `System.IObservable<T>` / `System.IObserver<T>` interfaces — implementing it manually (as this chapter does) builds the intuition needed to use those built-ins well.
5. Observer (parallel notification to all registered parties) is distinct from Chain of Responsibility (sequential notification until one handler fully processes the request) despite both patterns fanning a signal out across multiple objects.
6. This example predates modern C# (2018-era): it uses a `List<IObserver>` with manual `foreach` notification and no native `event`/`EventHandler` delegates — the registration/notification intent is identical in modern idiom, but production C# would typically use built-in events instead of a hand-rolled `Register`/`Unregister`/`NotifyRegisteredUsers` trio (see modern-csharp-notes.md).

## Connects To
- **Ch 17 (Command, referenced via Chain of Responsibility comparison)**: The book contrasts Observer's parallel notification with Chain of Responsibility's sequential handoff to clarify when each is appropriate.
- **Ch 29 (Memory leaks)**: The book explicitly flags the lapsed listener problem here and defers the full treatment of leak-avoidance techniques to its dedicated memory-leak chapter.
- **GoF 1994 catalog**: Observer is one of the original eleven Behavioral patterns and is the direct ancestor of the .NET `IObservable<T>`/`IObserver<T>` and event-delegate conventions.
- **GoF 1994 canonical entry**: GoF's push-vs-pull update models and its "unexpected updates"/dangling-reference liabilities give a sharper, implementation-independent account of the lapsed-listener risk than this chapter's C#-specific memory-leak framing.
