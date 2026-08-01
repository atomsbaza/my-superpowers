# Chapter 1: Introduction

## Core Idea

Software architecture is broader than a diagram or a chosen style. It combines the system’s structure, the architecture characteristics it must support, the decisions that constrain construction, and the principles that guide choices. The architect’s job is to keep those elements aligned with business goals while the system and its environment change.

## Frameworks Introduced

- **Four dimensions of architecture**: structure, architecture characteristics, architecture decisions, and design principles.
  - **When to use:** whenever someone describes an architecture only by a label such as “microservices” or “layered.”
  - **How:** ask what the structure is, which “-ilities” matter, which rules constrain implementation, and which principles guide exceptions.
- **Eight core expectations of an architect**: make decisions; continually analyze the architecture; keep current with trends; ensure compliance; maintain diverse exposure and experience; understand the business domain; possess interpersonal skills; navigate politics.
  - **When to use:** when defining an architect role or diagnosing why architecture work is failing.
  - **How:** evaluate both technical outputs and the feedback, communication, governance, and business context that make those outputs effective.
- **First Law of Software Architecture**: everything is a trade-off.
- **Second Law of Software Architecture**: why is more important than how.

## Key Concepts

- **Architecture structure** — the high-level form or style of the system.
- **Architecture characteristic** — a measurable or testable quality important to system success, such as availability, security, or time-to-market.
- **Architecture decision** — a rule that constrains how the system is built.
- **Design principle** — guidance that helps teams choose among allowed alternatives.
- **Architecture vitality** — the ability to keep architecture healthy as development and deployment continue.
- **Architecture and engineering** — architecture depends on automation, feedback, and repeatable engineering practices.

## Mental Models

Think of a style as scaffolding, not a complete architecture. Two systems can use the same style while having different quality goals, decisions, and operational realities.

Use “why before how” when reviewing diagrams. A topology without its drivers cannot explain whether a choice was deliberate, inherited, or accidental.

Treat architecture as a feedback loop spanning architecture, development, operations, process, and data. A decision that ignores one of those intersections is likely to create accidental complexity elsewhere.

## Anti-patterns

- **Architecture by label**: declaring “we use microservices” without identifying characteristics, decisions, or principles.
- **Architect as gatekeeper**: separating architects from developers so decisions flow only downward and implementation feedback never returns.
- **One-sided optimization**: treating performance, availability, flexibility, or cost as an absolute good without naming the sacrificed quality.

## Code Examples

An architecture decision should be expressed as a constraint plus its reason:

```text
Decision: only the business and service layers may access persistence.
Why: database changes should not force presentation changes.
Guidance: prefer a closed-layer dependency; document approved variances.
Fitness check: reject new presentation-to-data dependencies in CI.
```

## Reference Tables

| Architecture dimension | Question to ask | Typical artifact |
|---|---|---|
| Structure | What are the major elements and relationships? | Style/topology diagram |
| Characteristics | What must the system be good at? | Quality target and measure |
| Decisions | What is allowed or prohibited? | Decision record/standard |
| Principles | How should teams choose among options? | Design guidance |

## Worked Example

Suppose an organization says, “Use a three-tier architecture.” That states structure, but not enough to build or evaluate the system. The architect adds the drivers: fast change and strict auditability. The decisions constrain database access to the service layer, require immutable audit events, and define a deployment pipeline. The principles favor asynchronous communication for long-running work but allow synchronous calls where the user needs an immediate answer. The result is an architecture that can be reviewed against business intent rather than a style name.

## Key Takeaways

1. Architecture is structure plus characteristics, decisions, and principles.
2. Every architectural benefit carries a cost or a sacrificed quality.
3. Preserve the reason behind decisions, not only the topology.
4. Architecture must collaborate continuously with development, operations, process, and data.

## Connects To

- **Chapter 2:** develops architectural thinking and trade-off analysis.
- **Chapter 4:** defines architecture characteristics precisely.
- **Chapter 19:** captures the “why” in Architecture Decision Records.

