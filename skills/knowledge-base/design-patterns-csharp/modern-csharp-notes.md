# Modern C# Notes (2025-2026 Freshness Check)

This book was published in 2018, targeting roughly C# 6/7. The chapters preserve its code and terminology faithfully, but the C# language and .NET ecosystem have changed substantially since. This file summarizes what's changed, sourced from a Medium research pass (via `/mediumlm`, with Medium's search API blocked and results found via WebSearch `site:medium.com` fallback) covering articles published Aug 2025–Jan 2026. Read this alongside any chapter to calibrate how much of its code you'd actually write today.

**Sources**: [Modern C# Design Patterns You Should Actually Use in 2025](https://medium.com/@vahidbakhtiaryinfo/modern-c-design-patterns-you-should-actually-use-in-2025-32dd41df38f9) (Vahid Bakhtiary, Oct 2025); [Design Patterns in C#: Which Ones Still Matter in 2026](https://medium.com/@kerimkkara/design-patterns-in-c-which-ones-still-matter-in-2026-f41b057cfede) (Kerim Kara, Jan 2026); [Modern Design Patterns in .NET 10 and C# 12](https://medium.com/@zand.arash83/modern-design-patterns-in-net-21a69f955be7) (Arash Zand, Aug 2025).

## The Big Picture

Design patterns in C# have not become obsolete — they've been absorbed, simplified, or replaced by language/runtime features that didn't exist in 2018. Both 2025/2026 sources converge on the same framing: don't apply all 23 GoF patterns by rote; ask whether modern C# or .NET already gives you the pattern's benefit for free. Dependency Injection in particular is now described as "infrastructure, not a pattern" — `Microsoft.Extensions.DependencyInjection` is assumed present from the first line of any ASP.NET Core / minimal API / background service.

## Per-Pattern Status (book chapter → 2025/26 verdict)

| Pattern (book ch.) | 2025/26 status | What replaced or simplified it |
|---|---|---|
| Singleton (ch1) | **Mostly dead as hand-written code** | `builder.Services.AddSingleton<T>()` — DI container owns lifetime/creation/disposal; hand-rolled static-instance/double-checked-locking Singleton is now a red flag except in narrow low-level infra code (process-wide caches, native resource managers) |
| Prototype (ch2) | Niche, still valid | Records' `with` expressions (C# 9+) cover simple immutable-copy cases; classic `ICloneable`-style Prototype still used for deep-clone of mutable object graphs |
| Builder (ch3) | **Still fully relevant** | Optional parameters/records reduce *some* need, but fluent builders remain the standard for objects with validation, conditional construction, or many optional fields |
| Factory Method (ch4) / Abstract Factory (ch5) | **Radically simplified, situationally relevant** | DI containers act as large-scale object factories for most cases; factories still matter only when *creation logic is itself business logic* (e.g. picking a notification channel by user attributes) — and are now often written as a `switch` expression over pattern matching instead of a class hierarchy |
| Proxy (ch6) | **More relevant than ever** | Now mostly implicit — HTTP clients, gRPC stubs, `DelegatingHandler`, and resilience libraries (circuit breakers/retries) generate proxies for you; hand-written proxies still used for auth/caching gateways at trust boundaries |
| Decorator (ch7) | **Still fully relevant** | The standard idiom for cross-cutting concerns (caching, logging, retry) wrapped around a DI-registered interface; integrates natively with DI container composition |
| Adapter (ch8) | **Still essential**, least controversial pattern surviving | Used constantly at integration boundaries (third-party/legacy APIs); doesn't disappear because "integration never stops" |
| Facade (ch9) | **Still relevant**, but thinner | Modern Facades are intentionally small and delegate real work — a large "god class" Facade is now itself flagged as an anti-pattern, not a win |
| Flyweight (ch10) | Niche but real | Shows up in high-throughput logging/telemetry/data-processing where GC pressure from many similar objects matters; still requires immutable, thread-safe shared instances |
| Composite (ch11) | Stable, unchanged in spirit | No major replacement; tree-structured domain data still modeled this way |
| Bridge (ch12) | Stable, used sparingly | Still valuable for cross-platform SDKs/libraries; sources warn against applying it prematurely — only when independent abstraction/implementation evolution is truly needed |
| Visitor (ch13) | Stable but less common | Pattern matching over closed hierarchies (`sealed` + `switch` expressions) covers many cases that used to need Visitor's double-dispatch |
| Observer (ch14) | **Reframed, not dead** | C# `event`/`delegate` already *is* Observer, absorbed into the language; at scale it's now implemented via message brokers/event streams rather than in-memory subscriber lists — hand-rolled subscription-list management is now considered a mistake |
| Strategy (ch15) | **Aged the best of all 23 patterns** | Described as "the quiet backbone of modern C# systems" — pairs naturally with DI (`IEnumerable<IStrategy>` injection) and pattern matching; strategies are now often stateless records/delegates instead of full classes |
| Template Method (ch16) | **Largely replaced** | Modern C# favors composition (inject `Func<>`/`Action<>` delegates into a pipeline) over the inheritance-based abstract-method structure; called out as the pattern that "has not aged as gracefully as others" |
| Command (ch17) | **Quiet renaissance** | Central to CQRS-style APIs — a command is now typically a `record` (e.g. `record CreateOrderCommand(...)`), dispatched via a mediator library (MediatR) with pipeline behaviors for validation/logging/transactions |
| Iterator (ch18) | Absorbed into the language | `IEnumerable<T>`/`yield return`/LINQ already are this pattern; hand-written iterator classes are rarely needed for anything but bespoke traversal logic |
| Memento (ch19) | Still relevant, more so | Undo/redo, auditing, and state-recovery needs have grown; now often expressed as an immutable `record` snapshot, and pairs with event sourcing |
| State (ch20) | Stable, valuable for workflows | Particularly cited for long-running workflows (order processing, approvals) where state objects can be persisted/rehydrated across async boundaries |
| Mediator (ch21) | **Became foundational**, not niche | The "backbone of decoupled modern systems" via libraries like MediatR; commands/queries/notifications route through it, with pipeline behaviors replacing manual cross-cutting code |
| Chain of Responsibility (ch22) | Reframed as pipelines/middleware | ASP.NET Core middleware *is* Chain of Responsibility; rarely hand-implemented as a linked list of handler classes anymore |
| Interpreter (ch23) | Still rare, not obsolete | Used in rules engines, feature-flag evaluation, and config-driven access control; for general expression needs, most reach for expression trees/LINQ instead |
| Simple Factory (ch24) | Simplified via pattern matching | The `if`-chain factory of 2018 is now typically a `switch` expression over object patterns (`user switch { { IsInEU: true } => ..., _ => ... }`) |
| Null Object (ch25) | Stable, unchanged in spirit | No major replacement noted; still a clean way to avoid null checks scattered through calling code |
| MVC (ch26) | Displaced by newer architectural styles | ASP.NET Core still supports MVC, but Minimal APIs (route-grouped, delegate-based endpoints) are now the more common default for new services, especially APIs/microservices |
| Repository (referenced across chapters, not its own GoF chapter) | **Often misused** | EF Core already provides much of what a repository wraps; a repository that just forwards to `DbContext` adds no value — only justified when it protects invariants or coordinates complex persistence |

## Language Features That Now "Bake In" Old Patterns

- **Records + `with` expressions** (C# 9+) → replace hand-written Value Objects and much of Prototype's copy-semantics use case
- **Enhanced pattern matching / property patterns / switch expressions** (C# 8-12) → replace many Strategy/Factory `if`-chains with declarative dispatch
- **Primary constructors** (C# 12) → reduce DI constructor boilerplate
- **Source generators** → replace hand-written Factory/serialization boilerplate in performance-sensitive code
- **`IObservable<T>` / events / message brokers** → absorb Observer into the runtime/ecosystem rather than requiring a hand-rolled subject/observer class pair
- **Minimal APIs + route groups** → reduce the controller-based MVC ceremony the book's Chapter 26 demonstrates

## How to Use This With the Chapters

Each chapter file (ch01-ch26 covering actual patterns) still teaches the *correct* GoF intent, structure, and participant roles — that part is durable and this research doesn't change it. Where the chapter's C# code differs from what you'd write today, use the table above to know whether: (a) the pattern is still written by hand largely as shown (Builder, Composite, State, Null Object, Memento), (b) it's now usually delegate/record-based instead of class-hierarchy-based (Strategy, Command, Simple Factory), or (c) it's now typically provided by the framework/a library rather than hand-written (Singleton, Observer, Iterator, Chain of Responsibility, Mediator).
