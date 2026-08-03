# Chapter 18: Build Systems and Build Philosophy

## Core Idea

A build system transforms source into executable artifacts while managing dependencies, parallelism, caching, reproducibility, and developer feedback. Artifact-based systems such as Blaze/Bazel scale better than ad hoc task scripts when modules and dependencies are explicit and fine-grained.

## Frameworks Introduced

- **Artifact-based builds**: Describe what artifacts and dependencies exist; let the build system decide how to schedule the work.
  - When to use: Large repositories, incremental builds, distributed execution, and reproducibility.
  - How: Declare targets, inputs, outputs, and dependencies; avoid hidden filesystem or environment assumptions.
- **Task-based versus artifact-based**:
  - **Task-based**: An imperative sequence of commands.
  - **Artifact-based**: A declarative graph of reproducible outputs.
  - When to use: Prefer artifact graphs when scale, caching, and parallelism matter.
- **Fine-grained modules and the 1:1:1 rule**: Smaller targets improve caching, parallelism, impacted-test selection, and ownership clarity.
  - When to use: Structuring Bazel-like builds.
  - How: Align a package, target, and build definition where the language’s packaging model supports it; use automation to control maintenance cost.
- **Remote caching and execution**: Reuse or distribute build work across a shared fleet.
  - When to use: Large builds whose local execution wastes developer time.
  - How: Make inputs/outputs deterministic, cache artifacts, and execute isolated actions remotely.

## Key Concepts

- **Build artifact**: A generated output such as a binary, library, or test result.
- **Build graph**: Nodes for artifacts and edges for dependencies.
- **Task-based build**: Imperative commands describing a sequence.
- **Hermetic action**: A build action whose result depends only on declared inputs.
- **Incremental build**: Rebuilding only outputs affected by changed inputs.
- **Remote cache**: Shared storage for reusable build outputs.
- **Remote execution**: Running build actions on managed workers.
- **Module visibility**: Which targets are allowed to depend on a module.

## Mental Models

- The build graph is a dependency-management system with a performance contract.
- Fine-grained targets trade BUILD-file maintenance for faster, more selective work.
- Restriction is a feature: a build system is easier to reason about when it does not expose arbitrary scripting power.
- Reproducibility is the prerequisite for caching and distributed execution.

## Anti-patterns

- **Compiler-only thinking**: It ignores dependency discovery, testing, packaging, and reproducibility.
- **Shell-script build orchestration**: Hidden state and imperative order prevent reliable parallelism.
- **One giant target**: It defeats incremental and distributed builds.
- **Undeclared dependencies**: Local success turns into remote or clean-build failure.
- **Unversioned external inputs**: “Latest” dependencies make builds irreproducible.

## Worked Example

A single large target can build a project with little BUILD-file maintenance, but every change rebuilds everything and prevents selective tests. Splitting the project into package-aligned targets exposes dependencies and lets the system cache unaffected artifacts. The 1:1:1 convention is one practical expression of that trade-off, not a universal requirement for every language.

## Code Examples

~~~text
target(name = "service",
       sources = ["service.go"],
       deps = [":config", "//libs:logging"])
~~~

This reconstructed declaration shows the important property: dependencies are explicit inputs to an artifact, not hidden commands.

## Key Takeaways

1. Declare artifacts and dependencies explicitly.
2. Prefer reproducible graphs over opaque command sequences.
3. Use fine-grained targets when scale makes caching and parallelism valuable.
4. Minimize visibility to prevent accidental dependency growth.
5. Version external inputs and invest in remote build infrastructure only after determinism exists.

## Connects To

- **Chapter 16**: Version control and build graphs jointly define the source of truth.
- **Chapter 21**: External dependency choices affect reproducibility.
- **Chapter 23**: CI is a consumer of the build system’s determinism and feedback.

