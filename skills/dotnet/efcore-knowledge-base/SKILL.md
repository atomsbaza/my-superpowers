---
name: efcore-knowledge-base
description: "Research-synthesized knowledge base on EF Core performance and data-access architecture (NotebookLM deep research, 98 sources). Use when optimizing EF Core queries (single vs split query, Cartesian explosion), deciding between EF Core and Dapper for a data-access path, replacing load-modify-save loops with ExecuteUpdate/ExecuteDelete, designing a database-agnostic/multi-provider data layer, troubleshooting Hangfire or background-worker connection-pool exhaustion against MySQL-family databases, or working with the Pomelo provider against OceanBase MySQL-mode."
---

<!-- argument-hint: [topic, technique name, or topic number] -->

# EF Core Performance & Data-Access Architecture: A Research-Synthesized Knowledge Base
**Source**: NotebookLM deep web research (98 sources) | **Topics**: 5 | **Generated**: 2026-07-29

## How to Use This Skill

- **Without arguments** — load core frameworks below for reference
- **With a topic** — ask about `single vs split query`, `ExecuteUpdate`, `Dapper vs EF Core`, `Hangfire connections`, `OceanBase provider`, or another indexed topic; I find and read the relevant topic file
- **With a topic number** — ask for `topic02` or `topic05`; I load that specific topic
- **Browse** — ask "what topics do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read the relevant topic file before answering.

**Note on provenance:** this knowledge base is synthesized from web research, not a single authoritative source. See **Scope & Limits** below for an explicit, known gap in OceanBase-specific documentation coverage — do not treat OceanBase-specific claims here as verified without checking topic05 first.

---

## Core Frameworks & Mental Models

**ExecuteUpdate/ExecuteDelete over load-modify-save**. EF Core 7+'s `ExecuteUpdateAsync`/`ExecuteDeleteAsync` translate a LINQ expression straight into one SQL statement at the database, skipping entity materialization and the change tracker entirely — turning an $O(N)$ loop into a single round trip. The tradeoff: the change tracker has no idea the rows changed, so never mix these with tracked `SaveChanges()` writes against the same rows in one `DbContext` lifetime.

**Single query vs split query**. Eagerly loading (`Include`) more than one collection navigation on the same root entity in a single SQL query causes a **Cartesian explosion** — row count multiplies across every combination of the joined collections, even though the real object graph is much smaller (EF Core flags this as warning 20504). `.AsSplitQuery()` issues one query per collection instead, trading more round trips for no duplicated rows. Benchmarked: for 2+ collections, split queries were ~5.6x faster and used ~5.6x less memory than single queries in the sourced data; for a single collection, single query wins slightly.

**Dapper vs EF Core, by use case, not by default**. EF Core is the default choice for modeling, migrations, and CRUD where maintainability matters more than raw throughput. Dapper (or `EFCore.BulkExtensions`) wins decisively on raw insert/update throughput and memory footprint — but the right move is to identify specific hot paths and drop to Dapper there, not to replace EF Core wholesale. A recurring community framing: if your fix for a perf problem is "precompile the query," you're probably solving the wrong layer — check for an architectural fix (batching, split query, wrong tool for this path) first.

**Provider isolation for database-agnostic architecture**. To support swapping database providers (MS SQL / PostgreSQL / MySQL / OceanBase MySQL-mode) without breaking changes, split the data layer into a shared base project plus one project per provider. Provider-specific type quirks (e.g. MySQL/OceanBase having no native `money` type) get handled via `ApplyConfigurationsFromAssembly`-scoped `IEntityTypeConfiguration<T>` classes in that provider's project; migrations get a per-provider `IDesignTimeDbContextFactory<TContext>` so design-time tooling isn't ambiguous. Only worth the overhead when multi-provider support is an actual product requirement — not speculative.

**Connection-footprint math for background workers**. Frameworks like Hangfire that poll a shared database multiply their connection footprint by worker-count × process-count (default 10 workers/process). Under containerized scale-out, this alone can exhaust a MySQL-family database's max-connections limit before application traffic is even a factor. Fix order: reduce worker count first (cheap, no infra change), only raise DB max-connections after worker count is right-sized, and check the ADO.NET connection-pool size isn't itself oversized relative to the DB's ceiling.

**OceanBase (MySQL-mode) fits the "MySQL provider" slot**. OceanBase's MySQL-mode is wire-compatible with MySQL, so the standard Pomelo EF Core provider and the MySQL-mode-quirk workarounds (money type, connection-pool math) apply directly — no separate OceanBase EF Core provider needed for basic CRUD/migrations. But OceanBase-specific behavior beyond that baseline (partitioning syntax, index types, dialect differences) is an **explicit coverage gap** in this research run — see topic05 before relying on any OceanBase-specific claim.

---

## Topic Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [topic01](topics/topic01-database-agnostic-architecture.md) | Database-Agnostic Architecture | Provider isolation; `ApplyConfigurationsFromAssembly`; `IDesignTimeDbContextFactory` |
| [topic02](topics/topic02-bulk-operations-and-change-tracking.md) | Bulk Operations, Change Tracking, Dapper vs EF Core | `ExecuteUpdate`/`ExecuteDelete`; Dapper benchmark data |
| [topic03](topics/topic03-query-strategy-single-vs-split.md) | Single Query vs Split Query | Cartesian explosion; `.AsSplitQuery()`; warning 20504 |
| [topic04](topics/topic04-connection-and-resource-management.md) | Connection Pooling and Background-Job Resource Consumption | Hangfire worker-count math; connection-ceiling audits |
| [topic05](topics/topic05-oceanbase-and-pomelo-provider-notes.md) | OceanBase and Pomelo Provider Notes | What's verified vs the explicit OceanBase-docs coverage gap |

## Concept Index

- **`ApplyConfigurationsFromAssembly`** → topic01
- **Cartesian explosion** → topic03
- **Change tracker staleness** → topic02
- **Connection-pool exhaustion** → topic04
- **Dapper vs EF Core benchmarks** → topic02
- **`ExecuteUpdateAsync` / `ExecuteDeleteAsync`** → topic02
- **Hangfire worker count** → topic04
- **`IDesignTimeDbContextFactory`** → topic01
- **Money-type workaround (MySQL/OceanBase)** → topic01, topic05
- **OceanBase MySQL-mode** → topic01, topic05
- **Pomelo provider** → topic01, topic05
- **Provider isolation pattern** → topic01
- **Split query (`.AsSplitQuery()`)** → topic03
- **Warning 20504** → topic03

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and named patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the synthesized research content only, not a single canonical source. **Explicit gap**: this research run's automated fetch of 24 `en.oceanbase.com/docs/...` pages and 2 StackOverflow pages failed (likely JS-rendered content or scraper blocking) — so OceanBase-specific behavior beyond "it's MySQL-mode compatible via Pomelo" is **not verified** by this knowledge base. Check topic05 before relying on any OceanBase-specific claim, and consider re-running research with direct source URLs to close the gap.

For hands-on implementation, combine this with `implementing-dotnet` (writes the actual C#/EF Core code) and `designing-database-schema` (schema/index design) — this skill is the reference/knowledge layer, those are the doing layer.
