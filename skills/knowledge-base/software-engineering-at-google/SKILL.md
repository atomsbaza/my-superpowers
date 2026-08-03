---
name: software-engineering-at-google
description: "Knowledge base from Software Engineering at Google by Titus Winters, Tom Manschreck, and Hyrum Wright. Use when applying Google-scale practices for sustainable software, teams, testing, code review, build systems, dependency management, CI/CD, and managed compute."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Software Engineering at Google
**Authors**: Titus Winters, Tom Manschreck, and Hyrum Wright | **Pages**: ~602 | **Chapters**: 25 | **Generated**: 2026-08-03

## How to Use This Skill

- **Without arguments** — load the core frameworks below.
- **With a topic** — ask about testing, Hyrum’s Law, CI, dependency management, or another indexed topic; read the relevant chapter.
- **With a chapter** — ask for ch12 or ch23 to load that chapter’s detailed guidance.
- **Browse** — ask what chapters or patterns are available.

## Core Frameworks & Mental Models

### Sustainability over time and scale

Software engineering is programming plus the ability to maintain software over its useful life. Choose practices according to lifetime, number of users, number of engineers, and repeated organizational work. Treat slow-growing costs as boiled-frog risks: monitor build time, upgrade cost, integration latency, and support burden before they become crises.

### Hyrum’s Law

With enough users, every observable behavior becomes a dependency, whether or not it is documented. Design explicit contracts, but also search for accidental observables before changing APIs, runtimes, formats, or infrastructure. Make important behavior visible in tests and common CI.

### Scale through mechanisms

Replace heroics with policies, automation, canonical sources, searchable knowledge, shared heads, and repeatable workflows. Ask whether recurring work scales linearly in human effort. If one person is the only resolver, the organization owns a scaling bug.

### Teams and leadership

Humility, respect, and trust are engineering infrastructure. Psychological safety makes questions, feedback, and learning possible. Leaders serve the team by setting clear goals, removing roadblocks, teaching, delegating, being honest, and tracking team health. At scale: Always Be Deciding, Always Be Leaving, and Always Be Scaling.

### Measure decisions, not activity

Use GSM: define a goal, identify signals, and choose measurable metrics. Preserve traceability and check QUANTS—Quality, Attention, iNtel­lectual complexity, Tempo/velocity, and Satisfaction—so an apparent productivity gain does not silently damage another dimension. If results cannot change a decision, do not measure.

### Make code understandable and changeable

Style rules should pull their weight, optimize for readers, reduce danger, and build consistency. Code review should be small, polite, automated where possible, ownership-aware, and useful as organizational memory. Documentation is code-adjacent infrastructure: give it one job, an audience, an owner, a freshness signal, and the right kind of review.

### Testing as a change-enabling system

Use a layered suite: small tests for fast local behavior, medium tests for component boundaries, and larger tests for configuration, integration, load, deployment, and recovery. Prefer public APIs and state assertions. Prefer real implementations, then tested fakes, then narrow stubs; avoid interaction overspecification. CI should make failures fast, reproducible, actionable, and owned.

### Shared versions and managed change

Prefer one supported version at a common head when coordination permits. Treat dependencies as contracts and SemVer as a risk estimate, not proof. For deprecations and LSCs, assign ownership, discover consumers, automate migration, shard changes, test them, review them, and prevent backsliding.

### Developer infrastructure

Code Search should be global, complete enough to trust, low-latency, and integrated with documentation, ownership, and history. Artifact-based builds make dependencies explicit and enable incremental, cached, distributed work. Static analysis succeeds when it is usable, integrated, actionable, and tuned against false positives.

### Continuous delivery and compute

CI stages fast reliable presubmit checks and broad post-submit checks. Continuous delivery uses small batches, feature flags, staged rollouts, production evidence, and cleanup. Managed compute removes infrastructure toil but requires explicit state, resource needs, workload type, and failure behavior; choose standardization versus customization deliberately.

## Chapter Index

| # | Title | Key frameworks |
|---|---|---|
| [ch01](chapters/ch01-what-is-software-engineering.md) | What Is Software Engineering? | Sustainability, Hyrum’s Law, shifting left |
| [ch02](chapters/ch02-how-to-work-well-on-teams.md) | How to Work Well on Teams | Bus factor, humility/respect/trust, blameless postmortems |
| [ch03](chapters/ch03-knowledge-sharing.md) | Knowledge Sharing | Psychological safety, canonical sources, readability |
| [ch04](chapters/ch04-engineering-for-equity.md) | Engineering for Equity | Bias, multicultural capacity, outcomes |
| [ch05](chapters/ch05-how-to-lead-a-team.md) | How to Lead a Team | Servant leadership, influence without authority |
| [ch06](chapters/ch06-leading-at-scale.md) | Leading at Scale | Always Be Deciding/Leaving/Scaling |
| [ch07](chapters/ch07-measuring-engineering-productivity.md) | Measuring Engineering Productivity | GSM, QUANTS, actionability |
| [ch08](chapters/ch08-style-guides-and-rules.md) | Style Guides and Rules | Reader focus, consistency, automation |
| [ch09](chapters/ch09-code-review.md) | Code Review | Small changes, ownership, review memory |
| [ch10](chapters/ch10-documentation.md) | Documentation | Audience, one job, freshness |
| [ch11](chapters/ch11-testing-overview.md) | Testing Overview | Test sizes, scope, write-run-react |
| [ch12](chapters/ch12-unit-testing.md) | Unit Testing | Public APIs, state, DAMP |
| [ch13](chapters/ch13-test-doubles.md) | Test Doubles | Realism, fakes, stubs, interactions |
| [ch14](chapters/ch14-larger-testing.md) | Larger Testing | Fidelity, SUT/data/action/verification |
| [ch15](chapters/ch15-deprecation.md) | Deprecation | Milestones, migration, backsliding |
| [ch16](chapters/ch16-version-control-and-branch-management.md) | Version Control and Branch Management | One-Version Rule, shared head |
| [ch17](chapters/ch17-code-search.md) | Code Search | Trust, latency, history |
| [ch18](chapters/ch18-build-systems-and-build-philosophy.md) | Build Systems and Build Philosophy | Artifact graphs, fine-grained modules |
| [ch19](chapters/ch19-critiques-code-review-tool.md) | Critique: Google’s Code Review Tool | Review state, attention set, integration |
| [ch20](chapters/ch20-static-analysis.md) | Static Analysis | Tricorder, usability, suggested fixes |
| [ch21](chapters/ch21-dependency-management.md) | Dependency Management | Contracts, SemVer, MVS |
| [ch22](chapters/ch22-large-scale-changes.md) | Large-Scale Changes | LSCs, sharding, backsliding |
| [ch23](chapters/ch23-continuous-integration.md) | Continuous Integration | Presubmit/post-submit, hermeticity |
| [ch24](chapters/ch24-continuous-delivery.md) | Continuous Delivery | Feature flags, staged rollout, release train |
| [ch25](chapters/ch25-compute-as-a-service.md) | Compute as a Service | Managed compute, failure, abstraction |

## Topic Index

- **Artifact-based builds** → ch18
- **CaaS and containers** → ch25
- **CI/CD** → ch23, ch24
- **Code review** → ch09, ch19
- **Code search** → ch17
- **Documentation** → ch03, ch10
- **Dependencies** → ch01, ch15, ch16, ch18, ch21
- **Deprecation** → ch15, ch20, ch22
- **Equity and inclusion** → ch04
- **GSM and QUANTS** → ch07
- **Hyrum’s Law** → ch01, ch15, ch21
- **Knowledge sharing** → ch02, ch03, ch09
- **Leadership** → ch05, ch06
- **Large-Scale Changes** → ch22
- **One-Version Rule** → ch16, ch21
- **Static analysis** → ch08, ch15, ch20
- **Testing** → ch11, ch12, ch13, ch14, ch23
- **Test doubles** → ch12, ch13, ch14
- **Trunk-based development** → ch16, ch23, ch24
- **Version control** → ch16, ch22

## Supporting Files

- [glossary.md](glossary.md) — key terms and definitions
- [patterns.md](patterns.md) — reusable techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — decision rules, trade-offs, and smells

## Scope & Limits

This skill covers the concepts and practices presented in *Software Engineering at Google*. It does not claim that Google’s internal tools or processes are universally appropriate. Combine it with project-specific constraints, current platform documentation, security guidance, and local operating requirements.

