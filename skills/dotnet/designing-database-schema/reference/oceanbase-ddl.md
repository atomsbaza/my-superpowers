# OceanBase DDL Reference for .NET Projects

## Connection String Format

```
Server=<obproxy-host>;Port=2881;Database=<database>;
User=<username>@<tenant_name>#<cluster_name>;
Password=<password>;
CharSet=utf8mb4;
MaximumPoolSize=200;MinimumPoolSize=10;
ConnectionIdleTimeout=300;ConnectionLifeTime=1800;
DefaultCommandTimeout=60;ConnectionReset=true;
```

Alternative user format: `User=<cluster>:<tenant>:<username>`

## Partitioning DDL Examples

### RANGE by Month (Event/Audit Tables)

```sql
-- Applied via migrationBuilder.Sql() after CreateTable
ALTER TABLE order_events
PARTITION BY RANGE COLUMNS (created_at) (
    PARTITION p202601 VALUES LESS THAN ('2026-02-01 00:00:00'),
    PARTITION p202602 VALUES LESS THAN ('2026-03-01 00:00:00'),
    PARTITION p202603 VALUES LESS THAN ('2026-04-01 00:00:00'),
    PARTITION p202604 VALUES LESS THAN ('2026-05-01 00:00:00'),
    PARTITION p202605 VALUES LESS THAN ('2026-06-01 00:00:00'),
    PARTITION p202606 VALUES LESS THAN ('2026-07-01 00:00:00'),
    PARTITION p202607 VALUES LESS THAN ('2026-08-01 00:00:00'),
    PARTITION p202608 VALUES LESS THAN ('2026-09-01 00:00:00'),
    PARTITION p202609 VALUES LESS THAN ('2026-10-01 00:00:00'),
    PARTITION p202610 VALUES LESS THAN ('2026-11-01 00:00:00'),
    PARTITION p202611 VALUES LESS THAN ('2026-12-01 00:00:00'),
    PARTITION p202612 VALUES LESS THAN ('2027-01-01 00:00:00'),
    PARTITION pmax    VALUES LESS THAN MAXVALUE
);
```

Remove in Down():
```sql
ALTER TABLE order_events REMOVE PARTITIONING;
```

### HASH on Primary Key (High-Write Transactional Tables)

```sql
ALTER TABLE orders
PARTITION BY HASH(id) PARTITIONS 8;
```

### LIST by Tenant (Multi-Tenant Tables)

```sql
-- Use when tenant IDs are known at schema design time
ALTER TABLE documents
PARTITION BY LIST COLUMNS (tenant_id) (
    PARTITION p_tenant_a VALUES IN ('tenant-a-guid'),
    PARTITION p_tenant_b VALUES IN ('tenant-b-guid'),
    PARTITION p_default  DEFAULT
);
```

### Composite: RANGE + HASH Subpartition (High-Volume Event Tables)

```sql
ALTER TABLE metrics
PARTITION BY RANGE COLUMNS (recorded_at)
SUBPARTITION BY HASH(id) SUBPARTITIONS 4
(
    PARTITION p202601 VALUES LESS THAN ('2026-02-01'),
    PARTITION p202602 VALUES LESS THAN ('2026-03-01'),
    PARTITION pmax    VALUES LESS THAN MAXVALUE
);
```

## Adding New Monthly Partition (Maintenance Script)

```sql
-- Run monthly via scheduled job or migration
ALTER TABLE order_events ADD PARTITION (
    PARTITION p202701 VALUES LESS THAN ('2027-02-01 00:00:00')
);
```

## Known Incompatibilities with EF Core / Pomelo

| Feature | OceanBase Behavior | .NET Workaround |
|---|---|---|
| `ascii` charset | Not supported | Force `utf8mb4` globally via `CharSet(CharSet.Utf8Mb4)` |
| `SELECT FOR SHARE` | Not supported | Use `[Timestamp]` / `IsRowVersion()` for optimistic concurrency |
| `LOAD_FILE()` | Not supported | Use application-level file upload to blob storage |
| `GET_LOCK()` / `RELEASE_LOCK()` | Not supported | Use Redis distributed lock or DB-level advisory lock alternative |
| Spatial types | Not supported | Store as WKT string if geometry is needed |
| `ServerVersion.AutoDetect()` | Unreliable | Hardcode `new MySqlServerVersion(new Version(8, 0, 29))` |
| GUID columns via Pomelo default | Generates `ascii` charset | Explicitly configure `HasColumnType("char(36)").HasCharSet("utf8mb4")` |

## Index Recommendations

```sql
-- Partition pruning: queries MUST include the partition key in WHERE clause
-- For RANGE by created_at:
SELECT * FROM order_events WHERE created_at >= '2026-06-01' AND created_at < '2026-07-01';
-- ✅ Partition pruning applies — scans only p202606

SELECT * FROM order_events WHERE order_id = 'some-guid';
-- ❌ Full partition scan — add created_at to the query if possible
```

Create a covering index on frequently queried columns alongside the partition key:

```sql
CREATE INDEX ix_order_events_order_created
ON order_events (order_id, created_at);
```
