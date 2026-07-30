# Chapter 7: Classic multithreading pitfalls and how to avoid them

## Core Idea
Concurrent access to shared mutable state introduces race conditions, deadlocks, and memory visibility bugs. Using primitive synchronization objects (`lock`, `Interlocked`, `SemaphoreSlim`) correctly guarantees thread safety.

## Frameworks Introduced
- **The Synchronization Primitive Matrix**:
  - When to use: Protecting shared state from data races.
  - How:
    - Single integer/reference updates -> `Interlocked` (fastest, lock-free).
    - In-memory synchronous critical section -> `lock (object)` (fast, blocking).
    - Asynchronous critical section across `await` -> `SemaphoreSlim(1, 1)` (async-friendly).

## Key Concepts
- **Race Condition**: Undefined behavior when multiple threads read/write shared state concurrently without synchronization.
- **Deadlock**: Two or more threads waiting indefinitely for locks held by each other.
- **Lock-Free Atomic Operations**: Low-level hardware instructions (`Interlocked.Increment`, `Interlocked.CompareExchange`) that update memory atomically without thread blocking.
- **Asynchronous Lock (`SemaphoreSlim`)**: Standard `lock` statement cannot contain `await` calls; `SemaphoreSlim.WaitAsync()` allows locking asynchronously.

## Mental Models
- Think of **`lock`** as a single-occupancy bathroom door lock; think of **`SemaphoreSlim(N)`** as a bouncer allowing up to N guests into a club at a time.

## Anti-patterns
- **`await` inside a standard `lock` block**: C# compiler forbids `await` inside `lock(obj)` because the thread resuming after `await` may differ from the thread that acquired the lock, causing lock corruption or deadlocks.
- **Locking on `this` or `typeof(Foo)` or public strings**: Exposes lock objects globally, allowing external code to deadlock your class. Always lock on a `private final object _syncLock = new object();`.

## Code Examples
```csharp
// BAD: Race Condition on shared counter
public class UnsafeCounter
{
    private int _count = 0;
    public void Increment() => _count++; // NOT thread-safe! (Read-Modify-Write)
}

// GOOD: Atomic Lock-Free Counter
public class SafeCounter
{
    private int _count = 0;
    public void Increment() => Interlocked.Increment(ref _count); // Thread-safe!
    public int Value => Volatile.Read(ref _count);
}

// GOOD: Asynchronous Locking with SemaphoreSlim
public class AsyncCache
{
    private readonly SemaphoreSlim _mutex = new SemaphoreSlim(1, 1);

    public async Task AccessResourceAsync()
    {
        await _mutex.WaitAsync(); // Asynchronously waits for lock
        try
        {
            await Task.Delay(100); // Safe to await inside SemaphoreSlim!
        }
        finally
        {
            _mutex.Release(); // Always release in finally block!
        }
    }
}
```
- **What it demonstrates**: Thread safety via `Interlocked` for integers and `SemaphoreSlim` for async critical sections.

## Reference Tables
| Primitive | Supports `await`? | Overhead | Recommended Use Case |
|---|---|---|---|
| `Interlocked` | N/A (Atomic HW) | Lowest (~nanoseconds) | Counter, flags, reference swap |
| `lock(object)` | ❌ No | Low (~tens of ns) | In-memory sync critical section |
| `SemaphoreSlim` | ✅ Yes (`WaitAsync`) | Medium (~microseconds) | Async critical sections & rate-limiting |
| `ReaderWriterLockSlim` | ❌ No | Medium | High read / low write data structures |

## Worked Example
A classic deadlock scenario:
- Thread 1 locks `ResourceA`, then tries to lock `ResourceB`.
- Thread 2 locks `ResourceB`, then tries to lock `ResourceA`.
- Both threads hang forever.
- **Solution**: Always acquire multiple locks in a strict global lock ordering, or combine them into a single lock object.

## Key Takeaways
1. Never lock on public objects, `this`, or strings.
2. Use `Interlocked` for simple primitive operations.
3. Use `SemaphoreSlim` whenever you need synchronization around an `await`.
4. Always release locks/semaphores in a `finally` block.

## Connects To
- **Ch 4**: Threading basics.
- **Ch 13**: Thread-safe concurrent collections.
