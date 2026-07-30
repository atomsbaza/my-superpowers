# Async/Await Cheatsheet

## The Async Decision Tree

1. **Is the work CPU-Bound?** (e.g., complex math, image processing)
   - Yes: Use `Task.Run(() => Compute())`.
2. **Is the work I/O-Bound?** (e.g., database, network, disk)
   - Yes: Use native async APIs (e.g., `client.GetAsync()`). Do NOT wrap in `Task.Run`.
3. **Are you in a UI application?**
   - Yes: Await tasks normally to resume on the UI thread and update controls.
4. **Are you in a library or backend service (ASP.NET)?**
   - Yes: Suffix every await with `.ConfigureAwait(false)` to prevent deadlocks and unnecessary thread-hopping overhead.

## Quick Rules

- **Return Type**: Always return `Task` or `Task<T>`. Never `void` (unless it's a UI event handler).
- **Naming**: Always append `Async` to the name of asynchronous methods.
- **Cancellation**: Always accept a `CancellationToken` as the last parameter of an async method.
- **Exceptions**: Exceptions in async methods are caught by the compiler state machine and placed on the returning Task. They will be re-thrown when the Task is awaited.
- **Locking**: You cannot use `lock (object) { await ... }`. If you need to lock across an await, use `SemaphoreSlim` and `await semaphore.WaitAsync()`.

## Common TPL Methods

| Method | Purpose |
|---|---|
| `Task.Run` | Queues work to the ThreadPool (CPU-bound). |
| `Task.WhenAll` | Creates a task that completes when *all* provided tasks complete. |
| `Task.WhenAny` | Creates a task that completes when *any* of the provided tasks complete. |
| `Task.Delay` | An asynchronous equivalent of `Thread.Sleep`. Does not block the thread. |
| `Task.FromResult` | Creates a task that has already completed successfully with the specified result. Useful for mocking interfaces. |\n