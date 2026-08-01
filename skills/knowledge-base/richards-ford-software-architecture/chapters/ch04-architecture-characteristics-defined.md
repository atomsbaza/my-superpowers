# Chapter 4: Architecture Characteristics Defined

## Core Idea

Architecture characteristics are the “-ilities” and other qualities that shape structure. They are not a generic checklist to maximize. A characteristic belongs in architecture when it influences structural decisions, is important to application success, and can be specified or measured sufficiently to guide trade-offs.

## Frameworks Introduced

- **Three criteria for an architecture characteristic**:
  1. It influences some structural aspect of the design.
  2. It is important to application success.
  3. It can be specified in a measurable or testable way.
  - **When to use:** when deciding whether a quality belongs in architecture scope.
  - **How:** reject vague or merely desirable adjectives; turn valid concerns into observable targets.
- **Operational, structural, and cross-cutting characteristics**:
  - **Operational:** availability, reliability, performance, scalability, elasticity, recoverability.
  - **Structural:** modularity, configurability, extensibility, deployability, testability.
  - **Cross-cutting:** security, accessibility, legal compliance, privacy, supportability.
- **Least-worst architecture**: accept that architecture optimizes competing characteristics rather than maximizing all of them.

## Key Concepts

- **Availability** — proportion of time useful service is accessible.
- **Reliability** — ability to perform correctly over time.
- **Scalability** — ability to handle increased load by adding resources or changing capacity.
- **Elasticity** — ability to dynamically acquire and release resources as load changes.
- **Performance** — response behavior under a defined workload, including latency and throughput.
- **Deployability** — ease and safety of putting changes into production.
- **Testability** — ability to verify behavior and characteristics efficiently.
- **Maintainability** — effort required to understand, change, and repair the system.
- **Functional suitability** — functional completeness, correctness, and appropriateness.
- **“Italy-ility”** — a characteristic emphasized by a stakeholder for a specific local reason; it must still be examined rather than accepted as universal.

## Mental Models

Use “architecture characteristics” instead of generic “nonfunctional requirements.” The term reminds the team that these qualities drive structure, not merely implementation polish.

Use a small, prioritized set. Each additional characteristic creates constraints and trade-offs. A system designed for every possible quality often becomes expensive and mediocre at the qualities that actually matter.

When a stakeholder names a quality, ask for an observable scenario: actor, stimulus, environment, response, and measurable target.

## Anti-patterns

- **“-Ilities” shopping list**: listing dozens of qualities without priorities or measures.
- **Vague quality claims**: saying “high performance” or “secure” without workload, threat, or acceptance criteria.
- **Single-characteristic architecture**: maximizing one quality while ignoring the business outcome and sacrificed qualities.

## Code Examples

Turn a vague requirement into an architecture scenario:

```text
Characteristic: deployability
Stimulus: a backward-compatible order change is ready
Environment: normal production traffic
Response: release one service without stopping unrelated flows
Measure: rollbackable canary reaches 25% traffic within 15 minutes
```

## Reference Tables

| Category | Examples | Typical structural consequence |
|---|---|---|
| Operational | Availability, performance, elasticity | Topology, runtime, capacity, failure handling |
| Structural | Modularity, testability, deployability | Components, boundaries, build and release pipeline |
| Cross-cutting | Security, privacy, compliance | Policies and constraints across many elements |

## Worked Example

An organization says payment processing must be “secure and fast.” Security is refined into authenticated access, least privilege, auditability, and encryption. Performance becomes p95 response under peak checkout load. The resulting architecture may choose a synchronous authorization call for immediate feedback, an asynchronous settlement workflow, isolated payment data, and an auditable event trail. No single “secure-and-fast” setting would have produced those decisions.

## Key Takeaways

1. A valid architecture characteristic shapes structure, matters to success, and can be evaluated.
2. Prioritize a small set instead of maximizing every “-ility.”
3. Convert quality adjectives into measurable scenarios.
4. Every characteristic introduces trade-offs.

## Connects To

- **Chapter 5:** extracts characteristics from domain concerns and requirements.
- **Chapter 6:** measures and governs characteristics with fitness functions.
- **Chapter 18:** uses characteristic priorities to choose architecture styles.

