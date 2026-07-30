# Cheatsheet & Decision Guides — C# Concurrency

## Concurrency Decision Rules
- **If work is I/O-bound (DB, Web, Disk)** → Use `async` / `await` (`Task` / `ValueTask`). NEVER block via `.Result` or `.Wait()`.
- **If work is CPU-bound in a Desktop/Mobile UI app** → Offload with `await Task.Run(() => Compute())` to keep UI responsive.
- **If work is CPU-bound in an ASP.NET Web API** → Run synchronously on request thread. DO NOT use `Task.Run`.
- **If operation completes synchronously >80% of the time** → Return `ValueTask<T>` instead of `Task<T>`.
- **If writing a reusable class library / NuGet** → Append `.ConfigureAwait(false)` to every `await`.
- **If locking around an `await` statement** → Use `SemaphoreSlim(1, 1)` with `await _semaphore.WaitAsync()`. NEVER use standard `lock`.

## Synchronization Matrix
| Requirement | Primitive | Performance | Notes |
|---|---|---|---|
| Single int/bool counter | `Interlocked` | Highest (Nanoseconds) | Hardware atomic instruction |
| In-memory sync critical section | `lock(object)` | Fast (~tens of ns) | Lock on `private final object` |
| Async critical section (`await`) | `SemaphoreSlim(1, 1)` | Medium (Microseconds) | Release in `finally` block |
| Rate-limiting N concurrent tasks | `SemaphoreSlim(N, N)` | Medium | Limits max active execution |
| Lock-free Concurrent Map | `ConcurrentDictionary` | High | Idempotent factories in `GetOrAdd` |
| Read-only lookup at startup | `FrozenDictionary` | Maximum (.NET 8+) | Created via `.ToFrozenDictionary()` |

## Tells & Smells (Code Review Flags)
- 🚩 `async void` → High Risk! Unhandled exceptions crash process. (Allowed only in UI event handlers).
- 🚩 `Task.Result` / `Task.Wait()` → Deadlock risk! Sync-over-async anti-pattern.
- 🚩 `new Thread()` → Memory waste. Replace with `Task.Run()`.
- 🚩 `[ThreadStatic]` across `await` → Bug! Continuations jump threads. Use `AsyncLocal<T>`.
- 🚩 Awaiting `ValueTask` twice → Undefined behavior! Await exactly once.
- 🚩 Missing `ConfigureAwait(false)` in class libraries → Potential UI deadlock.
