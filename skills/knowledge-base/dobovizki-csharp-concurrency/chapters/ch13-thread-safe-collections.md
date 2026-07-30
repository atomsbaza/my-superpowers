# Chapter 13: Thread-safe collections

## Core Idea
Standard collections (`List<T>`, `Dictionary<TKey,TValue>`) are not thread-safe. .NET provides Concurrent Collections (`System.Collections.Concurrent`), Immutable Collections (`System.Collections.Immutable`), and Frozen Collections (`System.Collections.Frozen`) for safe concurrent access.

## Frameworks Introduced
- **The Collection Selection Matrix**:
  - Read-write concurrent access from multiple threads -> `ConcurrentDictionary`, `ConcurrentQueue`, `ConcurrentStack`.
  - Producer-consumer queue -> `BlockingCollection<T>` or `Channel<T>`.
  - Functional / Snapshot / Thread-safe sharing -> `ImmutableDictionary`, `ImmutableList`.
  - High-performance read-only lookup initialized at startup (.NET 8+) -> `FrozenDictionary`, `FrozenSet`.

## Key Concepts
- **ConcurrentDictionary<TKey, TValue>**: Lock-free fine-grained lock bucket dictionary (`GetOrAdd`, `AddOrUpdate`).
- **BlockingCollection<T>**: Thread-safe wrapper around concurrent queues supporting blocking consumption (`Take()`) and bounds.
- **Immutable Collections**: Unmodifiable data structures where mutations return a new reference, sharing underlying tree structures.
- **Frozen Collections (.NET 8+)**: Highly optimized read-only lookup structures created once at startup with zero lock overhead.

## Mental Models
- Think of **Immutable Collections** as git commits: you never alter history; modifying an item creates a new commit (version) pointing to shared history nodes.

## Anti-patterns
- **Using `lock` around regular `Dictionary` for reads**: Under heavy read workloads, lock contention degrades performance compared to `ConcurrentDictionary` or `FrozenDictionary`.
- **`ConcurrentDictionary.GetOrAdd` Factory Side Effects**: The value factory lambda in `GetOrAdd` may be executed multiple times concurrently if threads race! Keep factories idempotent.

## Code Examples
```csharp
// ConcurrentDictionary GetOrAdd pattern
public class ThreadSafeCache
{
    private readonly ConcurrentDictionary<string, string> _cache = new();

    public string GetOrCreate(string key)
    {
        // Safe atomic lookup and creation
        return _cache.GetOrAdd(key, k => FetchFromDatabase(k));
    }
}

// FrozenCollection in .NET 8 for fast read-only lookup
public class RoutingTable
{
    private readonly FrozenDictionary<string, RouteInfo> _routes;

    public RoutingTable(Dictionary<string, RouteInfo> initialRoutes)
    {
        // One-time optimization build step at startup
        _routes = initialRoutes.ToFrozenDictionary();
    }

    public RouteInfo GetRoute(string path) => _routes.GetValueOrDefault(path);
}
```
- **What it demonstrates**: Atomic cache access with `ConcurrentDictionary` and zero-lock fast lookup with `FrozenDictionary`.

## Reference Tables
| Collection Category | Mutability | Thread-Safety | Key Advantage |
|---|---|---|---|
| `Concurrent*` | Mutable | Thread-Safe (Lock-free/Fine lock) | High concurrent read/write |
| `Immutable*` | Immutable | Thread-Safe (No locks needed) | Snapshots, functional programming |
| `Frozen*` (.NET 8+) | Read-Only | Thread-Safe (Zero lock) | Fastest read lookup speed |

## Worked Example
A high-throughput web service with 1,000 requests/sec reading config flags:
- Standard `Dictionary` with `lock`: Thread contention causes bottleneck.
- `ConcurrentDictionary`: Lock-free reads, low contention.
- `FrozenDictionary` (.NET 8+): 2x-3x faster than `ConcurrentDictionary` for pure read workloads due to specialized hash table layout.

## Key Takeaways
1. Use `ConcurrentDictionary` for active read/write concurrent maps.
2. Ensure factories passed to `GetOrAdd` are idempotent.
3. Use `.ToFrozenDictionary()` (.NET 8+) for startup config and read-only lookups.

## Connects To
- **Ch 7**: Synchronization primitives.
- **Ch 8**: Producer-consumer patterns.
