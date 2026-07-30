# Chapter 6: General-Purpose Modules are Deeper

## Core Idea
When designing a module, making its interface slightly more general-purpose than the immediate use-case requires often leads to a simpler, deeper, and more reusable module.

## Frameworks Introduced
- **Somewhat General-Purpose Design**:
  - How: Don't build for every possible future use-case (YAGNI), but *do* make the interface general enough that it isn't tied exclusively to the current caller's specific needs.
  - Test: Can I explain the module's interface completely without mentioning the specific use-case of the current caller?

## Key Takeaways
1. A general-purpose interface is usually simpler than a special-purpose one.
2. Push specific, application-level knowledge up the call stack, keeping the lower-level modules general.\n