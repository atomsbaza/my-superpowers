# Chapter 9: Better Together Or Better Apart?

## Core Idea
Deciding whether to split a piece of functionality into multiple modules or combine it into one depends on which approach best hides information and reduces dependencies.

## Frameworks Introduced
- **When to Combine**:
  - The modules share information (e.g., they both understand a specific file format).
  - The modules are used together sequentially, and it's hard to use one without the other.
  - Combining them simplifies the interface (e.g., merging them eliminates pass-through variables or redundant method calls).
- **When to Split**:
  - The module is doing two completely unrelated things (it lacks cohesion).
  - Splitting them results in one highly general-purpose module and one highly specific module.

## Key Takeaways
1. Splitting code into smaller pieces does NOT inherently reduce complexity; it often increases cognitive load by spreading the logic across multiple files.
2. Only split modules if it creates deeper interfaces and tighter information hiding.\n