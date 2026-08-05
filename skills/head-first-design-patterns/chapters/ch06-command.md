# Chapter 6: Encapsulating Invocation — Command

## Core Idea

Command turns a request into an object that bundles the receiver and the actions to perform. An invoker can execute different requests through one interface without knowing the vendor-specific receiver, enabling undo, macros, queues, and logs.

## Frameworks Introduced

- **Command Pattern**: “Encapsulates a request as an object, thereby letting you parameterize other objects with different requests, queue or log requests, and support undoable operations.”
  - When to use: a requester must be decoupled from the object that performs an action, or requests must be stored, scheduled, replayed, or reversed.
  - How: define Command.execute(), bind a receiver in a concrete command, load commands into an invoker, and invoke without inspecting the receiver.
- **Null Object**: use a no-op command where a slot has no meaningful request so the invoker does not need null checks.
- **Undo command**: add undo() that reverses execute(); store the last command or a history stack.
- **Macro Command**: compose several commands and execute them as one request.

## Key Concepts

- **Client**: creates commands and supplies receivers.
- **Command**: common request interface, usually execute().
- **Concrete command**: binds a receiver and translates execute into receiver calls.
- **Receiver**: object with the knowledge needed to perform the work.
- **Invoker**: stores commands and triggers execute().
- **Request encapsulation**: the invoker knows only the command interface.
- **Null Object**: a valid no-op object used in place of null.
- **Macro command**: command containing an ordered collection of commands.
- **Command history**: stack or log of commands used for repeated undo or recovery.

## Mental Models

- Use the diner analogy: the waitress invokes an order slip; the cook knows how to prepare the meal.
- Think of a command as a durable verb: “turn this light on,” not merely “call Light.on.”
- Keep ordinary commands “dumb” when possible; they bind an action to a receiver rather than reimplementing the receiver.
- Undo is not magic: record the state needed to restore the receiver before changing it.

## Anti-patterns

- **Invoker full of receiver-specific conditionals**: adding a vendor class requires modifying the remote.
- **Smart command with all business logic**: reduces decoupling and makes receiver substitution harder.
- **Null checks in every invoker path**: use a NoCommand object when a no-op is valid.
- **Macro as hard-coded special case**: use a composite command so the command list remains configurable.

## Code Examples

~~~java
public interface Command {
    void execute();
    void undo();
}

public final class LightOnCommand implements Command {
    private final Light light;
    public LightOnCommand(Light light) { this.light = light; }
    public void execute() { light.on(); }
    public void undo() { light.off(); }
}

public final class RemoteControl {
    private Command command = new NoCommand();
    public void setCommand(Command command) { this.command = command; }
    public void press() { command.execute(); }
    public void undo() { command.undo(); }
}
~~~

- **What it demonstrates**: the remote is an invoker; the command binds the receiver and supplies reversible behavior.

## Reference Tables

| Extension | Command design |
|---|---|
| Delayed work | Put commands on a queue and let workers call execute() |
| Undo | Store inverse behavior or the prior receiver state |
| Multiple undo operations | Push executed commands onto a stack |
| Party mode | Execute a MacroCommand containing child commands |
| Crash recovery | Persist commands and replay them after a checkpoint |

## Worked Example

The home-automation remote has seven slots with on/off commands. A LightOnCommand stores the living-room Light; the remote only calls execute() for the selected slot. The same invoker can later receive GarageDoorOpenCommand without code changes. For a ceiling fan, execute() first records the previous speed, then sets the new speed; undo() restores that recorded speed. A party macro executes several device commands in order and undoes them in reverse order.

## Key Takeaways

1. Separate the requester from the receiver with a command object.
2. Bind the receiver when creating the command, not inside the invoker.
3. Add undo only when the command can define a reliable inverse or saved state.
4. Use macros, queues, and logs because commands are first-class objects.
5. NoCommand is a small but useful Null Object.

## Connects To

- **Chapter 2 — Observer**: Swing action listeners can be both observers and commands.
- **Chapter 9 — Composite**: MacroCommand composes requests into a tree-like aggregate.
- **Chapter 10 — State**: undo for the ceiling fan stores state before transition.

