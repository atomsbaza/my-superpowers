# Chapter 3: Task Continuations and Chaining

## Core Idea
Instead of blocking a thread to wait for a task to finish, you can chain a "continuation" task that automatically executes when the antecedent task completes.

## Key Concepts
- **ContinueWith**: The fundamental TPL method to attach a continuation task.
- **TaskContinuationOptions**: Flags to control when the continuation runs (e.g., `OnlyOnFaulted`, `OnlyOnRanToCompletion`).
- **Unwrapping**: Handling nested tasks (`Task<Task<T>>`) using the `Unwrap()` extension method to flatten them into `Task<T>`.

## Mental Models
- Think of continuations as a **callback chain**, but strongly typed and managed by the TPL runtime, ensuring exceptions and cancellation flow properly.

## Anti-patterns
- **Result/Wait Blocking**: Calling `.Result` or `.Wait()` on a task. This forces the current thread to block until the task finishes, destroying the benefits of asynchronous execution and risking deadlocks.

## Key Takeaways
1. Avoid blocking on Tasks. Let the TPL schedule continuations.
2. `ContinueWith` allows explicit control over error handling and success paths before `async/await` was available.\n