# Chapter 12: Big Refactorings

## Core Idea
While most refactorings are small, incremental steps, sometimes you need to tackle large-scale structural problems in a system. Big refactorings take months or years and are done gradually alongside regular feature work.

## Key Concepts
- **Tease Apart Inheritance**: Untangling a single inheritance hierarchy that is doing two jobs into two parallel hierarchies connected by delegation.
- **Convert Procedural Design to Objects**: Transforming a procedural program (records and long methods) into an object-oriented design by identifying data clumps and extracting methods onto new objects.
- **Extract Hierarchy**: Turning a single class that does too much (often driven by conditional logic) into a hierarchy of classes.

## Mental Models
- Think of big refactorings as **steering a large ship**. You don't turn it all at once; you make small adjustments over a long period to gradually change the course of the design.

## Key Takeaways
1. Never stop the world to do a big refactoring. Do it incrementally while continuing to deliver value.
2. Have a clear target architecture in mind, and let every small refactoring step move you closer to it.\n