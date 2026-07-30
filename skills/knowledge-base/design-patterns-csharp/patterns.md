# Patterns

## Singleton
**When to use**: Exactly one instance of a class must exist and be globally accessible (config, logging, connection pool).
**How**: Private constructor, static instance field, static accessor method (with lazy init/locking for thread safety).
**Trade-offs**: Hides dependencies (hard to test/mock), introduces global mutable state. In 2025/26 practice, mostly superseded by `services.AddSingleton<T>()` in a DI container — the container owns lifetime instead of the class owning itself. (Ch1)

## Prototype
**When to use**: Creating a new object is expensive or complex, but copying an existing similar instance is cheap.
**How**: Implement a `Clone()`-style method that returns a copy of the current instance (shallow or deep as needed).
**Trade-offs**: Deep-cloning object graphs with circular references is tricky. C# records' `with` expressions now cover many simple immutable-copy cases without a full Prototype implementation. (Ch2)

## Builder
**When to use**: An object has many optional parameters/construction steps, and a telescoping constructor would be unreadable.
**How**: A Builder interface with step methods (`WithX()`, `AddY()`) returning `this` for chaining, and a `Build()` method; optionally, a Director orchestrates step order.
**Trade-offs**: More boilerplate than a plain constructor for simple objects; still the standard fluent-API idiom for complex/validated construction as of 2025/26. (Ch3)

## Factory Method
**When to use**: Object creation logic needs to vary by subclass, but the calling code shouldn't know which concrete class it gets.
**How**: Define a creator abstract method; each concrete subclass overrides it to instantiate its own product type.
**Trade-offs**: Requires a class hierarchy just for creation; in modern C#, DI containers or a `switch` expression over pattern matching often replace this unless the creation logic is itself meaningful business logic. (Ch4)

## Abstract Factory
**When to use**: You need to create families of related objects (e.g., a UI toolkit's buttons+checkboxes for a specific theme) and enforce they're used consistently together.
**How**: Define an abstract factory interface with one creation method per product type; each concrete factory implements the whole family.
**Trade-offs**: Adding a new product type means changing every concrete factory; heavier than Factory Method, and in 2025/26 practice mostly relevant when building frameworks/SDKs rather than application code. (Ch5)

## Proxy
**When to use**: You need to control access to an object — lazy loading, access control, caching, or remote-call indirection — without changing the object's interface.
**How**: A Proxy class implements the same interface as the real subject, forwarding (or gating) calls to it.
**Trade-offs**: Adds an indirection layer; in modern systems, largely implicit now (HTTP clients, gRPC stubs, `DelegatingHandler`, resilience middleware generate proxies automatically) — hand-written proxies remain common for auth/caching at trust boundaries. (Ch6)

## Decorator
**When to use**: You need to add responsibilities (logging, caching, retry) to an object dynamically without subclassing every combination.
**How**: A Decorator implements the same interface as the wrapped object, holds a reference to it, and adds behavior before/after delegating.
**Trade-offs**: Many stacked decorators can be hard to debug/trace; remains the standard idiom for cross-cutting concerns wrapped around a DI-registered interface. (Ch7)

## Adapter
**When to use**: An existing class's interface doesn't match what a client expects (often a third-party or legacy API).
**How**: An Adapter class implements the client's expected interface and internally translates calls to the adaptee's actual interface.
**Trade-offs**: Only translates interface shape, not semantics — mismatched behavior underneath can still leak through; remains essential and largely unchanged in intent through 2025/26, since integration boundaries never disappear. (Ch8)

## Facade
**When to use**: A subsystem has many interacting classes and clients need a simple, focused entry point.
**How**: A Facade class exposes a small set of high-level methods that internally coordinate the subsystem's classes.
**Trade-offs**: Can become a "god object" if it grows unchecked — modern guidance (2025/26) explicitly flags large Facades as a smell; keep them thin and delegate real work. (Ch9)

## Flyweight
**When to use**: You need to represent very large numbers of similar fine-grained objects without exhausting memory.
**How**: Split object state into intrinsic (shared, immutable, cached) and extrinsic (passed in per use); a factory returns shared instances from a cache.
**Trade-offs**: Adds complexity and requires strict immutability/thread-safety discipline for shared state; a niche pattern, but still the right tool for high-throughput logging/telemetry/data-processing pipelines. (Ch10)

## Composite
**When to use**: You need to represent part-whole hierarchies (trees) and want clients to treat individual leaves and composite branches uniformly.
**How**: A common component interface implemented by both Leaf and Composite classes; Composite holds child components and delegates/aggregates operations across them.
**Trade-offs**: Can make it harder to restrict what types of children a composite may contain; stable pattern, unchanged in spirit through 2025/26. (Ch11)

## Bridge
**When to use**: Both an abstraction and its implementation need to vary independently, without a combinatorial explosion of subclasses.
**How**: The abstraction holds a reference to an implementation interface, delegating implementation-specific work to it instead of implementing it directly.
**Trade-offs**: Extra indirection is overhead if only one dimension of variation is ever needed; reserve for cross-platform libraries/SDKs where independent evolution is genuinely required. (Ch12)

## Visitor
**When to use**: You need to add new operations across a stable set of element classes without modifying those classes each time.
**How**: Each element accepts a Visitor and calls back into a type-specific `Visit()` method (double dispatch); new operations become new Visitor implementations.
**Trade-offs**: Adding a new element type requires updating every Visitor; modern C# pattern matching over closed (`sealed`) hierarchies covers many cases that used to require Visitor. (Ch13)

## Observer
**When to use**: One object's state change must notify multiple dependents without tightly coupling them.
**How**: A Subject maintains a list of Observers and calls a notify method on each when its state changes; Observers implement a common update interface.
**Trade-offs**: Manual subscription-list management risks memory leaks (lapsed listeners) if unsubscription is missed; C# `event`/`delegate` already implements this at the language level, and at scale it's now usually message-broker/event-stream based rather than in-memory. (Ch14)

## Strategy
**When to use**: You need to swap an algorithm/behavior at runtime without conditionals scattered through calling code.
**How**: Define a Strategy interface with one method; each concrete strategy implements a variant; the context holds a reference to the currently selected strategy.
**Trade-offs**: Requires the caller to know which strategy to select; described by 2025/26 sources as the GoF pattern that's aged best — pairs naturally with DI (`IEnumerable<IStrategy>` injection) and is now often stateless records/delegates rather than full classes. (Ch15)

## Template Method
**When to use**: Several classes share the same overall algorithm structure but differ in specific steps.
**How**: A base class defines a method with the fixed algorithm skeleton, calling abstract "hook" methods that subclasses override for the varying steps.
**Trade-offs**: Locks subclasses into a rigid inheritance hierarchy; modern C# increasingly prefers composition (injecting `Func<>`/`Action<>` delegates into a pipeline) over this inheritance-based approach. (Ch16)

## Command
**When to use**: You need to represent a request/action as a first-class object — for queuing, logging, undo/redo, or decoupling invoker from receiver.
**How**: A Command interface with an `Execute()` method; concrete commands hold a reference to a Receiver and the parameters needed to act on it.
**Trade-offs**: Adds a class per action if done rigidly; in 2025/26, commands are typically simple `record` types dispatched through a mediator library (e.g. MediatR) with pipeline behaviors for cross-cutting concerns — central to CQRS-style APIs. (Ch17)

## Iterator
**When to use**: Clients need sequential access to a collection's elements without depending on its internal structure.
**How**: An Iterator interface exposing `HasNext()`/`Next()`-style methods; the collection exposes a factory method to create an iterator over itself.
**Trade-offs**: Mostly absorbed into the language now — `IEnumerable<T>`, `yield return`, and LINQ already provide this; hand-written iterators remain useful only for bespoke traversal logic. (Ch18)

## Memento
**When to use**: You need to capture and later restore an object's internal state (undo/redo, checkpoints) without exposing its internals.
**How**: The Originator creates a Memento snapshot of its own state; a Caretaker stores Mementos without inspecting their contents; the Originator restores from a Memento when needed.
**Trade-offs**: Storing too many/large snapshots can be costly; increasingly relevant for undo/redo and auditing, now often expressed as an immutable `record` snapshot paired with event sourcing. (Ch19)

## State
**When to use**: An object's behavior must change based on its internal state, and state-conditional logic (`if`/`switch` on a state flag) has become unwieldy.
**How**: Each state is a class implementing a common State interface; the context delegates behavior to its current State object and can swap it to transition.
**Trade-offs**: Overkill for objects with only two simple states; particularly valuable for long-running, persistable workflows (order processing, approvals) where state objects can be rehydrated across async boundaries. (Ch20)

## Mediator
**When to use**: Many objects need to communicate, and direct references between them would create a tangled web of dependencies.
**How**: A Mediator object centralizes communication; colleague objects talk to the Mediator instead of directly to each other.
**Trade-offs**: The Mediator itself can become a complexity magnet if it absorbs too much logic; became foundational in 2025/26 practice via libraries like MediatR, routing commands/queries/notifications with pipeline behaviors replacing manual cross-cutting code. (Ch21)

## Chain of Responsibility
**When to use**: A request should be handled by one of several possible handlers, determined dynamically, without the sender knowing which handler will process it.
**How**: Handlers are linked in a chain; each handler either processes the request or passes it to the next handler in the chain.
**Trade-offs**: Debugging which handler ultimately processed a request can be harder in a long chain; now mostly implemented as ASP.NET Core middleware/pipelines rather than hand-rolled linked handler classes. (Ch22)

## Interpreter
**When to use**: You need to evaluate sentences in a small, well-defined grammar or expression language repeatedly.
**How**: Define a class hierarchy mirroring the grammar's rules, each implementing an `Evaluate()`/`Interpret()` method; compose them into expression trees representing input sentences.
**Trade-offs**: Grows complex/slow for anything beyond a small grammar; remains rare but not obsolete — used in rules engines, feature-flag evaluation, and config-driven access control; for general expression needs, expression trees/LINQ are usually preferred instead. (Ch23)

## Simple Factory
**When to use**: You need centralized, simple object-creation logic based on input, without the full ceremony of Factory Method's subclass hierarchy.
**How**: A single method/class with a conditional (`if`/`switch`) that returns the appropriate concrete instance based on input.
**Trade-offs**: Not part of the original GoF catalog — violates Open/Closed Principle more than Factory Method does (adding a type means editing the factory's conditional); in modern C#, this conditional is now typically a `switch` expression over pattern matching rather than an `if`-chain. (Ch24)

## Null Object
**When to use**: You want to avoid scattering null checks through calling code when "no object" is a legitimate, expected case.
**How**: Create a concrete class implementing the same interface as the real object, but with no-op/neutral behavior, and return it instead of `null`.
**Trade-offs**: Can silently mask a genuine missing-data bug if overused; stable pattern, no major modern replacement noted. (Ch25)

## MVC (Model-View-Controller)
**When to use**: An application needs a clean separation between data (Model), presentation (View), and request/input handling (Controller).
**How**: Model holds data and business rules; View renders it; Controller receives input, updates the Model, and selects the View to render.
**Trade-offs**: Can accumulate logic in the Controller if boundaries aren't disciplined; still supported in ASP.NET Core, but Minimal APIs (route-grouped, delegate-based endpoints) have become the more common default for new API/microservice code as of 2025/26. (Ch26)
