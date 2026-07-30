# Chapter 12: Exceptions and async/await

## Core Idea
Exceptions in asynchronous methods are caught by the state machine and stored in the returned `Task`. Awaiting the task unwraps and rethrows the first exception, preserving the original call stack. Handling `AggregateException` is required when working with task combinators.

## Frameworks Introduced
- **The Async Exception Propagation Rules**:
  - When to use: Handling exceptions in async code.
  - How:
    - Awaiting a `Task`: Unwraps `AggregateException` and throws the first inner exception directly.
    - `Task.WhenAll`: Captures all exceptions into `Task.Exception` (`AggregateException`). Awaiting it throws the first exception; inspect `task.Exception.InnerExceptions` to examine all failures.

## Key Concepts
- **Exception Unwrapping**: `await` unwraps the `AggregateException` wrapper for clean `try/catch` syntax.
- **ExceptionDispatchInfo**: Runtime mechanism used by `await` to rethrow exceptions while preserving the full original stack trace.
- **UnobservedTaskException**: Event raised when a faulted `Task` is garbage collected without being awaited or having its `.Exception` property read.

## Mental Models
- Think of `AggregateException` as a **Box of Broken Lightbulbs**: `await` opens the box and hands you the first broken bulb; inspecting `.Exception.InnerExceptions` checks every broken bulb in the box.

## Anti-patterns
- **`async void` Exception Disasters**: Exceptions in `async void` methods cannot be caught with `try/catch` around the invocation site and will crash the application.
- **Using `ex.StackTrace` vs `ExceptionDispatchInfo`**: Manually rethrowing `throw ex;` destroys the stack trace. Always use `throw;` or `ExceptionDispatchInfo.Capture(ex).Throw()`.

## Code Examples
```csharp
// Proper Exception Handling with Task.WhenAll
public async Task ProcessMultipleRequestsAsync(List<string> urls)
{
    var tasks = urls.Select(FetchUrlAsync).ToList();
    Task allTasks = Task.WhenAll(tasks);

    try
    {
        await allTasks; // Throws first exception
    }
    catch (Exception ex)
    {
        Console.WriteLine($"First exception: {ex.Message}");

        // Inspect ALL exceptions from WhenAll:
        if (allTasks.Exception != null)
        {
            foreach (var innerEx in allTasks.Exception.InnerExceptions)
            {
                Console.WriteLine($"Logged Failure: {innerEx.Message}");
            }
        }
    }
}
```
- **What it demonstrates**: Inspecting all inner exceptions from a faulted `Task.WhenAll`.

## Reference Tables
| Invocation Pattern | Exception Catching Behavior | Stack Trace Preservation |
|---|---|---|
| `await task` | Throws first inner exception | ✅ Preserved via ExceptionDispatchInfo |
| `task.Result` / `.Wait()` | Throws `AggregateException` | ⚠️ Wrapped in AggregateException |
| `async void` method | Uncatchable via caller `try/catch` | ❌ Process crash |

## Worked Example
3 parallel tasks run via `Task.WhenAll`:
- Task 1 throws `ArgumentException`.
- Task 2 throws `InvalidOperationException`.
- Task 3 succeeds.
- `await Task.WhenAll(...)` throws `ArgumentException` directly to `catch (Exception ex)`.
- Accessing `allTasks.Exception.InnerExceptions` contains both `ArgumentException` and `InvalidOperationException`.

## Key Takeaways
1. Always `await` tasks to ensure clean exception unwrapping and stack trace preservation.
2. Inspect `Task.Exception.InnerExceptions` when handling failures from `Task.WhenAll`.
3. Never use `async void` except in GUI event handlers.

## Connects To
- **Ch 3**: `Task.WhenAll` combinators.
- **Ch 9**: `OperationCanceledException` handling.
