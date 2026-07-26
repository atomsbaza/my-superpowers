# .NET Implementation Patterns Reference

## Outbox Pattern (Cross-Service Consistency)

Use when a domain operation must publish an event to an external system (message broker, webhook) and the persistence + publish must be atomic.

```csharp
// OutboxMessage entity — stored in same DB transaction as domain changes
public sealed class OutboxMessage
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public string Type { get; init; } = string.Empty;       // fully qualified event type name
    public string Payload { get; init; } = string.Empty;    // JSON-serialized event
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? ProcessedAt { get; set; }        // null = not yet processed
    public string? Error { get; set; }
}

// In handler: save domain entity + outbox message in one SaveChangesAsync call
var outbox = new OutboxMessage
{
    Type = nameof(OrderCreatedEvent),
    Payload = JsonSerializer.Serialize(new OrderCreatedEvent(order.Id))
};
_context.OutboxMessages.Add(outbox);
await _context.SaveChangesAsync(cancellationToken);

// Background worker polls unprocessed outbox messages and publishes them
```

## Domain Events (In-Process)

```csharp
// Raise in domain entity
public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();
private readonly List<IDomainEvent> _domainEvents = new();

protected void RaiseDomainEvent(IDomainEvent domainEvent) =>
    _domainEvents.Add(domainEvent);

// Dispatch via MediatR after SaveChangesAsync in a SaveChangesInterceptor
```

## Specification Pattern (Complex Queries)

```csharp
public abstract class Specification<T>
{
    public abstract Expression<Func<T, bool>> Criteria { get; }
    public List<Expression<Func<T, object>>> Includes { get; } = new();
    public Expression<Func<T, object>>? OrderBy { get; protected set; }
}

// Usage in repository
public async Task<IReadOnlyList<T>> ListAsync(Specification<T> spec, CancellationToken ct)
{
    var query = _context.Set<T>().Where(spec.Criteria);
    query = spec.Includes.Aggregate(query, (q, i) => q.Include(i));
    if (spec.OrderBy != null) query = query.OrderBy(spec.OrderBy);
    return await query.ToListAsync(ct).ConfigureAwait(false);
}
```

## Polly Resilience (External HTTP Calls)

```csharp
builder.Services.AddHttpClient<IExternalServiceClient, ExternalServiceClient>()
    .AddResilienceHandler("external-api", pipeline =>
    {
        pipeline.AddRetry(new HttpRetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential,
            ShouldHandle = args => args.Outcome.Exception is HttpRequestException
        });
        pipeline.AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions
        {
            SamplingDuration = TimeSpan.FromSeconds(30),
            FailureRatio = 0.5,
            MinimumThroughput = 5,
            BreakDuration = TimeSpan.FromSeconds(15)
        });
    });
```

## Structured Logging with Serilog

```csharp
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.WithCorrelationId()
    .Enrich.FromLogContext()
    .WriteTo.Console(new JsonFormatter())  // structured JSON in prod
    .CreateLogger();

// Never log: passwords, tokens, PII, connection strings
// Always include: correlation ID, user ID (not email), operation name
```

## OceanBase Partition DDL in EF Core Migration

```csharp
// In Up() method, after CreateTable:
migrationBuilder.Sql(@"
    ALTER TABLE order_events
    PARTITION BY RANGE COLUMNS (created_at) (
        PARTITION p202601 VALUES LESS THAN ('2026-02-01'),
        PARTITION p202602 VALUES LESS THAN ('2026-03-01'),
        PARTITION p202603 VALUES LESS THAN ('2026-04-01'),
        PARTITION pmax    VALUES LESS THAN MAXVALUE
    );
");

// In Down() method:
migrationBuilder.Sql("ALTER TABLE order_events REMOVE PARTITIONING;");
```

## Worker Service (Background Job)

```csharp
public sealed class OutboxProcessor : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly ILogger<OutboxProcessor> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await ProcessBatchAsync(stoppingToken).ConfigureAwait(false);
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken).ConfigureAwait(false);
        }
    }

    private async Task ProcessBatchAsync(CancellationToken cancellationToken)
    {
        using var scope = _scopeFactory.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        // ... process outbox messages
    }
}
```
