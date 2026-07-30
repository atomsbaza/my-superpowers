# Patterns & Refactorings

## Extract Method
**When to use**: You have a cohesive code fragment inside a longer method.
**How**: Move the fragment into a new method with a name that explains the purpose of the method.
**Trade-offs**: Introduces a small overhead of method calls, but massively improves readability and reuse.

## Replace Conditional with Polymorphism
**When to use**: You have a conditional (switch or if-else chain) that chooses different behavior depending on the type of an object.
**How**: Move each leg of the conditional to an overriding method in a subclass. Make the original method abstract.
**Trade-offs**: Increases the number of classes, but removes brittle switch statements that have to be updated whenever a new type is added.

## Extract Class
**When to use**: You have one class doing work that should be done by two.
**How**: Create a new class and move the relevant fields and methods from the old class into the new class.
**Trade-offs**: Increases the number of classes, but improves cohesion.

## Introduce Null Object
**When to use**: You have repeated checks for a null value.
**How**: Replace the null value with a null object that implements the interface and does the 'null' behavior (often doing nothing).
**Trade-offs**: Removes null checks throughout the codebase, but requires creating a new class.

## Replace Type Code with Class / Subclasses / State
**When to use**: You have a class with a primitive type code (e.g., int type = 1 for 'Employee', 2 for 'Manager') that affects behavior.
**How**: Replace the type code with a dedicated class, subclasses of the original class, or a State/Strategy object.
**Trade-offs**: Makes the type explicit and enables polymorphism, reducing reliance on switch statements.\n