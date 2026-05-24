---
name: health-check-generator
description: 'Health check patterns for KYC services. Scaffolds downstream service health checks in kyc-partner-api (interface, client, class, registration). Also covers /hc and /diag endpoint setup for new services. Use when adding health checks. Pairs with: devops-engineer subagent.'
---

# Health Check Generator

Scaffold a complete health check for a downstream service in one shot.

## When to invoke

- "add health check for [service]"
- "create health check for [client]"
- After adding a new `IKyc*Client` that calls another KYC service
- When asked to monitor a new dependency

## What it generates

For a given service (e.g., `Identification`):

### 1. AppSetting — add `HealthCheckApi` property (if missing)

```csharp
// DipChip.Common/AppSetting/Kyc{Service}Api.cs
public string HealthCheckApi { get; set; }
```

### 2. Interface — add `HealthCheckAsync()` method

```csharp
// IKyc{Service}Client.cs
Task<KycHealthCheckResponse> HealthCheckAsync();
```

### 3. Client implementation

```csharp
// Kyc{Service}Client.cs
public async Task<KycHealthCheckResponse> HealthCheckAsync()
{
    try
    {
        var apiResponse = await _client.GetAsync(_config.HealthCheckApi);
        if (!(apiResponse?.IsSuccessStatusCode ?? false))
        {
            return new KycHealthCheckResponse { Status = Constants.Unhealthy };
        }

        var responseString = await apiResponse.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<KycHealthCheckResponse>(responseString);
    }
    catch (Exception e)
    {
        _logger.LogError(e, "{Service} health check failed");
        return new KycHealthCheckResponse { Status = Constants.Unhealthy };
    }
}
```

### 4. Health check class

```csharp
// DipChip.API/HealthCheck/{Service}ApiHealthCheck.cs
public class {Service}ApiHealthCheck : IHealthCheck
{
    private readonly IKyc{Service}Client _client;

    public {Service}ApiHealthCheck(IKyc{Service}Client client)
    {
        _client = client;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = new())
    {
        var response = await _client.HealthCheckAsync();
        return response?.Status == Constants.Healthy
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Unhealthy();
    }
}
```

### 5. Startup registration

```csharp
// In Startup.cs ConfigureServices, add to the .AddHealthChecks() chain:
.AddCheck<{Service}ApiHealthCheck>("{Service} API", tags: new[] { "diagnostics" })
```

### 6. Config value

```json
{
  "Kyc{Service}Api": {
    "HealthCheckApi": "/hc"
  }
}
```

## Process

1. Ask which service/client to add a health check for
2. Check if `HealthCheckApi` property already exists in the settings class
3. Check if `HealthCheckAsync()` already exists on the interface
4. Generate only the missing pieces
5. Register in Startup.cs
6. Build to verify

## Setting Up Health Check Endpoints (new service)

When setting up `/hc` and `/diag` in a new service (not kyc-partner-api):

```csharp
// Registration
builder.Services.AddHealthChecks()
    .AddCheck<DatabaseHealthCheck>("database")
    .AddCheck<RedisCachingHealthCheck>("redis");

// Endpoints
app.MapHealthChecks("/hc", new HealthCheckOptions
{
    ResponseWriter = async (context, report) =>
    {
        context.Response.StatusCode = report.Status == HealthStatus.Healthy
            ? (int)HttpStatusCode.OK : (int)HttpStatusCode.BadRequest;
        await context.Response.WriteAsync(report.Status.ToString());
    }
});

app.MapHealthChecks("/diag", new HealthCheckOptions
{
    ResponseWriter = async (context, report) =>
    {
        context.Response.ContentType = "application/json";
        var result = JsonConvert.SerializeObject(new
        {
            status = report.Status.ToString(),
            checks = report.Entries.Select(e => new { name = e.Key, status = e.Value.Status.ToString() })
        });
        await context.Response.WriteAsync(result);
    }
});
```

DB and Redis health check classes:
```csharp
public class DatabaseHealthCheck(ILogger<DatabaseHealthCheck> logger, PrimaryDbContext dbContext) : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken ct = default)
    {
        try
        {
            await dbContext.Database.CanConnectAsync(ct);
            return HealthCheckResult.Healthy();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Database health check failed");
            return HealthCheckResult.Unhealthy();
        }
    }
}

public class RedisCachingHealthCheck(ILogger<RedisCachingHealthCheck> logger, IRedisCaching redisCaching) : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken ct = default)
    {
        try
        {
            var result = await redisCaching.Healthy();
            return result ? HealthCheckResult.Healthy() : HealthCheckResult.Unhealthy();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Redis health check failed");
            return HealthCheckResult.Unhealthy();
        }
    }
}
```

## Rules

- Follow the exact pattern of existing health checks (EKycApiHealthCheck, RiskAssessmentClientHealthCheck)
- Always use `KycHealthCheckResponse` from `DipChip.AppCommon.Data.Common`
- Always use `Constants.Healthy` / `Constants.Unhealthy` for comparison
- Always tag with `"diagnostics"`
- Health check endpoint is always `/hc` unless specified otherwise
- `/hc` returns 200 when healthy, 400 when unhealthy
- `/diag` returns JSON with per-check breakdown
- Docker HEALTHCHECK should use `/hc`
- Add `using DipChip.AppCommon.Data.Common;` to client if not present
