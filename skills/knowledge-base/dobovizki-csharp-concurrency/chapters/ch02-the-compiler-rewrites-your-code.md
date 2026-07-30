# Chapter 2: The compiler rewrites your code

## Core Idea
The C# compiler transforms methods marked with `async` into generated value-type state machines that implement `IAsyncStateMachine`. Understanding this transformation demystifies how `await` pauses execution and resumes later without holding a thread.

## Frameworks Introduced
- **The State Machine Transformation Framework**:
  - When to use: Analyzing memory allocation, performance, and stack frame behavior of async methods.
  - How: The compiler breaks your method at every `await` boundary into distinct state numbers (-1 = running/unstarted, 0..N = paused at await point N, -2 = completed). Local variables become fields on the compiler-generated struct.

## Key Concepts
- **IAsyncStateMachine**: The compiler interface containing `MoveNext()` and `SetStateMachine()`.
- **AsyncTaskMethodBuilder**: The helper struct that manages the `Task` lifecycle, state machine execution, and exception capturing.
- **Yield Return Parallels**: Like `IEnumerable` generator methods using `yield return`, `async` methods yield control back to the caller and save state for continuation.
- **Hoisted Variables**: Local variables inside an async method promoted to struct fields so their values survive across suspension points.

## Mental Models
- Think of an `async` method as a **Turn-based Board Game**: `MoveNext()` is invoked every time it is your turn (an awaited task completes), moving your piece to the next square (state number) until reaching the Finish box.

## Anti-patterns
- **Allocating excessive local variables across await points**: Every local variable active across an `await` gets hoisted to a field on the state machine struct, increasing its size and memory footprint.

## Code Examples
```csharp
// Original Developer Code:
public async Task<int> FetchLengthAsync(string url)
{
    var text = await _client.GetStringAsync(url);
    return text.Length;
}

// Compiler Generated Equivalent (Simplified Concept):
[CompilerGenerated]
private struct FetchLengthAsync_StateMachine : IAsyncStateMachine
{
    public int State;
    public AsyncTaskMethodBuilder<int> Builder;
    public string url;
    private string _text;
    private TaskAwaiter<string> _awaiter;

    public void MoveNext()
    {
        int num = State;
        try
        {
            if (num != 0)
            {
                _awaiter = _client.GetStringAsync(url).GetAwaiter();
                if (!_awaiter.IsCompleted)
                {
                    State = 0;
                    Builder.AwaitUnsafeOnCompleted(ref _awaiter, ref this);
                    return; // Yield control!
                }
            }
            _text = _awaiter.GetResult();
            Builder.SetResult(_text.Length);
        }
        catch (Exception ex)
        {
            Builder.SetException(ex);
        }
    }
}
```
- **What it demonstrates**: How `await` returns early if the underlying task is not completed, registering a continuation callback via `AwaitUnsafeOnCompleted`.

## Reference Tables
| Concept | Normal Method | Async Method |
|---|---|---|
| **Local Variables** | Reside on execution Thread Stack | Hoisted into State Machine Struct fields |
| **Return Mechanism** | Single `return` instruction | `Builder.SetResult()` / `Builder.SetException()` |
| **Execution Flow** | Continuous stack frame execution | Fragmented execution across `MoveNext()` calls |
| **Allocation Cost** | Zero heap allocation (stack only) | Task object allocation + state machine box (if boxed) |

## Worked Example
When `await GetStringAsync(url)` is executed:
1. `GetStringAsync` returns an uncompleted `Task<string>`.
2. The state machine sets `State = 0`.
3. `Builder.AwaitUnsafeOnCompleted` attaches `MoveNext` as a continuation to the `Task`.
4. `FetchLengthAsync` returns an incomplete `Task<int>` to its caller immediately.
5. When HTTP network data arrives 50ms later, the I/O completion thread invokes the continuation callback, calling `MoveNext()`, restoring state 0, fetching the result, and completing the caller's `Task<int>`.

## Key Takeaways
1. `async` is a compiler feature, not an OS or runtime kernel feature.
2. `await` does not block; it registers a continuation and returns.
3. Exceptions inside async methods are caught by the state machine and stored in the returned `Task`.

## Connects To
- **Ch 1**: Explains why async I/O releases threads.
- **Ch 3**: Explores `async`, `await`, `Task`, and `ValueTask` in detail.
