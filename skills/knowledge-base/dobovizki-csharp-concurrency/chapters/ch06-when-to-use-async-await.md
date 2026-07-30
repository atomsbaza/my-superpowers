# Chapter 6: When to use async/await

## Core Idea
Applying `async/await` in the right scenarios maximizes application responsiveness and server throughput. Knowing when NOT to use `async/await` avoids unnecessary overhead and anti-patterns.

## Frameworks Introduced
- **The Concurrency Decision Tree**:
  - Step 1: Is the operation I/O-bound (network, disk, DB)? -> Use `async/await`.
  - Step 2: Is the operation CPU-bound (math, rendering, parsing) AND in a UI app? -> Use `Task.Run` to keep UI thread responsive.
  - Step 3: Is the operation CPU-bound AND in a high-scale ASP.NET server app? -> Run synchronously on caller thread; avoid `Task.Run`.

## Key Concepts
- **UI Responsiveness**: Preventing main GUI thread freezing in Desktop/Mobile (WPF, WinForms, MAUI) apps.
- **Server Scalability**: Maximizing requests-per-second throughput in ASP.NET Core by freeing thread pool threads during I/O.
- **Overhead Threshold**: `async/await` has state machine allocation overhead. For microsecond in-memory operations, synchronous execution is faster.

## Mental Models
- Think of **Async in UI** as avoiding a frozen mouse cursor; think of **Async in Server** as increasing the number of web users the server can handle per gigabyte of RAM.

## Anti-patterns
- **Async All The Things (Over-application)**: Wrapping fast in-memory methods (e.g. `string.Concat` or simple getters) in `async/await`.
- **`Task.Run` on Web Servers**: Offloading CPU work to `Task.Run` inside an ASP.NET Core controller request does NOT increase server capacity—it uses two thread pool threads for one request!

## Code Examples
```csharp
// BAD: Task.Run on Web Server controller (Anti-pattern!)
[HttpGet("compute")]
public async Task<IActionResult> ComputeOnServer()
{
    // Uses 1 thread to accept request + 1 threadpool thread from Task.Run = 2 threads wasted!
    var result = await Task.Run(() => PerformCpuWork());
    return Ok(result);
}

// GOOD: Direct synchronous execution on server for CPU-bound task
[HttpGet("compute-correct")]
public IActionResult ComputeOnServerCorrect()
{
    // Runs directly on the request thread without threadpool hop overhead
    var result = PerformCpuWork();
    return Ok(result);
}
```
- **What it demonstrates**: Why `Task.Run` inside web servers is an anti-pattern that reduces throughput.

## Reference Tables
| Application Type | Work Type | Recommended Solution |
|---|---|---|
| Web API / ASP.NET | I/O-Bound | `async` / `await` |
| Web API / ASP.NET | CPU-Bound | Synchronous execution on request thread |
| Desktop / UI App | I/O-Bound | `async` / `await` |
| Desktop / UI App | CPU-Bound | `await Task.Run(...)` to free UI thread |

## Worked Example
Benchmark of 10,000 requests to an API endpoint:
- **Approach A (`Task.Run` wrapper)**: 1,200 req/sec, high context switching latency.
- **Approach B (Direct sync compute)**: 4,500 req/sec, minimal context switching, lower CPU usage.

## Key Takeaways
1. Use `async/await` for I/O operations everywhere.
2. Use `Task.Run` for CPU work ONLY in UI applications to unfreeze the interface.
3. Never use `Task.Run` in server-side web APIs to process CPU work.

## Connects To
- **Ch 1**: I/O vs CPU work fundamentals.
- **Ch 11**: UI thread marshalling.
