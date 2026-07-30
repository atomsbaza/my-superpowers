# Chapter 5: Information Hiding (and Leakage)

## Core Idea
The most important technique for achieving deep modules is information hiding: a module should encapsulate a few pieces of knowledge (design decisions) which are hidden from all other modules.

## Key Concepts
- **Information Hiding**: Designing a module so that it encapsulates a specific design decision or piece of knowledge (like a file format, a network protocol, or a parsing algorithm).
- **Information Leakage**: When a design decision is reflected in multiple modules. If the decision changes, all those modules must change. (A prime cause of Change Amplification).
- **Temporal Decomposition**: An anti-pattern where a system is structured based on the order in which operations happen (e.g., ReadFile, ParseFile, WriteFile), causing the file format knowledge to leak into all three modules.

## Anti-patterns
- **Leaky Abstractions**: Exposing internal details (like internal data structures) through the interface.
- **Pass-through Variables**: Variables passed down through a long chain of methods just so a deeply nested method can use them.

## Key Takeaways
1. When designing a module, ask: "What secret does this module hide?"
2. Information leakage is one of the biggest drivers of complexity.\n