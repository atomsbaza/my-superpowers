# Chapter 9: Canceling background tasks

## Core Idea
Cooperative cancellation in .NET relies on `CancellationTokenSource` and `CancellationToken`. Tasks do not forcibly terminate; instead, they periodically inspect tokens and exit gracefully, cleaning up resources.

## Frameworks Introduced
- **The Cooperative Cancellation Protocol**:
  - When to use: Gracefully stopping background work, handling HTTP request aborts, or enforcing timeouts.
  - How: The caller holds `CancellationTokenSource` and passes `cts.Token` to async methods. The worker passes `token` down the call stack or calls `token.ThrowIfCancellationRequested()`.

## Key Concepts
- **CancellationTokenSource (CTS)**: Signals cancellation requests (via `.Cancel()` or `.CancelAfter(timeout)`).
- **CancellationToken**: Read-only struct passed into asynchronous methods to observe cancellation state.
- **OperationCanceledException**: Exception thrown when work is cancelled before completion.
- **Linked Token Source**: Combining multiple tokens (e.g. user cancellation + timeout cancellation) using `CancellationTokenSource.CreateLinkedTokenSource`.

## Mental Models
- Think of a **CancellationToken** as a flare gun signal: the caller shoots the flare (`Cancel()`), and workers periodically look up at the sky (`IsCancellationRequested`) to see if they should pack up and head home.

## Anti-patterns
- **Thread.Abort() (Deprecated)**: Forcibly killing threads leaves locks held, files corrupted, and process state invalid. Always use cooperative cancellation.
- **Swallowing OperationCanceledException**: Catching `Exception` and hiding cancellation prevents callers from knowing the task was aborted.

## Code Examples
```csharp
// Graceful Cooperative Cancellation & Timeout
public async Task FetchDataWithTimeoutAsync(string url)
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5)); // 5s timeout

    try
    {
        using var client = new HttpClient();
        var response = await client.GetStringAsync(url, cts.Token);
        Console.WriteLine(response);
    }
    catch (OperationCanceledException)
    {
        Console.WriteLine("Operation timed out or was canceled by caller.");
    }
}

// Manual Loop Inspection
public void ProcessItems(List<string> items, CancellationToken token)
{
    foreach (var item in items)
    {
        token.ThrowIfCancellationRequested(); // Throws OperationCanceledException if canceled
        DoHeavyWork(item);
    }
}
```
- **What it demonstrates**: Automated timeouts via `CancellationTokenSource` and loop checking with `ThrowIfCancellationRequested()`.

## Reference Tables
| Method / Property | Function | Notes |
|---|---|---|
| `cts.Cancel()` | Triggers cancellation signal | Notifies all tokens created by this CTS |
| `cts.CancelAfter(time)` | Timed automatic cancellation | Perfect for SLA and HTTP timeouts |
| `token.ThrowIfCancellationRequested()` | Throws if token is canceled | Standard mechanism inside sync/async loops |
| `CreateLinkedTokenSource` | Merges N tokens into 1 | Cancels if ANY source token triggers |

## Worked Example
A user clicks "Cancel Export" in a desktop app:
1. UI event handler calls `_exportCts.Cancel()`.
2. The background database query receives the signal via `CancellationToken` and aborts network read.
3. `OperationCanceledException` propagates up.
4. The background task cleans up temp files in a `finally` block.
5. UI displays "Export Canceled" status without process corruption.

## Key Takeaways
1. Always pass `CancellationToken` as the last parameter in async methods.
2. Respect cancellation tokens inside long-running loops using `token.ThrowIfCancellationRequested()`.
3. Clean up resources in `finally` blocks during cancellation.

## Connects To
- **Ch 8**: Canceling background sequence processing.
- **Ch 14**: Canceling `IAsyncEnumerable` streams.
