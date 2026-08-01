---
name: dobovizki-csharp-concurrency
description: 'Knowledge base from "C# Concurrency: Asynchronous and multithreaded programming" by Nir Dobovizki. Use when applying C# async/await frameworks, multithreading patterns, thread safety primitives, and performance optimizations.'
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# C# Concurrency: Asynchronous and Multithreaded Programming
**Author**: Nir Dobovizki | **Pages**: ~250 | **Chapters**: 14 | **Generated**: 2026-07-31

## How to Use This Skill

- **Without arguments** — load core C# concurrency frameworks for reference
- **With a topic** — ask about `SynchronizationContext`, `ValueTask`, `SemaphoreSlim`, or `IAsyncEnumerable`; I find and read the relevant chapter
- **With chapter** — ask for `ch03` or `ch07`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to view the full index

---

## Core Frameworks & Mental Models

### 1. The I/O-Bound vs. CPU-Bound Execution Model
- **I/O-Bound Work**: Operates without consuming CPU threads while waiting for hardware, network, or disk responses. Use `async/await`. The OS uses I/O Completion Ports (IOCP) to wake up thread pool threads when data arrives.
- **CPU-Bound Work**: Consumes active CPU calculation cycles. Use `Task.Run` in UI applications to offload calculation from the main thread. Run synchronously in web server requests to avoid ThreadPool hop overhead.

### 2. Compiler State Machine Transformation
Methods marked `async` are rewritten by the C# compiler into value-type state machines implementing `IAsyncStateMachine`.
- Every `await` point marks a potential suspension point (`State = N`).
- If an awaited task is incomplete, `await` registers `MoveNext()` as a continuation and returns an incomplete `Task` immediately.
- Local variables active across `await` points are hoisted into fields on the state machine struct.

### 3. Synchronization & Thread Safety Hierarchy
- **Lock-Free Atomic Operations**: Use `Interlocked` for simple counters or reference swaps without thread locking overhead.
- **Synchronous Critical Sections**: Use `lock(_syncLock)` for fast in-memory mutual exclusion.
- **Asynchronous Critical Sections**: Use `SemaphoreSlim(1, 1)` with `await _semaphore.WaitAsync()` when critical sections contain `await` calls.

### 4. Thread Affinity & SynchronizationContext
- **UI Applications (WPF, WinForms, MAUI)**: `await` captures the `SynchronizationContext` and marshals continuation back to the UI thread.
- **Class Libraries & NuGets**: Append `.ConfigureAwait(false)` to all `await` calls to bypass context capturing, avoid UI thread deadlocks, and boost performance.

### 5. Asynchronous Data Pipelines & Streams
- **Bounded Backpressure**: Use `System.Threading.Channels` (`Channel.CreateBounded<T>`) for thread-safe producer-consumer background queues.
- **Controlled Parallel Async**: Use `Parallel.ForEachAsync` with `MaxDegreeOfParallelism` to process batch I/O without socket or memory exhaustion.
- **Async Streaming**: Use `IAsyncEnumerable<T>` with `yield return` and `await foreach` to stream datasets item-by-item.

---

## Chapter Index

| # | Title | Key Frameworks & Topics |
|---|-------|-------------------------|
| [ch01](chapters/ch01-asynchronous-programming-and-multithreading.md) | Asynchronous programming and multithreading | I/O vs CPU work, IOCP, thread efficiency |
| [ch02](chapters/ch02-the-compiler-rewrites-your-code.md) | The compiler rewrites your code | `IAsyncStateMachine`, `AsyncTaskMethodBuilder`, hoisted variables |
| [ch03](chapters/ch03-the-async-and-await-keywords.md) | The async and await keywords | `Task`, `ValueTask`, `Task.WhenAll`, `TaskCompletionSource` |
| [ch04](chapters/ch04-multithreading-basics.md) | Multithreading basics | `Thread`, `ThreadPool`, `Task.Run`, context switching |
| [ch05](chapters/ch05-async-await-and-multithreading.md) | async/await and multithreading | Continuation thread jumps, `AsyncLocal<T>`, ambient context |
| [ch06](chapters/ch06-when-to-use-async-await.md) | When to use async/await | UI responsiveness vs Server throughput, decision tree |
| [ch07](chapters/ch07-classic-multithreading-pitfalls-and-how-to-avoid-them.md) | Classic multithreading pitfalls and how to avoid them | Race conditions, deadlocks, `Interlocked`, `SemaphoreSlim` |
| [ch08](chapters/ch08-processing-a-sequence-of-items-in-the-background.md) | Processing a sequence of items in the background | `Parallel.ForEachAsync`, `Channel<T>`, backpressure |
| [ch09](chapters/ch09-canceling-background-tasks.md) | Canceling background tasks | `CancellationTokenSource`, `CancellationToken`, cooperative cancellation |
| [ch10](chapters/ch10-await-your-own-events.md) | Await your own events | Event-to-Task bridge, `TaskCompletionSource`, `GetAwaiter()` |
| [ch11](chapters/ch11-controlling-on-which-thread-your-asynchronous-code-runs.md) | Controlling on which thread your asynchronous code runs | `SynchronizationContext`, `ConfigureAwait(false)`, deadlock prevention |
| [ch12](chapters/ch12-exceptions-and-async-await.md) | Exceptions and async/await | `AggregateException`, unwrapping, `ExceptionDispatchInfo` |
| [ch13](chapters/ch13-thread-safe-collections.md) | Thread-safe collections | `ConcurrentDictionary`, `BlockingCollection`, `FrozenDictionary` |
| [ch14](chapters/ch14-generating-collections-asynchronously.md) | Generating collections asynchronously | `IAsyncEnumerable<T>`, `await foreach`, `[EnumeratorCancellation]` |

---

## Topic Index

- **AggregateException** → ch03, ch12
- **AsyncLocal<T>** → ch05
- **AsyncTaskMethodBuilder** → ch02
- **Atomic Operations / Interlocked** → ch07
- **Backpressure / Bounded Queue** → ch08
- **BlockingCollection** → ch13
- **CancellationToken / CancellationTokenSource** → ch09
- **Channels (System.Threading.Channels)** → ch08
- **ConfigureAwait(false)** → ch03, ch11
- **Deadlocks** → ch07, ch11
- **Event-to-Task Bridge** → ch10
- **Exception Handling** → ch12
- **FrozenCollection** → ch13
- **IAsyncEnumerable<T> / await foreach** → ch14
- **IAsyncStateMachine** → ch02
- **I/O vs CPU Bound Work** → ch01, ch06
- **Locking / SemaphoreSlim** → ch07
- **Parallel.ForEachAsync** → ch08
- **SynchronizationContext** → ch11
- **Task.Run vs ThreadPool** → ch04
- **ValueTask** → ch03

---

## Supporting Files

- [glossary.md](glossary.md) — complete A-Z glossary of C# concurrency terms
- [patterns.md](patterns.md) — concrete concurrent implementation patterns
- [cheatsheet.md](cheatsheet.md) — quick decision rules and anti-pattern smells

---

## Scope & Limits

This skill covers C# asynchronous and multithreaded programming concepts based on Nir Dobovizki's book. For project-specific architecture, combine with your codebase tools.
