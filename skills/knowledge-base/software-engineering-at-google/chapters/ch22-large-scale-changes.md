# Chapter 22: Large-Scale Changes

## Core Idea

Large-Scale Changes (LSCs) make organization-wide refactoring and migration a routine capability. At scale, a human editing a codebase manually cannot overcome repository size, merge conflicts, heterogeneity, testing, review, and ownership; dedicated infrastructure turns a global change into safe shards.

## Frameworks Introduced

- **LSC process**: Authorization, change creation, sharding/submission, testing, reviewer mailing, review, submission, and cleanup.
  - When to use: A consistent change must touch many files, teams, or repositories.
  - How: Define the transformation, generate changes mechanically, shard them, validate each shard, route to owners, and prevent backsliding.
- **Sharding**: Break a global change into reviewable, testable units.
  - When to use: Atomic repository-wide changes exceed review or infrastructure limits.
  - How: Partition by ownership or dependency boundary while preserving a coherent transformation and progress ledger.
- **Generated changes should look human-readable**: Automation must produce ordinary, reviewable code changes.
  - When to use: Designing refactoring tools and review policy.
  - How: Follow style, preserve local context, use tests, and make the transformation explainable.
- **Make LSCs habitual**: The organization gains leverage when broad cleanup is a normal operation instead of an exceptional campaign.
  - When to use: Technical-debt removal, API migrations, and policy enforcement.
  - How: Maintain tooling, ownership, test infrastructure, and a culture that funds recurring migrations.

## Key Concepts

- **LSC**: A coordinated change spanning a large portion of a codebase.
- **Shard**: A bounded piece of an LSC submitted and reviewed separately.
- **Rosie**: Google tooling used to manage large-scale changes.
- **TAP**: Test Automation Platform used to validate changes and shards.
- **Codebase insight**: Repository and ownership information needed to plan a broad change.
- **Backsliding**: New code reintroducing the pattern the LSC removed.
- **Cattle versus pets**: Treating shards as replaceable units managed by automation rather than hand-crafted artifacts.

## Mental Models

- An LSC is a distributed systems problem with code as the message.
- Review capacity, test capacity, and owner discovery are first-class constraints.
- Atomicity is a spectrum: make the global result coherent while keeping individual changes manageable.
- A migration is incomplete until the old form is prevented from returning.

## Anti-patterns

- **Hand-editing at scale**: It is slow, inconsistent, and impossible to audit.
- **One giant change**: It overloads review, testing, and merge infrastructure.
- **No owner routing**: Shards wait or are approved without the right context.
- **No backsliding control**: The codebase regresses after the campaign.
- **Ignoring heterogeneity**: A transformation assumes all code uses the same language, build, or style.

## Worked Example

Migrating C++ ownership from scoped_ptr to std::unique_ptr illustrates the process. A tool identifies references, generates a mechanical change, splits it into owner-sized shards, runs tests, mails appropriate reviewers, and submits only validated pieces. Static analysis then prevents new uses of the old type. The infrastructure makes a technically straightforward but organizationally enormous refactor feasible.

## Reference Table

| LSC phase | Required capability |
|---|---|
| Plan | Repository insight and authorization |
| Generate | Reliable transformation tooling |
| Shard | Ownership and review-size limits |
| Validate | CI, tests, and flake management |
| Review | Owner discovery and human verification |
| Submit | Safe sequencing and conflict handling |
| Prevent | Static checks and cleanup |

## Key Takeaways

1. Build LSC infrastructure before the next urgent migration.
2. Generate changes; do not hand-edit thousands of files.
3. Shard by ownership and validate each unit.
4. Preserve human review and readable output.
5. Finish by preventing backsliding.

## Connects To

- **Chapter 15**: Deprecation needs LSC machinery for discovery and migration.
- **Chapter 16**: A coherent head and repository ownership enable atomic change.
- **Chapter 20**: Static analysis keeps removed patterns from returning.

