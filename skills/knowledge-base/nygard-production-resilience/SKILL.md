---
name: nygard-production-resilience
description: "Knowledge base from Release It! Design and Deploy Production-Ready Software by Michael T. Nygard. Use when designing, reviewing, operating, or evolving production systems with stability, capacity, availability, failure containment, observability, and safe release concerns."
---

<!-- argument-hint: [topic, pattern, antipattern, or chapter number] -->

# Release It! — Production Resilience
**Author**: Michael T. Nygard | **Pages**: ~350 | **Chapters**: 18 | **Generated**: 2026-08-01

## How to Use This Skill

- **Without arguments** — load the core production-resilience toolkit.
- **With a topic** — ask about `timeouts`, `bulkheads`, `capacity`, `availability`, `transparency`, or another indexed term; read the relevant chapter file.
- **With a pattern or antipattern** — ask for the design trade-offs and failure mode.
- **With a chapter** — ask for `ch04` or `ch18` to load that chapter.
- **Browse** — ask what chapters or patterns are available.

This skill captures Nygard's reasoning from the book. It is not a substitute for current platform documentation or a codebase-specific runbook.

---

## Core Frameworks & Mental Models

### Design for production, not the lab

Treat production as the real test environment. Users, dependencies, operators, traffic spikes, partial failures, and changing conditions will exercise behaviors that QA cannot enumerate. Ask what the system must not do: crash, hang, lose data, amplify a dependency failure, or make recovery impossible.

### Stability comes before capacity

First keep the system alive under failure; then make it handle more load; then improve general design and operations. A fast system that falls over is not production-ready. Capacity work performed on an unstable system often optimizes the wrong constraint.

### Cracks must be contained

Failures are inevitable. A stability antipattern turns a small crack into a wider failure; a stability pattern limits propagation and preserves partial function. Review every boundary by asking: “What can fail here, how long can it block, and what else will it consume when it does?”

### The eight stability patterns

- **Timeouts** bound waiting and return control to the caller.
- **Circuit Breaker** stops calls to a known-troubled dependency and gives it time to recover.
- **Bulkheads** isolate resources or traffic classes so one failure cannot consume everything.
- **Steady State** makes normal operation explicit so abnormal behavior can be detected.
- **Fail Fast** rejects work that cannot complete within a useful budget.
- **Handshaking** verifies that endpoints agree on readiness, identity, and protocol before expensive work.
- **Test Harness** exercises real interactions and failure modes instead of only isolated units.
- **Decoupling Middleware** separates producers and consumers in time, rate, and availability.

Use patterns selectively. “More patterns” is not a quality metric; use the smallest set that contains the credible failure modes.

### Capacity is constrained and interrelated

Capacity is the useful work a system can perform under stated conditions, not a single hardware number. Identify constraints, measure the resource that actually limits throughput, and account for interactions among CPU, memory, storage, network, threads, connections, sessions, and downstream services. A larger resource pool can increase contention or overload a dependency.

### Availability is a feature-level economic decision

Do not promise “the system” or “five nines” without defining the user-visible functions, exclusions, dependencies, measurement window, and cost. Compare the cost of downtime with the cost of prevention. Design graceful degradation so a dependency outage removes a feature instead of taking down the whole product.

### Transparency closes the feedback loop

Operators need historical trends, future projections, present status, and instantaneous behavior. Expose business transactions, resource pools, dependency health, circuit states, and meaningful logs. A dashboard is useful only when its colors and thresholds are accurate enough to drive action.

### Release is the beginning of system life

Production reveals gaps and protrusions in the design. Adaptation is deliberate: every change has implementation cost and release cost. Make changes safer through loose coupling, dependency injection, protocol versioning, backward compatibility, zero-downtime deployment, small rollouts, and feedback from production.

---

## Chapter Index

| # | Title | Key frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-introduction.md) | Introduction | Production target, pragmatic architecture |
| [ch02](chapters/ch02-airline-outage.md) | The Exception That Grounded an Airline | Failure propagation, post-mortem thinking |
| [ch03](chapters/ch03-introducing-stability.md) | Introducing Stability | Stability, cracks, cynical design |
| [ch04](chapters/ch04-stability-antipatterns.md) | Stability Antipatterns | Coupling, cascades, blocked threads, SLA inversion |
| [ch05](chapters/ch05-stability-patterns.md) | Stability Patterns | Timeouts, Circuit Breaker, Bulkheads, fail-fast |
| [ch06](chapters/ch06-stability-summary.md) | Stability Summary | Recovery-oriented design |
| [ch07](chapters/ch07-trampled-by-customers.md) | Trampled by Your Own Customers | Load testing, production traffic, temporary fixes |
| [ch08](chapters/ch08-introducing-capacity.md) | Introducing Capacity | Constraints, scalability, capacity myths |
| [ch09](chapters/ch09-capacity-antipatterns.md) | Capacity Antipatterns | Contention, chatty clients, sessions, reloads, SQL |
| [ch10](chapters/ch10-capacity-patterns.md) | Capacity Patterns | Pools, bounded caches, precomputation, GC |
| [ch11](chapters/ch11-networking.md) | Networking | Multihoming, routing, virtual IPs |
| [ch12](chapters/ch12-security.md) | Security | Least privilege, secret configuration |
| [ch13](chapters/ch13-availability.md) | Availability | Requirements, load balancing, clustering |
| [ch14](chapters/ch14-administration.md) | Administration | Production parity, configuration, operations |
| [ch15](chapters/ch15-design-summary.md) | Design Summary | Cross-cutting production checklist |
| [ch16](chapters/ch16-phenomenal-powers.md) | Phenomenal Cosmic Powers, Itty-Bitty Living Space | Peak load, diagnosis, treatment |
| [ch17](chapters/ch17-transparency.md) | Transparency | Metrics, logging, monitoring, operations data |
| [ch18](chapters/ch18-adaptation.md) | Adaptation | Change cost, compatibility, safe releases |

## Topic Index

- **Administration** → ch14, ch15
- **Availability requirements** → ch13, ch15
- **Bulkheads** → ch04, ch05, ch07
- **Capacity** → ch07, ch08, ch09, ch10, ch16
- **Circuit Breaker** → ch04, ch05, ch17
- **Clustering** → ch11, ch13
- **Decoupling** → ch04, ch05, ch18
- **Fail Fast** → ch04, ch05, ch17
- **Handshaking** → ch04, ch05, ch11
- **Load testing** → ch07, ch08, ch16
- **Networking** → ch11
- **Observability / transparency** → ch16, ch17
- **Resource pools** → ch04, ch09, ch10, ch17
- **Safe release** → ch14, ch15, ch18
- **Security** → ch11, ch12, ch14
- **Steady State** → ch05, ch17
- **Timeouts** → ch04, ch05, ch11

## Supporting Files

- [glossary.md](glossary.md) — key terms and definitions
- [patterns.md](patterns.md) — stability, capacity, and release patterns
- [cheatsheet.md](cheatsheet.md) — decision rules and review prompts

## Scope & Limits

This skill covers the book's production-resilience concepts. It reflects a 2007-era book, so validate platform-specific commands, cloud services, security controls, and observability products against current documentation. Combine it with project-specific architecture, deployment, and incident-response skills.
