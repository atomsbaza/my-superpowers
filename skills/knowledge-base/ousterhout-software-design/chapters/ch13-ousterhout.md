# Chapter 13: Comments Should Describe Things that Aren't Obvious from the Code

## Core Idea
The purpose of comments is to capture information that was in the mind of the designer but couldn't be represented in the code itself.

## Frameworks Introduced
- **Interface Comments**: Describe the abstraction provided by the module, the arguments, the return value, and side effects. They must NOT mention implementation details.
- **Implementation Comments**: Describe *how* the code works internally, the "why" behind tricky algorithms, and any invariants.

## Anti-patterns
- **Repeating the Code**:
  ```csharp
  // Increment i by 1
  i++;
  ```
  This adds zero value and increases maintenance burden.

## Key Takeaways
1. If a comment can be deduced easily by reading the code, delete the comment.
2. Comments should be written at a higher level of abstraction than the code.\n