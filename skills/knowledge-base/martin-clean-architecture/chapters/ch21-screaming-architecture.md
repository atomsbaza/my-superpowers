# Chapter 21: Screaming Architecture

## Core Idea
A system's top-level architecture should "scream" its use cases and business domain (e.g., "Health Care System"), not the frameworks it happens to use (e.g., "Rails app") — frameworks are tools to be used, never the architecture itself.

## Frameworks Introduced
- **The "Scream" test**: judge an architecture by what its top-level directory/package structure communicates about intent.
  - When to use: any time evaluating or designing a codebase's top-level structure.
  - How: look at the highest-level source layout and ask whether it announces the domain (use cases) or the delivery mechanism/framework; if it announces the framework, the architecture has failed.
- **Use-case-driven architecture** (attributed to Ivar Jacobson's *Object Oriented Software Engineering: A Use Case Driven Approach*): structure the architecture to support and reveal the system's use cases first, deferring framework/tool/environment decisions.
  - When to use: at the outset of architecting any application.
  - How: design structures purely around use cases; treat frameworks, databases, web servers as details/options left open, decidable much later and changeable without redesign.

## Key Concepts
- **Delivery mechanism**: how the system is exposed to the world (web, console, thick client, service) — always a detail, never architecture-defining.
- **Framework as tool vs. framework as way of life**: frameworks should be adopted skeptically and kept at arm's length, not allowed to dictate the whole system's structure.
- **Testable architecture**: a direct consequence of use-case-centered design — use cases and Entities should be unit-testable without a running web server, database, or any framework in place.

## Mental Models
- Compare a house blueprint vs. a library blueprint — each "screams" its purpose through room layout, independent of construction materials; apply the same test to source trees: they should scream the domain, not "Spring/Hibernate" or "Rails."
- View every framework "with a jaded eye" — ask "how do I use it, and how do I protect myself from it?" rather than adopting the framework author's all-encompassing worldview.
- When a new engineer looks at the repo and asks "where are the views/controllers?", the correct answer is "those are details we can decide later" — use this as a litmus test for whether the architecture has stayed use-case-centric.

## Anti-patterns
- **Naming/structuring the top-level codebase after the framework** (e.g., organizing by Rails/MVC conventions at the top level): signals the architecture was outsourced to the framework instead of being driven by use cases, and locks in delivery-mechanism decisions prematurely.
- **Treating "the web" as an architecture-defining decision**: the web is just an IO device/delivery mechanism; committing to it early removes the option to deliver via console, thick client, or service without disruption.
- **Letting a framework's examples/conventions dictate system structure wholesale**: framework authors and their disciples present an "all-encompassing, let-the-framework-do-everything" stance that erodes use-case emphasis if adopted uncritically.

## Worked Example
Martin poses the question directly: what does your application's top-level directory structure scream?
- If it screams "HOME" for a house blueprint or "LIBRARY" for a library blueprint (via room arrangement, not building materials), a software architecture should analogously scream "Health Care System" or "Accounting System" or "Inventory Management System" from its top-level packages.
- Contrast: an architecture that instead screams "Rails," "Spring/Hibernate," or "ASP" has confused the delivery/framework layer for the actual architecture.
- Test for success: a new programmer reading the repo should be able to learn all the use cases of the system while remaining unable to tell whether it's delivered via web, console, or thick client — and should be able to unit-test all use cases without the web server or database running, because Entities are plain objects and use cases coordinate them without framework dependencies.

## Key Takeaways
1. Structure the top level of a codebase around use cases/domain, not around the framework in use.
2. Defer framework, database, and web-server decisions as long as possible — a good architecture makes these easy to change later.
3. Treat the delivery mechanism (web, console, thick client, service) as a detail, never as an architectural driver.
4. Use testability without frameworks/DB/web-server running as a litmus test for whether the architecture is properly use-case-centered.
5. Adopt frameworks skeptically — use their strengths without letting them dictate the whole system's structure.

## Connects To
- **Ch 20 (Business Rules)**: use cases are exactly the thing the architecture should scream about; screaming architecture is the packaging discipline that makes use cases visible.
- **Ch 22 (The Clean Architecture)**: the "frameworks as details on the outside" principle here becomes the literal outermost circle (Frameworks & Drivers) in the concentric diagram.
- **Ivar Jacobson, *Object Oriented Software Engineering: A Use Case Driven Approach***: the source of the use-case-driven architecture philosophy referenced directly.
