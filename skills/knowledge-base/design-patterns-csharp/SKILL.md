---
name: design-patterns-csharp
description: "Knowledge base from \"Design Patterns in C#: A Hands-on Guide with Real-World Examples\" (2018) by Vaskaran Sarcar. Use when applying GoF design patterns (Singleton, Factory, Strategy, Observer, Decorator, etc.) in C#/.NET, studying pattern intent/structure, or checking whether a 2018-era pattern implementation still matches 2025/26 idiomatic C#."
---

<!-- argument-hint: [pattern name, topic, or chapter number] -->

# Design Patterns in C#: A Hands-on Guide with Real-World Examples
**Author**: Vaskaran Sarcar | **Pages**: ~465 | **Chapters**: 30 (23 core GoF/common patterns + criticisms/anti-patterns/hardening/FAQ) | **Generated**: 2026-07-31

## How to Use This Skill

- **Without arguments** — load core frameworks below for reference
- **With a pattern name** — ask about `Strategy`, `Observer`, `Adapter vs Decorator`, or another indexed topic; I find and read the relevant chapter
- **With a chapter** — ask for `ch15` or `chapter 21`; I load that specific chapter file
- **Freshness check** — ask "is this pattern still relevant" or "how would this look in modern C#"; I'll read [modern-csharp-notes.md](modern-csharp-notes.md), which summarizes 2025/26 research on what's changed since this book's 2018 publication
- **Browse** — ask "what chapters do you have?" to see the full index

This book's C# code targets roughly C# 6/7 (2018). Pattern *intent and structure* are timeless (they're the original 1994 GoF catalog plus a few common non-GoF idioms), but the *idiomatic implementation* has shifted — see [modern-csharp-notes.md](modern-csharp-notes.md) for a per-pattern rundown of what's changed, sourced from a 2025/26 Medium research pass.

---

## Core Frameworks & Mental Models

**GoF's three pattern categories** — Creational (Singleton, Prototype, Builder, Factory Method, Abstract Factory, Simple Factory), Structural (Proxy, Decorator, Adapter, Facade, Flyweight, Composite, Bridge), Behavioral (Visitor, Observer, Strategy, Template Method, Command, Iterator, Memento, State, Mediator, Chain of Responsibility, Interpreter, Null Object). Category tells you *what kind* of problem a pattern solves — object creation, object composition, or object interaction. (Ch1-Ch25)

**Class patterns vs. Object patterns** — GoF's own split: class patterns (Template Method) fix relationships at compile time via inheritance; object patterns (most of the catalog) use composition, so relationships can change at runtime. Prefer object patterns/composition when variation is expected. (Ch30)

**"Does the framework already give me this?"** — the single most important modern-day filter before applying any pattern here. DI containers absorb Singleton/Factory. `event`/`IObservable<T>` absorb Observer. `IEnumerable<T>`/LINQ absorb Iterator. ASP.NET Core middleware absorbs Chain of Responsibility. Ask this before writing a pattern class by hand. (modern-csharp-notes.md)

**Proxy vs. Decorator vs. Adapter** — all three wrap another object and delegate, but differ by intent: Adapter translates a mismatched interface, Proxy controls/gates access, Decorator adds an orthogonal responsibility. The book itself repeatedly cross-references this distinction in its Q&A sections. (Ch6, Ch7, Ch8)

**Factory Method vs. Abstract Factory vs. Simple Factory** — Factory Method uses subclassing to vary a single product's creation; Abstract Factory creates whole families of related products; Simple Factory (not in the original GoF catalog) is just a centralized conditional/switch — don't over-engineer a Simple Factory need into a full Factory Method hierarchy. (Ch4, Ch5, Ch24)

**Strategy has aged the best of all 23 patterns** — per 2025/26 sources, Strategy pairs naturally with DI (`IEnumerable<IStrategy>` injection) and modern pattern matching; it remains the cleanest answer to "behavior must vary at runtime." (Ch15, modern-csharp-notes.md)

**Command + Memento for undo/redo and auditability** — Command encapsulates the action, Memento captures the state to roll back to; in 2025/26 practice both are typically `record` types, with Command dispatched through a mediator library. (Ch17, Ch19)

**Anti-patterns aren't the opposite of patterns — they're patterns applied wrong** — God class, Golden Hammer, Not-Invented-Here syndrome, and "reimplementing what the language already provides" are the book's named anti-patterns; recognizing them matters as much as knowing the patterns themselves. (Ch28)

---

## Chapter Index

| # | Pattern / Topic | Category |
|---|-------|----------------|
| [ch01](chapters/ch01-singleton-pattern.md) | Singleton | Creational |
| [ch02](chapters/ch02-prototype-pattern.md) | Prototype | Creational |
| [ch03](chapters/ch03-builder-pattern.md) | Builder | Creational |
| [ch04](chapters/ch04-factory-method-pattern.md) | Factory Method | Creational |
| [ch05](chapters/ch05-abstract-factory-pattern.md) | Abstract Factory | Creational |
| [ch06](chapters/ch06-proxy-pattern.md) | Proxy | Structural |
| [ch07](chapters/ch07-decorator-pattern.md) | Decorator | Structural |
| [ch08](chapters/ch08-adapter-pattern.md) | Adapter | Structural |
| [ch09](chapters/ch09-facade-pattern.md) | Facade | Structural |
| [ch10](chapters/ch10-flyweight-pattern.md) | Flyweight | Structural |
| [ch11](chapters/ch11-composite-pattern.md) | Composite | Structural |
| [ch12](chapters/ch12-bridge-pattern.md) | Bridge | Structural |
| [ch13](chapters/ch13-visitor-pattern.md) | Visitor | Behavioral |
| [ch14](chapters/ch14-observer-pattern.md) | Observer | Behavioral |
| [ch15](chapters/ch15-strategy-pattern.md) | Strategy (Policy) | Behavioral |
| [ch16](chapters/ch16-template-method-pattern.md) | Template Method | Behavioral |
| [ch17](chapters/ch17-command-pattern.md) | Command | Behavioral |
| [ch18](chapters/ch18-iterator-pattern.md) | Iterator | Behavioral |
| [ch19](chapters/ch19-memento-pattern.md) | Memento | Behavioral |
| [ch20](chapters/ch20-state-pattern.md) | State | Behavioral |
| [ch21](chapters/ch21-mediator-pattern.md) | Mediator | Behavioral |
| [ch22](chapters/ch22-chain-of-responsibility-pattern.md) | Chain of Responsibility | Behavioral |
| [ch23](chapters/ch23-interpreter-pattern.md) | Interpreter | Behavioral |
| [ch24](chapters/ch24-simple-factory-pattern.md) | Simple Factory (non-GoF) | Creational |
| [ch25](chapters/ch25-null-object-pattern.md) | Null Object (non-GoF) | Behavioral |
| [ch26](chapters/ch26-mvc-pattern.md) | MVC | Architectural |
| [ch27](chapters/ch27-criticisms-of-design-patterns.md) | Criticisms of Design Patterns | Discussion |
| [ch28](chapters/ch28-anti-patterns.md) | Anti-patterns | Discussion |
| [ch29](chapters/ch29-sealing-the-leaks.md) | Sealing the Leaks in Your Applications | Practical hardening |
| [ch30](chapters/ch30-faq.md) | FAQ | Cross-pattern Q&A digest |

## Topic Index

- **Access control / gating** → ch6 (Proxy)
- **Algorithm interchangeability** → ch15 (Strategy)
- **Anti-patterns / code smells** → ch27, ch28
- **Cross-cutting concerns (logging, caching, retry)** → ch7 (Decorator)
- **Cross-platform / independent abstraction & implementation** → ch12 (Bridge)
- **Event notification** → ch14 (Observer)
- **Family-of-objects creation** → ch5 (Abstract Factory)
- **Interface mismatch / legacy integration** → ch8 (Adapter)
- **Memory efficiency at scale** → ch10 (Flyweight)
- **Modern C# equivalents / freshness check** → [modern-csharp-notes.md](modern-csharp-notes.md)
- **MVC / presentation architecture** → ch26
- **Null handling without checks** → ch25 (Null Object)
- **Object creation (single instance)** → ch1 (Singleton)
- **Object creation (via copying)** → ch2 (Prototype)
- **Object creation (via subclassing)** → ch4 (Factory Method)
- **Object creation (via conditional)** → ch24 (Simple Factory)
- **Request encapsulation / undo-redo** → ch17 (Command), ch19 (Memento)
- **State-dependent behavior** → ch20 (State)
- **Step-by-step complex object construction** → ch3 (Builder)
- **Subsystem simplification** → ch9 (Facade)
- **Tree/part-whole structures** → ch11 (Composite)
- **Traversal without exposing structure** → ch18 (Iterator)
- **Loose coupling between many objects** → ch21 (Mediator)
- **Request handling chains / pipelines** → ch22 (Chain of Responsibility)
- **Grammar/expression evaluation** → ch23 (Interpreter)
- **Operations across a stable type hierarchy** → ch13 (Visitor)
- **Robustness / memory leaks / GC** → ch29 (Sealing the Leaks)
- **Cross-pattern Q&A** → ch30 (FAQ)

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all 26 techniques/patterns from the book with trade-offs
- [cheatsheet.md](cheatsheet.md) — decision rules, decision trees (Proxy/Decorator/Adapter, Factory variants), and tells/smells
- [modern-csharp-notes.md](modern-csharp-notes.md) — 2025/26 freshness check: per-pattern status table + what language/framework features now replace or simplify each pattern, sourced via `/mediumlm` research

---

## Scope & Limits

This skill covers the book's 2018-era content plus a supplementary 2025/26 modernization pass (see modern-csharp-notes.md). The book's C# code is preserved faithfully in each chapter — it is NOT rewritten to modern idiom, since the book's own syntax is what a reader following along would see. For current framework-specific guidance (exact .NET version APIs, current MediatR/DI syntax), verify against current Microsoft docs — the modernization notes summarize direction and status, not a full modern reimplementation of each pattern.
