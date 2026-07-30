# Chapter 7: Synchronization Primitives

## Core Idea
When multiple threads need to access shared state, you must coordinate their access to prevent race conditions and data corruption. .NET provides various synchronization primitives to achieve this.

## Key Concepts
- **lock (Monitor)**: The most common and easiest way to ensure only one thread executes a block of code at a time.
- **SemaphoreSlim**: A lightweight alternative to `Semaphore` that limits the number of threads that can access a resource concurrently. Crucially, it supports async waits via `WaitAsync()`.
- **Interlocked**: Provides atomic operations for variables that are shared by multiple threads (e.g., `Interlocked.Increment`).

## Anti-patterns
- **Locking on Async**: You cannot use the `lock` keyword across an `await` boundary. If you need to lock across asynchronous calls, use `SemaphoreSlim` with an initial count of 1.
- **Deadlocks**: Thread A holds Lock 1 and waits for Lock 2, while Thread B holds Lock 2 and waits for Lock 1.

## Key Takeaways
1. Avoid shared state whenever possible. If state isn't shared, it doesn't need synchronization.
2. Use `SemaphoreSlim.WaitAsync()` when you need asynchronous mutual exclusion.\n