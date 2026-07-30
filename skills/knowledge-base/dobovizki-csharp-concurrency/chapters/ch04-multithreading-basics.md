# Chapter 4: Multithreading basics

## Core Idea
Multithreading involves creating and executing multiple OS threads to perform CPU-intensive tasks simultaneously across available CPU cores. Proper use of the .NET `ThreadPool` and `Task.Run` avoids the high cost of manual thread creation and context switching.

## Frameworks Introduced
- **The Thread Management Hierarchy**:
  - When to use: Offloading CPU-bound tasks to worker threads.
  - How: Prefer `Task.Run()` (which uses the .NET ThreadPool). Avoid manually instantiating `new Thread()` unless you specifically require a long-running thread with custom stack size or thread priority.
- **The ThreadPool Hill-Climbing Algorithm**:
  - When to use: Understanding how .NET dynamically scales worker threads.
  - How: The .NET runtime monitors throughput and dynamically adds or removes threads from the pool based on workload demand and CPU utilization metrics.

## Key Concepts
- **Thread**: OS thread with kernel object overhead (~1MB stack reservation).
- **ThreadPool**: Managed pool of pre-allocated worker threads reused across multiple background tasks.
- **Task.Run**: Queues a delegate to run on a ThreadPool thread and returns a `Task` representing its execution.
- **Context Switch**: The OS CPU scheduler saving the state of one thread and restoring another (~microseconds overhead).

## Mental Models
- Think of manual **`new Thread()`** as hiring a new full-time employee for a 5-second task; think of **`ThreadPool` / `Task.Run`** as assigning a quick job ticket to an existing pool of active employees.

## Anti-patterns
- **Spawning hundreds of manual threads (`new Thread()`)**: Exhausts OS memory and causes extreme CPU thrashing due to continuous context switching.
- **ThreadPool Starvation**: Queueing long-running, blocking synchronous work onto ThreadPool threads, preventing other pool items from executing.

## Code Examples
```csharp
// BAD: Manual thread creation overhead
public void ProcessDataManual(byte[] data)
{
    Thread t = new Thread(() => HeavyComputation(data));
    t.IsBackground = true;
    t.Start();
    t.Join(); // Blocks calling thread!
}

// GOOD: ThreadPool via Task.Run
public async Task ProcessDataThreadPoolAsync(byte[] data)
{
    // Offloads work to ThreadPool worker thread without blocking current thread
    await Task.Run(() => HeavyComputation(data));
}
```
- **What it demonstrates**: Using `Task.Run` to delegate CPU-intensive work to the ThreadPool.

## Reference Tables
| Approach | Creation Cost | Lifecycle | Best Used For |
|---|---|---|---|
| `new Thread()` | High (~1MB stack + OS call) | Explicit `Start()` & `Join()` | Rare long-running background loops |
| `ThreadPool.QueueUserWorkItem` | Low (reused thread) | Fire-and-forget | Legacy .NET 1.1/2.0 code |
| `Task.Run` | Low (reused thread) | Managed via `Task` & `await` | Modern CPU-bound work in .NET |

## Worked Example
Computing a 3D raytracing render frame across an 8-core CPU:
- Divide image into 8 vertical strips.
- Dispatch 8 tasks via `Task.Run()` for each strip.
- Await `Task.WhenAll(tasks)`.
- All 8 CPU cores hit 100% utilization simultaneously, rendering the frame 7.5x faster than a single-threaded loop.

## Key Takeaways
1. Always use `Task.Run()` for CPU-bound tasks instead of `new Thread()`.
2. Do not use `Task.Run()` for I/O-bound operations (it wastes a thread pool thread).
3. ThreadPool threads are background threads; they terminate automatically when the main process exits.

## Connects To
- **Ch 1**: Contrasts CPU-bound work with I/O-bound async work.
- **Ch 5**: Integrates `Task.Run` with `async/await`.
