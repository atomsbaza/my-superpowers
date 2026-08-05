# Java-Oriented Design Checklist

Use this during implementation or review. The patterns are design tools; Java language and runtime details still need explicit decisions.

## Before choosing a pattern

- What requirement or change is driving the design?
- Which behavior, creation decision, representation, or collaboration varies?
- Is the variation real and recurring, or only hypothetical?
- Would a function, constructor, parameter, or small refactoring solve it more clearly?
- What are the expected object lifetime, ownership, and thread-safety rules?

## Abstractions and dependencies

- Do clients depend on interfaces or stable supertypes where substitution matters?
- Are concrete collaborators constructed in the right boundary rather than scattered through policy code?
- Are abstractions meaningful capabilities, or empty interfaces created only to fit a diagram?
- Is dependency injection clearer than a global access point?
- Are public methods expressing a contract instead of exposing implementation details?

## Composition and inheritance

- Can behavior be composed at runtime rather than baked into a subclass hierarchy?
- If using inheritance, is there a genuine shared algorithm skeleton or substitutability relationship?
- Does a subclass preserve the superclass contract?
- Are decorators, proxies, or adapters distinguishable by intent and named clearly?
- Are wrapper ordering, identity, equals/hashCode, and resource ownership defined?

## Observer and eventing

- How are observers registered and removed?
- Can subscriptions leak because a long-lived subject retains a short-lived observer?
- Is notification synchronous or asynchronous?
- Are event order, duplicate events, reentrancy, and failure isolation specified?
- Does the event carry enough information for observers to pull or receive the update?

## Factories and construction

- Which product families must remain compatible?
- Does a factory hide concrete classes without hiding important configuration errors?
- Should construction fail fast, return a result, or use a default?
- Can Builder validate an incomplete or conflicting configuration?
- If Prototype is used, are mutable nested objects copied at the intended depth?

## Commands and undo

- Does a command capture the receiver, request data, and execution-time dependencies safely?
- Is undo an inverse action or restoration of prior state?
- Is the command idempotent, retryable, serializable, and safe to queue?
- What happens when the receiver changes between execute and undo?
- Are macro failure and partial rollback defined?

## State machines

- Is every state/event pair defined, including invalid events?
- Where do transitions live, and why?
- Are guards, side effects, and terminal states explicit?
- Are State objects stateless and shareable, or do they carry context-specific data?
- Are state transitions observable and testable without relying on sleeps or timing?

## Collections and trees

- Is traversal independent from storage representation?
- What are iterator behavior and mutation guarantees?
- Does a Composite operation terminate correctly at leaves?
- Is the Composite interface transparent or safe, and is that trade-off intentional?
- Are deep trees, cycles, and large collections handled?

## Proxy and boundaries

- Is remote latency, failure, cancellation, and retry visible in the contract?
- Is lazy initialization safe under concurrent access?
- Are authorization checks enforced at the actual trust boundary?
- Are caching freshness and invalidation rules explicit?
- Does the proxy preserve the subject’s semantics closely enough for substitution?

## Testing

- Test each concrete strategy, state transition, factory family, and command.
- Test observer registration, removal, duplicate notification, and failure behavior.
- Test decorator order and adapter compatibility.
- Test Composite leaf and nested cases, including empty composites.
- Test proxy laziness, denied access, cache behavior, and failure paths.
- Test the smallest collaboration boundary rather than only large end-to-end examples.

