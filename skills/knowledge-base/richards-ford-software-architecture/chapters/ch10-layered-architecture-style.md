# Chapter 10: Layered Architecture Style

## Core Idea

Layered architecture organizes code by technical responsibility, commonly presentation, business, and data access. It is familiar and useful for many applications, but its quality depends on whether layers are truly isolated and whether the resulting structure supports the characteristics the business needs.

## Frameworks Introduced

- **Open and closed layers**:
  - **Closed layer:** a request must pass through the next layer; this preserves isolation and controls change.
  - **Open layer:** callers may bypass a layer; this improves convenience but increases coupling.
- **Layers of isolation**: each layer hides implementation details from the layer above and exposes a stable contract.
- **Architecture sinkhole anti-pattern**: requests pass through layers without meaningful behavior in each one, creating ceremony and performance cost.
- **Layered architecture characteristics rating**: use the style when simplicity, team familiarity, and local transactional consistency matter more than extreme agility or independent deployment.

## Key Concepts

- **Presentation layer** — user interaction and transport concerns.
- **Business layer** — domain or application rules.
- **Persistence/data layer** — storage access and mapping.
- **Closed layer** — cannot be bypassed by a caller above it.
- **Open layer** — may be bypassed for selected calls.
- **Layer isolation** — lower layers hide implementation decisions from higher layers.
- **Architecture sinkhole** — pass-through layers that add no behavior.

## Mental Models

Use closed layers to control change. If persistence changes often, preventing presentation code from reaching it directly reduces ripple effects.

Use open layers deliberately, with documented variances. A layer bypass that solves a real performance or access issue may be justified, but repeated exceptions indicate that the topology is wrong for the characteristic.

Think of layered architecture as technical partitioning. It promotes organization around infrastructure concerns rather than business capabilities, which can make domain-driven change cross many layers.

## Anti-patterns

- **Open-everywhere layering**: layers exist only as folders while every layer calls every other layer.
- **Architecture sinkhole**: requests traverse controllers, services, managers, and repositories that merely forward data.
- **Layer inflation**: adding layers to appear more architectural without improving isolation or responsibility.
- **Business logic in presentation or data mapping**: violating the intended change boundary.

## Code Examples

A closed-layer dependency rule:

```text
Presentation -> Business -> Data

Allowed: Presentation calls Business
Allowed: Business calls Data
Rejected: Presentation calls Data directly
```

An approved variance should be recorded with the reason, affected characteristic, and fitness check.

## Reference Tables

| Characteristic | Layered architecture tendency |
|---|---|
| Simplicity | Strong |
| Team familiarity | Strong |
| Local transactions | Strong |
| Testability | Moderate to weak when layers are tightly coupled |
| Deployability | Weak for independently changing features |
| Scalability | Usually scales as a unit |
| Agility | Weak when changes cross all layers |

## Worked Example

An order application uses presentation, business, and data layers. A new tax rule changes business logic and requires one data query. The closed-layer rule keeps presentation unchanged. Later, a high-volume read path requires a cache. Instead of allowing controllers to call Redis directly, the business layer exposes a quote operation and chooses the cache internally. The characteristic—performance—is addressed while the original isolation remains intact.

## Key Takeaways

1. Layered architecture is useful when technical separation and simplicity are primary drivers.
2. Closed layers protect change; open-layer exceptions require governance.
3. Pass-through layers are an architecture sinkhole.
4. Layering does not automatically provide domain modularity, testability, or independent deployment.

## Connects To

- **Chapter 3:** coupling and connascence explain why layer bypasses spread change.
- **Chapter 8:** contrasts technical partitioning with domain partitioning.
- **Chapter 18:** compares layered architecture against styles chosen for agility or independence.

