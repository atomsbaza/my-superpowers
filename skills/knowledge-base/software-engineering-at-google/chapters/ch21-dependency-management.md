# Chapter 21: Dependency Management

## Core Idea

Dependencies are ongoing relationships, not lines in a manifest. Each dependency adds compatibility, security, support, and upgrade cost. Version constraints such as SemVer encode human risk estimates imperfectly; testing and CI provide stronger evidence of whether a combination actually works.

## Frameworks Introduced

- **A dependency is a contract**: Providers promise behavior and support; consumers accept compatibility and usage responsibilities.
  - When to use: Importing, publishing, or changing a library/API.
  - How: State the supported surface, compatibility expectations, ownership, security response, and migration path.
- **Prefer source-control transparency**: Bringing more code into a coordinated source environment can simplify visibility and change.
  - When to use: Deciding between vendoring, external packages, and internal ownership.
  - How: Compare coordination benefits against update, licensing, and maintenance costs.
- **SemVer as lossy compression**: A version number compresses a human judgment about change risk into a small signal; it is not proof of compatibility.
  - When to use: Evaluating package-manager constraints.
  - How: Use version rules as a starting hypothesis, then validate actual combinations with tests and CI.
- **Minimum Version Selection (MVS)**: Prefer the minimum required version of each dependency while testing the selected graph.
  - When to use: Dependency resolution where “latest compatible” creates unnecessary churn.
  - How: Make minimum requirements explicit and let a reproducible resolver plus CI validate the graph.

## Key Concepts

- **Direct dependency**: A dependency named by a project.
- **Transitive dependency**: A dependency brought in through another dependency.
- **Diamond dependency**: Two paths require different versions of the same dependency.
- **Compatibility promise**: The behavior a provider commits to preserve.
- **Semantic Versioning**: Major/minor/patch labels used as a compatibility shorthand.
- **Dependency hell**: A graph whose constraints or combinations are difficult to resolve and support.
- **Bundled distribution**: Shipping dependencies together as a unit.
- **Live at head**: Consuming a coordinated current version rather than a long-lived pin.

## Mental Models

- Every dependency is a team you now coordinate with.
- A package manager solves selection, not whether the selected graph is correct.
- Importing a dependency transfers support obligations; exporting one creates reputation and compatibility obligations.
- Evidence from tests is stronger than a version string alone.

## Anti-patterns

- **Throw it over the wall**: Publish a dependency without ownership or compatibility support.
- **Unbounded latest**: Builds change without a deliberate source change.
- **Overconstrained graph**: Pinned versions prevent safe upgrades and create dependency hell.
- **SemVer absolutism**: Treating a label as proof that every consumer will work.
- **Unsupported stability**: Allowing users to depend on behavior while claiming no compatibility responsibility.

## Worked Example

In a diamond graph, service A requires library X at one version while library Y requires another. A resolver can select a mathematically permitted combination, but only tests reveal whether the APIs and runtime behavior actually work together. A stronger workflow records minimum requirements, updates dependencies intentionally, runs CI across the graph, and makes the provider/consumer contract explicit.

## Reference Table

| Approach | Strength | Risk |
|---|---|---|
| Static dependency model | Reproducible and simple | Slow updates |
| SemVer constraints | Compact compatibility hint | Overconstraint or overpromise |
| Bundled distribution | Consumer simplicity | Large coordinated releases |
| Live at head | Fast shared evolution | Requires strong testing and coordination |
| MVS plus CI | Controlled minimums with evidence | Needs reliable automation |

## Key Takeaways

1. Budget the ongoing cost before adding a dependency.
2. Treat provider and consumer responsibilities as a contract.
3. Use version labels as estimates, not evidence.
4. Prefer reproducible updates validated by tests and CI.
5. Prevent “no support” dependencies from becoming accidental public APIs.

## Connects To

- **Chapter 1**: Hyrum’s Law makes observable dependency behavior difficult to retract.
- **Chapter 16**: Version control determines how dependency state is coordinated.
- **Chapter 23**: CI makes dependency updates evidence-based.

