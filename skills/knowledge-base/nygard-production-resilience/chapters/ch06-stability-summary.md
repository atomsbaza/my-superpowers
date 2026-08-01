# Chapter 6: Stability Summary

## Core Idea

Astronomically unlikely combinations become ordinary when a system processes enough requests and dependencies. Failures cannot be eliminated, so the design objective is to limit damage, preserve useful service, and recover deliberately.

## Frameworks Introduced

- **Recovery-oriented mindset**: Expect cracks and make their consequences bounded.
  - When to use: As a review lens for every production component.
  - How: Identify threats, choose containment, expose state, and rehearse recovery.
- **Stability before capacity**: Do not optimize a system whose failure behavior is not understood.
  - When to use: When teams jump from an outage directly to performance tuning.
  - How: Remove propagation paths first, then measure capacity under realistic load.

## Key Concepts

- **Judgment**: Stability patterns are conditional tools; inappropriate patterns add complexity without protection.
- **Partial functionality**: A healthy system may intentionally disable a feature while preserving the rest.
- **Paranoia as good thinking**: Skepticism about dependencies is a practical design habit.

## Mental Models

- The question is not “Can this fail?” but “How far does it get when it fails?”
- A stable system buys time for humans and dependencies to recover.
- Availability, capacity, design, and operations are sequential concerns, but each reinforces the others.

## Anti-patterns

- Treating “five nines” as a universal target.
- Assuming redundancy alone creates resilience.
- Measuring quality by pattern count instead of failure containment.

## Code Examples

```text
for each feature:
    enumerate dependencies and finite resources
    model failure and overload
    choose timeout, isolation, fallback, and signal
    test normal, impulse, and recovery behavior
```

## Reference Table

| Stage | Primary question |
|---|---|
| Stability | Can the system survive faults without cascading? |
| Capacity | What useful load can it sustain at acceptable latency? |
| Design | Does the topology fit networks, security, availability, and operations? |
| Operations | Can people observe, diagnose, change, and recover it? |

## Worked Example

When a database is unavailable, a stable search product may show cached popular results or a “search temporarily unavailable” state while checkout and account pages remain usable. An unstable product lets every request wait on database connections until the entire site becomes unresponsive.

## Key Takeaways

1. A system is resilient when failures stay local and recovery is possible.
2. Use capacity and architecture work after stability establishes a safe base.
3. Make the recovery behavior visible, testable, and operationally familiar.

## Connects To

- **Ch 7**: Production load reveals the cost of unstable assumptions.
- **Ch 8**: Capacity is the next concern after staying alive.
