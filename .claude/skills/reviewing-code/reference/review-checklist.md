# Code Review Checklist

## Correctness
- [ ] All code paths return a value or throw — no implicit null returns on non-nullable types
- [ ] Async methods always `await` or explicitly fire-and-forget with a comment explaining why
- [ ] Nullable reference types respected — no unchecked `!` bang operators without comment
- [ ] No integer overflow in arithmetic on user-controlled or large values
- [ ] Collection iteration does not modify the collection in-place (use `.ToList()` copy if needed)
- [ ] Enum switches are exhaustive or have a default that throws `ArgumentOutOfRangeException`
- [ ] Comparisons use correct equality (`.Equals` for value semantics, `==` for reference check intent)

## Error Handling
- [ ] No empty catch blocks
- [ ] No swallowed exceptions — every catch either rethrows, converts, or logs + handles
- [ ] No misleading success state — method does not return `true`/`null` when it silently failed
- [ ] Background work has logging + retry or user-visible recovery
- [ ] Multi-step operations handle partial failure or make partial state observable
- [ ] Fallback behavior is explicit and tested

## Security
- [ ] No secrets, tokens, API keys, or connection strings in source code or logs
- [ ] Secrets read from `IConfiguration` (Key Vault / Secret Manager) — never hardcoded
- [ ] User input validated at the system boundary before reaching business logic — HTTP params, route values, headers, queue payloads, file names all treated as untrusted
- [ ] SQL built with EF Core LINQ or `FromSqlInterpolated` — never `FromSqlRaw` with user string concatenation
- [ ] No PII (email, phone, name, address, national ID) in log messages
- [ ] Authorization enforced on all endpoints that mutate state or return user-specific data (`.RequireAuthorization()`)
- [ ] Resource-level authorization checked (does this user own this resource?) — not just "is authenticated"
- [ ] File paths derived from user input sanitized: `Path.GetFullPath` + prefix check against base directory
- [ ] Error responses use Problem Details (RFC 7807) — no stack traces, DB error messages, or internal paths returned to callers
- [ ] New NuGet packages pinned to specific version — no floating `Version="*"`

## .NET-Specific
- [ ] Cancellation tokens propagated on all async method signatures in service/repository layers
- [ ] `ConfigureAwait(false)` in library projects and infrastructure code
- [ ] `IDisposable` / `IAsyncDisposable` disposed via `using` declarations or explicit disposal
- [ ] No `.Result` or `.Wait()` on async calls — deadlock risk in ASP.NET context
- [ ] `ILogger` uses structured message templates: `_logger.LogInformation("Order {OrderId} created", id)` — not `$"Order {id} created"`
- [ ] HttpClient not instantiated directly in service code — injected via `IHttpClientFactory`
- [ ] Large string operations use `StringBuilder` or `string.Create` where appropriate

## Logging Standard
- [ ] Structured message templates used throughout — no string interpolation in log calls
- [ ] No PII in any log message: no email, phone, name, address, national ID
- [ ] No secrets, tokens, or connection strings in any log message
- [ ] No raw DB exception messages logged (may contain query text with data values)
- [ ] CorrelationId present in log scope at request/handler entry point
- [ ] UserId logged as opaque GUID only — never email or username
- [ ] Log level is appropriate: `Information` for normal events, `Warning` for recoverable unexpected state, `Error` for operation failures
- [ ] Outbound HTTP calls propagate `X-Correlation-Id` header via `DelegatingHandler`
- [ ] `Microsoft.EntityFrameworkCore` log level set to `Warning` (not `Information`) in production config to prevent SQL flooding

## OceanBase-Specific
- [ ] No `SELECT FOR SHARE` — use optimistic concurrency (`IsRowVersion()`)
- [ ] All GUID and string columns explicitly configured with `HasCharSet("utf8mb4")` in Fluent API
- [ ] Queries on partitioned tables include partition key in WHERE clause for pruning
- [ ] Partitioning DDL is in `migrationBuilder.Sql(...)` — not in EF Core `ToTable()` / `HasAnnotation()`
- [ ] `ServerVersion` is hardcoded `new MySqlServerVersion(new Version(8, 0, 29))` — never `AutoDetect()`
- [ ] Connection string includes `CharSet=utf8mb4`
- [ ] EF Core migration does not use `ascii` charset anywhere (search migration file for "ascii")

## Testing
- [ ] Every changed public method/endpoint has at least one test
- [ ] New failure paths have a dedicated test covering the error case
- [ ] No assertions inside `if` blocks — assertions must always execute
- [ ] No `Assert.True(true)` or other trivially passing assertions
- [ ] Integration tests use Testcontainers — not EF Core in-memory provider
- [ ] Test names follow `MethodName_Scenario_ExpectedBehavior` convention
- [ ] Tests are parallel-safe — no shared static/global state mutated across tests
- [ ] No `Thread.Sleep` or `Task.Delay` in test assertions — use proper awaiting

## Migration Checklist (Schema Changes Only)
- [ ] `Up()` includes partition DDL for new large tables via `migrationBuilder.Sql(...)`
- [ ] `Down()` removes partitioning (`REMOVE PARTITIONING`) before dropping tables
- [ ] No `ascii` charset in generated migration DDL — search for "ascii" in the migration file
- [ ] Migration is idempotent when applied to a fresh database
- [ ] Rollback of the migration does not cause data loss beyond what is expected
- [ ] Index creation uses `IF NOT EXISTS` where the migration may be re-run
