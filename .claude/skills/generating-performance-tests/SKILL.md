---
name: generating-performance-tests
description: >
  Generates NBomber load test scenarios in C# from NFRs (non-functional
  requirements) or performance acceptance criteria. Covers steady-state load,
  spike testing, soak testing, and step-load patterns with p95/p99 assertions.
  Use when a PRD includes response time targets, throughput requirements, or
  concurrent user counts. Trigger keywords: performance test, load test,
  NBomber, stress test, soak test, spike test, response time, RPS, throughput,
  p95, p99, concurrent users, performance testing, load testing.
---

## Purpose

Generate runnable NBomber C# scenarios from NFR specifications with built-in assertions that fail CI when targets are missed.

## Input

- NFR section from requirements analysis (`qa-requirements-analysis.md` or workflow state)
- Direct user description of performance targets
- Existing API endpoints to test (read source code for routes)

If no NFRs are defined, ask: "What are the performance targets? (e.g., p95 ≤ 500ms at 100 RPS for 2 minutes)"

## NBomber vs k6

For .NET teams: **use NBomber**. It is C#-native, runs inside the test suite, and can share application code (DTOs, factories). k6 requires a separate binary and JavaScript — only use if the infra team owns performance testing independently.

## Process

### Step 1 — Extract NFRs

From requirements analysis, extract:
- **Target RPS or concurrent users** (e.g., 100 requests/second, 500 concurrent users)
- **Response time target** (e.g., p95 ≤ 500ms, p99 ≤ 1000ms)
- **Test duration** (e.g., 2 minutes steady-state, 30 minutes soak)
- **Spike pattern** (if mentioned)
- **Error rate threshold** (e.g., < 1% errors)

Default targets when not specified: p95 ≤ 500ms, p99 ≤ 1000ms, ≥ 95 RPS, < 1% error rate.

### Step 2 — Generate NBomber Scenarios

**Required NuGet packages:**
```xml
<PackageReference Include="NBomber" Version="5.5.0" />
<PackageReference Include="NBomber.Http" Version="5.5.0" />
```

#### Steady-State Load Test
```csharp
// tests/Performance/OrderApiLoadTests.cs
using NBomber.CSharp;
using NBomber.Http.CSharp;

namespace MyApp.Tests.Performance;

public class OrderApiLoadTests
{
    private const string BaseUrl = "https://localhost:5001";

    [Fact]
    public void OrderCreation_SteadyLoad_MeetsNfrTargets()
    {
        using var httpClient = new HttpClient { BaseAddress = new Uri(BaseUrl) };

        var scenario = Scenario.Create("order_creation_100rps", async context =>
        {
            var order = TestDataFactory.OrderFaker(seed: context.ScenarioInfo.ThreadNumber).Generate();
            using var request = Http.CreateRequest("POST", "/api/v1/orders")
                .WithJsonBody(order)
                .WithHeader("Authorization", $"Bearer {GetTestToken()}");

            return await Http.Send(httpClient, request);
        })
        .WithWarmUpDuration(TimeSpan.FromSeconds(15))
        .WithLoadSimulations(
            // 100 requests/second for 2 minutes
            Simulation.Inject(rate: 100,
                              interval: TimeSpan.FromSeconds(1),
                              during: TimeSpan.FromMinutes(2))
        );

        var stats = NBomberRunner
            .RegisterScenarios(scenario)
            .WithReportFolder("TestResults/Performance")
            .WithReportFormats(ReportFormat.Html, ReportFormat.Csv)
            .Run();

        // NFR Assertions
        var s = stats.ScenarioStats.First(s => s.ScenarioName == "order_creation_100rps");
        s.Ok.Latency.Percent95.Should().BeLessOrEqualTo(500,
            $"p95 was {s.Ok.Latency.Percent95}ms, NFR requires ≤500ms");
        s.Ok.Latency.Percent99.Should().BeLessOrEqualTo(1000,
            $"p99 was {s.Ok.Latency.Percent99}ms, NFR requires ≤1000ms");
        s.Ok.Request.RPS.Should().BeGreaterOrEqualTo(95,
            $"RPS was {s.Ok.Request.RPS}, NFR requires ≥95 RPS");
        s.Fail.Request.Percent.Should().BeLessOrEqualTo(1.0,
            $"Error rate was {s.Fail.Request.Percent}%, NFR requires <1%");
    }
```

#### Spike Test
```csharp
    [Fact]
    public void OrderCreation_SpikeLoad_RecoversWith200msDegradation()
    {
        using var httpClient = new HttpClient { BaseAddress = new Uri(BaseUrl) };

        var scenario = Scenario.Create("order_creation_spike", async context =>
        {
            var order = TestDataFactory.OrderFaker().Generate();
            using var request = Http.CreateRequest("POST", "/api/v1/orders")
                .WithJsonBody(order);
            return await Http.Send(httpClient, request);
        })
        .WithWarmUpDuration(TimeSpan.FromSeconds(10))
        .WithLoadSimulations(
            Simulation.Inject(rate: 50,  interval: TimeSpan.FromSeconds(1), during: TimeSpan.FromSeconds(30)),  // baseline
            Simulation.Inject(rate: 300, interval: TimeSpan.FromSeconds(1), during: TimeSpan.FromSeconds(30)),  // spike
            Simulation.Inject(rate: 50,  interval: TimeSpan.FromSeconds(1), during: TimeSpan.FromSeconds(60))   // recovery
        );

        var stats = NBomberRunner.RegisterScenarios(scenario).Run();

        // Recovery assertion: error rate returns to <1% in recovery phase
        var s = stats.ScenarioStats.First();
        s.Fail.Request.Percent.Should().BeLessOrEqualTo(5.0,
            "Spike error rate should not exceed 5% — system should shed load gracefully");
    }
```

#### Soak Test (Connection Pool / Memory Leak Detection)
```csharp
    [Fact(Skip = "Long-running — run in dedicated soak environment, not CI")]
    public void OrderApi_30MinuteSoak_NoMemoryLeakOrPoolExhaustion()
    {
        using var httpClient = new HttpClient { BaseAddress = new Uri(BaseUrl) };

        var scenario = Scenario.Create("order_soak", async context =>
        {
            var order = TestDataFactory.OrderFaker().Generate();
            using var request = Http.CreateRequest("POST", "/api/v1/orders")
                .WithJsonBody(order);
            return await Http.Send(httpClient, request);
        })
        .WithWarmUpDuration(TimeSpan.FromSeconds(30))
        .WithLoadSimulations(
            // 20 concurrent users sustained for 30 minutes
            Simulation.KeepConstant(copies: 20, during: TimeSpan.FromMinutes(30))
        );

        var stats = NBomberRunner.RegisterScenarios(scenario).Run();

        // Error rate should be stable throughout — not degrading over time
        var s = stats.ScenarioStats.First();
        s.Fail.Request.Percent.Should().BeLessOrEqualTo(1.0,
            "Soak test: error rate exceeded 1% — possible memory leak or connection pool exhaustion");
    }
}
```

### Step 3 — OceanBase Connection Pool Validation

For OceanBase-specific connection pool tests:

```csharp
[Fact]
public void OceanBasePool_UnderLoad_DoesNotExhaustConnections()
{
    // Test that MaximumPoolSize=200 setting is effective under sustained load
    // If pool exhausts, MySqlException "Timeout waiting for a connection" will appear
    using var httpClient = new HttpClient { BaseAddress = new Uri(BaseUrl) };

    var scenario = Scenario.Create("db_pool_pressure", async context =>
    {
        // Simulate concurrent DB-heavy operations
        using var request = Http.CreateRequest("GET", "/api/v1/orders?pageSize=50");
        return await Http.Send(httpClient, request);
    })
    .WithLoadSimulations(
        Simulation.KeepConstant(copies: 150, during: TimeSpan.FromMinutes(2))
    );

    var stats = NBomberRunner.RegisterScenarios(scenario).Run();
    var s = stats.ScenarioStats.First();

    // Pool exhaustion shows as 5xx errors
    s.Fail.Request.Percent.Should().BeLessOrEqualTo(0.5,
        "High 5xx rate suggests OceanBase connection pool exhaustion");
}
```

### Step 4 — Output

Write performance test files to `tests/Performance/`.

Update `.qa-workflow-state.json`:
```json
{
  "stage": "performance_tests_generated",
  "performance_test_files": ["tests/Performance/OrderApiLoadTests.cs"],
  "nfr_thresholds": {
    "p95_ms": 500,
    "p99_ms": 1000,
    "min_rps": 95,
    "max_error_rate_pct": 1.0
  },
  "error": null
}
```
