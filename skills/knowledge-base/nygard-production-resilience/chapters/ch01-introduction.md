# Chapter 1: Introduction

## Core Idea

Software design is incomplete if it describes only desired behavior. Production-ready design must also specify what the system must not do under stress: crash, hang, lose data, violate security boundaries, or turn a small fault into a company-wide outage.

## Frameworks Introduced

- **Aim for the right target**: Design for real users, real operations, real dependencies, and real change—not only the development lab or a scripted QA case.
  - When to use: During architecture, review, and readiness decisions.
  - How: List hostile inputs, partial failures, resource exhaustion, traffic impulses, operational actions, and deployment transitions.
- **Pragmatic architecture**: Prefer an architecture that is good enough for current stresses and can be changed when those stresses change.
  - When to use: When an “end-state” design is becoming rigid or over-engineered.
  - How: Keep feedback loops short, understand resource costs, and preserve local replaceability.

## Key Concepts

- **Production**: The environment where unpredictable users, dependencies, and business consequences exercise the system.
- **Quality of life**: Operational usability and predictable behavior matter as much as feature correctness.
- **Scope of the challenge**: Distributed systems amplify the number and interaction of possible failure conditions.

## Mental Models

- Think of every release as placing software in a hostile but ordinary environment.
- Ask “what must never happen?” before asking how to implement the happy path.
- Treat changeability as a quality attribute, not a future cleanup task.

## Anti-patterns

- **Lab-targeted design**: Passing known tests while ignoring production traffic, operations, and failure behavior.
- **Ivory-tower architecture**: Optimizing for a perfect final structure that cannot evolve.

## Code Examples

```text
For every dependency call:
  define a deadline
  bound resource consumption
  define failure/degraded behavior
  expose the result to operators
```

## Reference Table

| Question | Weak answer | Production-oriented answer |
|---|---|---|
| What does “works” mean? | The test case passes | The feature behaves usefully under stress and partial failure |
| What is architecture? | Components and APIs | Components, failure boundaries, operating model, and change path |
| When is the system born? | When coding starts | When users and operators exercise it in production |

## Worked Example

Reframe a checkout design review. Instead of checking only that a valid payment succeeds, ask what happens when the payment provider is slow, returns duplicate responses, loses the connection after charging, or is unavailable during a traffic spike. The review target becomes a bounded, observable transaction with explicit recovery semantics.

## Key Takeaways

1. Design against real-world conditions, not only expected inputs.
2. Define forbidden failure behavior as explicitly as desired functionality.
3. Prefer pragmatic, replaceable architecture over rigid perfection.

## Connects To

- **Ch 3**: Stability makes the production target concrete.
- **Ch 18**: Adaptation turns changeability into an operating discipline.
