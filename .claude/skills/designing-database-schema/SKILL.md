---
name: designing-database-schema
description: >
  Designs database schemas and EF Core entity configurations for OceanBase
  (MySQL-mode) targets. Produces Fluent API entity configurations, index
  definitions, and raw SQL migration snippets for OceanBase partitioning.
  Use when the user asks for database schema design, EF Core migration, entity
  configuration, OceanBase table design, DDL, partitioning strategy, or
  schema for a .NET project. Reads workflow-state.json for entity model context.
---

## Purpose

Produce schemas that are correct for OceanBase MySQL-mode, safe for EF Core migrations, and structured for the data access patterns the system requires.

## Input

- `workflow-state.json` → `design.entities` for entity model
- Direct entity descriptions from the user
- Existing schema to extend or review

## OceanBase Compatibility Rules (Non-Negotiable)

Apply every rule below without exception:

1. **`utf8mb4` charset everywhere.** OceanBase does not support `ascii`. Every `char`, `varchar`, and `text` column must use `utf8mb4`. Set globally on DbContext to avoid Pomelo defaulting to `ascii` for GUID columns.
2. **No `SELECT FOR SHARE`.** OceanBase does not support pessimistic concurrency via `FOR SHARE`. Use optimistic concurrency with `uint RowVersion` mapped as `.IsRowVersion()`.
3. **Partitioning via raw SQL.** EF Core cannot express OceanBase partition DDL natively. Always add `migrationBuilder.Sql(...)` after `CreateTable` for tables that need partitioning.
4. **Hardcode `ServerVersion(8, 0, 29)`.** Never use `AutoDetect()` — OceanBase's handshake version string can confuse Pomelo's feature detection.
5. **GUID columns.** Use `char(36)` with `utf8mb4` — not `binary(16)` which Pomelo may generate with `ascii`.

## Global DbContext Charset Configuration

Always include this in the Pomelo `UseMySql` options:

```csharp
options.UseMySql(connectionString,
    new MySqlServerVersion(new Version(8, 0, 29)),
    mySqlOptions => mySqlOptions.CharSet(CharSet.Utf8Mb4));
```

## Entity Configuration Template

```csharp
public sealed class ExampleEntityConfiguration : IEntityTypeConfiguration<ExampleEntity>
{
    public void Configure(EntityTypeBuilder<ExampleEntity> builder)
    {
        builder.ToTable("example_entities");

        // PK — GUID as char(36) utf8mb4
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id)
            .HasColumnType("char(36)")
            .HasCharSet("utf8mb4")
            .ValueGeneratedNever();

        // String columns — explicit utf8mb4
        builder.Property(x => x.Name)
            .HasMaxLength(256)
            .HasCharSet("utf8mb4")
            .IsRequired();

        // Enum as string
        builder.Property(x => x.Status)
            .HasConversion<string>()
            .HasMaxLength(64)
            .HasCharSet("utf8mb4");

        // Optimistic concurrency — replaces FOR SHARE
        builder.Property(x => x.RowVersion)
            .IsRowVersion()
            .HasColumnName("row_version");

        // DateTime — always UTC, stored as datetime(6)
        builder.Property(x => x.CreatedAt)
            .HasColumnType("datetime(6)")
            .HasConversion(
                v => v.UtcDateTime,
                v => new DateTimeOffset(v, TimeSpan.Zero));

        // Indexes
        builder.HasIndex(x => x.CreatedAt).HasDatabaseName("ix_example_created_at");
        builder.HasIndex(x => new { x.TenantId, x.Status })
            .HasDatabaseName("ix_example_tenant_status");
    }
}
```

## Partitioning Strategy Reference

Load `reference/oceanbase-ddl.md` for full DDL examples.

### When to Partition

| Table Type | Volume | Strategy | Partition Key |
|---|---|---|---|
| Event / audit log | > 10M rows/month | RANGE by month | `created_at` |
| High-write transactional | > 50M rows | HASH | Primary key |
| Multi-tenant data | Variable | LIST | `tenant_id` |
| Reference / config | < 100K rows | None | — |

### RANGE Partitioning (Event Tables)

```sql
ALTER TABLE order_events
PARTITION BY RANGE COLUMNS (created_at) (
    PARTITION p202601 VALUES LESS THAN ('2026-02-01'),
    PARTITION p202602 VALUES LESS THAN ('2026-03-01'),
    PARTITION pmax    VALUES LESS THAN MAXVALUE
);
```

**Important:** Always include a `pmax` partition to catch future data when partition management is not yet automated.

### HASH Partitioning (High-Write Tables)

```sql
ALTER TABLE orders
PARTITION BY HASH(id) PARTITIONS 8;
```

Use power-of-2 partition counts (4, 8, 16) to allow future repartitioning without full data movement.

## Migration Generation Process

For each entity:

1. Generate the entity class (Domain layer)
2. Generate the EF Core configuration class (Infrastructure layer)
3. Determine partitioning strategy based on entity type
4. Write the EF Core migration `Up()` method:
   - `migrationBuilder.CreateTable(...)` — standard EF Core DDL
   - `migrationBuilder.Sql(...)` — OceanBase partition DDL (if needed)
5. Write the `Down()` method with `REMOVE PARTITIONING` if applicable
6. Generate `DbContext` registration snippet

## Output

- Entity class files (Domain layer)
- Configuration class files (Infrastructure layer)
- Migration file (Infrastructure/Migrations)
- Connection string template for appsettings.json:

```json
{
  "ConnectionStrings": {
    "Default": "Server=<obproxy-host>;Port=2881;Database=<db>;User=<user>@<tenant>#<cluster>;Password=<pwd>;CharSet=utf8mb4;MaximumPoolSize=200;MinimumPoolSize=10;ConnectionIdleTimeout=300;ConnectionLifeTime=1800;DefaultCommandTimeout=60;"
  }
}
```

Update `workflow-state.json`:
```json
{
  "stage": "schema_designed",
  "schema": {
    "entities": ["EntityName"],
    "partitioned_tables": ["table_name"],
    "migration_files": ["path/to/migration.cs"]
  }
}
```
