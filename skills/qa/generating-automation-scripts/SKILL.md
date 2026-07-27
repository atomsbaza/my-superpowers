---
name: generating-automation-scripts
description: >
  Generates xUnit + Playwright E2E tests and xUnit + Testcontainers integration
  tests for .NET projects. Creates Page Object Model classes, test fixtures,
  Testcontainers WebApplicationFactory setup, and Bogus test data factories.
  Use when manual test cases or BDD scenarios need to be automated, or when
  coverage gaps need automation scripts. Trigger keywords: generate test code,
  automation script, Playwright test, xUnit test, integration test,
  Testcontainers, page object model, automate test cases, write test class,
  automation framework, test automation.
---

## Purpose

Generate runnable, maintainable C# automation code from test cases or gap analysis. Every generated test follows the AAA pattern, uses Page Object Model for UI, and has deterministic test data via Bogus seeds.

## Input

- `.qa-workflow-state.json` to determine source (manual test cases, gap report, or BDD scenarios)
- Source code files to test (read before generating to match existing patterns)
- Direct user instruction specifying what to automate

## Pre-flight

Before generating any code, read:
1. Existing test project `.csproj` files to identify installed packages and target framework
2. Any existing test base classes or fixtures to match patterns
3. Source code being tested to understand method signatures and return types

## Test Type Decision

| Scenario Type | Test Layer | Framework |
|---|---|---|
| Browser interaction, UI flow | E2E | Playwright + xUnit (`PageTest`) |
| HTTP API, database, external service | Integration | xUnit + Testcontainers + WebApplicationFactory |
| Pure C# logic, no I/O | Unit | xUnit + Moq/NSubstitute |

## E2E Tests: Page Object Model Pattern

### Directory Structure
```
tests/E2E/
├── Pages/           ← POM classes (locators + actions, no assertions)
├── Tests/           ← xUnit test classes (assertions only, no raw locators)
├── Fixtures/        ← shared browser state (e.g. pre-authenticated context)
└── TestData/        ← Bogus factories
```

### POM Class Template
```csharp
// tests/E2E/Pages/LoginPage.cs
namespace MyApp.Tests.E2E.Pages;

public sealed class LoginPage(IPage page)
{
    // Locators — always use data-testid where possible; fallback to role/text
    private readonly ILocator _emailInput    = page.Locator("[data-testid='email']");
    private readonly ILocator _passwordInput = page.Locator("[data-testid='password']");
    private readonly ILocator _submitButton  = page.Locator("[data-testid='submit']");
    private readonly ILocator _errorMessage  = page.Locator("[data-testid='error-msg']");

    public async Task LoginAsync(string email, string password)
    {
        await _emailInput.FillAsync(email);
        await _passwordInput.FillAsync(password);
        await _submitButton.ClickAsync();
    }

    public Task<string?> GetErrorMessageAsync() =>
        _errorMessage.TextContentAsync();

    public async Task WaitForNavigationAsync() =>
        await page.WaitForLoadStateAsync(LoadState.NetworkIdle);
}
```

### E2E Test Class Template
```csharp
// tests/E2E/Tests/LoginTests.cs
using Microsoft.Playwright.Xunit;

namespace MyApp.Tests.E2E;

public class LoginTests : PageTest
{
    [Fact]
    public async Task Login_WithValidCredentials_RedirectsToDashboard()
    {
        // Arrange
        var loginPage = new LoginPage(Page);
        await Page.GotoAsync("https://localhost:5001/login");

        // Act
        await loginPage.LoginAsync("user@test.com", "ValidPass1!");
        await loginPage.WaitForNavigationAsync();

        // Assert
        await Expect(Page).ToHaveURLAsync("**/dashboard");
    }

    [Theory]
    [InlineData("wrong@test.com",   "ValidPass1!",  "Invalid email or password")]
    [InlineData("user@test.com",    "wrongpass",    "Invalid email or password")]
    [InlineData("",                 "ValidPass1!",  "Email is required")]
    [InlineData("user@test.com",    "",             "Password is required")]
    public async Task Login_WithInvalidCredentials_ShowsError(
        string email, string password, string expectedError)
    {
        // Arrange
        var loginPage = new LoginPage(Page);
        await Page.GotoAsync("https://localhost:5001/login");

        // Act
        await loginPage.LoginAsync(email, password);

        // Assert
        var error = await loginPage.GetErrorMessageAsync();
        error.Should().Be(expectedError);
        await Expect(Page).ToHaveURLAsync("**/login");
    }
}
```

### Playwright `.runsettings` for Parallel Execution
```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <xUnit>
    <MaxParallelThreads>4</MaxParallelThreads>
  </xUnit>
  <Playwright>
    <BrowserName>chromium</BrowserName>
    <LaunchOptions>
      <Headless>true</Headless>
    </LaunchOptions>
  </Playwright>
</RunSettings>
```

## Integration Tests: Testcontainers Pattern

### OceanBase Container Fixture

**Use `ContainerBuilder` with `oceanbase/oceanbase-ce` — NOT `MySqlBuilder` for OceanBase-specific behavior.**

```csharp
// tests/Integration/Fixtures/OceanBaseFixture.cs
namespace MyApp.Tests.Integration.Fixtures;

public sealed class OceanBaseFixture : IAsyncLifetime
{
    // Real OceanBase container — required for partition tests
    private readonly IContainer _container = new ContainerBuilder()
        .WithImage("oceanbase/oceanbase-ce:4.2.2")
        .WithPortBinding(2881, assignRandomHostPort: true)
        .WithEnvironment("OB_ROOT_PASSWORD", "Test_Password_123!")
        .WithWaitStrategy(Wait.ForUnixContainer()
            .UntilPortIsAvailable(2881)
            .UntilMessageIsLogged("boot success!"))
        .Build();

    public string ConnectionString { get; private set; } = string.Empty;

    public async Task InitializeAsync()
    {
        await _container.StartAsync();
        var port = _container.GetMappedPublicPort(2881);
        ConnectionString =
            $"Server=localhost;Port={port};Database=testdb;" +
            $"User=root@test#myapp;Password=Test_Password_123!;" +
            $"CharSet=utf8mb4;Collation=utf8mb4_unicode_ci;SslMode=None;" +
            $"MaximumPoolSize=10;DefaultCommandTimeout=60;";
    }

    public async Task DisposeAsync() => await _container.DisposeAsync();
}

// For CRUD-only tests (no partition behavior) — faster startup:
public sealed class MySqlProxyFixture : IAsyncLifetime
{
    private readonly MySqlContainer _container = new MySqlBuilder()
        .WithImage("mysql:8.0")
        .WithDatabase("testdb")
        .Build();

    public string ConnectionString => _container.GetConnectionString() + "CharSet=utf8mb4;";

    public async Task InitializeAsync() => await _container.StartAsync();
    public async Task DisposeAsync() => await _container.DisposeAsync();
}

[CollectionDefinition("OceanBase")]
public class OceanBaseCollection : ICollectionFixture<OceanBaseFixture> { }

[CollectionDefinition("MySqlProxy")]
public class MySqlProxyCollection : ICollectionFixture<MySqlProxyFixture> { }
```

### Integration Test with WebApplicationFactory
```csharp
// tests/Integration/OrderApiTests.cs
[Collection("OceanBase")]
public class OrderApiTests(OceanBaseFixture db)
{
    [Fact]
    public async Task CreateOrder_WithValidRequest_PersistsAndReturns201()
    {
        // Arrange — build app with test DB
        await using var factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(b => b.ConfigureServices(services =>
            {
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(o =>
                    o.UseMySql(db.ConnectionString,
                        new MySqlServerVersion(new Version(8, 0, 29)),
                        m => m.CharSet(CharSet.Utf8Mb4)));
            }));

        // Apply migrations
        using (var scope = factory.Services.CreateScope())
        {
            var ctx = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            await ctx.Database.MigrateAsync();
        }

        var client = factory.CreateClient();
        var order = TestDataFactory.OrderFaker().Generate();

        // Act
        var response = await client.PostAsJsonAsync("/api/v1/orders", order);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var result = await response.Content.ReadFromJsonAsync<OrderDto>();
        result!.Id.Should().NotBeEmpty();
        result.CustomerId.Should().Be(order.CustomerId);
    }

    [Fact]
    public async Task CreateOrder_WithMissingCustomerId_Returns400()
    {
        await using var factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(b => b.ConfigureServices(services =>
            {
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(o =>
                    o.UseMySql(db.ConnectionString,
                        new MySqlServerVersion(new Version(8, 0, 29)),
                        m => m.CharSet(CharSet.Utf8Mb4)));
            }));

        var client = factory.CreateClient();
        var response = await client.PostAsJsonAsync("/api/v1/orders", new { });
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }
}
```

## Test Data Factory (Bogus)

```csharp
// tests/Shared/TestDataFactory.cs
using Bogus;

public static class TestDataFactory
{
    // Always use a fixed seed for CI reproducibility
    public static Faker<CreateOrderDto> OrderFaker(int seed = 42) =>
        new Faker<CreateOrderDto>()
            .UseSeed(seed)
            .RuleFor(o => o.CustomerId, f => f.Random.Guid())
            .RuleFor(o => o.ProductId, f => f.Random.Int(1, 1000))
            .RuleFor(o => o.Quantity, f => f.Random.Int(1, 99))
            .RuleFor(o => o.Notes, f => f.Lorem.Sentence()
                // OceanBase utf8mb4: strip surrogate pairs (emoji outside BMP)
                .Where(c => !char.IsSurrogate(c))
                .Aggregate("", (s, c) => s + c));

    public static Faker<User> UserFaker(int seed = 42) =>
        new Faker<User>()
            .UseSeed(seed)
            .RuleFor(u => u.Id, f => f.Random.Guid())
            .RuleFor(u => u.Email, f => f.Internet.Email())
            .RuleFor(u => u.Name, f => f.Name.FullName());
}
```

## Unit Test Template

```csharp
// tests/Unit/OrderHandlerTests.cs
public sealed class CreateOrderHandlerTests
{
    private readonly Mock<IOrderRepository> _repo = new();
    private readonly Mock<ILogger<CreateOrderHandler>> _logger = new();
    private readonly CreateOrderHandler _handler;

    public CreateOrderHandlerTests() =>
        _handler = new CreateOrderHandler(_repo.Object, _logger.Object);

    [Fact]
    public async Task Handle_WithValidCommand_CreatesAndReturnsOrder()
    {
        // Arrange
        var command = new CreateOrderCommand(CustomerId: Guid.NewGuid());
        _repo.Setup(r => r.AddAsync(It.IsAny<OrderHeader>(), It.IsAny<CancellationToken>()))
             .Returns(Task.CompletedTask);

        // Act
        var result = await _handler.Handle(command, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result.CustomerId.Should().Be(command.CustomerId);
        _repo.Verify(r => r.AddAsync(It.IsAny<OrderHeader>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Handle_WhenRepositoryThrows_PropagatesException()
    {
        // Arrange
        var command = new CreateOrderCommand(Guid.NewGuid());
        _repo.Setup(r => r.AddAsync(It.IsAny<OrderHeader>(), It.IsAny<CancellationToken>()))
             .ThrowsAsync(new InvalidOperationException("DB failure"));

        // Act & Assert
        await _handler
            .Invoking(h => h.Handle(command, CancellationToken.None))
            .Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("DB failure");
    }
}
```

## Output

- Write all files to correct test project paths
- Print a summary table: file path, test type, test count
- Update `.qa-workflow-state.json`:
```json
{
  "stage": "automation_scripts_generated",
  "test_files_created": ["tests/E2E/Tests/LoginTests.cs"],
  "pom_files_created": ["tests/E2E/Pages/LoginPage.cs"],
  "fixture_files_created": ["tests/Integration/Fixtures/OceanBaseFixture.cs"],
  "error": null
}
```
