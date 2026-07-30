---
name: pro-async-dotnet
description: "Knowledge base from 'Pro Asynchronous Programming with .NET' by Richard Blewett and Andrew Clymer. Use when working with C# async/await, Task Parallel Library (TPL), Synchronization Primitives, or diagnosing concurrency issues."
---

# Pro Asynchronous Programming with .NET
**Authors**: Richard Blewett, Andrew Clymer | **Pages**: ~336 | **Chapters**: 11 | **Generated**: 2026-07-31

## How to Use This Skill
- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `SynchronizationContext`, `ConfigureAwait`, or `TPL`; I find and read the relevant chapter
- **With chapter** — ask for `ch05` to dive into Async and Await

---

## Core Frameworks & Mental Models

### The Asynchrony Matrix (CPU vs I/O)
- **CPU-Bound**: The operation requires intense calculation (e.g., image processing, encryption). Use `Task.Run` or PLINQ to distribute the work across multiple threads and CPU cores (Parallelism).
- **I/O-Bound**: The operation spends time waiting for external hardware or a network response (e.g., database query, HTTP request). Use `async/await` and asynchronous APIs (e.g., `GetStringAsync`). No thread is required while waiting (Asynchrony).

### The SynchronizationContext and Await
When you `await` an incomplete task, the framework captures the current `SynchronizationContext`. When the task completes, the remainder of the method resumes on that captured context.
- **In UI apps (WPF/WinForms)**: The context is the UI thread. The continuation runs safely on the UI thread.
- **In ASP.NET (pre-Core)**: The context is the request context.
- **In Console/ASP.NET Core**: There is no SynchronizationContext (ThreadPool context).

### The ConfigureAwait Rule
In library or backend code where you do not need to resume on the original UI thread, ALWAYS use `ConfigureAwait(false)`. This tells the runtime to execute the continuation on a random ThreadPool thread, preventing deadlocks and reducing overhead.

### The Async Void Anti-pattern
Never use `async void` except for event handlers. `async void` methods cannot be awaited, and any exceptions thrown inside them will crash the entire process because they escape the normal `Task` exception-handling pipeline.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-async.md) | Introduction to Asynchronous Programming | Concurrency vs Parallelism |
| [ch02](chapters/ch02-async.md) | The Task Parallel Library (TPL) Fundamentals | Task, ThreadPool |
| [ch03](chapters/ch03-async.md) | Task Continuations and Chaining | ContinueWith |
| [ch04](chapters/ch04-async.md) | Error Handling and Cancellation | AggregateException, CancellationToken |
| [ch05](chapters/ch05-async.md) | Async and Await (C# 5.0) | async, await, ConfigureAwait |
| [ch06](chapters/ch06-async.md) | Concurrent Collections | ConcurrentDictionary, BlockingCollection |
| [ch07](chapters/ch07-async.md) | Synchronization Primitives | lock, SemaphoreSlim |
| [ch08](chapters/ch08-async.md) | PLINQ (Parallel LINQ) | AsParallel, ForAll |
| [ch09](chapters/ch09-async.md) | The BackgroundWorker and EAP (Legacy) | BackgroundWorker |
| [ch10](chapters/ch10-async.md) | APM (Asynchronous Programming Model) (Legacy) | IAsyncResult |
| [ch11](chapters/ch11-async.md) | Async UI and ASP.NET | Scalability vs Responsiveness |

## Topic Index
- **AggregateException** → ch04
- **async void** → ch05
- **CancellationToken** → ch04
- **Concurrent Collections** → ch06
- **ConfigureAwait** → ch05, ch11
- **ContinueWith** → ch03
- **PLINQ** → ch08
- **SemaphoreSlim** → ch07
- **SynchronizationContext** → ch05
- **Task.Run** → ch02

## Supporting Files
- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides\n