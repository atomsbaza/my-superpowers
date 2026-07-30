# Chapter 11: Dealing with Generalization

## Core Idea
Generalization (inheritance and interfaces) is a powerful tool for removing duplication and organizing code, but it is often misused. Refactoring generalization involves moving members up and down the hierarchy or replacing inheritance with delegation.

## Key Concepts
- **Pull Up Field/Method**: Moving a field or method from subclasses to their common superclass to eliminate duplication.
- **Push Down Field/Method**: Moving a field or method from a superclass to the specific subclasses that actually use it.
- **Extract Superclass / Extract Interface**: Creating a new superclass or interface to capture common behavior among existing classes.
- **Replace Inheritance with Delegation**: When a subclass uses only a portion of a superclass's interface or doesn't want to inherit its data, replace the inheritance relationship with a field containing the former superclass, and delegate methods to it.

## Anti-patterns
- **Refused Bequest**: A subclass inherits methods and data from a superclass but doesn't want or need them. This indicates the hierarchy is wrong; inheritance should be replaced with delegation, or a new sibling class should be created.

## Key Takeaways
1. Inheritance is often overused. Favor composition (delegation) over inheritance when the "is-a" relationship isn't strictly true.\n