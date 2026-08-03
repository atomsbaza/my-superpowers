# Chapter 15: Deprecation

## Core Idea

Deprecation is a managed transition, not a warning annotation. Existing users depend on old behavior, so removal requires owners, discovery, migration, milestones, tooling, and protection against backsliding. Evolving in place is often cheaper than replacement once ecosystem costs are included.

## Frameworks Introduced

- **Deprecation as a product**: The old system has consumers, promises, support costs, and a migration experience.
  - When to use: Removing APIs, libraries, services, or infrastructure.
  - How: Define the replacement and success condition, identify consumers, communicate milestones, migrate, and retire the old path.
- **Advisory versus compulsory deprecation**:
  - **Advisory**: Signals that users should move but does not block use.
  - **Compulsory**: Enforces migration through tooling or removal.
  - When to use: Match enforcement to risk, readiness, and the cost of continuing support.
- **Prevent backsliding**: After migration, stop new uses of the deprecated system.
  - When to use: Any deprecation that takes time or spans many teams.
  - How: Add static checks, presubmit failures, ownership rules, or automated migration support.
- **Deprecation milestones**: Discovery, migration, and removal are separate states.
  - When to use: Planning a large transition.
  - How: Assign process owners, publish dates/criteria, measure progress, and make the next step obvious.

## Key Concepts

- **Advisory deprecation**: A nonblocking signal to migrate.
- **Compulsory deprecation**: A policy or tool that prevents continued use.
- **Turndown cost**: The effort and risk required to remove an old system.
- **Ecosystem cost**: Diffuse cost from supporting multiple similar systems and compatibility paths.
- **Backsliding**: New code reintroducing a dependency that a migration removed.
- **Discovery**: Finding consumers and observable dependencies.

## Mental Models

- Removing software is often harder than building it because the ecosystem has adapted around it.
- “Deprecated” is not a plan; it is a state transition with an owner and exit criteria.
- The cheapest migration is the one designed into the API before adoption.
- Treat every user as a potential implicit dependency under Hyrum’s Law.

## Anti-patterns

- **Announcement-only deprecation**: Users cannot discover every consumer or prioritize migration.
- **Premature deletion**: Removing the old path before consumers and replacements are ready.
- **No owner**: Warnings accumulate without decisions or support.
- **No backsliding control**: Migration progress is undone by new uses.
- **Replacement without parity**: The new system shifts work to consumers or loses important behavior.

## Worked Example

A typical migration replaces an old API with a safer one. First, tooling finds references and classifies consumers. An advisory warning and migration guide establish the path; automated edits handle mechanical changes; presubmit checks prevent new references. A milestone moves the warning to a compulsory check only after the replacement is viable. Removal follows cleanup and confirmation that the old dependency is no longer needed.

## Reference Table

| Stage | Primary question | Mechanism |
|---|---|---|
| Design | Can future removal be cheap? | Stable abstraction and migration path |
| Discovery | Who depends on the old system? | Search, ownership, usage analysis |
| Migration | How do consumers move? | Docs, tools, sharded changes, support |
| Prevention | How do we stop new use? | Static analysis and presubmit |
| Removal | Is the ecosystem ready? | Milestone review and cleanup |

## Key Takeaways

1. Budget maintenance and turndown costs before adopting a system.
2. Assign a deprecation owner and explicit milestones.
3. Use discovery and automation to reduce migration cost.
4. Prevent new uses while old consumers migrate.
5. Prefer evolution in place when replacement costs exceed the benefit.

## Connects To

- **Chapter 1**: Observable behavior and implicit dependencies make removal difficult.
- **Chapter 20**: Static analysis prevents backsliding.
- **Chapter 22**: Large-scale changes provide the machinery for migration.

