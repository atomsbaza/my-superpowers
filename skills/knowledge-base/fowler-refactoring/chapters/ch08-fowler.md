# Chapter 8: Organizing Data

## Core Idea
Data structures dictate the clarity of the code that operates on them. Refactoring data involves replacing primitive data types with objects, encapsulating fields, and making associations between objects clearer.

## Key Concepts
- **Replace Data Value with Object**: Creating a class for a data item that requires additional data or behavior (e.g., turning a simple String phone number into a PhoneNumber object).
- **Encapsulate Field**: Making a public field private and providing accessors, allowing control over how the data is read and modified.
- **Replace Type Code with Class/Subclasses/State/Strategy**: Replacing arbitrary integers or strings used to dictate behavior with polymorphic objects.

## Mental Models
- Think of primitive obsession as a **missed opportunity for a domain concept**. A ZIP code is not just a string; it has validation rules and specific formatting.

## Key Takeaways
1. Data wants to be encapsulated. Hide internal data representations behind clear interfaces.
2. Avoid primitive obsession; use small objects to represent domain concepts.\n