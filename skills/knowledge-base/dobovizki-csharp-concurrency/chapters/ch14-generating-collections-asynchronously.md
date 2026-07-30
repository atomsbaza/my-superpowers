# Chapter 14: Generating collections asynchronously / await foreach and IAsyncEnumerable

## Core Idea
`IAsyncEnumerable<T>` (introduced in C# 8 / .NET Core 3.0) enables asynchronous streaming of data sequences. It combines `async/await` with `yield return`, allowing callers to consume items asynchronously as they arrive using `await foreach`.

## Frameworks Introduced
- **The Asynchronous Streaming Pattern**:
  - When to use: Streaming database query results, reading paginated API results, or processing file lines asynchronously.
  - How: Return `IAsyncEnumerable<T>`, use `yield return` inside the method, and consume via `await foreach (var item in stream)`. Pass `[EnumeratorCancellation] CancellationToken` for stream cancellation.

## Key Concepts
- **IAsyncEnumerable<T>**: Interface representing an asynchronous enumerator (`GetAsyncEnumerator()`).
- **await foreach**: Language keyword for enumerating an `IAsyncEnumerable<T>` asynchronously.
- **[EnumeratorCancellation]**: Attribute applied to `CancellationToken` in `IAsyncEnumerable` methods to bind caller tokens correctly.
- **System.Linq.Async**: NuGet package providing LINQ operators (`Where`, `Select`, `ToListAsync`) for `IAsyncEnumerable<T>`.

## Mental Models
- Think of `IEnumerable<T>` as a **DVD**: The whole movie is ready on disk.
- Think of `IAsyncEnumerable<T>` as **YouTube Live Streaming**: Video frames arrive piece-by-piece over time, and you watch (`await foreach`) each frame as it streams in.

## Anti-patterns
- **Buffering Streams into `List<T>` (`ToListAsync`) unnecessarily**: Loading a 1,000,000 item stream into an in-memory `List<T>` defeats the purpose of streaming and causes high memory spikes.

## Code Examples
```csharp
// Producer: Asynchronous Data Generator with Cancellation Support
public async IAsyncEnumerable<int> FetchPagedDataAsync(
    [EnumeratorCancellation] CancellationToken cancellationToken = default)
{
    for (int page = 1; page <= 5; page++)
    {
        cancellationToken.ThrowIfCancellationRequested();

        // Simulate async DB / API page fetch
        await Task.Delay(100, cancellationToken);

        yield return page * 100; // Stream item to consumer
    }
}

// Consumer: Awaiting stream iteration
public async Task ConsumeStreamAsync()
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(2));

    await foreach (var item in FetchPagedDataAsync().WithCancellation(cts.Token))
    {
        Console.WriteLine($"Received item: {item}");
    }
}
```
- **What it demonstrates**: Generating and consuming an asynchronous stream with `IAsyncEnumerable<T>` and `[EnumeratorCancellation]`.

## Reference Tables
| Interface | Pull Model | Async Support | Best For |
|---|---|---|---|
| `IEnumerable<T>` | Synchronous | ❌ No | In-memory arrays, lists |
| `Task<List<T>>` | Async (Bulk) | ✅ Yes (Whole list at end) | Small responses |
| `IAsyncEnumerable<T>` | Async (Stream) | ✅ Yes (Item-by-item) | DB pagination, IoT sensor streams |

## Worked Example
Exporting 500,000 database rows to a CSV download endpoint:
- **`Task<List<Row>>` Approach**: Loads all 500,000 rows into server RAM first (~250MB), delays response by 5 seconds, then sends payload.
- **`IAsyncEnumerable<Row>` Approach**: Fetches and streams 100 rows at a time, begins writing HTTP response immediately (~50KB RAM used), user receives first bytes in 10ms.

## Key Takeaways
1. Use `IAsyncEnumerable<T>` for streaming large datasets or paginated APIs.
2. Use `yield return` inside `IAsyncEnumerable<T>` methods.
3. Always attribute the cancellation token parameter with `[EnumeratorCancellation]`.
4. Use `WithCancellation(cts.Token)` when calling `await foreach`.

## Connects To
- **Ch 2**: Compiler yield return and state machine mechanics.
- **Ch 8**: Sequence processing and background pipelines.
- **Ch 9**: Cooperative cancellation patterns.
