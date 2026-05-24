---
name: prototype
description: "Build a throwaway prototype to answer a design question before committing to production code. Use when exploring designs, sanity-checking models, or trying multiple approaches."
---


# Prototype

Build a throwaway prototype to answer a design question before committing to production code.

## When to Use

- User wants to explore a design before committing
- Sanity-check a data model, state machine, or workflow
- Try multiple approaches to see which fits
- Says "prototype this", "let me play with it", "try a few designs"

## Pick a Branch

Identify the question being answered:

- **"Does this logic/state model feel right?"** → **Logic prototype**: Build a minimal console app that exercises the state machine or business logic through hard-to-reason-about cases.

- **"What should the API contract look like?"** → **API prototype**: Scaffold a minimal controller with hardcoded responses so the consumer can validate the shape.

- **"How should these services interact?"** → **Integration prototype**: Minimal handler + fake dependencies to prove the flow works.

## Rules

1. **Throwaway and clearly marked.** Place in a `_prototype/` folder or name files with `Prototype` prefix. Never in production paths.

2. **One command to run.** `dotnet run` from the prototype folder. No external dependencies required.

3. **No persistence by default.** State lives in memory. If the question involves DB, use EF Core InMemory.

4. **Skip the polish.** No tests, no error handling beyond what makes it runnable, no abstractions. Learn fast, then delete.

5. **Surface the state.** After every action, print/log the full relevant state so the user sees what changed.

6. **Delete or absorb when done.** When the question is answered, either delete the prototype or fold the validated decision into real code.

## Output

When the prototype has answered its question, capture:
- The **question** it was answering
- The **answer/decision** reached
- Any **constraints discovered** during prototyping

Record this in the relevant spec's design.md or as a comment in the issue.

## Example: Logic Prototype

```csharp
// _prototype/RiskScoringPrototype/Program.cs
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Hardcoded scenarios to exercise
var scenarios = new[]
{
    new { Capital = 500000m, BizType = "Restaurant", Expected = "Medium" },
    new { Capital = 50000000m, BizType = "Casino", Expected = "High" },
};

foreach (var s in scenarios)
{
    var result = CalculateRisk(s.Capital, s.BizType);
    Console.WriteLine($"Capital={s.Capital}, BizType={s.BizType} → Risk={result} (expected: {s.Expected})");
}
```

## Example: API Prototype

```csharp
// _prototype/NewEndpointPrototype/Program.cs
app.MapPost("/api/v1/business/new-feature", () =>
    Results.Ok(new { applicationNumber = "APP-2026-000001", status = 5 }));

// Run and hit with curl/Postman to validate contract with consumer
```
