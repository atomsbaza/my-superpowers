# Chapter 8: Processing a sequence of items in the background

## Core Idea
Processing large batches or streams of data in the background requires controlling parallelism, queue size, and throughput. .NET provides modern primitives like `Parallel.ForEachAsync` and `Channel<T>` for efficient background pipeline execution.

## Frameworks Introduced
- **The Bounded Pipeline Pattern**:
  - When to use: Processing items from a queue in the background without blowing up memory.
  - How: Use `Channel.CreateBounded<T>(capacity)` to create backpressure between producer threads and worker consumer tasks.
- **Parallel.ForEachAsync Throttling Framework**:
  - When to use: Processing collection items with limited concurrent I/O calls.
  - How: Set `ParallelOptions.MaxDegreeOfParallelism` to bound active concurrent requests.

## Key Concepts
- **Backpressure**: Preventing producers from queuing more work items than consumers can process, avoiding out-of-memory crashes.
- **Parallel.ForEachAsync**: Modern .NET 6+ API for processing async work across collections with controlled parallelism.
- **Channels (`System.Threading.Channels`)**: High-performance, lock-free thread-safe producer-consumer queue.

## Mental Models
- Think of a **Bounded Channel** as a conveyor belt in a factory with limited space: if the belt is full, the producer waits until consumers take an item off.

## Anti-patterns
- **Unbounded Queueing (`Task.WhenAll` on 100,000 items)**: Launching 100,000 concurrent network requests at once exhausts sockets, causes timeouts, and crashes memory.
- **Using `Parallel.ForEach` for Async Work**: `Parallel.ForEach` is for CPU-bound sync work; using it with `async` delegates causes fire-and-forget execution without awaiting tasks properly.

## Code Examples
```csharp
// GOOD: Controlled Parallel Async Processing with Parallel.ForEachAsync
public async Task ProcessUrlsConcurrentlyAsync(IEnumerable<string> urls, CancellationToken ct)
{
    var options = new ParallelOptions
    {
        MaxDegreeOfParallelism = 10, // Limit to 10 concurrent HTTP calls
        CancellationToken = ct
    };

    await Parallel.ForEachAsync(urls, options, async (url, token) =>
    {
        using var client = new HttpClient();
        var content = await client.GetStringAsync(url, token);
        Console.WriteLine($"Processed {url}: {content.Length} bytes");
    });
}
```
- **What it demonstrates**: Bounded parallel async execution using `Parallel.ForEachAsync`.

## Reference Tables
| Primitive | Work Type | Control Feature | Best Used For |
|---|---|---|---|
| `Parallel.ForEach` | CPU-Bound Sync | `MaxDegreeOfParallelism` | In-memory math, data transformations |
| `Parallel.ForEachAsync` | I/O-Bound Async | `MaxDegreeOfParallelism` + `CancellationToken` | Batch HTTP requests, DB updates |
| `Channel<T>` | Producer-Consumer | Bounded Capacity (Backpressure) | Background worker queues, ingestion pipelines |

## Worked Example
Processing 50,000 customer invoice PDFs:
- Unbounded `Task.WhenAll`: 50,000 tasks allocated -> OutOfMemoryException / TCP port exhaustion.
- `Parallel.ForEachAsync` (MaxDegreeOfParallelism = 16): Exactly 16 concurrent HTTP/Disk operations -> Stable memory, optimal throughput, finishes cleanly.

## Key Takeaways
1. Always throttle concurrent background I/O operations using `Parallel.ForEachAsync`.
2. Use `System.Threading.Channels` for producer-consumer background queues.
3. Never use `Parallel.ForEach` for `async` lambda functions; use `Parallel.ForEachAsync`.

## Connects To
- **Ch 9**: Adding cancellation support to background pipelines.
- **Ch 14**: Generating streams asynchronously with `IAsyncEnumerable`.
