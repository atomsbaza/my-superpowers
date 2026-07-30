# Chapter 18: Code Should be Obvious

## Core Idea
Code is obvious if a developer can read it quickly and guess what it does without having to study it intensely. Obscurity is the enemy of obviousness.

## Key Concepts
- **Obscurity**: When important information is hidden (e.g., a critical side-effect tucked away in an unrelated method, or magic numbers).
- **Red Flags**:
  - Event-driven programming (can obscure the flow of control).
  - Generic containers (e.g., `Pair<int, int>`) where the meaning of the elements is lost.
  - Different types of software coupling.

## Key Takeaways
1. If someone else reading your code has to ask you what it does, it's not obvious.
2. Choose clarity over cleverness.\n