---
name: testing
description: 'Testing skills bundle: TDD workflow, xUnit best practices, and WebApplicationFactory integration tests. Pairs with: test-generator subagent.'
---

# Testing

Three sections:
1. **TDD workflow** — red-green-refactor loop for new features and bug fixes
2. **xUnit unit tests** — test structure, assertions, data-driven tests
3. **Integration tests** — WebApplicationFactory with InMemory DB and faked external services

---

## 1. TDD Workflow

### Philosophy

**Tests verify behavior through public interfaces, not implementation details.** Code can change entirely; tests shouldn't break unless behavior changes.

### Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.**

```
WRONG (horizontal):
  RED: test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

### Workflow

1. **Plan** — Confirm interface changes, list behaviors to test, get user approval
2. **Tracer bullet** — Write ONE test for ONE behavior → fails → write minimal code → passes
3. **Loop** — For each behavior: RED → GREEN
4. **Refactor** — Only when GREEN. Never refactor while RED.

### Per-Cycle Checklist

- [ ] Test describes behavior, not implementation
- [ ] Test uses public interface only
- [ ] Test would survive internal refactor
- [ ] Code is minimal for this test
- [ ] No speculative features added

---

## 2. xUnit Best Practices

### Project Setup

- Test project naming: `[ProjectName].Tests` or `[ProjectName].Test.{Unit|Integration}`
- Required packages: `Microsoft.NET.Test.Sdk`, `xunit`, `xunit.runner.visualstudio`
- Add `FakeItEasy` and `FluentAssertions` for KYC platform

### Test Structure

- Use `[Fact]` for simple tests, `[Theory]` + `[InlineData]` for data-driven
- Constructor for setup, `IDisposable.Dispose()` for teardown
- `IClassFixture<T>` for shared context within a class
- `ICollectionFixture<T>` for shared context across multiple classes
- Follow Arrange/Act/Assert (AAA) pattern

### Naming Convention

```
When_{Scenario}_Then_{ExpectedResult}
```

Examples:
- `When_ValidRequest_Then_ReturnsSuccess`
- `When_DuplicateRefId_Then_ReturnsConflict`
- `When_NullDopaResponse_Then_RetriesUpToThreeTimes`

### Assertions

- `Assert.Equal` for value equality, `Assert.Same` for reference equality
- `Assert.Throws<T>` / `Assert.ThrowsAsync<T>` for exceptions
- Prefer FluentAssertions: `result.Should().Be(expected)`, `action.Should().Throw<T>()`

### Mocking with FakeItEasy

```csharp
var fakeRepo = A.Fake<IKycApplicationRepository>();
A.CallTo(() => fakeRepo.GetById(123)).Returns(new KycApplication { Id = 123 });
// ... act ...
A.CallTo(() => fakeRepo.Save(A<KycApplication>._)).MustHaveHappenedOnceExactly();
```

### Data-Driven Tests

```csharp
[Theory]
[InlineData(1, true)]
[InlineData(0, false)]
public void When_StatusCode_Then_IsValid(int code, bool expected) { ... }

[Theory]
[MemberData(nameof(GetTestData))]
public void When_X_Then_Y(int input) { ... }
public static IEnumerable<object[]> GetTestData() => ...;
```

### Test Organization

- Group by feature/component
- Use `[Trait("Category", "Integration")]` to filter: `dotnet test --filter Category=Integration`
- Keep tests independent and idempotent

---

## 3. Integration Tests (WebApplicationFactory)

Tests the full HTTP pipeline including middleware, routing, model binding, response serialization.

### What to Fake vs Keep Real

| Layer | Integration Test | Why |
|-------|-----------------|-----|
| Controller/Routing | ✅ Real | Verify routing, model binding, auth |
| MediatR Pipeline | ✅ Real | Verify handler dispatch, validation |
| FluentValidation | ✅ Real | Verify request validation |
| Repository + EF Core | ✅ Real (InMemory) | Verify queries, transactions |
| External HTTP (DOPA, DBD) | ❌ Fake | Unreliable, slow, costs money |
| AWS S3/SQS | ❌ Fake | Infrastructure dependency |
| Redis | ❌ Fake or skip | Use `SKIP_REDIS=true` env var |

### Test Pattern

```csharp
public class SaveIndividualIntegrationTest : IClassFixture<CustomWebApplicationFactory>
{
    private readonly HttpClient _client;

    public SaveIndividualIntegrationTest(CustomWebApplicationFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task When_ValidRequest_Then_Returns200WithApplicationNumber()
    {
        var request = CreateValidRequest();
        var response = await _client.PostAsJsonAsync("/api/v1/business/save-individual-customer", request);

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var body = await response.Content.ReadFromJsonAsync<SuccessResponse>();
        body!.ApplicationNumber.Should().NotBeNullOrEmpty();
        body.Status.Should().Be(5);
    }
}
```

### CustomWebApplicationFactory

```csharp
public class CustomWebApplicationFactory : WebApplicationFactory<Program>
{
    public CustomWebApplicationFactory()
    {
        // Prevent external service connections during startup
        Environment.SetEnvironmentVariable("APP_SECRET_MANAGER", "");
        Environment.SetEnvironmentVariable("SKIP_REDIS", "true");
        Environment.SetEnvironmentVariable("AWS_ACCESS_KEY_ID", "test");
        Environment.SetEnvironmentVariable("AWS_SECRET_ACCESS_KEY", "test");
        Environment.SetEnvironmentVariable("AWS_REGION", "ap-southeast-1");
    }

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureAppConfiguration((context, config) =>
        {
            config.AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["Database:PrimaryConnection"] = "Server=localhost;Database=test",
                ["Database:ReplicaConnection"] = "Server=localhost;Database=test",
                ["Database:Version"] = "8.0.0",
                ["Database:TimeoutInSeconds"] = "30",
                ["Authentication:Key"] = "test-key-for-hmac-auth-12345678",
                ["Serilog:WriteTo:0:Args:nodeUris"] = "http://localhost:9200",
            });
        });

        builder.ConfigureTestServices(services =>
        {
            // Replace DB with InMemory
            services.RemoveAll<DbContextOptions<PrimaryDbContext>>();
            services.RemoveAll<PrimaryDbContext>();
            services.AddDbContext<PrimaryDbContext>(opts =>
                opts.UseInMemoryDatabase(Guid.NewGuid().ToString()));

            services.RemoveAll<DbContextOptions<ReplicaDbContext>>();
            services.RemoveAll<ReplicaDbContext>();
            services.AddDbContext<ReplicaDbContext>(opts =>
                opts.UseInMemoryDatabase(Guid.NewGuid().ToString()));

            // Fake external services
            services.RemoveAll<IVerificationService>();
            services.AddSingleton(A.Fake<IVerificationService>());

            services.RemoveAll<ISqsPublisher>();
            services.AddSingleton(A.Fake<ISqsPublisher>());

            // Replace auth with test scheme
            services.AddAuthentication("Test")
                .AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("Test", _ => { });
        });

        builder.UseEnvironment("Development");
    }
}
```

### Test Auth Handler

```csharp
public class TestAuthHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    public TestAuthHandler(IOptionsMonitor<AuthenticationSchemeOptions> options,
        ILoggerFactory logger, UrlEncoder encoder) : base(options, logger, encoder) { }

    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        var claims = new[] { new Claim(ClaimTypes.Name, "test-user") };
        var identity = new ClaimsIdentity(claims, "Test");
        var ticket = new AuthenticationTicket(new ClaimsPrincipal(identity), "Test");
        return Task.FromResult(AuthenticateResult.Success(ticket));
    }
}
```

### Required Startup Guards

Projects need these to support integration testing:

| Guard | Where | Purpose |
|-------|-------|---------|
| `if (!string.IsNullOrEmpty(env("APP_SECRET_MANAGER")))` | `Program.cs` | Skip AWS Secrets Manager |
| `if (string.IsNullOrEmpty(env("SKIP_REDIS")))` | `ServiceCollectionExtensions.cs` | Skip Redis `AddCaching()` |
| `public partial class Program { }` | End of `Program.cs` | Expose entry point |
| `<InternalsVisibleTo>` | API `.csproj` | Allow test project to reference internal `Program` |
| `Serilog:WriteTo:0:Args:nodeUris` | InMemory config | Prevent OpenSearch URI parse error |

### File Structure

```
tests/
└── {Project}.Test.Integration/
    ├── {Project}.Test.Integration.csproj
    ├── Fixtures/
    │   └── CustomWebApplicationFactory.cs
    └── Controllers/
        └── {Controller}IntegrationTest.cs
```

### Required Packages

```xml
<PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.x" />
<PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" Version="8.0.x" />
<PackageReference Include="FakeItEasy" />
<PackageReference Include="FluentAssertions" />
```

---

## KYC Platform Conventions

- **Framework**: xUnit + FakeItEasy + FluentAssertions
- **Pattern**: Arrange/Act/Assert
- **Handler tests**: Fake repository & service interfaces, assert on response codes and side effects
- **Repository tests**: EF Core InMemory provider
- **Naming**: `When_{Scenario}_Then_{ExpectedResult}`
- **Build check**: Run `dotnet test` after each GREEN to confirm no regressions
- **Test categories**: Use `[Trait("Category", "Integration")]` to separate slow tests
