# Martin Clean Code Glossary

**Abstract Factory** — pattern hiding object creation behind an abstract interface so callers don't depend on concrete types (Ch 6, Ch 16).
**Acceptance Test** — executable spec jointly written by business and devs defining "done" (Ch 24).
**Active Record** — DTO with public accessors plus navigational methods (save/find); keep business rules out of it (Ch 6).
**Adapter Pattern** — bridges your own interface to a third-party/undefined API once it exists (Ch 8).
**Adversarial Roles** — devs and managers each defend their objectives assertively to reach the best outcome (Ch 19).
**AOP (Aspect-Oriented Programming)** — weaves cross-cutting concerns (logging, persistence) into code non-invasively (Ch 11).
**Bean** — DTO with private fields and public getters/setters; illusion of encapsulation without real behavior (Ch 6).
**Big Design Up Front (BDUF)** — designing full architecture before coding; discouraged in favor of incremental growth (Ch 11).
**Boundary** — the contact point between your code and third-party/undefined code, kept small and wrapped (Ch 8).
**Boy Scout Rule** — leave the code cleaner than you found it, on every touch (Ch 1, Ch 15, Ch 18).
**Coding Dojo / Kata / Wasa / Randori** — deliberate solo, paired, and group practice exercises for reflexive coding skill (Ch 23).
**Cohesion** — how many methods use how many instance variables; low cohesion signals a hidden class (Ch 10).
**Command Query Separation** — a function should either do something or answer something, not both (Ch 3).
**Commitment (Say-Mean-Do)** — a real promise is "I will X by Y," stated to someone, and honored (Ch 20).
**Concurrency Defense Principles** — SRP for concurrency, limit shared data scope, use copies, keep threads independent (Ch 13).
**Cross-Cutting Concerns** — behaviors (persistence, security, transactions) that span normal class boundaries; solved via AOP/proxies (Ch 11).
**Data/Object Anti-Symmetry** — objects hide data and expose behavior; data structures expose data and have no behavior (Ch 6).
**Dependency Injection (DI) / Inversion of Control** — an object never builds its own collaborators; a container/main wires them in (Ch 11).
**Dependency Inversion Principle (DIP)** — depend on abstractions, not concrete/volatile implementations (Ch 10).
**DRY (No Duplication)** — eliminate duplicated code/logic; the highest-priority code smell (Ch 1, Ch 12, Ch 17).
**DTO (Data Transfer Object)** — pure data class with public fields and no behavior (Ch 6).
**Emergent Design** — good architecture arising from continuously applying the Four Rules rather than upfront planning (Ch 12).
**Extract Try/Catch** — pull try and catch bodies into their own named functions so error handling is isolated (Ch 3, Ch 7).
**Feature Envy** — a method that reaches into another object's data more than its own (Ch 6, Ch 16, Ch 17).
**F.I.R.S.T.** — Fast, Independent, Repeatable, Self-Validating, Timely: properties of clean unit tests (Ch 9).
**Flag Argument** — a boolean parameter signaling a function does two different things; a smell (Ch 3, Ch 17).
**Focus-Manna / Pomodoro** — treat focus as a depleting resource; protect it with 25-minute timeboxed work blocks (Ch 26).
**Four Rules of Simple Design (Kent Beck)** — passes tests, no duplication, expresses intent, minimizes classes/methods, in priority order (Ch 1, Ch 12).
**God Class** — a class that has accreted far too many unrelated responsibilities (Ch 10).
**Grand Redesign in the Sky** — the failure pattern of rewriting a mess from scratch instead of continuous cleanup (Ch 1).
**Hybrid (structure)** — a class that is half object (behavior) and half data structure (exposed fields); worst of both worlds (Ch 6).
**Intention-Revealing Names** — a name should answer why it exists, what it does, and how it's used, without needing a comment (Ch 2).
**Law of Demeter** — a method should only call methods on itself, its args, objects it creates, or its own fields — "talk to friends, not strangers" (Ch 6).
**Learning Tests** — tests written purely to verify and document understanding of a third-party API (Ch 8).
**Newspaper Metaphor** — structure a file like an article: name/summary at top, increasing detail descending (Ch 5).
**One Level of Abstraction per Function** — every statement in a function must sit at the same conceptual altitude (Ch 3).
**Open-Closed Principle (OCP)** — classes should be open for extension, closed for modification (Ch 10).
**PERT (Program Evaluation and Review Technique)** — converts optimistic/nominal/pessimistic estimates into a probability distribution (µ=(O+4N+P)/6, σ=(P−O)/6) (Ch 27).
**POJO** — a domain object with zero framework dependencies, kept simple and testable (Ch 11).
**Race Condition / Deadlock / Livelock / Starvation** — concurrency failure modes from unpredictable thread interleaving or resource contention (Ch 13).
**Special Case Pattern** — encapsulate an exceptional business case inside an object so callers need no branch (Fowler) (Ch 7).
**SRP (Single Responsibility Principle)** — a class/module should have one, and only one, reason to change (Ch 10, Ch 13).
**Stepdown Rule** — order functions so each is followed by those one level of abstraction below it (Ch 3, Ch 10).
**Successive Refinement** — write dirty code first, then clean it in many small test-protected steps (Ch 14).
**Team (Gelled)** — a persistent, full-time team that outlives projects and takes 6–12 months to gel (Ch 30).
**Template Method** — hoists a shared algorithm skeleton into a base class, deferring varying steps to subclasses (Ch 12).
**Test Automation Pyramid (Mike Cohn)** — layered test strategy: unit, component, integration, system, manual exploratory, decreasing in volume (Ch 25).
**Three Laws of TDD** — no production code before a failing test; write only enough test to fail; only enough code to pass (Ch 9, Ch 22).
**Train Wreck** — a chain of method calls (`a.getB().getC()`) that leaks an object's internal structure (Ch 6).
**Wideband Delphi** — team-consensus estimation technique (Flying Fingers, Planning Poker, Affinity Estimation) (Ch 27).

## Short Terms
**Bound resource / Mutual exclusion** — fixed-size shared resource; guarantee of single-thread access (Ch 13).
**Broken Windows** — visible neglect invites further decay in a codebase (Ch 1).
**Command/Query naming** — name methods so mutators don't read as queries and vice versa (Ch 16).
**Disinformation (naming)** — a name carrying an entrenched but false meaning (Ch 2).
**Domain-Specific Testing Language** — test-only helper layer that makes tests read like prose (Ch 9).
**Encapsulate Conditionals** — extract boolean expressions into well-named predicate functions (Ch 15, Ch 17).
**Hungarian Notation** — obsolete practice of encoding type/scope into a name (Ch 2).
**LeBlanc's Law** — "later equals never"; deferred cleanup rarely happens (Ch 1).
**Mocking / Test Double** — stand-in objects used to isolate a unit under test from collaborators (Ch 8, Ch 25).
**QA Should Find Nothing** — code sent to QA should already be known to work (Ch 18, Ch 25).
**Rule of Holes** — when you realize you're in a blind alley, stop digging (Ch 26).
**Vertical Formatting (openness/density/distance/ordering)** — blank-line and placement rules governing file readability top-to-bottom (Ch 5).
**Wading** — the struggle of reading through tangled, bad code (Ch 1).
