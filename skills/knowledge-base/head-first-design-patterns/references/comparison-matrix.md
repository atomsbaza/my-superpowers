# Pattern Comparison Matrix

Pattern names often overlap in structure. Use intent, ownership, and change pressure to distinguish them.

| If the primary question is… | Consider | Mechanism | Key distinction |
|---|---|---|---|
| Which complete algorithm should run? | Strategy | Composition | Client or context selects a whole algorithm |
| Which steps in a fixed algorithm vary? | Template Method | Inheritance | Superclass owns the skeleton |
| What does this lifecycle event mean now? | State | Delegation | Current state owns phase-specific behavior |
| Who should be notified? | Observer | Subscription | Subject knows observers through an abstraction |
| How should many objects coordinate? | Mediator | Central coordination | Colleagues communicate through a coordinator |
| How should this request be represented? | Command | Request object | Enables invoker, queue, log, macro, and undo |
| How can a new behavior wrap one object? | Decorator | Recursive composition | Same interface, added responsibility |
| How can an old interface fit a new client? | Adapter | Interface translation | Compatibility, not added responsibility |
| How can clients use a subsystem simply? | Facade | Unified entry point | Orchestration and complexity hiding |
| How can access be controlled? | Proxy | Surrogate | Same interface, mediated access |
| How can a collection be traversed? | Iterator | External traversal object | Representation stays private |
| How can a tree be treated uniformly? | Composite | Recursive composition | Leaves and containers share a component protocol |
| How should one product be created? | Factory Method | Deferred creation | Subclass decides concrete product |
| How should a compatible product family be created? | Abstract Factory | Factory family | Products are coordinated across a family |
| How should a complex product be assembled? | Builder | Staged construction | Construction process is separated from product |
| How can an expensive configured object be duplicated? | Prototype | Copying | New object starts from a prototype |

## Decision heuristics

- Strategy versus Template Method: choose Strategy for runtime substitution and independent algorithm families; choose Template Method when one algorithm skeleton is stable and subclasses fill steps.
- State versus Strategy: choose State when behavior changes as events move an object through phases; choose Strategy when the variation is a selected algorithm without a lifecycle graph.
- Adapter versus Decorator: choose Adapter when the client interface is wrong; choose Decorator when the interface is right but responsibilities need extension.
- Decorator versus Proxy: choose Decorator when composition should add behavior; choose Proxy when a boundary should control or defer access.
- Facade versus Adapter: choose Facade when simplifying a set of interfaces; choose Adapter when translating one existing interface.
- Factory Method versus Abstract Factory: choose Factory Method for one product with subclass-controlled creation; choose Abstract Factory for a product family whose members must fit together.
- Composite versus Decorator: both can wrap or contain components, but Composite models part-whole hierarchy while Decorator models layered responsibility.
- Command versus Strategy: both encapsulate behavior, but Command represents an invocation while Strategy represents an algorithm.

## Review prompts

1. What change would force the most existing code to be edited?
2. Which object should own that decision?
3. Is the variation per object, per class hierarchy, per request, or per lifecycle state?
4. Does the proposed pattern reduce coupling enough to justify its indirection?
5. What are the failure, ownership, thread-safety, and testing consequences?

