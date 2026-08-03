# Chapter 1: What Is Software Engineering?

## Core Idea

Software engineering is programming viewed across the useful life of a system. The engineering discipline begins where “make it work” ends: sustaining change as dependencies, technology, users, and organizational scale evolve.

## Frameworks Introduced

- **Time and scale**: Judge practices against how long the code will live and how many people, systems, and users it will affect.
  - When to use: Before choosing a process, architecture, or level of rigor.
  - How: Estimate the expected lifetime and scale; invest in practices that keep future change feasible.
- **Hyrum’s Law**: With enough users, every observable behavior becomes a dependency, whether or not it is documented.
  - When to use: API design, compatibility work, migrations, and infrastructure upgrades.
  - How: Inventory observable behavior, distinguish intended contracts from accidental behavior, and plan migration/testing around the accidental dependencies that will emerge.
- **Shifting left**: Find expensive failures earlier in the developer workflow.
  - When to use: Any repeated validation or release process.
  - How: Move checks toward editing, review, presubmit, and continuous integration when earlier feedback is cheaper and more actionable.
- **The Beyoncé Rule**: If a behavior matters, put a test for it in the common CI path; bespoke tests that infrastructure cannot discover do not scale.
  - When to use: Infrastructure changes that might affect many teams.
  - How: Make the dependency visible through automated, centrally discoverable tests.

## Key Concepts

- **Sustainability**: The ability to respond to change over the expected life of software.
- **Observable behavior**: Anything users can see, measure, infer, or rely on, including behavior outside the published API.
- **Implicit dependency**: A reliance on an implementation detail rather than an explicit contract.
- **Scale**: Growth in people, code, users, operations, or repeated process work.
- **Boiled-frog problem**: A slowly worsening cost that escapes attention because no single event triggers action.
- **Inputs to decisions**: Data, assumptions, precedent, and argument; data is valuable but rarely complete.

## Mental Models

- Think of a codebase as an investment whose return is its ability to absorb future change.
- Treat every observable behavior as a possible API surface.
- Separate “we choose not to change” from “we cannot change”; only the latter is unsustainable.
- Prefer scalable policies over heroics when the same decision recurs across an organization.

## Anti-patterns

- **“Because I said so” governance**: It hides the trade-off and cannot teach people how to make the next decision.
- **Aiming for “nothing changes”**: Avoiding change does not remove dependency, security, or product pressure; it only removes preparedness.
- **Manual exception tracking**: A process that requires someone to remember every affected consumer becomes the bottleneck as the organization grows.

## Worked Example

Hash-table ordering illustrates Hyrum’s Law. The implementation may promise no ordering, yet callers eventually observe a stable traversal order and build behavior around it. A later runtime change that randomizes or alters the order can break those callers. The lesson is not “never change hash tables”; it is to expose, test, and migrate observable behavior when the cost of change matters.

The compiler-upgrade example makes the same point at organizational scale: years without upgrades allowed many implicit dependencies to accumulate. Continuous testing and visible upgrade work make the next upgrade less of a heroic event.

## Reference Table

| Situation | Appropriate emphasis |
|---|---|
| Short-lived script, one user | Optimize for immediate problem solving |
| Long-lived product | Invest in maintainability and change safety |
| Small team | Lightweight conventions may be enough |
| Large organization | Automate, standardize, and make dependencies visible |

## Key Takeaways

1. Define engineering practice by lifetime and scale, not fashion.
2. Assume users will depend on observable behavior.
3. Make recurring work linear or better in human effort.
4. Move feedback earlier and into common workflows.
5. Revisit decisions when evidence or assumptions change.

## Connects To

- **Chapter 7**: Measurement makes hidden productivity costs visible.
- **Chapter 15**: Deprecation manages the cost of accumulated dependencies.
- **Chapter 23**: CI operationalizes shifting left and the Beyoncé Rule.

