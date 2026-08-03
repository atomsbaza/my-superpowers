# Patterns

## Goals → Signals → Metrics
**When to use**: Designing a productivity or developer-experience measurement.
**How**: Define the decision and goal; identify signals; choose measurable proxies; preserve traceability; act on either result.
**Trade-offs**: Takes longer than collecting convenient numbers, but avoids the streetlight effect and vanity metrics.

## QUANTS Coverage
**When to use**: Evaluating productivity or workflow changes.
**How**: Check Quality, Attention, iNtel­lectual complexity, Tempo/velocity, and Satisfaction for goals and trade-offs.
**Trade-offs**: Broader measurement costs more, but prevents single-axis optimization.

## Canonical Source
**When to use**: Multiple documents or answers compete.
**How**: Assign an owner, place the source under version control, publish a stable link, and retire duplicates.
**Trade-offs**: Central authority needs maintenance; fragmentation costs more at scale.

## Reviewable Change
**When to use**: Any code change entering a shared repository.
**How**: Keep purpose narrow, explain intent, automate checks, route to the right owners, and preserve history.
**Trade-offs**: Smaller submissions require sequencing but improve review quality and recovery.

## Layered Test Suite
**When to use**: A system needs both fast feedback and realistic confidence.
**How**: Use small tests for local behavior, medium tests for boundaries, and larger tests for integration, deployment, load, and recovery risks.
**Trade-offs**: Larger tests add fidelity and latency; units alone leave important gaps.

## State-Oriented Unit Test
**When to use**: Testing a stable public API.
**How**: Arrange explicit inputs, invoke the API, and assert observable state and failure behavior.
**Trade-offs**: Less coupled than interaction tests, but may require a usable fake or larger test.

## Realism-First Test Double
**When to use**: Deciding whether to mock a dependency.
**How**: Try the real implementation; if too slow or nondeterministic, use a tested fake; use stubs narrowly; interaction-test only meaningful state changes.
**Trade-offs**: Realism costs setup; doubles cost fidelity and maintenance.

## Deprecation Pipeline
**When to use**: Retiring an API, library, service, or behavior.
**How**: Assign owner, discover consumers, publish replacement, warn, migrate, prevent new use, then remove.
**Trade-offs**: Takes sustained coordination but avoids abrupt ecosystem breakage.

## One-Version / Shared Head
**When to use**: Many teams consume a common library or repository.
**How**: Maintain one supported version at a common head; keep release branches narrow and temporary.
**Trade-offs**: Requires coordinated migration and strong CI, but removes repeated version choice.

## Artifact Build Graph
**When to use**: Builds need reproducibility, caching, parallelism, or distributed execution.
**How**: Declare targets, inputs, outputs, and dependencies; use fine-grained modules and controlled visibility.
**Trade-offs**: More dependency metadata in exchange for selective, cacheable work.

## Static-Analysis Feedback Loop
**When to use**: Codifying repeatable safety or quality guidance.
**How**: Start advisory, tune false positives, explain the finding, suggest a fix, integrate with review/presubmit, then block only high-confidence cases.
**Trade-offs**: Platform investment is significant; poor signal quality destroys trust.

## Large-Scale Change
**When to use**: A consistent migration spans many files or owners.
**How**: Generate mechanically, shard by ownership, test, route reviewers, submit, and prevent backsliding.
**Trade-offs**: Infrastructure and policy work precede the migration, but hand-editing does not scale.

## CI Feedback Staging
**When to use**: A test suite contains both fast deterministic checks and broad expensive checks.
**How**: Put focused checks in presubmit; run comprehensive and less deterministic checks post-submit; make failures actionable.
**Trade-offs**: Some confidence arrives later, but developer latency stays usable.

## Flagged Staged Rollout
**When to use**: A risky behavior must be deployed before broad exposure.
**How**: Deploy dark, enable for a small cohort, observe, expand or disable, then remove the flag.
**Trade-offs**: Adds temporary configuration complexity; sharply reduces blast radius.

## Managed Compute Fit
**When to use**: Choosing a runtime platform or abstraction.
**How**: Classify workload as batch or serving, externalize durable state, define resource needs, handle rescheduling, and choose the highest abstraction that preserves required control.
**Trade-offs**: Standardization removes toil but may constrain specialized workloads.

