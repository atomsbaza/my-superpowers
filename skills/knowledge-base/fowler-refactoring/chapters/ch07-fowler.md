# Chapter 7: Moving Features Between Objects

## Core Idea
One of the most fundamental decisions in object-oriented design is where to put responsibilities. As a system evolves, responsibilities often end up in the wrong places. This chapter focuses on moving state and behavior between classes to improve cohesion and reduce coupling.

## Key Concepts
- **Move Method**: Moving a method to the class that contains the data it uses most.
- **Move Field**: Moving a field from one class to another where it is more frequently used.
- **Extract Class**: Creating a new class to take over some responsibilities from a class that has grown too large (violating the Single Responsibility Principle).
- **Inline Class**: Merging a class that isn't doing enough into another class.

## Anti-patterns
- **Feature Envy**: A method in Class A that calls half a dozen getters on Class B to calculate a value. The method (or part of it) probably belongs on Class B.

## Key Takeaways
1. Keep data and the behavior that operates on that data together in the same class.
2. Don't be afraid to create new classes to represent new concepts that emerge during refactoring.\n