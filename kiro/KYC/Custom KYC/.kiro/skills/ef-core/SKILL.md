---
name: ef-core
description: 'EF Core + database performance patterns: NoTracking, read/write split, N+1 prevention, query splitting, row limits, explicit updates. Works with Pomelo MySQL provider.'
---

# Entity Framework Core & Database Performance

## Core Principles

1. **NoTracking by default** — opt-in to tracking only for writes
2. **Separate read/write models** — ReplicaDbContext for reads, PrimaryDbContext for writes
3. **Never do application-side joins** — joins happen in SQL
4. **Always apply row limits** — no unbounded result sets
5. **Explicit Updates** — when NoTracking, use `dbContext.Update(entity)` or `.AsTracking()`
6. **Never edit migrations manually** — use CLI commands only

## NoTracking + Explicit Update Pattern

```csharp
// READ — no tracking (default in KYC services)
var app = await _replicaDb.KycApplication
    .AsNoTracking()
    .FirstOrDefaultAsync(a => a.Id == id);

// WRITE — must explicitly mark for update
var app = await _primaryDb.KycApplication.FirstOrDefaultAsync(a => a.Id == id);
app.StatusCode = 6;
_primaryDb.KycApplication.Update(app); // Required when NoTracking is default
await _primaryDb.SaveChangesAsync();
```

## Read/Write Split (KYC Pattern)

```csharp
// Reads go to replica
var data = await _replicaDb.KycApplication.AsNoTracking().Where(...).ToListAsync();

// Writes go to primary
await _primaryDb.KycApplication.AddAsync(entity);
await _primaryDb.SaveChangesAsync();

// IMPORTANT: Read-after-write must use PRIMARY (replica has lag)
await _primaryDb.SaveChangesAsync();
var inserted = await _primaryDb.KycApplication.FirstAsync(a => a.Id == entity.Id); // NOT replica!
```

## N+1 Prevention

```csharp
// BAD — N+1
var orders = await _db.Orders.ToListAsync();
foreach (var o in orders)
    var items = await _db.OrderItems.Where(i => i.OrderId == o.Id).ToListAsync(); // N queries!

// GOOD — Include
var orders = await _db.Orders.Include(o => o.Items).AsNoTracking().ToListAsync();

// GOOD — Projection (only needed fields)
var summaries = await _db.Orders
    .Select(o => new { o.Id, o.Status, ItemCount = o.Items.Count })
    .ToListAsync();
```

## Query Splitting (multiple collections)

```csharp
// Avoid cartesian explosion with multiple Includes
var product = await _db.Products
    .Include(p => p.Reviews)
    .Include(p => p.Images)
    .AsSplitQuery() // Separate SQL per collection
    .FirstOrDefaultAsync(p => p.Id == id);
```

## Row Limits

```csharp
// ALWAYS limit results
var apps = await _replicaDb.KycApplication
    .Where(a => a.StatusCode == 6)
    .OrderByDescending(a => a.Id)
    .Take(100) // Never unbounded
    .ToListAsync();
```

## Entity Configuration (KYC Pattern)

```csharp
// Fluent API in OnModelCreating or IEntityTypeConfiguration
entity.Property(e => e.ApplicationNo).IsRequired().HasMaxLength(20);
entity.Property(e => e.StatusCode).IsRequired();
entity.HasIndex(e => new { e.ProductId, e.RefId, e.SystemCompanyId });
```

## DbContext Factory (for parallel processing)

```csharp
// When processing items in parallel (like approval service)
services.AddDbContextFactory<eKYCRWContext>(options => ...);

// Each parallel task gets its own context
using var context = _contextFactory.CreateDbContext();
```

## Transaction Pattern

```csharp
await using var transaction = await _primaryDb.Database.BeginTransactionAsync();
try
{
    await _primaryDb.KycApplicationAddress.AddAsync(address);
    await _primaryDb.SaveChangesAsync();
    
    application.MailingAddressId = address.Id;
    await _primaryDb.KycApplication.AddAsync(application);
    await _primaryDb.SaveChangesAsync();
    
    await transaction.CommitAsync();
}
catch
{
    await transaction.RollbackAsync();
    throw;
}
```

## Anti-Patterns

- ❌ `SELECT *` when you only need 2 fields — use projection
- ❌ Application-side joins (`.ToList()` then LINQ join in memory)
- ❌ Missing `.Take()` on list queries
- ❌ Reading from replica immediately after write
- ❌ Forgetting `.Update()` when DbContext uses NoTracking
- ❌ Multiple `.Include()` without `.AsSplitQuery()` (cartesian explosion)
- ❌ `SaveChanges()` inside a loop (batch outside)
