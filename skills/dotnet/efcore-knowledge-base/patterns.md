# Patterns and Techniques

## Provider isolation (database-agnostic architecture)
Split the data-access layer into a shared base project plus one project per database provider. Provider-specific type mapping, migrations, and connection setup live only in that provider's project via `ApplyConfigurationsFromAssembly` and a provider-scoped `IDesignTimeDbContextFactory`. See [topic01](topics/topic01-database-agnostic-architecture.md).

## Bypass-the-tracker bulk writes
Replace load → mutate → `SaveChanges()` loops with `ExecuteUpdateAsync`/`ExecuteDeleteAsync` for set-based updates/deletes. Never mix this with tracked writes against the same rows in the same `DbContext` lifetime — the tracker won't know the rows changed. See [topic02](topics/topic02-bulk-operations-and-change-tracking.md).

## Hybrid ORM
Default to EF Core for modeling/migrations/CRUD. Drop to Dapper or `EFCore.BulkExtensions` only on identified hot paths (bulk inserts, reporting queries) rather than replacing EF Core wholesale. See [topic02](topics/topic02-bulk-operations-and-change-tracking.md).

## Split-query-on-multiple-collections
Apply `.AsSplitQuery()` whenever eager-loading more than one collection navigation on the same root entity, especially when those collections carry large payloads. Leave single collections on the default single-query mode. See [topic03](topics/topic03-query-strategy-single-vs-split.md).

## Connection-footprint audit for background workers
Before scaling out process count to fix background-job throughput, multiply worker-count × process-count and compare against the database's max-connections ceiling — this is what breaks first, not the job logic. See [topic04](topics/topic04-connection-and-resource-management.md).

## MySQL-mode fallback for OceanBase
Treat OceanBase as a MySQL-mode target through the Pomelo provider for anything not OceanBase-specific (partitioning, global indexes). Verify OceanBase-specific claims directly against OceanBase docs — this knowledge base's automated fetch of those docs failed; see [topic05](topics/topic05-oceanbase-and-pomelo-provider-notes.md) for the exact gap.
