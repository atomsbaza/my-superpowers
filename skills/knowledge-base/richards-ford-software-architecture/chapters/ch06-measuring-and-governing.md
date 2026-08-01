# Chapter 6: Measuring and Governing Architecture Characteristics

## Core Idea

Architecture characteristics become useful when teams can observe whether the architecture is preserving them. Measurements are imperfect and context-dependent, so governance should combine operational, structural, and process measures with automated fitness functions that provide fast feedback as the system evolves.

## Frameworks Introduced

- **Operational measures**: observe runtime qualities such as performance, availability, scalability, and reliability under a defined workload.
- **Structural measures**: inspect code and dependencies for complexity, cycles, coupling, and architectural rules.
- **Process measures**: observe how the team builds and changes the system, including deployment frequency, lead time, and feedback.
- **Architecture fitness function**: an objective integrity assessment of an architecture characteristic, implemented as a metric, test, monitor, or other automated check.
  - **When to use:** when a characteristic must survive ongoing change.
  - **How:** encode a target, run it at a useful feedback frequency, and fail or alert when the architecture drifts.

## Key Concepts

- **Measurement context** — the workload, environment, and definition needed to interpret a number.
- **Cyclomatic complexity** — a graph-based measure of independent control-flow paths.
- **Cyclic dependency** — a dependency path that returns to an earlier module or package.
- **Fitness function** — an automated architecture integrity check.
- **Governance** — mechanisms that guide and verify adherence to architecture decisions.
- **Structural fitness function** — a check over dependencies, packages, layers, or modules.
- **Operational fitness function** — a runtime check over latency, throughput, availability, or capacity.
- **Process fitness function** — a check over delivery or change behavior.

## Mental Models

Measurements are not physics. “Performance” and “availability” have different definitions across systems; always state the workload and threshold.

Use the fastest feedback loop that can answer the question. A dependency-cycle test belongs in CI; a capacity test may run periodically; a resilience experiment may run in a controlled environment.

Govern the characteristic, not the implementation detail. A test that forbids one framework can become obsolete; a test that preserves a deployability or layering property remains useful across technology changes.

## Anti-patterns

- **Metric without context**: using a number without defining workload, environment, or percentile.
- **Manual governance only**: relying on architecture reviews to catch violations that tooling can detect continuously.
- **Proxy metric fixation**: optimizing cyclomatic complexity while the real risk is runtime coupling or slow deployment.
- **Fitness-function theater**: creating checks that never fail, alert, or influence decisions.

## Code Examples

A conceptual layering fitness function:

```text
for dependency in dependency_graph:
    if dependency.from_layer == "presentation" \
       and dependency.to_layer == "data":
        fail("presentation must not access data directly")
```

The exact tool may be ArchUnit, NetArchTest, a dependency analyzer, or a custom script; the architectural rule is the durable part.

## Reference Tables

| Measure type | Example | Feedback loop |
|---|---|---|
| Operational | p95 latency, error rate, availability | Runtime/continuous |
| Structural | Cycles, layer violations, complexity | Build/CI |
| Process | Lead time, deployment frequency, recovery time | Iteration/release |

## Worked Example

An architecture requires presentation code to depend only on application services. The team writes a dependency rule that fails the build when a presentation package imports a persistence package. A second fitness function checks that the number of independently deployable services remains within the operational team’s capacity. The tests protect both structure and the process reality that makes the structure supportable.

## Key Takeaways

1. Define the characteristic and context before choosing a metric.
2. Use operational, structural, and process measures together.
3. Automate architecture rules wherever the signal is stable.
4. Fitness functions protect architecture during evolution; they do not replace judgment.

## Connects To

- **Chapter 4:** defines the qualities to measure.
- **Chapter 19:** records the decision and its consequences.
- **Chapter 22:** uses checklists and guidance to make governance workable for teams.

