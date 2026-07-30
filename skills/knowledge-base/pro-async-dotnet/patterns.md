# Patterns & Refactorings

## Async over Sync (Anti-pattern)
**When to use**: Never.
**How**: Wrapping a truly synchronous, blocking operation in a `Task.Run` just to expose an asynchronous signature.
**Trade-offs**: This burns a ThreadPool thread just to block it, offering no scalability benefits and misleading callers into thinking the operation is truly asynchronous.

## Sync over Async (Anti-pattern)
**When to use**: Avoid at all costs, unless deeply integrating with legacy synchronous systems.
**How**: Calling `.Result` or `.Wait()` on a Task inside synchronous code.
**Trade-offs**: This blocks the calling thread while another thread executes the task. If the task requires the calling thread's SynchronizationContext to complete (common in UI apps), it causes a classic deadlock.

## The Fire-and-Forget Pattern
**When to use**: When you need to start an asynchronous operation but do not care when it finishes or if it succeeds.
**How**: Store the Task in a local variable or use a fire-and-forget extension method that explicitly catches and logs exceptions. Never use `async void`.
**Trade-offs**: You lose the ability to track completion, but it frees the caller immediately.

## The Producer-Consumer Pattern
**When to use**: When you have one or more threads creating data (Producers) and one or more threads processing that data (Consumers).
**How**: Use a `BlockingCollection<T>`. Producers call `Add()`, Consumers iterate over `GetConsumingEnumerable()`.
**Trade-offs**: Provides a highly robust, thread-safe queue with built-in blocking, vastly simplifying coordination between threads.\n