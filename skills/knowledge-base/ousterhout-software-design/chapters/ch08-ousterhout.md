# Chapter 8: Pull Complexity Downwards

## Core Idea
It is better to have a slightly more complex implementation (internally) if it means providing a simpler interface to the caller. You should "pull complexity downwards" into your module.

## Frameworks Introduced
- **Pulling Complexity Down**:
  - When to use: When a module requires the caller to manage configuration, state, or error recovery that the module could theoretically handle itself.
  - How: Make the module do more work so the caller does less. (e.g., instead of making the caller check if a configuration file exists before loading it, make the `LoadConfig` method handle the missing file gracefully).

## Key Takeaways
1. Most modules have more users (callers) than implementers. Optimizing for the caller's ease-of-use is the right trade-off.
2. Don't let your module's internal difficulties bleed into its interface.\n