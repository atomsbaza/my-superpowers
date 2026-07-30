# Chapter 2: The Task Parallel Library (TPL) Fundamentals

## Core Idea
The `Task` class is the foundation of modern .NET concurrency. It represents an ongoing operation, which might be CPU-bound (running on the ThreadPool) or I/O-bound (no thread attached).

## Frameworks Introduced
- **Task Creation**:
  - When to use: When you need to offload CPU-bound work.
  - How: Use `Task.Run(Action)` to queue work to the ThreadPool. (Avoid the older `new Task().Start()` unless necessary for complex scenarios).

## Key Concepts
- **Task**: An object that represents the future completion of an operation.
- **ThreadPool**: A managed pool of background worker threads that minimizes the overhead of thread creation and destruction.
- **TaskStatus**: The lifecycle of a task (Created, WaitingToRun, Running, RanToCompletion, Faulted, Canceled).

## Code Examples
```csharp
// Offloading CPU-bound work to the ThreadPool
Task<int> computeTask = Task.Run(() => {
    return HeavyMathComputation();
});
```
- **What it demonstrates**: Using `Task.Run` to easily schedule work on a background thread.

## Key Takeaways
1. Prefer `Task.Run` for offloading CPU-bound work.
2. A `Task` does not necessarily mean a dedicated thread is running; it's a promise of completion.\n