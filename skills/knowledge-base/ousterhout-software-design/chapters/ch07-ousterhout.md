# Chapter 7: Different Layer, Different Abstraction

## Core Idea
Software systems are composed in layers, and each layer should provide a different abstraction. If two layers provide the same abstraction, the system is overly complex (shallow).

## Key Concepts
- **Pass-through Methods**: A method that does nothing but call another method with the exact same signature. This indicates that adjacent layers have the same abstraction and should probably be merged.
- **Decorators/Wrappers**: Often result in shallow classes. If you have many small classes that just wrap each other, you are adding interface complexity without hiding implementation complexity.

## Anti-patterns
- **Classitis / Interfaceitis**: The belief that "more, smaller classes" is inherently better. Ousterhout argues that excessive splitting leads to shallow modules and high cognitive load because developers must jump between dozens of files to understand a simple flow.

## Key Takeaways
1. Each layer of a system must provide a distinct abstraction.
2. If a layer just passes data through, question its existence.\n