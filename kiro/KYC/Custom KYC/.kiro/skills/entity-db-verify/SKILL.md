---
name: entity-db-verify
description: "Verify EF Core entity mappings match the actual MySQL table schema. Use when: adding new entities, debugging 'Unknown column' or 'doesn't have a default value' errors, or before deploying entity changes. Pairs with: db-migration, bug-investigator subagents."
---

# Entity-DB Verification

Verify that C# entity classes match the real database schema. Prevents INSERT/SELECT failures from column mismatches.

## When to Use

- Adding a new entity or property to an existing entity
- `Unknown column 'X' in 'field list'` error
- `Field 'X' doesn't have a default value` error
- Before deploying any entity change to SIT/UAT/PROD
- After scaffolding entities from DB (verify nothing drifted)

## Steps

### 1. Get actual DB schema

```sql
DESCRIBE TableName;
```

### 2. Compare with entity

For each DB column, verify:

| Check | DB | C# Entity | Common mistake |
|-------|-----|-----------|----------------|
| Column exists | ✅ in DESCRIBE | Property mapped | Entity has property for non-existent column |
| Column name | Exact match | `HasColumnName("X")` | PascalCase vs DB name (e.g., `CountryID` vs `CountryId`) |
| Type | `int(11)` | `int` | Using `string` for an `int` column, or `long` for `int` |
| Nullable | `YES`/`NO` | `int?` vs `int` | Non-nullable value type for nullable column |
| Default | Has default? | Value-type defaults to 0 | NOT NULL + no default + no value = INSERT fails |

### 3. Type mapping reference

| MySQL | C# | Notes |
|-------|-----|-------|
| `bigint(20)` | `long` | |
| `int(11)` | `int` | |
| `tinyint(4)` | `sbyte` | |
| `bit(1)` | `ulong` | EF Core maps BIT to ulong |
| `varchar(N)` | `string?` | Usually nullable |
| `datetime` | `DateTime?` | Usually nullable |
| `decimal(15,N)` | `decimal?` | |
| `text` / `json` | `string?` | |

### 4. Fix patterns

**Column doesn't exist in DB but entity has it:**
- Remove from entity, OR
- Add column: `ALTER TABLE X ADD COLUMN Y type NULL;`

**Column exists in DB but entity doesn't have it:**
- If NOT NULL without default → MUST add to entity (value types default to 0 on INSERT)
- If nullable → safe to ignore (EF won't include it in INSERT)

**Column name mismatch:**
```csharp
entity.Property(e => e.CountryId).HasColumnName("CountryID");
```

**NOT NULL column without default (e.g., PIC):**
- Add property as value type (int, not int?) — C# defaults to 0
- Or add DB default: `ALTER TABLE X ALTER COLUMN Y SET DEFAULT 0;`

## Checklist Before Deploy

- [ ] Ran `DESCRIBE TableName` for every modified entity
- [ ] All column names match (case-sensitive)
- [ ] All types match (int vs long vs string)
- [ ] All NOT NULL columns without defaults have a mapped property with a value
- [ ] No extra properties that don't exist in the table
- [ ] Entity configuration `HasColumnName` used for any non-PascalCase DB columns
