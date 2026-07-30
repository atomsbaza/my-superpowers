# Refactoring Cheatsheet

## The Refactoring Workflow
1. **Ensure Tests Exist**: You need a green test suite before starting.
2. **Identify Smell**: Find a structural issue in the code.
3. **Select Refactoring**: Choose the appropriate refactoring from the catalog to address the smell.
4. **Apply Small Step**: Perform the refactoring mechanics meticulously.
5. **Run Tests**: If tests fail, you know exactly which small step broke them. Revert or fix immediately.
6. **Commit**: Save your progress.

## Code Smells & Cures

| Smell | Primary Cure |
|---|---|
| **Duplicated Code** | Extract Method, Pull Up Method |
| **Long Method** | Extract Method, Replace Temp with Query |
| **Large Class** | Extract Class, Extract Subclass |
| **Long Parameter List** | Replace Parameter with Method, Preserve Whole Object, Introduce Parameter Object |
| **Divergent Change** (One class changed in different ways for different reasons) | Extract Class |
| **Shotgun Surgery** (One change requires modifying many classes) | Move Method, Move Field, Inline Class |
| **Feature Envy** | Move Method, Extract Method |
| **Data Clumps** (Fields hanging around together) | Extract Class, Introduce Parameter Object |
| **Primitive Obsession** | Replace Data Value with Object |
| **Switch Statements** | Replace Conditional with Polymorphism |
| **Lazy Class** (A class not doing enough to pay for itself) | Inline Class, Collapse Hierarchy |
| **Message Chains** (a.getB().getC().getD()) | Hide Delegate |\n