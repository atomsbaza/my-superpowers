# Chapter 24: Continuous Delivery

## Core Idea

Continuous delivery reduces release risk by integrating changes continuously, isolating behavior, validating reality through staged rollout, and shipping small batches. Velocity is a team property: architecture, testing, flags, deployment, monitoring, and culture must support the same flow.

## Frameworks Introduced

- **Velocity is a team sport**: Release speed depends on the whole system, not one team’s coding rate.
  - When to use: Improving delivery throughput or diagnosing release bottlenecks.
  - How: Reduce integration batch size, modularize architecture, automate deployment, and align teams around a shared flow.
- **Feature-flag isolation**: Separate deploying code from exposing behavior.
  - When to use: Risky changes, experiments, incremental rollout, and rapid rollback.
  - How: Guard a feature, enable it for a controlled population, observe, and disable without reverting the binary.
- **Release train**: Provide a predictable cadence and shared discipline for shipping changes.
  - When to use: Teams that need agility without ad hoc release chaos.
  - How: Establish a regular train, automate qualification, and make exceptions explicit.
- **Ship only what gets used**: Production usage and value determine whether a feature justifies its ongoing cost.
  - When to use: Feature lifecycle and product cleanup.
  - How: Monitor adoption, value, and maintenance; retire unused behavior.
- **Shift left and faster is safer**: Move evidence earlier and reduce the size and duration of each change.
  - When to use: Release-risk reduction.
  - How: Test continuously, stage rollout, and prefer frequent small releases over infrequent large ones.

## Key Concepts

- **Continuous delivery**: Keeping software in a releasable state through automation.
- **Feature flag**: A runtime control that isolates code deployment from behavior exposure.
- **Staged rollout**: Releasing to progressively larger populations.
- **Release train**: A predictable release cadence.
- **Release qualification**: Evidence that a candidate is safe enough to ship.
- **Rollback**: Reverting exposed behavior or a release after a problem.
- **User value**: Real-world benefit measured after deployment.

## Mental Models

- A binary is not the same thing as a release; exposure is a separate control plane.
- Production is the benchmark for user-facing behavior, but staged rollout limits blast radius.
- Small batches reduce both diagnosis scope and time to recovery.
- Feature flags are temporary safety infrastructure and need ownership and cleanup.

## Anti-patterns

- **Big-bang release**: Many changes become difficult to qualify and diagnose together.
- **Branch-based isolation**: Delays integration and discovers conflicts late.
- **Flag without lifecycle**: Permanent flags create hidden paths and configuration debt.
- **Synthetic-only qualification**: A clean test environment misses production diversity.
- **Ship-and-forget**: Features remain costly despite little user value.

## Worked Example

A risky feature can be deployed dark, enabled for internal users, then rolled out to a small production cohort. Metrics and user feedback determine whether to expand, pause, or disable it. Because the binary remains integrated and the behavior is isolated, rollback can be a flag change rather than a large emergency revert.

## Code Examples

~~~text
if flags.new_behavior.enabled_for(request.user):
    serve_new_path()
else:
    serve_existing_path()
~~~

The pattern is safe only when flag ownership, default behavior, monitoring, and cleanup are explicit.

## Key Takeaways

1. Make delivery a cross-team system.
2. Integrate continuously and ship small batches.
3. Isolate risky behavior with flags and staged rollout.
4. Use production evidence, not only synthetic qualification.
5. Track and remove unused features and temporary flags.

## Connects To

- **Chapter 11**: Automated tests make frequent releases possible.
- **Chapter 23**: CI supplies the fast, broad feedback loop.
- **Chapter 25**: Managed compute affects deployment and runtime operations.

