# Patterns & Refactorings

## Design it Twice
**When to use**: Before committing to the architecture of any non-trivial module.
**How**: Sketch out two radically different designs for the module. Compare them based on their depth, the simplicity of their interfaces, and how well they hide information. Pick the best one or combine their strengths.
**Trade-offs**: Takes slightly more time upfront, but usually results in a much deeper module and prevents expensive refactoring later.

## Pull Complexity Downwards
**When to use**: When an interface requires the caller to manage configuration, state, or handle predictable errors.
**How**: Move the logic that handles that complexity into the module itself, simplifying the interface.
**Trade-offs**: Makes the module harder to implement, but easier to use. Since a module is usually called more times than it is implemented, this is almost always the right trade-off.

## Define Errors Out of Existence
**When to use**: When designing APIs that traditionally throw exceptions for edge cases (e.g., deleting a missing item, reading out of bounds).
**How**: Change the semantics of the method so the edge case is handled naturally. For example, `Delete` means "ensure this item is not present", so calling it on a non-existent item just returns success.
**Trade-offs**: Dramatically reduces the exception-handling burden on callers. Cannot be used for true catastrophic failures (like a missing database connection).

## Write Comments First (Comment-Driven Design)
**When to use**: When designing a new class or method.
**How**: Write the interface comments (describing what it does) *before* writing any code. If the comment is difficult to write, long, or requires explaining internal details, redesign the interface.
**Trade-offs**: Forces you to confront the complexity of the interface before getting invested in the implementation.\n