# Chapter 22: The Clean Architecture

## Core Idea
Clean Architecture synthesizes Hexagonal, DCI, and BCE architectures into one concentric-circle model — Entities, Use Cases, Interface Adapters, Frameworks & Drivers — governed by a single non-negotiable rule: **source code dependencies must point only inward, toward higher-level policies.**

## Frameworks Introduced
- **The Clean Architecture (four concentric circles)**: a synthesis of Hexagonal/Ports-and-Adapters (Cockburn; Freeman & Pryce), DCI (Coplien & Reenskaug), and BCE (Jacobson) into one diagram, chosen because all three share the same objective (separation of concerns via layering: business rules layer(s) + interface layer(s)).
  - When to use: as the default target shape for any nontrivial application architecture.
  - How: place software into four rings by level of abstraction/policy — Entities (innermost) → Use Cases → Interface Adapters → Frameworks & Drivers (outermost) — and enforce the Dependency Rule between them. Nothing stops you from having more than four rings; the count is schematic, the rule is not.
- **The Dependency Rule**: "Source code dependencies must point only inward, toward higher-level policies." Nothing in an inner circle may know anything about an outer circle — not a function, class, variable, or data format from an outer ring may be named in an inner ring.
  - When to use: as the single test applied at every layer boundary, always.
  - How: when control flow must cross from inner to outer (e.g., a use case needs to invoke a presenter), do not call outward directly — define an interface ("output port") in the inner circle and have the outer-circle class implement it, using dynamic polymorphism/Dependency Inversion so source dependencies oppose the flow of control exactly at the boundary.
- **Crossing boundaries with simple data**: only plain, isolated data structures (DTOs, structs, hashmaps, or function arguments) cross a boundary — never Entity objects or framework-native structures (e.g., ORM "row structures"), and always in the format most convenient for the *inner* circle receiving them.
  - When to use: every time data moves across a circle boundary (Controller → UseCaseInteractor → Presenter, etc.).
  - How: package data into request/response objects owned by (or shaped for) the inner circle; convert framework-native formats at the outer edge before they cross inward.

## Key Concepts
- **Entities**: encapsulate enterprise-wide Critical Business Rules; can be objects with methods or plain data structures + functions; reusable across many applications; least likely to change; unaffected by any operational/UI/security change.
- **Use Cases**: application-specific business rules; orchestrate the flow of data to/from Entities and direct Entities to apply their Critical Business Rules; isolated from DB/UI/framework changes but affected when the use case's operational details change.
- **Interface Adapters**: converts data between the format convenient for use cases/entities and the format convenient for an external agency (DB, web); wholly contains MVC (controllers, presenters, views); all SQL is confined here if a SQL DB is used.
- **Frameworks and Drivers**: outermost ring — DB, web framework, and other tools/details; mostly glue code connecting inward; "the web is a detail, the database is a detail."
- **Output port**: an interface declared in an inner circle (e.g., use-case layer) that an outer-circle class (e.g., presenter) implements, so a use case can "call outward" without violating the Dependency Rule.
- **Level (carried over from Ch. 19)**: the deeper (more inward) a ring, the higher its level of abstraction/policy and the lower its rate of change.

## Mental Models
- The outer circles are *mechanisms*; the inner circles are *policies* — always ask "is this a mechanism (detail) or a policy (decision)?" to place code in the right ring.
- Use the Dependency Rule as a naming test: if code in ring N would need to *mention the name* of something declared in ring N+1 (a class, function, or even a data format), that's a violation — regardless of which direction data or control actually flows.
- When control needs to flow outward but dependencies must point inward, use dynamic polymorphism to make the source-code dependency arrow oppose the control-flow arrow exactly at the crossing point (Dependency Inversion applied at every boundary).
- Judge architecture quality by five properties simultaneously: independent of frameworks, testable without UI/DB/web server, independent of UI, independent of database, independent of any external agency.

## Anti-patterns
- **Passing Entity objects or database row structures across a boundary**: forces an inner circle to know about outer-circle formats (e.g., an ORM's row structure), directly violating the Dependency Rule.
- **Letting a use case call a presenter or view directly**: a direct call from an inner-circle use case to an outer-circle presenter violates the "no naming outward" rule; must go through an output port interface owned by the inner circle.
- **Assuming exactly four circles is mandatory**: the ring count is schematic — rigidly forcing every system into four layers when more are warranted misapplies the pattern; what's mandatory is the Dependency Rule, not the ring count.
- **Letting the database or web framework leak into use cases/entities** (e.g., SQL or `HttpRequest` types appearing inward of Interface Adapters): destroys the independence-from-DB/UI properties that are the entire point of the architecture.

## Reference Tables
| Ring (outer → inner) | Contains | Changes when... | Knows about |
|---|---|---|---|
| Frameworks & Drivers | DB, web framework, glue code | Tooling/infra choices change | Interface Adapters (inward only) |
| Interface Adapters | Controllers, Presenters, Views, gateways, data converters | UI/DB technology or presentation format changes | Use Cases (inward only) |
| Use Cases | Application-specific business rules, orchestration of Entities | This application's operational rules change | Entities (inward only) |
| Entities | Critical Business Rules, Critical Business Data | Enterprise-wide business rules change (rare) | Nothing outward |

| Clean Architecture ring | Prior architectures' equivalent |
|---|---|
| Entities / Use Cases | Hexagonal's "inside" (business logic) |
| Interface Adapters / Frameworks & Drivers | Hexagonal's "outside" (ports & adapters) |
| — | DCI (Coplien & Reenskaug), BCE (Jacobson) — same separation-of-concerns objective, different vocabulary |

## Worked Example
**A typical web-based Java system with a database (Fig. 22.2), tracing how data crosses boundaries:**
1. The web server gathers user input and hands it to the **Controller** (Interface Adapters ring).
2. The Controller packages that input into a **plain old Java object** (an Input Data structure) and passes it through an **InputBoundary** interface — owned by the inner ring — into the **UseCaseInteractor** (Use Cases ring). This is the DTO-not-Entity rule in action: the Controller never hands the interactor a database row or framework request object.
3. The `UseCaseInteractor` interprets that data and "controls the dance of the Entities" — invoking Critical Business Rules on Entity objects (innermost ring).
4. To load/persist Entity data, the interactor calls a **DataAccessInterface** (an output port it owns) — the Database implementation lives outward and implements that interface, so the dependency still points inward even though control flows outward to fetch data.
5. On completion, the interactor gathers results from the Entities and builds an **OutputData** object — again a plain old Java object, not an Entity — and passes it outward through an **OutputBoundary** interface to the **Presenter**.
6. The **Presenter** (Interface Adapters ring) repackages `OutputData` into a **ViewModel** — another plain object containing only Strings, booleans, and enums (e.g., a `Date` becomes a pre-formatted date string; a `Currency` becomes a formatted string plus a "negative" boolean flag; button/menu labels and their grayed-out flags are precomputed here).
7. The **View** (outermost of Interface Adapters, bordering Frameworks & Drivers) does almost nothing but copy ViewModel fields onto the screen/HTML — it is the Humble Object with no logic to test.

Every arrow in this flow that crosses a ring boundary points inward — even where control flow (step 4, step 5-6) moves outward, the corresponding *source-code dependency* (via DataAccessInterface / OutputBoundary) points back toward the Use Cases/Entities rings, satisfying the Dependency Rule.

## Key Takeaways
1. Memorize and apply verbatim: "Source code dependencies must point only inward, toward higher-level policies" — this is the one rule that makes the whole architecture work.
2. Never let inner-circle code name (reference) anything declared in an outer circle — classes, functions, variables, or data formats.
3. When control must flow outward, invert the dependency with an interface (output port) owned by the inner circle and implemented outward — never call outward directly.
4. Only simple, boundary-owned data structures (DTOs/request-response objects) cross ring boundaries — never Entities, never framework-native row/request objects.
5. The four rings are schematic, not sacred — add more if your system needs them, but the Dependency Rule is non-negotiable regardless of ring count.
6. A correctly built Clean Architecture yields five properties simultaneously: framework-independent, testable, UI-independent, database-independent, and independent of any external agency.

## Connects To
- **Ch 19 (Policy and Level)**: the ring model is level-based dependency direction generalized into a full concentric structure — "the further in you go, the higher level."
- **Ch 20 (Business Rules)**: Entities and Use Cases chapters map directly onto the two innermost rings here.
- **Ch 21 (Screaming Architecture)**: Frameworks & Drivers being the outermost, least significant ring is the architectural embodiment of "frameworks are details, not architecture."
- **Ch 23 (Presenters and Humble Objects)**: the Presenter/View split and DataAccessInterface/gateway pattern introduced here are elaborated as instances of the Humble Object pattern.
- **Ch 24 (Partial Boundaries)**: discusses cheaper, partial ways to implement the same boundary-crossing discipline when a full reciprocal-interface boundary isn't yet justified.
- **Dependency Inversion Principle**: the core mechanism (interfaces owned inward, implemented outward) used to reconcile inward dependencies with outward control flow at every boundary.
