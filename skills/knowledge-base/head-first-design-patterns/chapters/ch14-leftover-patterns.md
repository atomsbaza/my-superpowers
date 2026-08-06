# Chapter 14: Appendix — Leftover Patterns

## Core Idea

The appendix gives a compact tour of additional GoF patterns. The goal is recognition: know the problem each pattern addresses, the shape of its solution, and the trade-off that should make you reach for it.

## Frameworks Introduced

- **Bridge**: decouples an abstraction from its implementation so the two can vary independently.
- **Builder**: separates the construction of a complex object from its representation so the same construction process can create different representations.
- **Chain of Responsibility**: passes a request along a chain of handlers until one handles it or the chain ends.
- **Flyweight**: uses sharing to support large numbers of fine-grained objects efficiently; intrinsic state is shared and extrinsic state is supplied by clients.
- **Interpreter**: represents a grammar for a language and provides an interpreter for sentences in that language.
- **Mediator**: defines an object that encapsulates how a set of objects interact, reducing direct many-to-many coupling.
- **Memento**: captures and externalizes an object’s internal state so it can be restored later without violating encapsulation.
- **Prototype**: creates new objects by copying a prototypical instance, useful when construction is expensive or complicated.
- **Visitor**: represents an operation to be performed on elements of an object structure, allowing new operations without changing element classes; it trades away some encapsulation.

## Key Concepts

- **Abstraction and implementation axes**: Bridge is useful when both dimensions need independent extension.
- **Construction recipe**: Builder makes ordered construction and validation explicit.
- **Handler chain**: Chain of Responsibility localizes decisions and lets a request move through handlers.
- **Intrinsic versus extrinsic state**: Flyweight shares intrinsic data and receives contextual data at operation time.
- **Grammar**: Interpreter models language rules as objects, often recursively.
- **Central colleague coordination**: Mediator replaces direct colleague references with a coordinator.
- **Originator and caretaker**: Memento’s originator creates/restores state; caretaker stores it without inspecting internals.
- **Clone semantics**: Prototype requires a clear shallow/deep-copy policy and identity policy.
- **Double dispatch**: Visitor selects an operation based on both visitor type and visited element type.

## Mental Models

- **Bridge**: a remote-control abstraction can vary independently from television implementations.
- **Builder**: a meal order is assembled step by step while the finished meal remains a separate product.
- **Chain of Responsibility**: a support ticket moves from first-line support to specialists.
- **Flyweight**: a text editor shares glyph shape data while each character occurrence supplies position and style.
- **Mediator**: air-traffic control coordinates aircraft so planes do not negotiate every interaction directly.
- **Memento**: an editor checkpoint stores enough state to undo without exposing the document’s private representation.
- **Prototype**: duplicate a configured game enemy rather than rebuild it from scratch.
- **Visitor**: add a new report operation over a stable syntax tree when changing node classes is more expensive.

## Anti-patterns

- **Bridge added before two axes vary**: creates an abstraction hierarchy with no real pressure.
- **Builder for a trivial object**: adds ceremony where a constructor or factory is clearer.
- **Unbounded handler chain**: requests become difficult to trace and may silently go unhandled.
- **Flyweight with mutable shared state**: one client can corrupt every other client’s view.
- **Mediator god object**: coordination becomes a new monolith with all business rules.
- **Memento with excessive snapshots**: memory usage grows without a meaningful undo policy.
- **Prototype shallow-copy bug**: mutable nested state is accidentally shared between supposedly independent objects.
- **Visitor on a frequently changing hierarchy**: every new element forces changes to every visitor.

## Code Examples

~~~java
public final class Director {
    public Meal construct(MealBuilder builder) {
        return builder.addMain().addSide().addDrink().build();
    }
}
~~~

~~~java
public abstract class SupportHandler {
    private SupportHandler next;

    public SupportHandler setNext(SupportHandler next) {
        this.next = next;
        return next;
    }

    public final void handle(Ticket ticket) {
        if (canHandle(ticket)) respond(ticket);
        else if (next != null) next.handle(ticket);
        else throw new IllegalStateException("No handler");
    }

    protected abstract boolean canHandle(Ticket ticket);
    protected abstract void respond(Ticket ticket);
}
~~~

~~~java
public interface DocumentVisitor {
    void visit(Paragraph paragraph);
    void visit(Image image);
}

public interface DocumentElement {
    void accept(DocumentVisitor visitor);
}
~~~

- **What it demonstrates**: Builder centralizes construction, Chain of Responsibility controls fallback, and Visitor adds operations through a stable accept/visit protocol.

## Reference Tables

| Pattern | Primary variation or problem | Main trade-off |
|---|---|---|
| Bridge | Abstraction and implementation vary independently | More indirection |
| Builder | Complex, staged construction | More builder types and ceremony |
| Chain of Responsibility | Multiple possible request handlers | Harder tracing and possible unhandled requests |
| Flyweight | Many similar fine-grained objects | Shared-state discipline and lookup cost |
| Interpreter | Small language grammar | Poor fit for large or evolving grammars |
| Mediator | Many-to-many colleague communication | Coordinator can become complex |
| Memento | Save and restore encapsulated state | Snapshot storage cost |
| Prototype | Copy configured/expensive objects | Copy depth and identity concerns |
| Visitor | Add operations over stable structures | New element types are expensive; encapsulation weakens |

| Pattern family | Patterns in the main text |
|---|---|
| Creational | Factory Method, Abstract Factory, Singleton, Prototype, Builder |
| Structural | Decorator, Adapter, Facade, Composite, Proxy, Bridge, Flyweight |
| Behavioral | Strategy, Observer, Command, Template Method, Iterator, State, Chain of Responsibility, Interpreter, Mediator, Memento, Visitor |

## Worked Example

An expression editor may have a stable syntax tree but frequently need new operations such as pretty printing, validation, and code generation. Visitor can add those operations without changing every node class, provided the element hierarchy is stable and exposing traversal hooks is acceptable. If new node types arrive constantly, ordinary polymorphic methods or a different decomposition may be safer.

## Key Takeaways

1. Recognize the design pressure before selecting an appendix pattern.
2. Bridge and Builder separate dimensions or steps that would otherwise multiply combinations.
3. Chain of Responsibility and Mediator manage communication with different topologies: linear fallback versus centralized coordination.
4. Flyweight and Memento trade memory or encapsulation for scale and reversibility.
5. Prototype and Visitor are powerful when their respective object construction or operation-extension assumptions hold.

## Connects To

- **Chapter 4 — Factory**: Builder and Prototype provide alternative creation strategies.
- **Chapter 6 — Command**: Memento commonly supplies state for undoable commands.
- **Chapter 9 — Composite**: Visitor is frequently applied to Composite structures.
- **Chapter 13 — Real World**: use consequences and forces to decide whether an “extra” pattern earns its complexity.

