# Chapter 4: Error Handling and Cancellation

## Core Idea
In asynchronous programming, exceptions are caught by the framework, stored in the `Task` object, and rethrown when the task is awaited or queried. Cancellation is cooperative, relying on `CancellationToken`.

## Key Concepts
- **AggregateException**: A wrapper exception used by TPL to hold one or more exceptions thrown by tasks (especially when awaiting multiple tasks like `Task.WhenAll`).
- **CancellationTokenSource (CTS)**: The object that initiates cancellation.
- **CancellationToken**: The struct passed to asynchronous methods that they periodically check to see if cancellation was requested.

## Code Examples
```csharp
public void DoWork(CancellationToken token)
{
    for (int i = 0; i < 100; i++)
    {
        // Throw OperationCanceledException if cancellation requested
        token.ThrowIfCancellationRequested(); 
        ComputeStep(i);
    }
}
```
- **What it demonstrates**: Cooperative cancellation. The worker method explicitly checks if it should stop.

## Key Takeaways
1. Always pass `CancellationToken` all the way down the call stack.
2. Use `.Flatten()` on `AggregateException` to easily process deeply nested exception trees.\n