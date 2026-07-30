# Concurrency Patterns & Techniques — C# Concurrency

## Bounded Producer-Consumer Pipeline Pattern
**When to use**: Ingesting and processing continuous streams of data (e.g. log ingestion, message processing) without exceeding memory boundaries.
**How**:
1. Create a `Channel<T>` with `Channel.CreateBounded<T>(capacity)`.
2. Launch background producer tasks writing to `channel.Writer.WriteAsync(item)`.
3. Launch worker consumer tasks reading with `await foreach (var item in channel.Reader.ReadAllAsync())`.
**Trade-offs**: Prevents OutOfMemoryException by pausing producers when capacity is full; introduces backpressure latency.

## Controlled Parallel Async Processing Pattern
**When to use**: Processing thousands of items requiring asynchronous I/O calls (e.g. HTTP web scraping, DB batching).
**How**: Use `Parallel.ForEachAsync(items, new ParallelOptions { MaxDegreeOfParallelism = N }, async (item, token) => ... )`.
**Trade-offs**: Prevents socket/memory exhaustion; requires tuning `MaxDegreeOfParallelism` to server constraints.

## Async Lock Pattern
**When to use**: Protecting a critical section that contains `await` statements (which standard C# `lock` forbids).
**How**:
```csharp
private readonly SemaphoreSlim _mutex = new SemaphoreSlim(1, 1);
await _mutex.WaitAsync();
try { await PerformAsyncWork(); }
finally { _mutex.Release(); }
```
**Trade-offs**: Allows async execution inside critical section; requires strict `try/finally` handling to prevent leaked locks.

## Event-to-Task Conversion Pattern
**When to use**: Wrapping legacy event-driven APIs or callbacks into modern `async/await` syntax.
**How**: Use `TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously)`. Subscribe to the event, trigger `tcs.TrySetResult(args)` or `tcs.TrySetException()`, and unsubscribe in the handler.
**Trade-offs**: Clean call-site code; requires careful event unsubscription to avoid memory leaks.

## Asynchronous Streaming Pattern (IAsyncEnumerable)
**When to use**: Streaming large datasets from DB or external APIs directly to clients without buffering full lists in memory.
**How**: Implement `async IAsyncEnumerable<T>` returning items via `yield return`. Attribute `CancellationToken` with `[EnumeratorCancellation]`. Consume via `await foreach`.
**Trade-offs**: Near-zero memory consumption; requires active connection while streaming.
