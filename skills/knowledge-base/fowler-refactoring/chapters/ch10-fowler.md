# Chapter 10: Making Method Calls Simpler

## Core Idea
Interfaces should be easy to use correctly and hard to use incorrectly. This chapter focuses on refining method signatures, parameters, and return types to improve the communication between caller and callee.

## Key Concepts
- **Rename Method**: Changing a method's name to clearly indicate its intention.
- **Add/Remove Parameter**: Modifying the signature to reflect the data the method actually needs.
- **Preserve Whole Object**: Passing an entire object as a parameter instead of passing several of its fields individually.
- **Replace Parameter with Explicit Methods**: Replacing a method that takes a parameter dictating its behavior with separate methods for each behavior.

## Key Takeaways
1. The name of a method is its most important documentation.
2. Long parameter lists are hard to understand; group them into objects or pass the whole object.\n