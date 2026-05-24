---
name: docker-multistage
description: 'Multi-stage Dockerfile for .NET services with layer caching, health checks, and minimal image size. Use when creating or optimizing a Dockerfile. Pairs with: devops-engineer subagent.'
---

# Docker Multi-Stage Build

## When to Use
- Creating a Dockerfile for a new service
- Optimizing an existing Dockerfile for build speed or image size
- Adding a worker/batch service container

## Template

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:{{DotnetVersion}} AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:{{DotnetVersion}} AS build
WORKDIR /src

# Copy csproj files first for layer caching
COPY ["src/{{Project}}.API/{{Project}}.API.csproj", "src/{{Project}}.API/"]
COPY ["src/{{Project}}.Application/{{Project}}.Application.csproj", "src/{{Project}}.Application/"]
COPY ["src/{{Project}}.Domain/{{Project}}.Domain.csproj", "src/{{Project}}.Domain/"]
COPY ["src/{{Project}}.Infrastructure/{{Project}}.Infrastructure.csproj", "src/{{Project}}.Infrastructure/"]
RUN dotnet restore "src/{{Project}}.API/{{Project}}.API.csproj"

# Copy everything and build
COPY . .
WORKDIR "/src/src/{{Project}}.API"
RUN dotnet build "{{Project}}.API.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "{{Project}}.API.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "{{Project}}.API.dll"]
```

## Worker Variant
```dockerfile
# Same as above but change the entry project:
COPY ["src/{{Project}}.Worker/{{Project}}.Worker.csproj", "src/{{Project}}.Worker/"]
ENTRYPOINT ["dotnet", "{{Project}}.Worker.dll"]
```

## Conventions
- Base image: `mcr.microsoft.com/dotnet/aspnet:{version}` (Linux)
- Build image: `mcr.microsoft.com/dotnet/sdk:{version}`
- Always use specific version tags, never `latest`
- Health check endpoint: `/hc`
- Expose port 8080
- Use `/p:UseAppHost=false` to skip native host

## .dockerignore
```
**/.git
**/bin
**/obj
**/node_modules
**/.vs
**/tests
```

## Validation
- [ ] Uses specific .NET version tag matching project's TargetFramework
- [ ] csproj files copied before source (layer caching)
- [ ] No secrets or appsettings with real values in image
- [ ] .dockerignore excludes test projects and .git
- [ ] Image builds successfully: `docker build -f src/{{Project}}.API/Dockerfile .`

## Versions
| .NET | Base Image | SDK Image |
|------|-----------|-----------|
| 6 | `mcr.microsoft.com/dotnet/aspnet:6.0` | `mcr.microsoft.com/dotnet/sdk:6.0` |
| 8 | `mcr.microsoft.com/dotnet/aspnet:8.0` | `mcr.microsoft.com/dotnet/sdk:8.0` |
| 10 | `mcr.microsoft.com/dotnet/aspnet:10.0` | `mcr.microsoft.com/dotnet/sdk:10.0` |
