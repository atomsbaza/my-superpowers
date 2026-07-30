# Chapter 15: Write The Comments First

## Core Idea
Using comments as a design tool produces both better designs and better comments. Write the interface comments *before* you write the code.

## Frameworks Introduced
- **Comment-Driven Design**:
  - How: When creating a new module, first write the class-level comment describing its abstraction. Then write the method signatures and their interface comments. *Only then* write the implementation.
  - Why: If the comment is hard to write, long, or confusing, it is a massive red flag that the interface itself is too complex (shallow).

## Key Takeaways
1. Writing comments first acts as a forcing function for good design.
2. It is much cheaper to redesign a bad interface when it's just a comment than after the implementation is written.\n