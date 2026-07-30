# Chapter 17: Command Pattern

## Core Idea
Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

## Frameworks Introduced
- **Command**: Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.
  - When to use: When you need to decouple the object that issues a request from the object that performs it, especially to support undo/redo, macros (sequences of commands), queuing, or logging of requests.
  - How: Four roles participate — `client` (holds invoker and command objects, decides which command to run), `invoker` (holds a command and calls its execute method without knowing implementation details), `command` (an object, typically implementing an `ICommand` interface, that encapsulates a call to a specific receiver method), and `receiver` (the object that actually performs the work).

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations."

**Also Known As**: Action, Transaction

**Applicability** — GoF says use this pattern when you want to:
- Parameterize objects by an action to perform (Command is the object-oriented replacement for a procedural callback function).
- Specify, queue, and execute requests at different times, potentially with a lifetime independent of the original request (including across address spaces).
- Support undo — Execute stores enough state to reverse itself, and a paired Unexecute/Undo traverses a history list backward and forward for unlimited undo/redo.
- Support logging changes so they can be reapplied after a crash, by augmenting the Command interface with load/store operations.
- Structure a system around high-level operations built on primitive operations, as with transactions in information systems.

**Participants**:
- **Command** — declares an interface for executing an operation.
- **ConcreteCommand** (PasteCommand, OpenCommand) — binds a Receiver to an action and implements Execute by invoking the corresponding operation(s) on it.
- **Client** (Application) — creates a ConcreteCommand and sets its receiver.
- **Invoker** (MenuItem) — asks the command to carry out the request.
- **Receiver** (Document, Application) — knows how to perform the operations needed to carry out the request; any class may serve as a Receiver.

**Consequences**:
1. Command decouples the object that invokes an operation from the object that knows how to perform it.
2. Commands are first-class objects that can be manipulated and extended like any other object.
3. Commands can be assembled into a composite command (GoF's **MacroCommand**, itself an instance of Composite) — a MacroCommand has no explicit receiver of its own, since each subcommand carries its own.
4. New commands are easy to add without changing existing classes.

**Implementation notes**:
- A command can range from a thin receiver/action binding to one that implements the whole action itself with no receiver — useful when there's no natural receiver or the command knows its receiver implicitly.
- Undo/redo requires storing the receiver, the operation's arguments, and any original receiver values that must be restored; multi-level undo needs a history list of executed commands, traversed backward (Unexecute) and forward (Execute) to cancel or replay effects. A command whose state varies per invocation must be **copied** onto the history list before re-use — such copyable commands act as a **Prototype**.
- Errors can accumulate across repeated execute/unexecute/reexecute cycles ("hysteresis"); GoF suggests using **Memento** to store enough state in the command to restore objects reliably without exposing their internals.

**Known Uses (1994-era)**: A paper by Lieberman is credited as the earliest example; MacApp popularized commands for undoable operations; ET++, Interviews (an `Action` class plus a parameterized `ActionCallback` template), and Unidraw (whose commands double as interpretable messages routed like Chain of Responsibility) also implement it; the THINK class library calls its commands "Tasks."

**Related Patterns (per GoF)**: Composite (163) — can implement MacroCommand. Memento (283) — can keep the state a command needs to undo its effect. Prototype (117) — a command that must be copied before going on the history list acts as a Prototype.

## Key Concepts
- **Invoker**: The object that triggers execution of a command (e.g., `ExecuteCommand()`) without needing to know what the command does internally.
- **Receiver**: The object that contains the actual business logic the command ultimately invokes (e.g., `PerformUndo()`, `Add2WithNumber()`).
- **Command object**: Encapsulates a method invocation as an object, implementing a common interface (`ICommand`) with a `Do()` (and optionally `UnDo()`) method.
- **Client**: Holds references to both the invoker and the concrete command objects, and decides which command to hand to the invoker.
- **Macro**: A sequence of commands that can be composed and executed together, one of Command's practical benefits.
- **Optional pre/post-processing**: Commands may wrap the receiver's core action with prior and post tasks (e.g., `OptionalTaskPriorToUndo()`), useful for connect/process/disconnect-style workflows.
- **Encapsulation of requests, not just data**: Unlike typical OOP encapsulation of data + methods, Command encapsulates the *request itself* as a first-class object.

## Mental Models
- Real-life analogy from the book: drawing a picture and needing to redraw (undo) parts of it to improve it — commands capture discrete actions you may want to reverse.
- Computer-world analogy: menu systems in an editor or IDE, and WPF's `ICommand` interface (`System.Windows.Input`), which binds UI events (button clicks, keyboard shortcuts) to command objects in XAML or code-behind.
- Think of Command as "encapsulating instructions" the way normal OOP encapsulates data — you're packaging up *what to do* and *to whom*, so it can be handed off, queued, logged, or reversed independently of when/where it was created.
- Use an invoker when you need to track multiple commands (in a log or queue) for undo/redo or replay; for a single simple command with one execute call, the invoker is not strictly mandatory.

## Anti-patterns
- **Skipping the receiver abstraction when multiple receiver types exist**: Without an `IReceiver` interface, adding a second receiver type (e.g., `Receiver2`) forces duplicated or brittle command code.
- **Conflating Command with Interpreter**: Commands are objects representing discrete requests; Interpreter deals with parsing/executing sentences in a defined grammar — treating one as the other misapplies both patterns.
- **Adding a new command class per new operation without bound**: This is a real cost of Command — supporting more operations means more classes, which increases long-term maintenance burden.

## Code Examples
```csharp
using System;
namespace CommandPattern
{
    public interface ICommand
    {
        void Do();
    }
    public class MyUndoCommand: ICommand
    {
        private Receiver receiver;
        public MyUndoCommand(Receiver recv) { receiver=recv; }
        public void Do()
        {
            //Perform any optional task prior to UnDo
            receiver.OptionalTaskPriorToUndo();
            //Call UnDo in receiver now
            receiver.PerformUndo();
        }
    }
    public class MyRedoCommand : ICommand
    {
        private Receiver receiver;
        public MyRedoCommand(Receiver recv) { receiver=recv; }
        public void Do()
        {
            //Perform any optional task prior to ReDo
            receiver.OptionalTaskPriorToRedo();
            //Call ReDo in receiver now
            receiver.PerformRedo();
        }
    }
    //Receiver Class
    public class Receiver
    {
        public void PerformUndo() { Console.WriteLine("Executing-MyUndoCommand"); }
        public void PerformRedo() { Console.WriteLine("Executing-MyRedoCommand"); }
        public void OptionalTaskPriorToUndo() { Console.WriteLine("Executing-Optional Tasks prior to  execute undo command"); }
        public void OptionalTaskPriorToRedo() { Console.WriteLine("Executing-Optional Tasks prior to  execute redo command"); }
    }
    //Invoker class
    public class Invoke
    {
        ICommand commandToBePerformed;
        public void SetCommand(ICommand command) { this.commandToBePerformed = command; }
        public void ExecuteCommand() { commandToBePerformed.Do(); }
    }
}
```
- **What it demonstrates**: `MyUndoCommand`/`MyRedoCommand` encapsulate a call to `Receiver`; `Invoke` (the invoker) holds and executes whichever command is set, without needing to know the receiver's details.

## Reference Tables
| Aspect | Command Pattern | Memento Pattern |
|---|---|---|
| What is stored | Every action, as a command object | Only the state, saved on request |
| Undo/redo mechanism | Explicit undo/redo operation per command | Restore previously captured state |
| Storage cost driver | Number of executed commands | Number of saved states/mementos |

## Worked Example
The base implementation wires a single `Receiver` with `MyUndoCommand` and `MyRedoCommand`, both implementing `ICommand.Do()`. An `Invoke` (invoker) holds whichever command the `Client` sets and calls `ExecuteCommand()`, which delegates to the command's `Do()`, which in turn calls the receiver's optional pre-task and core method.

The Q&A extension generalizes this to multiple receivers via an `IReceiver` interface (`Receiver1` starting at 10, `Receiver2` starting at 75), each supporting `Add2WithNumber()`/`Remove2FromNumber()` plus pre/post-processing hooks. `ICommand` gains an `UnDo()` method; `AdditionCommand` implements both `Do()` (add 2, with pre/post tasks) and `UnDo()` (subtract 2, refusing to go below the receiver's starting value). The `Invoker` exposes both `ExecuteCommand()` and `UndoCommand()`. The client executes the addition command twice on `Receiver1` (10→12→14), then tries to undo three times — the third undo hits the floor (10) and reports "Nothing more to undo..." — then repeats a shorter sequence against `Receiver2` (75→77, then undo back to 75 with one no-op undo).

## Key Takeaways
1. Command decouples the requester (client/invoker) from the performer (receiver), so clients don't need to know how a request is ultimately carried out.
2. The invoker is optional for trivial single-command cases but becomes essential once you need to track, queue, log, or sequence multiple commands for undo/redo or macros.
3. Supporting multiple receiver types cleanly requires an `IReceiver`-style abstraction; otherwise the command classes become tightly coupled to one concrete receiver.
4. Command and Memento are related but distinct ways to support undo: Command re-executes an inverse operation (e.g., subtract what was added); Memento restores a previously captured state snapshot — a single application can combine both.
5. The main cost of Command is class proliferation: each new operation typically needs a new command class, which raises long-term maintenance overhead.
6. This 2018-era C# code predates modern idioms (records, pattern matching, primary constructors); the Command intent — encapsulating a request as an object — still holds, but a modern implementation might lean on delegates/`Action` or records for lighter-weight commands.

## Connects To
- **Ch 19 (Memento)**: Both support undo, but Command stores/replays discrete inverse actions while Memento stores full state snapshots; the GoF explicitly treats them as related patterns often used together.
- **GoF 1994 catalog**: Command is one of the original 23 GoF behavioral patterns; the book also notes its real-world adoption in WPF's `ICommand` (`System.Windows.Input`) and Java Swing's `Action`.
- **GoF 1994 canonical entry**: GoF's MacroCommand (a receiver-less Composite of subcommands, unwound in reverse order for undo) gives a concrete, canonical shape to the "macros/sequences of commands" benefit this chapter only gestures at.
