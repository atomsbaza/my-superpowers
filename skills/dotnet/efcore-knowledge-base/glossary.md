# Glossary

**Cartesian explosion** — the row-count blowup that occurs when a single SQL query joins across more than one collection navigation, returning every combination of rows across those collections instead of the actual (smaller) object graph.

**Change tracker** — EF Core's in-memory record of tracked entities and their original vs current values, used to compute the SQL statements `SaveChanges()` issues. Untouched by `ExecuteUpdate`/`ExecuteDelete`.

**Compiled query** — a pre-built, cached LINQ-to-SQL translation that skips EF Core's query-compilation step on repeat execution. Treated by the research as a micro-optimization, not a fix for architectural performance problems.

**`ExecuteUpdateAsync` / `ExecuteDeleteAsync`** — EF Core 7+ methods that translate a LINQ expression directly into a single `UPDATE`/`DELETE` SQL statement executed at the database, bypassing entity materialization and the change tracker.

**`IDesignTimeDbContextFactory<TContext>`** — an interface implemented per database provider so `dotnet ef migrations` design-time tooling knows how to construct that provider's `DbContext` without ambiguity when multiple providers exist in one solution.

**Pomelo (Pomelo.EntityFrameworkCore.MySql)** — the community-maintained EF Core provider for MySQL-protocol databases; used for both MySQL and OceanBase MySQL-mode.

**Provider isolation** — architectural pattern of splitting database-provider-specific code (migrations, type mappings, connection setup) into separate projects per provider, keeping shared/core code provider-agnostic.

**Split query (`.AsSplitQuery()`)** — a query execution mode that issues one SQL query per collection navigation instead of one query joined across all of them, avoiding Cartesian explosion at the cost of more round trips.

**Single query (default)** — EF Core's default eager-loading mode: one SQL query with joins across all included navigations.

**Warning 20504** — EF Core's runtime warning raised when a compiled query is detected to risk Cartesian-explosion-style row growth.
