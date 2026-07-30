# Chapter 3: Bad Smells in Code

## Core Idea
Knowing *how* to refactor is only half the battle; knowing *when* to refactor is just as important. Code "smells" are subjective indicators or patterns in code that suggest there might be a deeper problem requiring refactoring.

## Frameworks Introduced
- **Smell Identification**:
  - When to use: When reading code and feeling that it is harder to understand or modify than it should be.
  - How: Look for common structural patterns (smells) and map them to specific refactoring techniques.

## Key Concepts
- **Code Smell**: A surface indication that usually corresponds to a deeper problem in the system.
- **Duplicated Code**: The most common smell; identical or very similar code structures in more than one place.
- **Long Method**: A method that has grown too large, doing too many things, making it hard to understand.
- **Large Class**: A class trying to do too much, often indicated by too many instance variables.
- **Feature Envy**: A method that seems more interested in a class other than the one it actually is in (often invoking many getters on another object).

## Mental Models
- Think of smells as **diagnostics for your code**. Just as certain symptoms indicate specific illnesses, certain smells point to specific design flaws that can be cured with specific refactorings.

## Anti-patterns
- **Ignoring the Odor**: Leaving bad smells in the code because "it works." This guarantees the codebase will become unmaintainable over time.
- **Over-zealous cleaning**: Trying to eradicate every single smell, even those that don't hinder current development. Pragmatism is key.

## Key Takeaways
1. If it stinks, change it.
2. Duplication is the root of all software evil.
3. Shorter methods and smaller classes with clear responsibilities are the target state.

## Connects To
- **Ch 6 - Ch 11**: The catalogs of refactorings that provide the specific "cures" for these smells.\n