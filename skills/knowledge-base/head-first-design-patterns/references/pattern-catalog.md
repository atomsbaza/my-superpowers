# Pattern Catalog

Use this file for quick recognition. Read the linked chapter when the pattern appears relevant.

## Creational patterns

| Pattern | Intent | Reach for it when | Watch for |
|---|---|---|---|
| Factory Method | Let subclasses decide which class to instantiate through a creation interface | A framework owns the creation process but subclasses choose the product | Inheritance couples creation to a class hierarchy |
| Abstract Factory | Create families of related objects without naming concrete classes | Products must be mutually compatible across a product family | Families can become difficult to extend with a new product kind |
| Singleton | Ensure one instance and a global access point | Uniqueness is a real, enforced domain or infrastructure constraint | Hidden global state, tests, class loaders, reflection, serialization, and concurrency |
| Builder | Separate complex construction from representation | Construction is staged, optional, validated, or has many parameters | Ceremony for simple products |
| Prototype | Create by copying a configured prototype | Construction is expensive or the concrete type is selected at runtime | Shallow versus deep copy and identity semantics |

## Behavioral patterns

| Pattern | Intent | Reach for it when | Watch for |
|---|---|---|---|
| Strategy | Encapsulate interchangeable algorithms | A family of algorithms varies independently from clients | Too many tiny strategies can obscure a trivial decision |
| Observer | Notify many dependents when one subject changes | Subscribers should update without the subject knowing concrete details | Notification order, leaks, storms, and push/pull contract ambiguity |
| Command | Encapsulate a request as an object | Actions need undo, queueing, logging, retries, or macros | Commands can become an anemic wrapper or capture stale state |
| Template Method | Fix an algorithm skeleton and defer steps to subclasses | Implementations share an invariant sequence | Inheritance rigidity and hooks with unsafe defaults |
| Iterator | Traverse an aggregate without exposing representation | Several collection types need one traversal protocol | Mutation, invalidation, and traversal cost |
| State | Alter behavior as internal state changes | Lifecycle states make conditionals unstable | State explosion and unclear transition ownership |
| Chain of Responsibility | Pass a request through possible handlers | Multiple handlers may accept or reject a request | Unhandled requests and difficult tracing |
| Mediator | Centralize interactions among colleagues | Direct many-to-many communication is tangled | Mediator becoming a god object |
| Memento | Save and restore state without exposing internals | Undo, checkpoints, or rollback are required | Snapshot size and retention policy |
| Interpreter | Represent and interpret a grammar | A small, stable language needs a direct object model | Poor scalability for large grammars |
| Visitor | Add operations across a stable element structure | Operations change more often than element classes | New element types require every visitor update |

## Structural patterns

| Pattern | Intent | Reach for it when | Watch for |
|---|---|---|---|
| Decorator | Add responsibilities dynamically through wrapping | Behavior should be combined per object without subclass explosion | Deep chains, ordering, and identity-sensitive code |
| Adapter | Convert an existing interface to the one clients expect | Incompatible classes must collaborate | Adapter proliferation or a wrong abstraction boundary |
| Facade | Provide a unified higher-level subsystem interface | Clients should not orchestrate subsystem details | Facade becoming a second domain layer |
| Composite | Treat leaves and compositions uniformly in a tree | The domain is recursive and part-whole | Transparent interfaces with invalid leaf operations |
| Proxy | Control access through a surrogate with the same interface | Access requires remoting, laziness, protection, caching, or synchronization | Hidden latency and changed failure semantics |
| Bridge | Separate abstraction from implementation | Both axes need independent extension | Indirection before the axes actually vary |
| Flyweight | Share intrinsic state across many fine-grained objects | Object count or memory is the limiting pressure | Mutable shared state and context lookup complexity |

