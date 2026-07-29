# Cheatsheet

## EF Core vs Dapper — which to reach for

| Scenario | Choice |
|---|---|
| Standard CRUD, modeling, migrations | EF Core |
| Bulk insert of many rows | Dapper or `EFCore.BulkExtensions` |
| Set-based update/delete, no need for tracked entities back | `ExecuteUpdateAsync`/`ExecuteDeleteAsync` |
| Reporting / read-heavy hot path | Dapper (raw SQL) |
| You're tempted to "just precompile the query" for perf | Stop — check for the actual architectural issue first (batching, split query, wrong ORM for this path) |

## Single query vs split query

| Eager-loaded collection navigations | Use |
|---|---|
| 0–1 | Single query (default) |
| 2+ | `.AsSplitQuery()` |
| 2+ AND large payload columns in the collections | `.AsSplitQuery()`, high priority |
| EF Core logs warning 20504 | Investigate for this shape |

## Bulk write decision

| Need the updated/deleted entities back as tracked objects? | Use |
|---|---|
| No | `ExecuteUpdateAsync`/`ExecuteDeleteAsync` |
| Yes | Standard tracked `SaveChanges()` (accept the cost) |
| Mixing both in one `DbContext`? | Don't — refresh/discard context between them |

## Hangfire + MySQL-family DB connection troubleshooting

1. Check worker count (default 10/process) × process count vs DB max-connections.
2. Reduce worker count first — cheapest, no infra change.
3. Raise DB max-connections only after worker count is right-sized.
4. Check ADO.NET pool size (Pomelo/MySqlConnector) isn't itself oversized relative to DB limits.

## OceanBase specifics — what's verified here vs not

| Claim | Status |
|---|---|
| Wire-compatible with MySQL via Pomelo provider | Verified (research-sourced) |
| Fits the provider-isolation pattern as a "MySQL" provider | Verified (research-sourced) |
| Partitioning syntax, global/local indexes, dialect-specific SQL gen | **Not verified** — fetch of OceanBase docs failed this run, see [topic05](topics/topic05-oceanbase-and-pomelo-provider-notes.md) |
