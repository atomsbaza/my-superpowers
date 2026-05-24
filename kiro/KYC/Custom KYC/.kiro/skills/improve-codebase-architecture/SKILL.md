---
name: improve-codebase-architecture
description: "Surface architectural friction and propose deepening opportunities — refactors that turn shallow modules into deep ones, improving testability and maintainability. Pairs with: sa-architect subagent."
---


# Improve Codebase Architecture

Surface architectural friction and propose deepening opportunities. Pairs with: sa-architect subagent. — refactors that turn shallow modules into deep ones, improving testability and maintainability.

## When to Use

- User wants to improve architecture or find refactoring opportunities
- Consolidate tightly-coupled modules
- Make a codebase more testable
- Reduce complexity in a service

## Vocabulary

- **Module** — anything with an interface and implementation (class, service, handler, repository)
- **Depth** — high leverage: lots of behavior behind a small interface
- **Shallow** — interface nearly as complex as the implementation (pass-through layers)
- **Seam** — where an interface lives; a place behavior can be altered without editing in place
- **Deletion test** — imagine deleting the module. If complexity vanishes, it was pass-through. If it reappears across N callers, it was earning its keep.

## Process

### 1. Explore

Read the project's steering files (`.kiro/steering/`) and existing specs first. Then walk the codebase and note friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but real bugs hide in how they're called?
- Where do tightly-coupled modules leak across their seams?
- Which parts are untested or hard to test through their current interface?
- Where is the same validation/mapping logic duplicated across handlers?

Apply the **deletion test** to anything you suspect is shallow.

### 2. Present Candidates

Present a numbered list of deepening opportunities. For each:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture causes friction
- **Solution** — plain English description of what would change
- **Benefits** — in terms of testability, locality, and reduced duplication
- **Risk** — what could break, how to mitigate

Do NOT propose code yet. Ask: "Which of these would you like to explore?"

### 3. Design Conversation

Once the user picks a candidate:

- Walk through constraints and dependencies
- Discuss the shape of the deepened module
- Identify what sits behind the seam
- Determine what tests survive the refactor
- Consider cross-service impact (check project-map.md)

### 4. Execute

After agreement:
- Implement the refactor incrementally
- Run tests after each step
- Ensure no behavior changes (unless explicitly agreed)

## KYC-Specific Patterns to Watch For

| Smell | Where to Look | Deepening Opportunity |
|-------|--------------|----------------------|
| Duplicate validation logic | Handlers across services | Shared validation module behind interface |
| Pass-through repository methods | Infrastructure layer | Consolidate into richer domain methods |
| Copy-paste entity mapping | Handler → Entity builders | Domain factory or builder pattern |
| Scattered encryption calls | Multiple repositories | Centralized PII encryption seam |
| Repeated SQS publish patterns | Multiple handlers | Unified event publisher |
| Similar risk assessment logic | Multiple handlers | Risk calculation module |

## Constraints

- Respect existing ADRs and steering docs
- Don't break cross-service contracts (check shared-conventions.md)
- Maintain backward compatibility on API endpoints
- Keep stored procedure interfaces stable (DB team dependency)
