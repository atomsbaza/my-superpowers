---
name: richards-ford-software-architecture
description: "Knowledge base from Fundamentals of Software Architecture: An Engineering Approach by Mark Richards and Neal Ford. Use when applying architecture characteristics, trade-off analysis, modularity, connascence, architecture styles, quanta, fitness functions, ADRs, risk storming, diagrams, team guidance, or architecture leadership."
---

<!-- argument-hint: [topic, architecture style, decision technique, or chapter number] -->

# Fundamentals of Software Architecture: An Engineering Approach
**Authors**: Mark Richards & Neal Ford | **Pages**: ~422 | **Chapters**: 24 + appendix | **Generated**: 2026-08-01

## How to Use This Skill

- **Without arguments** — load the core architecture reasoning toolkit.
- **With a topic** — ask about `connascence`, `architecture quantum`, `fitness functions`, `microservices`, `risk storming`, or another indexed term; read the relevant chapter.
- **With a style** — compare `layered`, `pipeline`, `microkernel`, `service-based`, `event-driven`, `space-based`, `orchestration-driven SOA`, or `microservices`.
- **With a chapter** — ask for `ch03`, `ch18`, or `ch20` to load that chapter.
- **Browse** — ask what chapters, styles, or decision techniques are available.

This skill extracts the authors’ engineering vocabulary and decision heuristics. It is a reasoning aid, not a universal architecture standard; validate targets against the actual domain, team, operations, and current platform capabilities.

## Core Frameworks & Mental Models

### Architecture is four things

Describe architecture through **structure**, **architecture characteristics**, **architecture decisions**, and **design principles**. A style label such as “microservices” covers only structure. Always ask what qualities matter, which rules constrain construction, and which principles guide choices.

### The laws of architecture

- **First Law:** everything in software architecture is a trade-off. If a choice looks free, the sacrificed quality or hidden cost has not been found yet.
- **Second Law:** why is more important than how. Preserve the driver and consequences, not only the topology.

### Think in characteristics

An architecture characteristic should influence structure, be important to success, and be measurable or testable. Extract a small prioritized set from domain concerns, requirements, constraints, and operations. Convert vague words such as “fast,” “secure,” or “zero downtime” into scenarios with an actor, stimulus, environment, response, and measure.

### Modularity and connascence

Maximize cohesion within boundaries and minimize coupling across them. **Connascence** describes change relationships that ordinary dependency counts miss: name, type, meaning, position, algorithm, execution, timing, and identity. Encapsulate strong relationships; prefer weaker, more local, and static connascence across architectural boundaries.

### Architecture quantum

An architecture quantum is an independently deployable artifact with high functional cohesion and synchronous connascence. Use it to reason about the real scope of availability, scalability, deployability, and failure. A service that shares a synchronous database transaction or coordinated release is not operationally independent just because it has a separate process.

### Measure architecture continuously

Use operational, structural, and process measures. Encode durable rules as **fitness functions**: dependency checks, layer tests, complexity thresholds, runtime probes, performance tests, or delivery checks. Choose the feedback frequency that matches the risk; a noisy or never-failing check is not governance.

### Choose styles by fit

Use the least-worst architecture for the current characteristics, domain, team, process, and operations. Layered architecture favors simplicity and technical separation; pipeline favors sequential transformation; microkernel favors a stable core with variants; service-based favors coarse capabilities; event-driven favors temporal decoupling and fan-out; space-based addresses centralized bottlenecks; orchestration-driven SOA makes workflows explicit; microservices favors independent teams, deployment, data, and scaling. A modular monolith is often the best evolutionary starting point.

### Record why and analyze risk

Use ADRs for architecturally significant decisions: context, alternatives, decision, consequences, status, compliance, and notes. Use risk storming to identify risk individually, reach consensus collaboratively, and assign mitigations with evidence. Repeat it after meaningful change.

### Architecture is a team practice

Architecture and design evolve together. Use communication, collaboration, clarity, and conciseness. Explain reasons before constraints, demonstrate technical alternatives, qualify extreme requirements to the smallest necessary scope, and use the smallest amount of control that protects the important characteristic.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|---|---|
| [ch01](chapters/ch01-introduction.md) | Introduction | Four dimensions, laws, architect expectations |
| [ch02](chapters/ch02-architectural-thinking.md) | Architectural Thinking | Breadth/depth, trade-offs, business drivers |
| [ch03](chapters/ch03-modularity.md) | Modularity | Cohesion, coupling, connascence |
| [ch04](chapters/ch04-architecture-characteristics-defined.md) | Architecture Characteristics Defined | Criteria, categories, least-worst trade-offs |
| [ch05](chapters/ch05-identifying-architecture-characteristics.md) | Identifying Architectural Characteristics | Domain extraction, requirements, katas |
| [ch06](chapters/ch06-measuring-and-governing.md) | Measuring and Governing Architecture Characteristics | Measures, fitness functions, governance |
| [ch07](chapters/ch07-scope-of-architecture-characteristics.md) | Scope of Architecture Characteristics | Quanta, granularity, bounded contexts |
| [ch08](chapters/ch08-component-based-thinking.md) | Component-Based Thinking | Partitioning, Conway’s Law, discovery |
| [ch09](chapters/ch09-foundations.md) | Foundations | Monolith/distribution, eight fallacies |
| [ch10](chapters/ch10-layered-architecture-style.md) | Layered Architecture Style | Open/closed layers, sinkhole |
| [ch11](chapters/ch11-pipeline-architecture-style.md) | Pipeline Architecture Style | Pipes, filters, backpressure |
| [ch12](chapters/ch12-microkernel-architecture-style.md) | Microkernel Architecture Style | Core, plugins, registry, contracts |
| [ch13](chapters/ch13-service-based-architecture-style.md) | Service-Based Architecture Style | Coarse services, data partitioning |
| [ch14](chapters/ch14-event-driven-architecture-style.md) | Event-Driven Architecture Style | Broker, mediator, events, sagas |
| [ch15](chapters/ch15-space-based-architecture-style.md) | Space-Based Architecture Style | Processing units, grids, data pumps |
| [ch16](chapters/ch16-orchestration-driven-soa.md) | Orchestration-Driven SOA | Service taxonomy, orchestration, reuse |
| [ch17](chapters/ch17-microservices-architecture.md) | Microservices Architecture | Bounded contexts, data, autonomy, sagas |
| [ch18](chapters/ch18-choosing-the-appropriate-architecture-style.md) | Choosing the Appropriate Architecture Style | Criteria, isomorphism, case studies |
| [ch19](chapters/ch19-architecture-decisions.md) | Architecture Decisions | Anti-patterns, ADRs, RFCs |
| [ch20](chapters/ch20-analyzing-architecture-risk.md) | Analyzing Architecture Risk | Matrix, assessments, risk storming |
| [ch21](chapters/ch21-diagramming-and-presenting-architecture.md) | Diagramming and Presenting Architecture | UML, C4, ArchiMate, presentation |
| [ch22](chapters/ch22-making-teams-effective.md) | Making Teams Effective | Control, guidance, checklists |
| [ch23](chapters/ch23-negotiation-and-leadership-skills.md) | Negotiation and Leadership Skills | 4 C’s, demonstration, justification |
| [ch24](chapters/ch24-developing-a-career-path.md) | Developing a Career Path | 20-Minute Rule, technology radar |
| [appendix](chapters/appendix-self-assessment.md) | Self-Assessment Questions | Review prompts |

## Topic Index

- **ADRs** → ch19
- **Architecture characteristics** → ch01, ch04, ch05, ch06, ch07, ch18
- **Architecture decisions** → ch01, ch02, ch19
- **Architecture quantum** → ch07, ch08, ch17
- **Architecture styles** → ch09–ch18
- **Bounded Context** → ch07, ch17
- **C4** → ch21
- **Cohesion/coupling** → ch03, ch07, ch08
- **Connascence** → ch03, ch07, ch17
- **Conway’s Law** → ch08, ch22
- **Event-driven architecture** → ch14, ch17
- **Fitness functions** → ch06, ch19
- **Microservices** → ch07, ch09, ch17, ch18
- **Modular monolith** → ch08, ch18
- **Negotiation/leadership** → ch02, ch22, ch23
- **Pipeline** → ch09, ch11
- **Risk storming** → ch20
- **Sagas** → ch14, ch17
- **Team boundaries** → ch08, ch18, ch22
- **Trade-offs** → ch01, ch02, ch04, ch18

## Supporting Files

- [glossary.md](glossary.md) — key terms and definitions
- [patterns.md](patterns.md) — architecture techniques and patterns
- [cheatsheet.md](cheatsheet.md) — decision rules and comparison tables

## Related Skills

- `ousterhout-software-design` — complexity, deep modules, and information hiding.
- `khononov-ddd` — domain modeling, bounded contexts, and strategic design.
- `designing-systems` — project-specific system-design workflow and artifacts.
- `nygard-production-resilience` — stability, capacity, availability, and production failure containment.

## Scope & Limits

This skill covers the contents and reasoning of the first edition of the book. It does not replace current platform documentation, security guidance, or codebase-specific constraints. Apply the frameworks with measured business drivers, team capability, operational reality, and current technology behavior.
