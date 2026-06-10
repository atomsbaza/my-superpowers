# Logging Standard — C# .NET / Serilog

## Setup

```csharp
// Program.cs
builder.Host.UseSerilog((context, services, config) =>
{
    config
        .ReadFrom.Configuration(context.Configuration)
        .ReadFrom.Services(services)
        .Enrich.FromLogContext()           // picks up BeginScope properties
        .Enrich.WithCorrelationId()        // Serilog.Enrichers.CorrelationId
        .Enrich.WithMachineName()
        .Enrich.WithEnvironmentName()
        .WriteTo.Console(new JsonFormatter()) // structured JSON in all environments
        .WriteTo.OpenTelemetry();             // OTLP sink for observability platform
});

// Request logging middleware — replaces IIS/Kestrel default logs with structured equivalents
app.UseSerilogRequestLogging(options =>
{
    options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
    {
        diagnosticContext.Set("UserId", httpContext.User.GetUserId());
        diagnosticContext.Set("TenantId", httpContext.User.GetTenantId());
    };
    // Exclude health check endpoints from request logs
    options.GetLevel = (ctx, _, _) =>
        ctx.Request.Path.StartsWithSegments("/health") ? LogEventLevel.Verbose : LogEventLevel.Information;
});
```

## Correlation ID Pattern

Every inbound request must carry a correlation ID through all log entries and outbound calls.

```csharp
// Middleware — attach correlation ID at the entry point
public sealed class CorrelationIdMiddleware : IMiddleware
{
    private const string Header = "X-Correlation-Id";

    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        var correlationId = context.Request.Headers[Header].FirstOrDefault()
            ?? Activity.Current?.Id
            ?? Guid.NewGuid().ToString();

        context.Response.Headers[Header] = correlationId;

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await next(context);
        }
    }
}

// MediatR pipeline behavior — propagate into all handlers
public sealed class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        var operationName = typeof(TRequest).Name;
        _logger.LogInformation("Handling {OperationName}", operationName);
        try
        {
            var response = await next();
            _logger.LogInformation("Handled {OperationName} successfully", operationName);
            return response;
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            _logger.LogError(ex, "Handling {OperationName} failed", operationName);
            throw;
        }
    }
}
```

## Log Levels — When to Use Each

| Level | When | Example |
|---|---|---|
| `Verbose` | Trace-level debugging — never in production | `"Entering method {Method} with args {Args}"` |
| `Debug` | Development only — disabled in staging/prod | `"Cache miss for key {CacheKey}"` |
| `Information` | Normal operational events worth recording | `"Order {OrderId} created"`, `"Job {JobName} started"` |
| `Warning` | Recoverable unexpected state — watch, may need action | `"Retry attempt {Attempt} for {Operation}"`, `"Deprecated endpoint called"` |
| `Error` | Operation failed — requires investigation | `"Failed to save order {OrderId}"` + exception |
| `Fatal` | System cannot continue — page someone now | `"Cannot connect to OceanBase on startup"` |

## What to Always Include

Every meaningful log entry must carry:
- `CorrelationId` — from request or generated (via `LogContext.PushProperty`)
- `UserId` — internal GUID only, never email, username, or phone number
- `TenantId` — when the system is multi-tenant
- `OperationName` — handler class name or endpoint route

```csharp
// Explicitly push context at handler scope when not using middleware enrichment
using (_logger.BeginScope(new Dictionary<string, object>
{
    ["UserId"] = command.UserId,
    ["TenantId"] = command.TenantId,
    ["OperationName"] = nameof(CreateOrderHandler)
}))
{
    // all _logger.Log* calls inside inherit these properties automatically
}
```

## What to Never Log

| Category | Examples | Why |
|---|---|---|
| Passwords | `user.Password`, `request.NewPassword` | Credential exposure |
| Tokens | JWT, API keys, refresh tokens, session IDs | Account takeover |
| Connection strings | `ConnectionStrings__Default` value | DB credential exposure |
| PII | Email, phone, name, address, national ID, DOB | GDPR / compliance |
| Payment data | Card numbers, CVV, bank account numbers | PCI DSS |
| Full request body | `JsonSerializer.Serialize(request)` when body may contain any of the above | Catch-all risk |
| Raw DB error messages | OceanBase/MySQL error text | May contain query fragments with data |

**Exception handling — mask carefully:**

```csharp
catch (MySqlException ex)
{
    // ✅ Log error code and correlation — enough to diagnose, no query text leaked
    _logger.LogError("Database operation failed. ErrorCode={ErrorCode} CorrelationId={CorrelationId}",
        ex.ErrorCode, correlationId);

    // ❌ Avoid: ex.Message may contain SQL fragment with user data values
    _logger.LogError("Database error: {Message}", ex.Message);
}
```

## Outbound HTTP — Propagate Correlation

```csharp
// DelegatingHandler — attach correlation ID to all outbound HttpClient requests
public sealed class CorrelationIdHandler : DelegatingHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var correlationId = Activity.Current?.Id ?? Guid.NewGuid().ToString();
        request.Headers.TryAddWithoutValidation("X-Correlation-Id", correlationId);
        return base.SendAsync(request, cancellationToken);
    }
}

// Registration
builder.Services.AddHttpClient<IExternalServiceClient, ExternalServiceClient>()
    .AddHttpMessageHandler<CorrelationIdHandler>();
```

## appsettings.json Serilog Configuration

```json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning",
        "System": "Warning"
      }
    },
    "Enrich": ["FromLogContext", "WithMachineName", "WithThreadId"],
    "Properties": {
      "Application": "MyProject.Api"
    }
  }
}
```

Override `Microsoft.EntityFrameworkCore` to `Warning` (or `Information` only when debugging queries) to prevent EF Core from flooding logs with SQL text that may contain parameter values.
