---
name: writing-tests
description: >
  Writes comprehensive test suites for C# .NET code using xUnit, Moq or
  NSubstitute, and Testcontainers. Produces unit tests, integration tests,
  and contract tests. Use when the user asks to write tests, generate unit
  tests, add integration tests, create test coverage, use xUnit or NUnit,
  test a service, test an endpoint, or verify behavior with tests.
  For OceanBase integration tests, generates Testcontainers setup using
  MySQL container image with OceanBase-compatible schema.
---

## Purpose

Generate tests that actually catch regressions. Tests are first-class code: same quality standards as production code. No flaky sleeps, no testing internals, no tests that pass by construction.

## Input

- Source code files to test (read them before generating tests)
- `workflow-state.json` → `implementation.files_created` for context
- Direct specification of what to test

Always read the source code before writing tests. Tests must reflect actual implementation, not assumptions.

## Testing Principles

1. Test behavior through public interfaces, not private internals.
2. One assertion concept per test (can have multiple `Assert` calls for the same concept).
3. AAA structure: Arrange / Act / Assert with a blank line between sections.
4. Tests must be deterministic — no `Thread.Sleep`, no `DateTime.Now`, no random data without a fixed seed.
5. Mock at stable boundaries (interfaces), not arbitrary internals.
6. Integration tests hit real infrastructure (Testcontainers) — no in-memory database for persistence tests.

## Naming Convention

`MethodName_Scenario_ExpectedBehavior`

Examples:
- `PlaceOrder_WithValidCustomer_ReturnsCreatedOrder`
- `PlaceOrder_WithInvalidCustomerId_ThrowsValidationException`
- `GetOrder_WhenOrderNotFound_ReturnsNull`
- `ProcessOutbox_WhenMessageFails_MarksErrorAndContinues`

## Unit Tests (xUnit + Moq/NSubstitute)

```csharp
public sealed class CreateOrderHandlerTests
{
    private readonly Mock<IOrderRepository> _repositoryMock;
    private readonly Mock<ILogger<CreateOrderHandler>> _loggerMock;
    private readonly CreateOrderHandler _handler;

    public CreateOrderHandlerTests()
    {
        _repositoryMock = new Mock<IOrderRepository>();
        _loggerMock = new Mock<ILogger<CreateOrderHandler>>();
        _handler = new CreateOrderHandler(_repositoryMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task Handle_WithValidCommand_CreatesOrderAndReturnsDto()
    {
        // Arrange
        var customerId = Guid.NewGuid();
        var command = new CreateOrderCommand(customerId);
        _repositoryMock
            .Setup(r => r.AddAsync(It.IsAny<OrderHeader>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _handler.Handle(command, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result.CustomerId.Should().Be(customerId);
        _repositoryMock.Verify(r => r.AddAsync(It.IsAny<OrderHeader>(), It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task Handle_RepositoryThrows_PropagatesException()
    {
        // Arrange
        var command = new CreateOrderCommand(Guid.NewGuid());
        _repositoryMock
            .Setup(r => r.AddAsync(It.IsAny<OrderHeader>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidOperationException("DB unavailable"));

        // Act & Assert
        await _handler.Invoking(h => h.Handle(command, CancellationToken.None))
            .Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("DB unavailable");
    }
}
```

## Integration Tests (Testcontainers + WebApplicationFactory)

```csharp
// Shared fixture — one container per test class
public sealed class OceanBaseFixture : IAsyncLifetime
{
    private MySqlContainer _container = null!;
    public string ConnectionString { get; private set; } = string.Empty;

    public async Task InitializeAsync()
    {
        // OceanBase uses MySQL wire protocol — use MySQL image for Testcontainers
        _container = new MySqlBuilder()
            .WithImage("mysql:8.0")
            .WithDatabase("testdb")
            .WithUsername("testuser")
            .WithPassword("testpassword")
            .Build();

        await _container.StartAsync();

        ConnectionString = _container.GetConnectionString() + ";CharSet=utf8mb4;";

        // Apply schema (run EF Core migrations or seed SQL)
        await ApplySchemaAsync();
    }

    private async Task ApplySchemaAsync()
    {
        using var scope = /* get DI scope */;
        var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await context.Database.MigrateAsync();
    }

    public async Task DisposeAsync() => await _container.DisposeAsync();
}

// Integration test using the fixture
public sealed class OrderRepositoryTests : IClassFixture<OceanBaseFixture>
{
    private readonly OceanBaseFixture _fixture;

    public OrderRepositoryTests(OceanBaseFixture fixture) => _fixture = fixture;

    [Fact]
    public async Task AddAsync_WithValidOrder_PersistsToDatabase()
    {
        // Arrange
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseMySql(_fixture.ConnectionString, new MySqlServerVersion(new Version(8, 0, 29)),
                o => o.CharSet(CharSet.Utf8Mb4))
            .Options;

        await using var context = new AppDbContext(options);
        var repository = new OrderRepository(context);
        var order = OrderHeader.Create(Guid.NewGuid());

        // Act
        await repository.AddAsync(order, CancellationToken.None);

        // Assert
        var stored = await context.Orders.FindAsync(order.Id);
        stored.Should().NotBeNull();
        stored!.CustomerId.Should().Be(order.CustomerId);
    }
}
```

## API Integration Tests (WebApplicationFactory)

```csharp
public sealed class OrderEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrderEndpointTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real DB with Testcontainers connection string
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseMySql(TestConnectionString,
                        new MySqlServerVersion(new Version(8, 0, 29)),
                        o => o.CharSet(CharSet.Utf8Mb4)));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task PostOrder_WithValidRequest_Returns201()
    {
        // Arrange
        var request = new { CustomerId = Guid.NewGuid() };

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var body = await response.Content.ReadFromJsonAsync<OrderDto>();
        body!.CustomerId.Should().Be(request.CustomerId);
    }

    [Fact]
    public async Task PostOrder_WithInvalidRequest_Returns400()
    {
        var response = await _client.PostAsJsonAsync("/api/v1/orders", new { });
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }
}
```

## Required Test Coverage Checklist

For each feature, generate tests covering:

- [ ] Happy path (valid input, expected output)
- [ ] Invalid/missing input (validation errors)
- [ ] Not found case (null / 404)
- [ ] Concurrency conflict (rowversion mismatch)
- [ ] Repository failure propagation (exception not swallowed)
- [ ] Cancellation (CancellationToken respected)
- [ ] Idempotency (double-submit behavior)
- [ ] Authorization boundary (unauthorized request rejected)

## Output

- Test files written to correct test project paths
- Unit tests in `tests/[Project].UnitTests/`
- Integration tests in `tests/[Project].IntegrationTests/`
- Summary of test count per category

Update `workflow-state.json`:
```json
{
  "stage": "tested",
  "tests": {
    "unit_test_files": ["path/to/test.cs"],
    "integration_test_files": ["path/to/test.cs"],
    "coverage_checklist": "complete"
  }
}
```
