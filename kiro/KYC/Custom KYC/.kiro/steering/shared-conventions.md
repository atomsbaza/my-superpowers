# Shared Conventions

## Service-to-Service Auth
- HMAC internal auth: X-Refer, X-Client, X-Request-Time headers + Authorization (HMAC signature from Authentication.Key)
- X-Correlation-Id for distributed tracing

## Database
- MySQL with Primary (write) + Replica (read) pattern
- EF Core via Pomelo.EntityFrameworkCore.MySql
- Stored procedures prefixed with `sp` (e.g., `spDipChipApi_XXXXX`)
- Connection strings from common secret: `Database:PrimaryConnection`, `Database:ReplicaConnection`
- **Never use `GetConnectionString()`** — always `configuration["Database:PrimaryConnection"]`
- Entity properties MUST match actual DB column names — verify with `DESCRIBE TableName` when adding new entities
- `int` value-type properties default to `0` on INSERT (useful for columns like `PIC` that need a default)

## Security
- PII fields: Always AES encrypted at rest
- Logs: Sensitive data masked (ExceptLastFour, LaserId, Name, Date, Email, All)
- Encryption/decryption configured per endpoint via JSON path rules

## Naming
- C# public members: PascalCase
- JSON serialization: camelCase (via CamelCasePropertyNamesContractResolver)
- Constants: UPPER_SNAKE_CASE or PascalCase depending on project

## Messaging
- AWS SQS for async communication between services
- Used for triggering CDD after customer save
- **QueueUrl must be full URL**: `https://sqs.{region}.amazonaws.com/{account-id}/{queue-name}`
- **Never just the queue name** — AWS SDK requires full URL, bare name causes NullReferenceException
- **Null-safe iteration**: Always `response.Messages ?? []` in consumers

### SQS Message Contracts

| Producer | Queue | Consumer | Message Shape |
|----------|-------|----------|---------------|
| kyc-partner-api | kyc-cdd-business-worker-{env} | kyc-customer-due-diligence (Batch.Business) | `{Id: long, Origin: sbyte, UpdateBy: int}` |
| identification | kyc-cdd-business-worker-{env} | kyc-customer-due-diligence (Batch.Business) | `{Id: long, Origin: sbyte, UpdateBy: int}` |

### LogOrigin Enum Values
1=AdminKYCApplicationMain, 2=AdminKYCApplicationPerson, 3=AdminExternalCddCheck, 4=EkycApi, 5=PartnerApi, 6=Batch

## Cloud
- AWS: S3 (file storage), SQS (messaging), Secrets Manager (config)
- Docker: Linux containers, multi-stage builds
- CI/CD: Jenkins pipelines

## Testing
- xUnit + FakeItEasy (or Moq) + FluentAssertions
- EF Core InMemory provider for repository tests
- Pattern: Arrange/Act/Assert with faked dependencies

### Integration Test Startup Guards

When adding WebApplicationFactory-based integration tests, these guards prevent external connections during test host startup:

| Guard | Where | Purpose |
|-------|-------|---------|
| `APP_SECRET_MANAGER=""` | Env var in factory constructor | Skip AWS Secrets Manager |
| `SKIP_REDIS="true"` | Env var in factory constructor | Skip Redis `AddCaching()` |
| `public partial class Program { }` | End of `Program.cs` | Expose entry point to WebApplicationFactory |
| `InternalsVisibleTo` | API `.csproj` | Allow test project to reference internal `Program` |
| `Serilog:WriteTo:0:Args:nodeUris` | InMemory config | Prevent OpenSearch URI parse error (`***` placeholder) |

### Integration Test Packages

```xml
<PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.x" />
<PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" Version="8.0.x" />
```

## Application Status Codes

| Value | Name | Description |
|-------|------|-------------|
| 1 | Waiting for Approval | Initial state after risk assessment |
| 2 | Approved | Application approved |
| 3 | Rejected | Application rejected |
| 4 | Terminated | Application terminated |
| 5 | Processing | Saved by Identification, awaiting CDD |
| 6 | CDD Checked | CDD screening complete |
| 7 | Risk Assessing | Risk assessment in progress |

Status flow: `5 (Processing) → 6 (CDD Checked) → 7 (Risk Assessing) → 2 (Approved) / 3 (Rejected) / 1 (Waiting for Approval if manual review needed)`

## Error Response Standard

All APIs return errors in this shape:
```json
{
  "code": "E03",
  "description": "Invalid request parameter"
}
```
Common codes across services:
- `000` — Success
- `E03` — Invalid request / validation error
- `E05` — System error
- `D01` — Data not found
- `D02` — Data mismatch

## API Versioning
- URL-segment versioning: `/api/v{version}/...`
- Never break existing versions — create new version folder for breaking changes
- Handlers versioned in folders: `Handler/V1/`, `Handlers/V2/`, etc.

## Docker
- Base image: `mcr.microsoft.com/dotnet/aspnet:{version}` (Linux)
- Build image: `mcr.microsoft.com/dotnet/sdk:{version}`
- Health check endpoint: `/hc` (ready) and `/diag` (diagnostics)

## Logging & Observability
- Serilog → OpenSearch (index: `kyc-{service-name}-{yyyy.MM}`)
- **Always set Serilog overrides in code** (not just appsettings) — secrets manager can overwrite config:
  ```csharp
  opts.MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Error);
  ```
- `IgnoreRequestLoggingPaths` in appsettings: `["hc", "diag", "favicon.ico"]`
- DevII.Observability `SuccessRateMiddleware` logs INCOMING_MESSAGE → OUTGOING_MESSAGE per request
- Correlation: `X-Correlation-Id` header flows across services, logged as `CorrelationId`
- Request tracing: `RequestId` = `{ConnectionId}:{RequestNumber}` (Kestrel-generated)

## Secrets Manager
- `AddSecretsManagerWithCommonAsync()` loads two secrets:
  - `APP_SECRET_MANAGER` env var → project-specific config
  - `COMMON_SECRET_MANAGER` env var → shared config (DB connections, encryption keys)
- Common secret provides: `Database:PrimaryConnection`, `Database:ReplicaConnection`, `Database:Version`, `Database:AesKey`
- Secrets override appsettings values — code-level config (like Serilog overrides) takes precedence


## Subagent Routing

When a task matches these patterns, delegate to the specialized subagent role:

| Trigger | Role | When |
|---------|------|------|
| "trace this request", trace ID given, "check logs" | `log-investigator` | Searching OpenSearch logs, correlating across services |
| "why is this failing", stack trace, 500 error | `bug-investigator` | Root cause analysis from Jira tickets or error logs |
| "review this PR", "scrutinize", "/scrutinize" | `compliance-reviewer` or use scrutinize skill | Code review for correctness |
| "write tests for", "add test coverage" | `test-generator` | Generating xUnit test scenarios |
| "how does X work", "trace the flow" | Use `flow-tracer` skill directly | No subagent needed — skill has instructions |
| Multi-file change across projects | `cross-project` | Contract changes spanning services |
| "optimize", "slow query", "N+1" | `performance-analyst` | Query optimization, caching strategy |
| "write the post-mortem", "document this fix" | `post-mortem` skill directly | After a debug session lands a fix |
| DB schema change needed | `db-migration` | ALTER TABLE, stored procedures, EF Core migration |
| "design the API", "what should the contract look like" | `api-contract-designer` | Request/response schemas, error codes, versioning |
| Production incident, service down, cascading failure | `incident-debugger` | Traces across services using logs + correlation IDs |
| "deploy", Dockerfile, Jenkins, env config | `devops-engineer` | Dockerfile optimization, pipelines, deployment |
| "release", changelog, deploy order | `release-coordinator` | Cross-service release planning, rollback |
| "write spec", requirements → design | `spec-writer` | Feature specification (requirements → design → tasks) |
| "document this", README, onboarding guide | `tech-writer` | API docs, READMEs, changelogs |
| "convert BRD to PRD", product requirements | `tpm-brd-to-prd` | Business requirements → product requirements |
| "design the system", architecture, data model | `sa-architect` | Technical design docs, sequence flows, failure analysis |
| "create a skill", reusable pattern | `skills-creator` | Creates SKILL.md from recurring patterns |

### Skills That Enhance Subagent Work

These skills provide patterns/templates that subagents should load when executing:

| Skill | Used by subagent | How |
|-------|-----------------|-----|
| `endpoint-scaffolding` | `api-contract-designer` | Scaffold after contract is designed |
| `testing` | `test-generator` | TDD + xUnit + WebApplicationFactory integration tests |
| `hmac-internal-auth` | `cross-project` | Auth setup for new service calls |
| `contract-change` | `cross-project` | Safe contract migration steps |
| `async-messaging` | `cross-project`, `db-migration`, `performance-analyst` | SQS publisher/consumer, BackgroundService + DLQ, Quartz jobs, async patterns |
| `docker-multistage` | `devops-engineer` | Dockerfile patterns |
| `logging-diagnostics` | `log-investigator`, `incident-debugger` | What good logging looks like |
| `pii-encryption` | `compliance-reviewer` | AES encryption patterns |
| `health-check-generator` | `devops-engineer` | Health check setup |
| `management-talk` | `release-coordinator`, `tech-writer` | Non-technical communication |
| `scrutinize` | `compliance-reviewer` | End-to-end code review |
| `post-mortem` | `bug-investigator` | After fix is landed |
| `to-issues` | `spec-writer`, `sa-architect` | Break specs into tickets |
| `improve-codebase-architecture` | `sa-architect` | Architectural refactoring |
| `flow-tracer` | `log-investigator`, `incident-debugger` | Trace request paths |
