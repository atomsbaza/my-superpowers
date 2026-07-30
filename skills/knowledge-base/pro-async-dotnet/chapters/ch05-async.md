# Chapter 5: Async and Await (C# 5.0)

## Core Idea
The `async` and `await` keywords are compiler magic that transforms synchronous-looking code into a state machine of task continuations, eliminating the callback hell of raw `ContinueWith`.

## Key Concepts
- **async**: A modifier that enables the use of the `await` keyword inside a method and dictates that the method must return `void`, `Task`, or `Task<T>`.
- **await**: An operator that suspends evaluation of the enclosing async method until the awaited asynchronous operation completes. It yields control back to the caller.
- **SynchronizationContext**: An abstraction representing the environment the code is running in (e.g., UI thread, ASP.NET request context). `await` captures this by default to resume on the correct thread.

## Mental Models
- Think of `await` as an **invisible `ContinueWith`**. Everything after the `await` keyword is packed up into a delegate and scheduled to run when the awaited Task completes.

## Anti-patterns
- **async void**: Using `async void` anywhere except for event handlers. It breaks the exception handling pipeline (crashing the process) and cannot be awaited.
- **Capturing Context Unnecessarily**: Not using `ConfigureAwait(false)` in library code, leading to deadlocks and unnecessary thread hops.

## Code Examples
```csharp
public async Task<string> FetchDataAsync(string url)
{
    using (var client = new HttpClient())
    {
        // Yields execution here; thread goes back to ThreadPool
        string result = await client.GetStringAsync(url).ConfigureAwait(false);
        return result;
    }
}
```
- **What it demonstrates**: A standard, non-blocking asynchronous I/O call using best practices (`ConfigureAwait(false)`).

## Key Takeaways
1. Return `Task` instead of `void` for async methods.
2. Use `ConfigureAwait(false)` in all library/backend code that doesn't need to resume on a specific UI thread.\n