# Topic 3: Single Query vs Split Query

## The problem: Cartesian explosion

When a single EF Core query eagerly loads (`Include`) more than one collection navigation on the same root entity, EF Core generates one SQL query with joins across all collections. Because SQL joins are flat, each combination of rows across the collections is returned as a separate row — row count multiplies across collections even though the actual object graph is much smaller. This is a **Cartesian explosion**: redundant data transferred over the wire and re-assembled client-side.

EF Core detects this at runtime and raises warning **20504** when a query risks it.

## The fix: `.AsSplitQuery()`

Split queries issue one SQL query per collection navigation instead of one query with joins across all of them. No duplicated rows, no Cartesian growth — at the cost of more round trips to the database.

## Benchmark data points from research

| Method | Mean Time | Memory Allocated |
|---|---|---|
| Single Query (simple, one collection) | 16.64 ms | 4.04 MB |
| Split Query (simple, one collection) | 18.97 ms | 4.25 MB |
| Single Query (multiple collections) | 200.60 ms | 46.93 MB |
| Split Query (multiple collections) | 35.62 ms | 8.35 MB |

Reading this: for a **single** collection navigation, Single Query wins slightly (fewer round trips, no Cartesian risk since there's only one collection to multiply against). Once **multiple** collection navigations are eagerly loaded together, Split Query wins decisively — roughly 5.6x faster and 5.6x less memory in this benchmark, because Single Query's Cartesian growth compounds with each additional collection.

## Decision rule

- One collection navigation eagerly loaded → default (Single Query) is fine.
- Two or more collection navigations eagerly loaded on the same root → apply `.AsSplitQuery()`, especially if any of those collections carry large payloads (binary blobs, long text columns) that would otherwise be duplicated per Cartesian row.
- If EF Core logs warning 20504 for a query you didn't expect to be risky, that's the signal to check for exactly this shape and consider splitting.
