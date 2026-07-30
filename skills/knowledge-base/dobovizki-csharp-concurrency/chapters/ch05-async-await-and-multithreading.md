# Chapter 5: async/await and multithreading

## Core Idea
`async/await` and multithreading are complementary concepts: `async/await` manages asynchronous state transitions and continuations, while multithreading provides execution threads. Understanding how `await` transitions between threads is key to writing clean concurrent code.

## Frameworks Introduced
- **The Continuation Thread Scheduling Model**:
  - When to use: Tracking which thread executes your code before and after an `await`.
  - How: Code before `await` runs on the initial thread. When `await` completes, the continuation code executes on a ThreadPool thread (or UI thread if a `SynchronizationContext` is captured).

## Key Concepts
- **Thread Context Switch at Await Boundary**: An `async` method can start on Thread A (e.g. ThreadPool thread #3), await an I/O task, and resume after the await on Thread B (ThreadPool thread #7).
- **Thread-Local State Caution**: Thread-local storage (`[ThreadStatic]`, `ThreadLocal<T>`) does NOT persist across `await` points because continuation may run on a different thread.
- **AsyncLocal<T>**: Ambient context storage that flows across `await` points and asynchronous calls.

## Mental Models
- Think of `AsyncLocal<T>` as a **Baton in a Relay Race**: As execution jumps from thread to thread across `await` calls, the ambient context baton is passed along to the next runner.

## Anti-patterns
- **Using `[ThreadStatic]` across await boundaries**: Expecting thread-static variables to hold values after an `await` causes bugs because the continuation thread is different.

## Code Examples
```csharp
// AsyncLocal vs ThreadStatic behavior
public class ContextFlowExample
{
    private static ThreadLocal<string> _threadLocal = new ThreadLocal<string>();
    private static AsyncLocal<string> _asyncLocal = new AsyncLocal<string>();

    public async Task DemonstrateFlowAsync()
    {
        _threadLocal.Value = "Tenant-123";
        _asyncLocal.Value = "Tenant-123";

        Console.WriteLine($"Before Await: Thread={Thread.CurrentThread.ManagedThreadId}");
        await Task.Delay(100); // Resume on any ThreadPool thread
        Console.WriteLine($"After Await:  Thread={Thread.CurrentThread.ManagedThreadId}");

        // BROKEN: ThreadLocal may be null or hold another thread's value!
        Console.WriteLine($"ThreadLocal: { _threadLocal.Value ?? "NULL" }");

        // CORRECT: AsyncLocal flows context correctly across await!
        Console.WriteLine($"AsyncLocal:  { _asyncLocal.Value }");
    }
}
```
- **What it demonstrates**: Why `AsyncLocal<T>` must be used instead of `ThreadLocal<T>` in async code.

## Reference Tables
| Mechanism | Survives Across `await`? | Scope |
|---|---|---|
| `[ThreadStatic]` | ❌ No | Tied to physical OS Thread ID |
| `ThreadLocal<T>` | ❌ No | Tied to physical OS Thread ID |
| `AsyncLocal<T>` | ✅ Yes | Flows down execution context tree |

## Worked Example
In ASP.NET Core request processing:
- A web request arrives on ThreadPool Thread #1.
- `AsyncLocal<T>` stores the Request Correlation ID (`TraceId`).
- The action awaits a database query (`await _db.Users.ToListAsync()`).
- Database query completes, continuation resumes on ThreadPool Thread #4.
- `AsyncLocal<T>` automatically presents the correct `TraceId` on Thread #4.

## Key Takeaways
1. An async method does not guarantee execution on a single thread throughout its lifetime.
2. Never rely on Thread ID or `ThreadLocal` in methods containing `await`.
3. Use `AsyncLocal<T>` for ambient request context, correlation IDs, or security tokens in async code.

## Connects To
- **Ch 4**: Low-level thread pool mechanics.
- **Ch 11**: `SynchronizationContext` and thread affinity.
