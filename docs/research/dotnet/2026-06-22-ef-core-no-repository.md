# Why You Don't Need a Repository in EF Core

Source: https://antondevtips.com/blog/why-you-dont-need-a-repository-in-ef-core  
Author: Anton Martyniuk  
Saved: 2026-06-22

---

## Core Claim

`DbContext` already implements the Repository and Unit of Work patterns. Wrapping it in a custom repository adds a layer that provides no value.

## Problems with Repositories

- **Bloat** — A `ShipmentRepository` accumulates dozens of query methods over time and becomes unmaintainable.
- **Cross-entity confusion** — Queries spanning `Shipments`, `ShipmentItems`, `Orders` have no clear home; repos end up either bloated or arbitrarily split.

## Common Justifications Refuted

| Justification | Counter |
|---|---|
| "We might switch databases" | 99% of apps never do. When they do, most EF Core code is unchanged anyway. |
| "Mocking repos makes testing easier" | Mocked repos produce fragile tests that don't reflect real query behavior. Integration tests against a real DB are better. |

## Recommended Alternatives

1. **Inject `DbContext` directly** into services/handlers — no intermediary layer.
2. **Specification Pattern** — small, composable filter classes for reusable complex queries instead of a fat repo.
3. **Testing** — EF Core InMemory provider for unit tests; real database for integration tests.

## Architecture Fit

| Style | Recommendation |
|---|---|
| N-Layered | Application layer calls `DbContext` directly |
| Clean Architecture (pragmatic) | EF Core belongs in application use cases |
| Vertical Slice | Features own both query and persistence logic |

## When Repositories Still Make Sense

- Complex queries reused across many features
- Team convention requiring consistency
- Cross-cutting concerns: caching, auditing, logging
- Wrapping external data sources or Dapper

## Takeaway for This Stack

Aligns with MediatR handler approach: inject `DbContext` directly into handlers, use Specification Pattern as the escape valve for reusable query logic. Default to no repository unless one of the exceptions above applies.
