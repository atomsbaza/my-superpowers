---
name: implementing-dotnet
description: >
  Implements production-quality C# .NET 8 or .NET 10 code from a design document,
  specification, or direct request. Use when the user asks to implement a feature,
  write C# code, generate .NET code, code a service, build an endpoint, or create
  any .NET implementation. Enforces principal engineer coding standards: minimal APIs,
  record DTOs, IOptions, ILogger, cancellation tokens, Pomelo EF Core for OceanBase.
  Reads workflow-state.json for design context when available.
---

## Purpose

Generate production-ready C# .NET code that a principal engineer would not be embarrassed to review. No placeholder TODOs, no empty catch blocks, no missing cancellation tokens.

## Input

- `workflow-state.json` → `design` for entity model and service structure
- Direct specification or user description
- Existing code to extend (read the files first before generating)

Always read existing code before generating new code for an established project. Match the existing patterns and style exactly.

## Pre-flight Checks

Before generating any code:
1. Check the target .NET version. If .NET 6 is detected, state: "⚠️ .NET 6 is EOL (November 2024). Consider upgrading to .NET 8 or .NET 10."
2. Check if Pomelo EF Core is already configured. If yes, match the existing `ServerVersion`.
3. Check if the project uses minimal API or controller-based routing. Match it.
4. Read `reference/patterns.md` for project-specific patterns before generating.

## Coding Standards

### Project Structure

```
src/
  MyProject.Api/           # Minimal API host
  MyProject.Application/   # MediatR handlers, DTOs, interfaces
  MyProject.Domain/        # Entities, value objects, domain events
  MyProject.Infrastructure/# EF Core, repositories, external services
tests/
  MyProject.UnitTests/
  MyProject.IntegrationTests/
```

### Entity Implementation

```csharp
// Domain entity — no data annotations on complex mappings
public sealed class OrderHeader
{
    public Guid Id { get; private set; }
    public Guid CustomerId { get; private set; }
    public OrderStatus Status { get; private set; }
    public DateTimeOffset CreatedAt { get; private set; }
    public uint RowVersion { get; private set; } // optimistic concurrency for OceanBase

    private OrderHeader() { } // EF Core constructor

    public static OrderHeader Create(Guid customerId)
    {
        ArgumentException.ThrowIfNullOrEmpty(customerId.ToString());
        return new OrderHeader
        {
            Id = Guid.NewGuid(),
            CustomerId = customerId,
            Status = OrderStatus.Draft,
            CreatedAt = DateTimeOffset.UtcNow
        };
    }
}
```

### EF Core Configuration (Fluent API, OceanBase-safe)

```csharp
public sealed class OrderHeaderConfiguration : IEntityTypeConfiguration<OrderHeader>
{
    public void Configure(EntityTypeBuilder<OrderHeader> builder)
    {
        builder.ToTable("order_headers");
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id).HasColumnType("char(36)").HasCharSet("utf8mb4");
        builder.Property(x => x.Status).HasConversion<string>();
        // Optimistic concurrency — OceanBase does not support FOR SHARE
        builder.Property(x => x.RowVersion).IsRowVersion().HasColumnName("row_version");
    }
}
```

### DbContext Registration (.NET 8)

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseMySql(
        builder.Configuration.GetConnectionString("Default"),
        new MySqlServerVersion(new Version(8, 0, 29)), // hardcoded — never AutoDetect
        mySqlOptions => mySqlOptions
            .CharSet(CharSet.Utf8Mb4) // override ascii charset — OceanBase compatibility
            .EnableRetryOnFailure(3, TimeSpan.FromSeconds(5), null)
    )
);
```

### Minimal API Endpoint

```csharp
app.MapPost("/api/v1/orders", async (
    CreateOrderRequest request,
    IMediator mediator,
    CancellationToken cancellationToken) =>
{
    var result = await mediator.Send(new CreateOrderCommand(request.CustomerId), cancellationToken);
    return Results.CreatedAtRoute("GetOrder", new { id = result.Id }, result);
})
.WithName("CreateOrder")
.Produces<OrderDto>(StatusCodes.Status201Created)
.ProducesValidationProblem()
.RequireAuthorization();
```

### MediatR Handler

```csharp
public sealed class CreateOrderHandler : IRequestHandler<CreateOrderCommand, OrderDto>
{
    private readonly IOrderRepository _repository;
    private readonly ILogger<CreateOrderHandler> _logger;

    public CreateOrderHandler(IOrderRepository repository, ILogger<CreateOrderHandler> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    public async Task<OrderDto> Handle(CreateOrderCommand request, CancellationToken cancellationToken)
    {
        var order = OrderHeader.Create(request.CustomerId);
        await _repository.AddAsync(order, cancellationToken).ConfigureAwait(false);
        _logger.LogInformation("Order {OrderId} created for customer {CustomerId}", order.Id, request.CustomerId);
        return OrderDto.From(order);
    }
}
```

### Repository Pattern

```csharp
public sealed class OrderRepository : IOrderRepository
{
    private readonly AppDbContext _context;

    public OrderRepository(AppDbContext context) => _context = context;

    public async Task<OrderHeader?> GetByIdAsync(Guid id, CancellationToken cancellationToken) =>
        await _context.Orders
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken)
            .ConfigureAwait(false);

    public async Task AddAsync(OrderHeader order, CancellationToken cancellationToken)
    {
        await _context.Orders.AddAsync(order, cancellationToken).ConfigureAwait(false);
        await _context.SaveChangesAsync(cancellationToken).ConfigureAwait(false);
    }
}
```

### Configuration Binding

```csharp
public sealed class DatabaseOptions
{
    public const string Section = "Database";
    public string ConnectionString { get; init; } = string.Empty;
    public int MaxPoolSize { get; init; } = 200;
}

// Registration
builder.Services.Configure<DatabaseOptions>(
    builder.Configuration.GetSection(DatabaseOptions.Section));
```

### Error Handling

Use Problem Details (RFC 7807) for all API errors:

```csharp
builder.Services.AddProblemDetails();
app.UseExceptionHandler();
// In handler: throw new ValidationException(...) → maps to 400
// Uncaught: maps to 500 with correlation ID
```

Never swallow exceptions. Never use empty catch blocks. Log at the appropriate level and rethrow or convert to a domain result.

## Security Standards

Apply every rule below. These are not optional.

### Input Validation

Validate at the system boundary — HTTP endpoint, message consumer, file reader — before the input reaches any business logic.

```csharp
// FluentValidation validator registered as a pipeline behavior
public sealed class CreateOrderCommandValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderCommandValidator()
    {
        RuleFor(x => x.CustomerId).NotEmpty();
        RuleFor(x => x.Items).NotEmpty().ForEach(item =>
        {
            item.ChildRules(i =>
            {
                i.RuleFor(x => x.ProductId).NotEmpty();
                i.RuleFor(x => x.Quantity).GreaterThan(0).LessThanOrEqualTo(1000);
            });
        });
    }
}
```

Never trust: HTTP headers, query string parameters, route values, message payloads, file names, file contents.

### Secrets Handling

```csharp
// ✅ Read from IConfiguration (backed by Key Vault or Secret Manager in prod)
var apiKey = configuration["ExternalService:ApiKey"]
    ?? throw new InvalidOperationException("ExternalService:ApiKey is not configured.");

// ❌ Never hardcode
const string apiKey = "sk-abc123...";

// ❌ Never log
_logger.LogInformation("Calling external service with key {ApiKey}", apiKey);
```

### Auth Enforcement

Every endpoint that mutates state or returns data specific to a user/tenant requires authorization:

```csharp
app.MapPost("/api/v1/orders", handler).RequireAuthorization();
app.MapGet("/api/v1/orders/{id}", handler).RequireAuthorization();

// For resource-level authorization (owns the order?)
public class OrderAuthorizationHandler : AuthorizationHandler<OwnsResourceRequirement, OrderHeader>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OwnsResourceRequirement requirement,
        OrderHeader resource)
    {
        var userId = context.User.GetUserId();
        if (resource.CustomerId == userId)
            context.Succeed(requirement);
        return Task.CompletedTask;
    }
}
```

### Safe SQL

EF Core LINQ and `FromSqlInterpolated` are safe. `FromSqlRaw` with user input is not.

```csharp
// ✅ Safe — EF Core parameterizes automatically
var order = await _context.Orders
    .Where(o => o.CustomerId == customerId && o.Status == status)
    .FirstOrDefaultAsync(ct);

// ✅ Safe — interpolated string is parameterized by EF Core
var orders = await _context.Orders
    .FromSqlInterpolated($"SELECT * FROM orders WHERE customer_id = {customerId}")
    .ToListAsync(ct);

// ❌ Unsafe — string concatenation reaches SQL
var orders = await _context.Orders
    .FromSqlRaw($"SELECT * FROM orders WHERE customer_id = '{customerId}'")
    .ToListAsync(ct);
```

### Safe Error Responses

```csharp
// Global exception handler — strips internal detail, exposes only correlation ID
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var problemDetails = new ProblemDetails
        {
            Status = 500,
            Title = "An unexpected error occurred.",
            Extensions = { ["correlationId"] = Activity.Current?.Id ?? context.TraceIdentifier }
        };
        // Never include: exception.Message, exception.StackTrace, inner DB errors
        context.Response.StatusCode = 500;
        await context.Response.WriteAsJsonAsync(problemDetails);
    });
});
```

### File Path Safety

```csharp
// Sanitize any file path derived from user input
private static string SafePath(string userInput, string baseDirectory)
{
    var fullPath = Path.GetFullPath(Path.Combine(baseDirectory, userInput));
    if (!fullPath.StartsWith(baseDirectory, StringComparison.OrdinalIgnoreCase))
        throw new InvalidOperationException("Path traversal attempt detected.");
    return fullPath;
}
```

## Logging Standard

Read `reference/logging-standard.md` for full Serilog setup. Summary of mandatory rules:

```csharp
// ✅ Structured template — Serilog captures OrderId as a typed property
_logger.LogInformation("Order {OrderId} created for customer {CustomerId}",
    order.Id, order.CustomerId);

// ❌ String interpolation — collapses to flat string, loses structure
_logger.LogInformation($"Order {order.Id} created for customer {order.CustomerId}");

// ❌ PII in log
_logger.LogInformation("Customer {Email} placed order", customer.Email);

// ❌ Secret in log
_logger.LogDebug("Calling external API with key {Key}", apiKey);
```

**Always enrich with correlation context at the entry point:**

```csharp
// In middleware or MediatR pipeline behavior
using (_logger.BeginScope(new Dictionary<string, object>
{
    ["CorrelationId"] = correlationId,
    ["UserId"] = userId,        // GUID only, never email
    ["TenantId"] = tenantId
}))
{
    // all log calls inside inherit these properties
}
```

**Log levels:**
- `Information` — normal operational event (order created, job completed)
- `Warning` — recoverable unexpected state (retry #2, fallback activated, deprecated endpoint called)
- `Error` — operation failed, needs investigation (exception at handler boundary, save failed)
- `Critical` — system cannot continue (startup config missing, health check breached)

## Output

- Write all generated files to their correct project paths.
- List every file created/modified in a summary table.
- Update `workflow-state.json`:
```json
{
  "stage": "implemented",
  "implementation": {
    "files_created": ["path/to/file.cs"],
    "files_modified": ["path/to/file.cs"]
  }
}
```
