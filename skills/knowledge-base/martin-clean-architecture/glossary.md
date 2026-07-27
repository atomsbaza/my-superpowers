# Glossary — Clean Architecture (Robert C. Martin)

**Abstract Factory** — a pattern where an interface with a creation method is implemented by a concrete factory, so callers depend only on abstractions when instantiating volatile concrete classes (Ch 11).

**Abstractness (A)** — component metric: `A = Na / Nc` (number of abstract classes/interfaces over total classes); 0 = fully concrete, 1 = fully abstract (Ch 14).

**Acyclic Dependencies Principle (ADP)** — "Allow no cycles in the component dependency graph" (Ch 14).

**Axis of change** — a dimension along which parts of a system change at different rates/for different reasons; boundaries are drawn where an axis of change appears (Ch 7, Ch 17, Ch 25).

**Boundary** — a line separating software elements such that those on one side cannot know about those on the other, managed by source-code dependency direction (Ch 17, Ch 18).

**Central Transform** — the highest-level component in a data-flow diagram, farthest from both inputs and outputs, where converging streams of data meet (Ch 19, Ch 25).

**Clean Architecture** — a synthesis of Hexagonal, DCI, and BCE architectures into four concentric circles (Entities, Use Cases, Interface Adapters, Frameworks & Drivers) governed by the Dependency Rule (Ch 22).

**Common Closure Principle (CCP)** — "Gather into components those classes that change for the same reasons and at the same times. Separate into different components those classes that change at different times and for different reasons" (Ch 13).

**Common Reuse Principle (CRP)** — "Don't force users of a component to depend on things they don't need" (Ch 13).

**Component** — "the smallest entities that can be deployed as part of a system"; must be both independently deployable and independently developable (Ch 12).

**Conway's Law** — "Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure" (Ch 16).

**Dependency Injection (confined to Main)** — DI framework resolution should occur only inside Main; the rest of the system receives plain objects (Ch 26).

**Dependency Inversion Principle (DIP)** — "The most flexible systems are those in which source code dependencies refer only to abstractions, not to concretions" (Ch 5, Ch 11).

**Dependency Rule** — "Source code dependencies must point only inward, toward higher-level policies"; nothing in an inner circle may know anything about an outer circle (Ch 11, Ch 22).

**Distance from Main Sequence (D)** — `D = |A + I - 1|`; measures how far a component sits from the ideal abstractness/instability balance (Ch 14).

**Entity** — an object binding Critical Business Rules to Critical Business Data; enterprise-wide, reusable, unaware of use cases (Ch 20, Ch 22).

**Facade (partial boundary)** — a class listing all services as methods and delegating to them, the cheapest boundary placeholder with no dependency inversion, leaving a transitive dependency intact (Ch 24).

**Facade (SRP solution)** — a thin class that instantiates and delegates to separated single-responsibility classes so callers don't manage multiple objects (Ch 7).

**Firmware (redefined)** — code classified by what it depends on (hardware/processor/OS specifics), not by storage medium (Ch 29).

**Humble Object pattern** — splitting hard-to-test behavior (kept mechanically trivial) from a sibling that holds all testable logic; recurs as Presenter/View, gateway/database, service listener/service (Ch 23).

**Instability (I)** — component metric: `I = Fan-out / (Fan-in + Fan-out)`; 0 = maximally stable, 1 = maximally unstable (Ch 14).

**Interface Adapters** — the Clean Architecture ring converting data between formats convenient for use cases/entities and formats convenient for external agencies (DB, web); contains MVC (Ch 22).

**Interface Segregation Principle (ISP)** — don't force clients to depend on interfaces (operations) they don't use (Ch 10).

**Level** — a component's distance from system inputs/outputs; higher level = farther from I/O, more abstract policy (Ch 19).

**Liskov Substitution Principle (LSP)** — a type S is a true subtype of T only if objects of S can replace objects of T in any program without altering that program's observable behavior (Ch 9).

**Main component** — the ultimate detail and lowest-level policy in a system; creates and wires Factories/Strategies, then hands control to high-level abstractions; treated as a plugin (Ch 26).

**Main Sequence** — the line on the A/I graph connecting (0,1) and (1,0), representing the ideal balance of abstractness and stability for a component (Ch 14).

**Object-Oriented Programming (architectural definition)** — "the ability, through the use of polymorphism, to gain absolute control over every source code dependency in the system" (Ch 5).

**Open-Closed Principle (OCP)** — "A software artifact should be open for extension but closed for modification" (Bertrand Meyer, 1988) (Ch 8).

**Output port** — an interface declared in an inner circle that an outer-circle class implements, letting inner code "call outward" without violating the Dependency Rule (Ch 22).

**Package by Component** — Simon Brown's preferred organizational style: bundle all responsibilities for one business capability behind a single clean interface (Ch 34).

**Package by Feature** — vertical slicing by domain concept/feature, with all related types in one package (Ch 34).

**Package by Layer** — horizontal slicing by technical role (web/service/persistence); strict layered architecture depends only on the next lower layer (Ch 34).

**Plugin architecture** — arrangement where core business rules are independent of components with optional or multiple implementations; dependencies point from detail toward policy (Ch 5, Ch 17, Ch 19).

**Policy vs. Details** — every system decomposes into policy (business rules, the true value) and details (IO devices, databases, frameworks) that policy should not depend on (Ch 15).

**Ports and Adapters (Hexagonal Architecture)** — domain-focused "inside" fully independent of technical "outside" (UI, DB, integrations); outside depends on inside, never the reverse (Ch 22, Ch 34).

**Reuse/Release Equivalence Principle (REP)** — "The granule of reuse is the granule of release" (Ch 13).

**Screaming Architecture** — a system's top-level structure should announce its use cases/business domain, not the framework it uses (Ch 21).

**Segregation of Mutability** — splitting an application into immutable (purely functional) components and a smaller set of mutable components protected by transactional memory (Ch 6).

**Service** — the strongest architectural boundary type: an independent process communicating purely over the network, with the highest latency and no shared address space (Ch 18); by itself not architecturally significant unless it follows the Dependency Rule (Ch 27).

**Single Responsibility Principle (SRP)** — "A module should be responsible to one, and only one, actor" (Ch 7).

**Software architecture, goal of** — "to minimize the human resources required to build and maintain the required system" (Ch 1).

**Stable Abstractions Principle (SAP)** — "A component should be as abstract as it is stable" (Ch 14).

**Stable Dependencies Principle (SDP)** — "Depend in the direction of stability" (Ch 14).

**Structured Programming** — imposes discipline on direct transfer of control, replacing unrestrained `goto` with sequence, selection, and iteration (Dijkstra, 1968) (Ch 3, Ch 4).

**Testing API** — a dedicated API, a superset of production interactors, that tests use to verify business rules while bypassing security and expensive resources (Ch 28).

**Two values of software** — behavior (does it work) and architecture/structure (is it easy to change); structure is the more important because it keeps software "soft" (Ch 2).

**Use Case** — application-specific business rules describing how an automated system is used; orchestrates Entities but only exists because the system is automated (Ch 20, Ch 22).

**Zone of Pain** — the region near (0,0) on the A/I graph: stable and concrete, therefore rigid and hard to extend (Ch 14).

**Zone of Uselessness** — the region near (1,1) on the A/I graph: abstract with no dependents, i.e., useless leftover abstractions (Ch 14).
