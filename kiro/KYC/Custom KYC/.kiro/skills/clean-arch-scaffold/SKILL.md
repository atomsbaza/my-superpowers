---
name: clean-arch-scaffold
description: 'Scaffold a new Clean Architecture .NET project with Domain/Application/Infrastructure/API layers. Use when creating a new microservice from scratch.'
---

# Clean Architecture Scaffold

## When to Use
- Creating a brand new microservice
- Setting up project structure for a new bounded context

## Steps

1. **Create solution and projects**:
```bash
dotnet new sln -n {{ServiceName}}
dotnet new webapi -n {{ServiceName}}.API -o src/{{ServiceName}}.API
dotnet new classlib -n {{ServiceName}}.Application -o src/{{ServiceName}}.Application
dotnet new classlib -n {{ServiceName}}.Domain -o src/{{ServiceName}}.Domain
dotnet new classlib -n {{ServiceName}}.Infrastructure -o src/{{ServiceName}}.Infrastructure
dotnet new xunit -n {{ServiceName}}.Tests -o tests/{{ServiceName}}.Tests

dotnet sln add src/{{ServiceName}}.API
dotnet sln add src/{{ServiceName}}.Application
dotnet sln add src/{{ServiceName}}.Domain
dotnet sln add src/{{ServiceName}}.Infrastructure
dotnet sln add tests/{{ServiceName}}.Tests
```

2. **Set up references** (dependency rule):
```bash
# API → Application, Infrastructure (DI only)
dotnet add src/{{ServiceName}}.API reference src/{{ServiceName}}.Application
dotnet add src/{{ServiceName}}.API reference src/{{ServiceName}}.Infrastructure

# Application → Domain
dotnet add src/{{ServiceName}}.Application reference src/{{ServiceName}}.Domain

# Infrastructure → Application, Domain
dotnet add src/{{ServiceName}}.Infrastructure reference src/{{ServiceName}}.Application
dotnet add src/{{ServiceName}}.Infrastructure reference src/{{ServiceName}}.Domain

# Tests → all
dotnet add tests/{{ServiceName}}.Tests reference src/{{ServiceName}}.Application
dotnet add tests/{{ServiceName}}.Tests reference src/{{ServiceName}}.Infrastructure
```

3. **Domain layer** — entities, repository interfaces, constants:
```
Domain/
├── Entities/
├── Repository/IBaseRepository.cs
├── Constants/
└── ObjectValue/
```

4. **Application layer** — handlers, validation, interfaces:
```
Application/
├── Handler/V1/
├── Interface/
├── Exceptions/ (BadRequest, Forbidden, Unauthorized implementing IAppException)
├── GuardAgainst/
└── ServiceCollectionExtensions.cs
```

5. **Infrastructure layer** — EF Core, repos, clients:
```
Infrastructure/
├── Context/PrimaryDbContext.cs, ReplicaDbContext.cs
├── Data/EntityConfiguration/
├── Repository/BaseRepository.cs
├── Setting/
├── HealthCheck/
└── ServiceCollectionExtensions.cs
```

6. **API layer** — controllers, middleware, Program.cs:
```
API/
├── Controllers/
├── Middleware/ExceptionHandlingMiddleware.cs, RequestLoggingMiddleware.cs
└── Program.cs
```

## Key Packages

| .NET 8+ | .NET 6 |
|---------|--------|
| DevII.Authentication | Issuing.Authentication |
| DevII.Caching | Issuing.Caching |
| DevII.SecretsManager | Issuing.SecretsManager |
| DevII.Logging | Issuing.Logging |

Common: MediatR, FluentValidation, Pomelo.EntityFrameworkCore.MySql, Serilog, xUnit, FakeItEasy

## Validation
- [ ] Domain has zero project references
- [ ] Application does NOT reference Infrastructure
- [ ] Solution builds: `dotnet build`
- [ ] Health check at `/hc` responds 200
- [ ] ExceptionHandlingMiddleware catches IAppException
- [ ] .kiro/steering/ files created (tech.md, structure.md, guardrails.md)
