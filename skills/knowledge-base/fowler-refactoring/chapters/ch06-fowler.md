# Chapter 6: Composing Methods

## Core Idea
The most common problems in code revolve around methods that are too long. Composing methods involves packaging code properly to reduce method size, clarify intent, and remove duplication.

## Key Concepts
- **Extract Method**: Moving a cohesive fragment of code into a new method with a name that explains its purpose.
- **Inline Method**: The reverse of Extract Method; replacing a method call with the method's body when the body is just as clear as the name.
- **Replace Temp with Query**: Extracting the expression assigned to a temporary variable into a method, replacing all references to the temp with the new method call.

## Mental Models
- Think of a method as a **newspaper headline and paragraphs**. The high-level method should read like headlines (calling other methods), and the details should be in the lower-level methods (the paragraphs).

## Anti-patterns
- **Comments as Deodorant**: Using comments to explain a block of code instead of extracting that block into a well-named method.

## Key Takeaways
1. Shorter methods are easier to read, easier to reuse, and easier to override.
2. Name methods for *what* they do (intent), not *how* they do it (implementation).\n