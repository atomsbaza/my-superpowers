# Topic 1: History and Origins

## Core Idea
Test-Driven Development emerged in the late 1990s as a core practice of Extreme Programming, codified by Kent Beck on the Chrysler Comprehensive Compensation System (C3) project, then split into two lineages — Detroit and London — as different communities reinterpreted what "unit" and "isolation" should mean.

## Frameworks Introduced
- **Extreme Programming (XP)**: the agile methodology TDD was born inside of, not a standalone invention.
  - When to use: context for why TDD exists — it is one of XP's core practices, alongside things like pair programming and continuous integration (per the research, not detailed further in this topic).
  - How: TDD supplied XP with a fast feedback loop; the discipline of write-test-first became one of XP's defining practices.
- **Detroit School (Classicist)**: originating from the original XP practices in Michigan, promoted by Kent Beck, Robert C. Martin (Uncle Bob), Ron Jeffries, and Martin Fowler.
  - When to use: legacy modernization, domain logic that is already well-understood, technical-debt reduction work.
  - How: test a module (a class or set of related classes) using real collaborators, reserving test doubles for "awkward" dependencies only; verify by checking final state.
- **London School (Mockist)**: developed in the early 2000s by the London Extreme Tuesday Club (XTC), distilled by Steve Freeman and Nat Pryce in *Growing Object-Oriented Software Guided by Tests* (GOOS).
  - When to use: new feature development where the design is being discovered through roles and collaborations between objects.
  - How: isolate a single class (the Subject Under Test) from all its collaborators using mocks, then verify correctness through interaction (were the right calls made) rather than state.

## Key Concepts
- **Extreme Programming (XP)**: an agile software development methodology, of which TDD is one of the founding practices.
- **Chrysler Comprehensive Compensation System (C3) project**: the payroll project led by Kent Beck where TDD's modern practice was first developed and proven out.
- **Kent Beck's *Test-Driven Development By Example***: the book in which Beck codified the technique for a general audience, after its origin on the C3 project.
- **Detroit School origin**: the original, Michigan-based branch of TDD practice tracing directly to Beck's XP circle.
- **London School / XTC origin**: the early-2000s branch that grew out of the London Extreme Tuesday Club, a separate community of practitioners refining an interaction-based style of TDD.
- **Freeman & Pryce's GOOS book**: *Growing Object-Oriented Software, Guided by Tests* — the text that formalized and popularized the London School's mock-driven, outside-in approach.

## Mental Models
- **TDD as a practice born of a specific project, not an abstract theory** — its origin on the C3 payroll system means it was pressure-tested against real delivery constraints from day one, not designed in the abstract.
- **TDD as one practice nested inside a larger philosophy (XP)** — separating TDD from XP's other values (communication, simplicity, feedback, courage, respect — covered in Topic 13) loses context for why the discipline exists.
- **Two schools as a fork, not a contradiction** — Detroit and London are not "correct vs incorrect" TDD; they are divergent answers to the same open question ("what is a unit, and what should be isolated?") that happened to crystallize in different cities and communities.
- **Geography as a rough label, not a rigid boundary** — "Detroit" and "London" are shorthand for lineages of practitioners and their published work, not literal claims about where every practitioner is located.

## Anti-patterns
(omit — not covered in this topic's research; anti-patterns of practice are covered in Topic 8)

## Code Examples
(omit — not code-heavy)

## Reference Tables
(omit — the Detroit vs. London comparison table belongs to Topic 3)

## Worked Example
Kent Beck led the Chrysler Comprehensive Compensation System (C3) project in the late 1990s, where he practiced and refined the write-test-first discipline that would become Test-Driven Development. This happened inside his broader push for Extreme Programming, an agile methodology built around tight feedback loops. Beck later wrote *Test-Driven Development By Example* to generalize what he had learned into a teachable technique.

As TDD spread beyond Beck's immediate circle, it evolved along two paths. In Michigan, the original XP community — Beck, Robert C. Martin, Ron Jeffries, and Martin Fowler — continued practicing what came to be called the Detroit (or Classicist) style: testing modules with real collaborators, verifying final state, and reserving mocks for awkward external dependencies. In London, a separate group — the London Extreme Tuesday Club — began experimenting with a more isolated, interaction-focused style in the early 2000s. Steve Freeman and Nat Pryce, key figures in that community, wrote *Growing Object-Oriented Software, Guided by Tests* to formalize this approach: isolate a single class from every collaborator via mocks, and let the interactions between objects — not just their final state — drive both the tests and the design.

The two schools never fully reconciled; they represent different bets about what unit tests are for (confirming correctness vs. driving design through simulated collaborations) and resurface throughout later debates about mocking, refactoring cost, and what TDD is "supposed to" look like (see Topic 12, the "Is TDD Dead?" debate).

## Key Takeaways
1. TDD did not arise as pure theory — it was forged on a real, high-stakes project (Chrysler's C3) under Kent Beck's leadership.
2. TDD is inseparable from its origin as an Extreme Programming practice; understanding XP's values clarifies why TDD looks the way it does.
3. The Detroit/London split is a difference in philosophy about "unit" and "isolation," not a matter of one school being a corruption of the other.
4. Kent Beck's book and Freeman & Pryce's GOOS book are the two canonical texts anchoring each school — read them to understand the primary-source reasoning, not just the summary.
5. When adopting TDD on a team, naming which school you're following (even implicitly) helps explain downstream disagreements about mocking, test scope, and refactoring cost.

## Connects To
- **Topic 3 (Classicist vs Mockist Schools)**: the direct continuation of this topic — takes the Detroit/London split introduced here and details the concrete practice differences (unit definition, isolation target, verification style).
- **Topic 4 (Inside-Out vs Outside-In)**: the design-flow consequence of the Detroit/London split — Detroit tends inside-out, London tends outside-in.
- **Topic 12 (The "Is TDD Dead?" Debate)**: the 2014 DHH/Fowler/Beck debate that revisited these same origins and lineages decades later, especially critiquing the London/mockist style.
- **Topic 13 (XP Values & Test Code Quality)**: the broader XP philosophy (Communication, Simplicity, Feedback, Courage, Respect) that TDD was born to serve.
- **External concept — Extreme Programming (XP)**: the parent methodology; TDD is best understood as one of its practices, not a freestanding technique.
