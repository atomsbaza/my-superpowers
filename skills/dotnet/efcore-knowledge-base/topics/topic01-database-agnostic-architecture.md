# Topic 1: Database-Agnostic Architecture

**Source case study**: Virto Commerce's migration to support MS SQL, PostgreSQL, and MySQL/OceanBase interchangeably.

## The problem

A platform built against one database provider accumulates provider-specific assumptions (types, SQL dialects, migration history) that make swapping providers a breaking change. Virto Commerce's stated goal: let users switch database providers "without disruption."

## The pattern

- **Provider isolation by project**: split the Data layer into a shared base project (`CartModule.Data`) plus one project per provider (`CartModule.Data.SqlServer`, `CartModule.Data.MySql`, …). Provider-specific code — connection setup, type mappings, migrations — never leaks into the shared project.
- **Extensibility framework**: the shared project exposes extension points so a new provider can be added later without touching existing core logic.
- **Per-provider entity configuration**: use EF Core's `ApplyConfigurationsFromAssembly` to apply `IEntityTypeConfiguration<T>` classes scoped to a provider assembly. This is where provider quirks get handled — e.g. MySQL has no native `money` type, so the MySQL configuration project maps money fields to `decimal` explicitly via Fluent API, while the SQL Server project can use `money` directly.
- **Per-provider migrations**: implement `IDesignTimeDbContextFactory<TContext>` once per provider project so `dotnet ef migrations` can be pointed at a specific provider's context without the design-time tooling guessing which connection string/provider to use.

## Why this matters for OceanBase (MySQL-mode)

OceanBase's MySQL-mode is wire-compatible with MySQL via the Pomelo provider, so it slots into the "MySQL" provider project in this pattern with no additional isolation needed — the same `CartModule.Data.MySql`-style project and money-type workaround apply. Anything OceanBase does differently at the SQL level (partitioning syntax, specific index types) should still live in that provider-scoped project, not in shared code.

## When to reach for this

Only worth the structural overhead if multi-provider support is an actual product requirement (self-hosted customers choosing their own DB, or a migration path off a legacy provider). For a single-provider service, this is unnecessary indirection — see the `ponytail`/YAGNI skill before adopting it speculatively.
