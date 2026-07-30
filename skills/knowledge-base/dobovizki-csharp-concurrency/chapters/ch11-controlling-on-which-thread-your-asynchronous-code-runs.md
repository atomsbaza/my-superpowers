# Chapter 11: Controlling on which thread your asynchronous code runs

## Core Idea
The `SynchronizationContext` controls thread affinity after an `await`. In UI applications (WPF, WinForms, MAUI), continuations default to the main UI thread. In non-UI libraries, using `ConfigureAwait(false)` avoids UI thread context switching overhead and prevents deadlocks.

## Frameworks Introduced
- **The SynchronizationContext Capture Protocol**:
  - When to use: Deciding whether to capture thread context during `await`.
  - How:
    - In UI Code: Use default `await` (which captures `SynchronizationContext` to update UI elements safely).
    - In Class Libraries / Business Logic: Use `await task.ConfigureAwait(false)` to bypass context capturing and run continuations on ThreadPool threads.

## Key Concepts
- **SynchronizationContext**: An abstraction representing a specific execution context (e.g. WPF Dispatcher thread, WinForms UI thread).
- **ConfigureAwait(false)**: Configures the awaiter to NOT marshal the continuation back to the captured `SynchronizationContext`.
- **ASP.NET Core Note**: ASP.NET Core (.NET Core 1.0+) has NO `SynchronizationContext`. `ConfigureAwait(false)` is optional in ASP.NET Core controllers, but remains critical for reusable class libraries.

## Mental Models
- Think of `SynchronizationContext` as a **Home Address**: When an async call finishes, default `await` takes a taxi back to your home address (UI thread). `ConfigureAwait(false)` tells the taxi to drop you off at the nearest coffee shop (ThreadPool worker thread).

## Anti-patterns
- **Sync-over-Async Deadlock in Legacy ASP.NET / UI**: Calling `.Result` or `.Wait()` on an async method that captures `SynchronizationContext` blocks the UI/request thread while the continuation waits for the thread to become free, causing a classic deadlock.

## Code Examples
```csharp
// CLASS LIBRARY CODE: Always use ConfigureAwait(false)
public async Task<byte[]> DownloadFileAsync(string url)
{
    using var client = new HttpClient();
    // Bypasses SynchronizationContext marshalling
    var bytes = await client.GetByteArrayAsync(url).ConfigureAwait(false);
    return ProcessBytes(bytes);
}

// UI CODE (WPF / WinForms / MAUI): Do NOT use ConfigureAwait(false) when updating UI
private async void OnDownloadButtonClick(object sender, EventArgs e)
{
    StatusText.Text = "Downloading...";
    // Default await captures UI SynchronizationContext!
    var data = await DownloadFileAsync("https://example.com/file.bin");
    // Resumes safely on UI thread to update controls:
    StatusText.Text = $"Downloaded {data.Length} bytes";
}
```
- **What it demonstrates**: Using `ConfigureAwait(false)` in class libraries while retaining default `await` in UI components.

## Reference Tables
| Application Context | Default Await Behavior | Needs `ConfigureAwait(false)`? |
|---|---|---|
| WPF / WinForms / MAUI | Captures UI Thread | ❌ No in UI code; ✅ Yes in Class Libraries |
| ASP.NET Core (.NET 6+) | No SyncContext (ThreadPool) | Optional, but recommended for reusable NuGets |
| Console Application | ThreadPool | Optional |

## Worked Example
Why `.Result` causes deadlocks in UI apps:
1. User clicks button on UI Thread #1.
2. Code calls `GetDataAsync().Result`. Thread #1 is now blocked waiting for `Task`.
3. `GetDataAsync` reaches `await http.GetAsync()`.
4. `GetAsync` finishes on I/O thread. It attempts to post the continuation back to UI Thread #1.
5. Thread #1 is blocked in Step 2 waiting for `Task`. Continuation cannot run -> Deadlock!

## Key Takeaways
1. Always use `ConfigureAwait(false)` in reusable class libraries and NuGet packages.
2. Never use `ConfigureAwait(false)` when subsequent code must update UI controls.
3. Never use `.Result` or `.Wait()` on tasks; use `await` end-to-end.

## Connects To
- **Ch 3**: `async` and `await` fundamentals.
- **Ch 12**: Exception handling across context boundaries.
