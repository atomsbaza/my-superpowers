# Chapter 4: Modules Should Be Deep

## Core Idea
The best modules are those that provide powerful functionality while hiding that functionality behind a simple interface.

## Frameworks Introduced
- **Deep Modules**:
  - What it is: A module whose interface is much simpler than its implementation. (e.g., File I/O in Unix: open, read, write, close—hiding massive OS-level complexity).
  - Why: They maximize the amount of complexity hidden from the rest of the system.
- **Shallow Modules**:
  - What it is: A module whose interface is relatively complex compared to the functionality it provides (e.g., a method that just passes its arguments to another method).
  - Why to avoid: They don't hide much complexity and force the caller to understand the implementation.

## Key Concepts
- **Interface**: Everything a developer needs to know in order to use a module.
- **Implementation**: The code inside the module that carries out its promises.

## Mental Models
- Think of a module as an **iceberg**. The interface is the tip above the water (small, visible, easy to grasp). The implementation is the massive bulk below the water (hidden, doing the heavy lifting).

## Modern Context
In modern microservices or API design, the "Deep Module" philosophy applies strongly to service boundaries. A microservice with an API that perfectly mirrors its database schema is a "shallow" service; it provides little abstraction over the raw data.\n