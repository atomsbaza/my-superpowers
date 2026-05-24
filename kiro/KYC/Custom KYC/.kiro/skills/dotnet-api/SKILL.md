---
name: dotnet-api
description: 'ASP.NET Core Web API + Entity Framework Core patterns for Clean Architecture. Covers controllers, middleware, EF Core DbContext, repository pattern, Fluent API configuration, auth, caching, and performance best practices.'
---

# .NET API Development (ASP.NET Core + EF Core)

You are an expert in ASP.NET Core Web API and Entity Framework Core development following Clean Architecture.

## Controller Design

- Keep controllers thin — only `mediator.Send()` and return result
- Use `[ApiController]` and `[Route]` attributes
- Return appropriate status codes (Ok, NotFound, NoContent, CreatedAt)
- Use `[Authorize]` by default, `[AllowAnonymous]` only for public endpoints
- Use API versioning: `[ApiVersion(1)]`, `[Route("api/v{version:apiVersion}")]`

## Middleware Order

1. Exception handling
2. Request logging
3. HTTPS redirection
4. Authentication
5. Authorization
6. Custom middleware
7. Endpoints

## EF Core — DbContext

- Use Primary/Replica pattern: `PrimaryDbContext` for writes, `ReplicaDbContext` for reads
- Use `QueryTrackingBehavior.NoTracking` by default
- Apply configurations from assembly: `modelBuilder.ApplyConfigurationsFromAssembly()`
- Use interceptors for logging/auditing

## EF Core — Entity Configuration

```csharp
public class EntityConfig : IEntityTypeConfiguration<MyEntity>
{
    public void Configure(EntityTypeBuilder<MyEntity> entity)
    {
        entity.ToTable("TableName");
        entity.HasKey(e => e.Id).HasName("PRIMARY");
        entity.Property(e => e.Id).HasColumnType("bigint(20)").HasColumnName("ID");
    }
}
```

## Repository Pattern

- `IBaseRepository<T>` with GetAsync, GetPrimaryAsync, AddAsync, UpdateAsync, DeleteAsync
- Read from replica, write to primary
- Use `LogStartProcessing()` / `LogEndProcessing()` for timing
- Never expose `IQueryable` or `DbContext` outside Infrastructure

## Performance

- Use `AsNoTracking()` for read-only queries
- Use `Select()` projection to retrieve only needed fields
- Avoid N+1 queries — use `Include()` or explicit joins
- Use compiled queries for hot paths
- Batch `SaveChangesAsync()` calls (e.g. `UpdateRange` for bulk updates)

## Validation

- Use FluentValidation with MediatR `ValidationBehavior` pipeline
- Validate in the pipeline, not in controllers
- `CascadeMode.Stop` for early exit on first failure

## Error Handling

- Throw typed exceptions (BadRequest, Forbidden, Unauthorized, InternalServerError)
- All exceptions implement `IAppException`
- Caught by `ExceptionHandlingMiddleware` — never handle in controllers

## Caching

- Use `IDistributedCache` (Redis) for shared state
- Cache read-heavy, rarely-changing data
- Use cache keys from constants class

## Configuration

- Use Options pattern: `configuration.GetSection("X").Get<XSetting>()`
- Register settings as singletons
- Never hardcode connection strings or secrets

### Secrets Manager (DevII.SecretsManager)

Projects use `AddSecretsManagerWithCommonAsync()` which loads two secrets:
- **App secret** (`APP_SECRET_MANAGER` env var) — project-specific config
- **Common secret** (`COMMON_SECRET_MANAGER` env var) — shared across KYC services

The common secret provides database connection strings at:
```
Database:PrimaryConnection
Database:ReplicaConnection
Database:Version
Database:TimeoutInSeconds
Database:AesKey
```

**Always read DB config from `Database:` section** — never use `GetConnectionString()`:
```csharp
// ✅ Correct — matches common secret structure
var primary = configuration["Database:PrimaryConnection"];

// ❌ Wrong — looks for ConnectionStrings:Primary which doesn't exist in secrets
var primary = configuration.GetConnectionString("Primary");
```

For Serilog override to stick regardless of secrets config ordering, set it in code:
```csharp
builder.Services.AddSerilog(opts =>
{
    opts.ReadFrom.Configuration(builder.Configuration);
    opts.MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Error);
});
```

## Authentication & Authorization

- Use `[Authorize]` by default on controllers
- `[AllowAnonymous]` only for public endpoints (health checks, callbacks from external systems)
- For internal service-to-service: HMAC auth via `Issuing.Authentication` / `DevII.Authentication`
- For external partner APIs: JWT Bearer or custom token validation
- Policy-based authorization for role-specific endpoints:
  ```csharp
  options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
  ```

## Swagger/OpenAPI

```csharp
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "My API", Version = "v1" });
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Type = SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT"
    });
});
```
