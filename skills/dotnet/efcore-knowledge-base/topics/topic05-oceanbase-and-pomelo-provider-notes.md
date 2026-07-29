# Topic 5: OceanBase (MySQL-mode) and the Pomelo EF Core Provider — Coverage Notes

## Known-good from research

- OceanBase's MySQL-mode is wire-protocol compatible with MySQL, so it works through the standard **Pomelo.EntityFrameworkCore.MySql** provider — no OceanBase-specific EF Core provider is needed for basic CRUD, migrations, or LINQ translation.
- The database-agnostic architecture pattern in [topic01](topic01-database-agnostic-architecture.md) treats OceanBase as a MySQL-mode provider: same project-isolation approach, same `money`-type Fluent API workaround MySQL itself needs (no native `money` type).
- General MySQL-family connection-pooling pressure from background job workers ([topic04](topic04-connection-and-resource-management.md)) applies equally to OceanBase deployments.

## Explicit coverage gap

This research run's automated fetch of `en.oceanbase.com/docs/...` pages (24 URLs) and 2 StackOverflow pages **failed** — likely JS-rendered content or scraper blocking, not absence of the content. As a result, this knowledge base does **not** yet have direct sourcing on:

- OceanBase-specific partitioning syntax and how it interacts with EF Core migrations
- OceanBase's global/local index types and whether/how Pomelo's index Fluent API maps to them
- Any OceanBase-specific SQL dialect differences from stock MySQL that would affect generated LINQ-to-SQL translation
- OceanBase-specific performance tuning parameters beyond generic MySQL connection limits

## How to close this gap

Re-run `notebooklm source add` with the specific `en.oceanbase.com/docs/...` URLs directly (rather than via `source add-research`'s web search, which hit the fetch failures) — a direct fetch through the CLI may succeed where the research crawler didn't, or the pages may need a rendered-fetch tool. Until then, treat any OceanBase-specific claim beyond "Pomelo/MySQL-mode compatibility" in this skill as **unverified** — check OceanBase's official docs directly for partitioning/indexing specifics before relying on this skill for those.
