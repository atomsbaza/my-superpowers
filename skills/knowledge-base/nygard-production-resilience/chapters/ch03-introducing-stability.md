# Chapter 3: Introducing Stability

## Core Idea

Enterprise software must be deliberately cynical: expect bad things to happen, distrust dependencies and itself, and install barriers that keep faults from spreading. Stability is the prerequisite for capacity, features, and long-term improvement.

## Frameworks Introduced

- **Define stability**: A stable system remains available and useful despite ordinary failures, bad inputs, and changing conditions.
  - When to use: When a team treats uptime as the absence of crashes only.
  - How: Include hangs, resource exhaustion, partial feature loss, data integrity, recovery, and operator control.
- **Cracks propagate**: A local defect becomes an incident when coupling, shared resources, or retries transfer its effects.
  - When to use: During boundary and dependency reviews.
  - How: Trace the fault’s path through threads, pools, queues, nodes, services, and users.

## Key Concepts

- **Failure mode**: A way a component can behave incorrectly or become unavailable.
- **Propagation**: The movement or amplification of a local failure into other components.
- **Chain of failure**: A sequence where each consequence creates the conditions for the next failure.
- **Stability antipattern**: A recurring design force that creates, accelerates, or multiplies cracks.

## Mental Models

- Stability is not a feature added after functionality; it is the platform on which functionality has value.
- The first failure is often less damaging than the system’s reaction to it.
- “Impossible” events become routine when a system has enough requests and dependencies.

## Anti-patterns

- **Optimizing only the happy path**: The system performs well until a dependency or resource behaves normally-but-badly.
- **Eliminating every possible bug as the only strategy**: Bugs cannot be eliminated; the design must survive them.

## Code Examples

```text
failure at dependency
  -> bounded wait?
  -> resource released?
  -> retries limited?
  -> caller isolated?
  -> degraded response available?
  -> operator can see and act?
```

## Reference Table

| Concern | Stability question |
|---|---|
| Dependency | Can it hang, fail, return bad data, or change behavior? |
| Resource | What is finite, and what happens when it is exhausted? |
| Failure response | Does the response contain damage or amplify it? |
| Recovery | Can the system return to normal without a full restart? |

## Worked Example

Take a search service that calls inventory, pricing, and content systems. A stable design accepts that any one call may fail or slow down, sets separate deadlines, returns a partial result where valid, and exposes dependency health. An unstable design waits indefinitely, retries every error, and allows all request threads to block.

## Key Takeaways

1. Expect failure and make it survivable.
2. Find propagation paths, not just individual defects.
3. Establish stability before optimizing capacity or adding features.

## Connects To

- **Ch 4**: Catalogs common propagation forces.
- **Ch 5**: Provides patterns for stopping cracks.
- **Ch 8**: Capacity work is meaningful only after stable behavior exists.
