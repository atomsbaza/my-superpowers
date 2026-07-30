# Chapter 3: The async and await keywords

## Core Idea
The `async` and `await` keywords provide idiomatic asynchronous control flow in C#. Mastering task combinators (`Task.WhenAll`, `Task.WhenAny`), `ValueTask`, and `ConfigureAwait` allows writing performant, non-blocking asynchronous C# code.

## Frameworks Introduced
- **The Task Combinator Selection Framework**:
  - When to use: Coordinating multiple asynchronous operations.
  - How: Use `Task.WhenAll` when all tasks must complete concurrently. Use `Task.WhenAny` for speculative execution or timeouts.
- **The ValueTask Allocation Hierarchy**:
  - When to use: High-throughput APIs where operations frequently complete synchronously (e.g. from memory cache).
  - How: Return `ValueTask<T>` instead of `Task<T>` to avoid allocating a `Task` object on the heap when the result is available immediately.

## Key Concepts
- **Task / Task<T>**: Reference type representing a promise of future work or completion.
- **ValueTask / ValueTask<T>**: Discriminated union struct (`TResult` vs `Task<T>`) designed to eliminate heap allocation when completing synchronously.
- **TaskCompletionSource<T>**: An explicit producer interface for creating and completing manual `Task<T>` objects (bridging callback/event APIs to async).
- **ConfigureAwait(false)**: Directs `await` not to capture the current SynchronizationContext, allowing continuation on any thread pool thread.

## Mental Models
- Think of a **Task** as a claim check ticket at a coat check: you hold the ticket while waiting for your coat.
- Think of **TaskCompletionSource** as the coat check clerk who hands you the ticket and later fulfills it when your coat is found.

## Anti-patterns
- **Async Void**: Methods declared `async void` (except UI event handlers). Exceptions cannot be caught by callers and will crash the process.
- **Awaiting ValueTask Multiple Times**: `ValueTask` can only be awaited once. Awaiting it twice causes undefined behavior or runtime exceptions.
- **Ignoring Task Errors**: Fire-and-forget without handling exceptions leads to unobserved task exceptions.

## Code Examples
```csharp
// Task.WhenAll: Concurrent execution of independent async operations
public async Task<DashboardData> LoadDashboardAsync(int userId)
{
    Task<UserProfile> profileTask = _userRepo.GetProfileAsync(userId);
    Task<List<Order>> ordersTask = _orderRepo.GetOrdersAsync(userId);
    Task<UserStats> statsTask = _statsRepo.GetStatsAsync(userId);

    // Run concurrently, await all
    await Task.WhenAll(profileTask, ordersTask, statsTask);

    return new DashboardData(
        Profile: await profileTask,
        Orders: await ordersTask,
        Stats: await statsTask
    );
}

// Bridging Legacy Callback Events via TaskCompletionSource
public Task<string> DownloadStringWithEventsAsync(string url)
{
    var tcs = new TaskCompletionSource<string>();
    var client = new WebClient();
    client.DownloadStringCompleted += (s, e) =>
    {
        if (e.Error != null) tcs.SetException(e.Error);
        else if (e.Cancelled) tcs.SetCanceled();
        else tcs.SetResult(e.Result);
    };
    client.DownloadStringAsync(new Uri(url));
    return tcs.Task;
}
```
- **What it demonstrates**: Concurrent execution with `Task.WhenAll` and converting event-based legacy APIs into modern `Task`-returning methods.

## Reference Tables
| Method / Keyword | Use Case | Behavioral Notes |
|---|---|---|
| `Task.WhenAll` | Fan-out / Parallel Async | Awaits all tasks; aggregates all exceptions into `AggregateException`. |
| `Task.WhenAny` | Timeout / First Responder | Awaits the first task to finish; returns the completed task. |
| `ValueTask<T>` | Micro-optimization | Use when >80% of calls complete synchronously. Await ONCE only. |
| `async void` | Event Handlers ONLY | Never use in normal methods. Unhandled exceptions crash process. |

## Worked Example
Fetching cached user profile vs remote DB fetch:
- If `GetUserAsync(id)` checks a memory cache and finds the item 95% of the time:
  - With `Task<User>`: 95% of calls allocate a new `Task<User>` heap object just to wrap an already-known `User`.
  - With `ValueTask<User>`: 95% of calls return a value-type wrapper with zero heap allocation. 5% fallback to `Task<User>` for DB network I/O.

## Key Takeaways
1. Always return `Task` or `Task<T>` instead of `async void`.
2. Use `Task.WhenAll` to execute independent async requests concurrently instead of awaiting them sequentially.
3. Bridge legacy callback/event APIs to async using `TaskCompletionSource<T>`.
4. Use `ConfigureAwait(false)` in non-UI class libraries.

## Connects To
- **Ch 2**: Explains state machine generation for `await`.
- **Ch 11**: Explains `ConfigureAwait(false)` and `SynchronizationContext`.
