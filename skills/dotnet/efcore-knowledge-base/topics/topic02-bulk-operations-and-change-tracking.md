# Topic 2: Bulk Operations, Change Tracking, and Dapper vs EF Core

## The default EF Core cost model

Standard EF Core writes follow load → track → mutate → `SaveChangesAsync()`. Every tracked entity costs change-tracker snapshot memory and comparison overhead at `SaveChanges` time — fine for a handful of entities, expensive at bulk scale (an $O(N)$ loop of loads plus $O(N)$ update statements, or worse).

## ExecuteUpdate / ExecuteDelete (EF Core 7+)

`ExecuteUpdateAsync` / `ExecuteDeleteAsync` translate a LINQ expression directly into a single SQL `UPDATE`/`DELETE` statement, executed against the database with **no entity materialization and no change tracker involvement**.

- Turns an $O(N)$ load-modify-save loop into a single round trip.
- **Critical caveat**: because these bypass the change tracker, any entities of the affected rows already tracked in the current `DbContext` become stale — the tracker has no idea the database changed underneath it. Don't mix tracked `SaveChanges()` work and untracked `Execute*` calls against the same rows within one `DbContext` lifetime; if you must, discard/refresh the context afterward.
- Good fit for: bulk cleanup jobs, expiring stale rows, mass status updates — anything where you don't need the updated entities back as tracked objects.

## Dapper vs EF Core (2025 benchmark data points from research)

| Operation | Dapper | EF Core |
|---|---|---|
| Insert throughput | ~65x faster | baseline (tracking overhead dominates) |
| Single record update | 169.2 µs | 209.1 µs |
| Memory, 1 insert | 18.23 KB | 39.09 KB |
| Memory, 30 inserts | 427.73 KB | 753.61 KB |

Treat the 65x figure as an extreme-case number (likely bulk insert with tracking enabled and no batching) rather than a universal multiplier — but the direction (Dapper wins on raw insert/update throughput and allocates less) is consistent across sources.

**Community framing** (paraphrased from r/dotnet): if your performance fix is "let's precompile the LINQ query," you're solving the wrong layer of the problem — the real fix is usually architectural (batching, split queries, or dropping to Dapper/raw SQL for the hot path), not micro-tuning the ORM.

## Decision rule

- **EF Core**: default choice for modeling, migrations, standard CRUD, anything where developer productivity and maintainability outweigh raw throughput.
- **Dapper or `EFCore.BulkExtensions`**: reach for these specifically on identified hot paths — high-volume inserts, reporting queries, batch jobs — not as a wholesale replacement for EF Core in a codebase.
- **`ExecuteUpdate`/`ExecuteDelete`**: use in place of Dapper for simple set-based updates/deletes where you're already in EF Core and don't want a second data-access technology just for one query.
