# Chapter 10: Await your own events

## Core Idea
Standard .NET events (`event EventHandler`) can be converted into awaitable `Task` objects using `TaskCompletionSource<T>`. Understanding custom awaiter patterns allows awaiting non-task objects or building custom asynchronous primitives.

## Frameworks Introduced
- **The Event-to-Task Bridge Pattern**:
  - When to use: Turning event-driven or callback-based legacy code into `async/await` compatible code.
  - How: Instantiating `TaskCompletionSource<T>`, subscribing to the event to trigger `tcs.SetResult()`, and awaiting `tcs.Task`.

## Key Concepts
- **TaskCompletionSource<T>**: Producer side of a `Task<T>` that allows manually setting results, exceptions, or cancellation.
- **Custom Awaiter Pattern**: Any type in C# can be awaited if it implements a `GetAwaiter()` method returning an object that implements `INotifyCompletion` with `IsCompleted`, `GetResult()`, and `OnCompleted()`.
- **TaskCreationOptions.RunContinuationsAsynchronously**: Prevents continuation code from executing synchronously on the thread that calls `tcs.SetResult()`, preventing stack overflows and deadlocks.

## Mental Models
- Think of `TaskCompletionSource` as a **Buzzer at a Restaurant**: You hold the buzzer (the `Task`), and when your table is ready, the host presses the button (`SetResult()`), making your buzzer light up (`await` completes).

## Anti-patterns
- **Omitting `RunContinuationsAsynchronously`**: Calling `tcs.SetResult()` without `RunContinuationsAsynchronously` runs the awaited continuation synchronously on the calling thread, potentially leading to unintended lock escalation or stack overflows.

## Code Examples
```csharp
// Converting a legacy single-fire Event into an Awaitable Task
public static class EventExtensions
{
    public static Task<TEventArgs> WaitForEventAsync<TEventArgs>(
        Action<EventHandler<TEventArgs>> subscribe,
        Action<EventHandler<TEventArgs>> unsubscribe,
        CancellationToken ct = default)
    {
        var tcs = new TaskCompletionSource<TEventArgs>(TaskCreationOptions.RunContinuationsAsynchronously);
        EventHandler<TEventArgs> handler = null;

        handler = (sender, args) =>
        {
            unsubscribe(handler); // Clean up event subscription!
            tcs.TrySetResult(args);
        };

        subscribe(handler);

        if (ct.CanBeCanceled)
        {
            ct.Register(() =>
            {
                unsubscribe(handler);
                tcs.TrySetCanceled(ct);
            });
        }

        return tcs.Task;
    }
}
```
- **What it demonstrates**: Safe conversion of .NET events into awaitable tasks with automatic event unsubscription and cancellation support.

## Reference Tables
| Custom Awaitable Component | Required Signature | Role |
|---|---|---|
| Method on Target Type | `GetAwaiter()` | Enables the `await` keyword syntax |
| Property on Awaiter | `bool IsCompleted { get; }` | Checks if result is already available |
| Method on Awaiter | `void OnCompleted(Action continuation)` | Registers callback for continuation |
| Method on Awaiter | `T GetResult()` | Returns the result or throws captured exception |

## Worked Example
Awaiting a socket connection event:
- Call `WaitForEventAsync(h => socket.Connected += h, h => socket.Connected -= h)`.
- The UI or caller uses `await socketConnectedTask;` cleanly without messy event handler boilerplate.

## Key Takeaways
1. Always use `TaskCreationOptions.RunContinuationsAsynchronously` when instantiating `TaskCompletionSource`.
2. Always unsubscribe from events inside the continuation handler to prevent memory leaks.
3. C# `await` syntax is duck-typed based on the `GetAwaiter()` pattern.

## Connects To
- **Ch 3**: Foundations of `Task` and `TaskCompletionSource`.
- **Ch 11**: Thread scheduling of continuations.
