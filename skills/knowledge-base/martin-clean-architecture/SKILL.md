---
name: martin-clean-architecture
description: "Knowledge base from \"Clean Architecture: A Craftsman's Guide to Software Structure and Design\" by Robert C. Martin. Use when applying SOLID principles, component cohesion/coupling principles, the Dependency Rule, drawing architecture boundaries, designing use cases and entities, or referencing the Clean Architecture concentric-circle model."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Clean Architecture: A Craftsman's Guide to Software Structure and Design
**Author**: Robert C. Martin | **Pages**: ~364 | **Chapters**: 34 + Appendix A | **Generated**: 2026-07-26

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `SRP`, `component coupling`, `boundaries`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch22`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**The goal of architecture**: minimize the human resources required to build and maintain a system over its lifetime — behavior gets a system used, architecture keeps it changeable. When forced to choose, fight for architecture; the business almost always undervalues it until it's too late.

**SOLID** (the class/module level, but their real payoff is at the component/architecture level):
- **SRP** — A module should be responsible to one, and only one, *actor* (not "one thing"). Symptoms of violation: accidental duplication, painful merges. Fix: separate code that different actors depend on for different reasons.
- **OCP** — A software artifact should be open for extension but closed for modification. Achieved by arranging components so higher-level policy is protected from changes in lower-level detail (directional control via interfaces).
- **LSP** — Subtypes must be substitutable for their base types without altering correctness. Violations at the architecture level (not just class level) manifest as extra `if`/type-check machinery at integration points — a design smell worth extra vigilance for.
- **ISP** — Don't force clients to depend on interfaces (or, at the architecture level, modules/components) they don't use. Depending on something carrying baggage you don't need forces unnecessary recompilation/redeployment.
- **DIP** — Depend on abstractions, not concretions. Flexible systems keep source-level dependencies pointing only at interfaces/abstract classes, never at volatile concrete implementations. Use Abstract Factory to keep the `new` keyword out of business logic.

**Component principles** — cohesion (what goes together):
- **REP** (Reuse/Release Equivalence) — the granule of reuse is the granule of release; group classes that are versioned/released together.
- **CCP** (Common Closure) — gather classes that change for the same reasons at the same times; keep single-reason changes inside a single component (SRP for components).
- **CRP** (Common Reuse) — don't force users of a component to depend on things they don't need; don't group classes that aren't used together.
- These three fight each other — the tension diagram: early in a project, favor CCP over REP (developability); as a component matures for external reuse, shift toward REP.

**Component principles** — coupling (the dependency graph between components):
- **ADP** (Acyclic Dependencies) — no cycles in the component dependency graph. Break cycles with DIP + a new component, never by "just adding one more dependency."
- **SDP** (Stable Dependencies) — depend in the direction of stability; a component should not depend on something less stable (more likely to change) than itself.
- **SAP** (Stable Abstractions) — a component's abstractness should increase with its stability. Measured via **I** (instability = fan-out/(fan-in+fan-out)) and **A** (abstractness); plot components on the A/I graph — the **Main Sequence** is the target line; the **Zone of Pain** (stable+concrete, hard to change) and **Zone of Uselessness** (abstract+unstable, no one depends on it) are anti-patterns.

**The Dependency Rule** (the heart of Clean Architecture): source-code dependencies must point only inward, toward higher-level policy. Nothing in an inner circle can know anything about an outer circle — including names, formats, or frameworks. Concentric rings, outer to inner: Frameworks & Drivers → Interface Adapters (Controllers/Presenters/Gateways) → Application Business Rules (Use Cases) → Enterprise Business Rules (Entities). Data that crosses a boundary is always a simple DTO/request-response struct, never an Entity or database row — crossing in the direction against source-code dependency (e.g., inner Use Case calling outer Presenter) is done via DIP: define the interface on the inner side, implement it on the outer side.

**Boundaries cost real engineering effort — don't draw one speculatively.** Only draw an architecture boundary where an actual axis of change exists today, or where you have strong reason to expect one. See `cheatsheet.md` for the full decision rule and `patterns.md` for Partial Boundaries (cheaper, less-committed alternatives).

**Screaming Architecture**: a system's top-level directory/package structure should scream its use cases and domain, not the framework or delivery mechanism it happens to use (frameworks, DBs, and the web are all *details* — see Ch 30-32).

**Humble Object pattern**: split hard-to-test behavior from easy-to-test behavior at a natural architectural boundary; keep the untestable part (UI rendering, DB calls) "humble" — as thin and dumb as possible — and push all logic into the testable part (Presenter, Interactor).

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-what-is-design-and-architecture.md) | What Is Design and Architecture? | goal of architecture |
| [ch02](chapters/ch02-a-tale-of-two-values.md) | A Tale of Two Values | behavior vs. architecture, Eisenhower Matrix |
| [ch03](chapters/ch03-paradigm-overview.md) | Paradigm Overview | 3 paradigms |
| [ch04](chapters/ch04-structured-programming.md) | Structured Programming | discipline on direct transfer of control |
| [ch05](chapters/ch05-object-oriented-programming.md) | Object-Oriented Programming | discipline on indirect transfer of control, polymorphism as DIP |
| [ch06](chapters/ch06-functional-programming.md) | Functional Programming | discipline on assignment, immutability, event sourcing |
| [ch07](chapters/ch07-srp-single-responsibility-principle.md) | SRP | Single Responsibility Principle |
| [ch08](chapters/ch08-ocp-open-closed-principle.md) | OCP | Open-Closed Principle, directional control |
| [ch09](chapters/ch09-lsp-liskov-substitution-principle.md) | LSP | Liskov Substitution Principle |
| [ch10](chapters/ch10-isp-interface-segregation-principle.md) | ISP | Interface Segregation Principle |
| [ch11](chapters/ch11-dip-dependency-inversion-principle.md) | DIP | Dependency Inversion Principle, Abstract Factory |
| [ch12](chapters/ch12-components.md) | Components | relocatability, linkers |
| [ch13](chapters/ch13-component-cohesion.md) | Component Cohesion | REP, CCP, CRP, tension diagram |
| [ch14](chapters/ch14-component-coupling.md) | Component Coupling | ADP, SDP, SAP, Main Sequence |
| [ch15](chapters/ch15-what-is-architecture.md) | What Is Architecture? | policy vs. detail, device independence |
| [ch16](chapters/ch16-independence.md) | Independence | Conway's Law, decoupling modes |
| [ch17](chapters/ch17-boundaries-drawing-lines.md) | Boundaries: Drawing Lines | plugin architecture, axis of change |
| [ch18](chapters/ch18-boundary-anatomy.md) | Boundary Anatomy | monolith/deployment/process/service boundaries |
| [ch19](chapters/ch19-policy-and-level.md) | Policy and Level | level as distance from I/O |
| [ch20](chapters/ch20-business-rules.md) | Business Rules | Entities, Use Cases |
| [ch21](chapters/ch21-screaming-architecture.md) | Screaming Architecture | use-case-first directory structure |
| [ch22](chapters/ch22-the-clean-architecture.md) | The Clean Architecture | Dependency Rule, concentric circles |
| [ch23](chapters/ch23-presenters-and-humble-objects.md) | Presenters and Humble Objects | Humble Object pattern |
| [ch24](chapters/ch24-partial-boundaries.md) | Partial Boundaries | cheaper boundary variants |
| [ch25](chapters/ch25-layers-and-boundaries.md) | Layers and Boundaries | multi-boundary systems |
| [ch26](chapters/ch26-the-main-component.md) | The Main Component | Main as a plugin |
| [ch27](chapters/ch27-services-great-and-small.md) | Services: Great and Small | services aren't automatically architecture |
| [ch28](chapters/ch28-the-test-boundary.md) | The Test Boundary | tests as the outermost circle |
| [ch29](chapters/ch29-clean-embedded-architecture.md) | Clean Embedded Architecture | HAL/PAL/OSAL |
| [ch30](chapters/ch30-the-database-is-a-detail.md) | The Database Is a Detail | DB as a plugin |
| [ch31](chapters/ch31-the-web-is-a-detail.md) | The Web Is a Detail | delivery mechanism as a plugin |
| [ch32](chapters/ch32-frameworks-are-details.md) | Frameworks Are Details | don't marry a framework |
| [ch33](chapters/ch33-case-study-video-sales.md) | Case Study: Video Sales | end-to-end applied example |
| [ch34](chapters/ch34-the-missing-chapter.md) | The Missing Chapter | Package by Layer/Feature/Component, Ports and Adapters |
| [ch35](chapters/ch35-architecture-archaeology.md) | Appendix A: Architecture Archaeology | 45 years of real-world war stories |

## Topic Index

- **Abstract Factory** → ch11
- **Acyclic Dependencies Principle (ADP)** → ch14
- **Boundary anatomy (monolith/deployment/process/service)** → ch18, ch25
- **Business rules (Entities, Use Cases)** → ch20
- **Clean Architecture (concentric circles, Dependency Rule)** → ch22
- **Common Closure Principle (CCP)** → ch13
- **Common Reuse Principle (CRP)** → ch13
- **Component cohesion / coupling** → ch13, ch14
- **Conway's Law** → ch16
- **Dependency Inversion Principle (DIP)** → ch11, ch22
- **Embedded architecture (HAL/PAL/OSAL)** → ch29
- **Humble Object pattern** → ch23
- **Interface Segregation Principle (ISP)** → ch10
- **Liskov Substitution Principle (LSP)** → ch09
- **Main component as a plugin** → ch26
- **Open-Closed Principle (OCP)** → ch08
- **Package by Layer / Feature / Component / Ports-and-Adapters** → ch34
- **Partial boundaries** → ch24
- **Plugin architecture pattern** → ch17
- **Presenters and View Models** → ch23
- **Screaming Architecture** → ch21
- **Services vs. architecture boundaries** → ch27
- **Single Responsibility Principle (SRP)** → ch07
- **Stable Abstractions Principle (SAP)** → ch14
- **Stable Dependencies Principle (SDP)** → ch14
- **Test boundary / Testing API** → ch28

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase,
combine with project-specific tools. For topics beyond this book, check related skills
or ask the agent directly. See also the sibling skill `martin-clean-code` for "Clean Code"
and "The Clean Coder" by the same author.
