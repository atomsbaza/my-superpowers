# Chapter 23: Continuous Integration

## Core Idea

Continuous integration is the feedback system that keeps a growing codebase integrable. It decides what to test and when, separates fast reliable presubmit checks from broader post-submit checks, and makes failures accessible, actionable, attributable, and auditable.

## Frameworks Introduced

- **Fast feedback loops**: Put quick, deterministic checks before commit and slower or less deterministic checks after commit.
  - When to use: Designing CI stages.
  - How: Optimize presubmit for developer latency; use post-submit for broad coverage, release confidence, and resource-heavy validation.
- **Accessible and actionable feedback**: A red build must tell the right person what failed and what to do next.
  - When to use: Test failures, infrastructure errors, and large organizations.
  - How: Preserve logs, identify culprits, route ownership, and provide stable reproduction paths.
- **Hermetic testing**: Control test inputs and dependencies so failures are meaningful and reproducible.
  - When to use: Large CI fleets and tests with environmental sensitivity.
  - How: Isolate state, declare dependencies, control time/network, and make setup reproducible.
- **CI as alerting**: CI is an operational signal about the health of the development system.
  - When to use: Managing broken builds, resource constraints, and failure queues.
  - How: Assign ownership, prioritize recovery, and prevent persistent red states from becoming normal.

## Key Concepts

- **Continuous build**: Automatically building changes as they enter the shared repository.
- **Presubmit**: Validation before a change is committed.
- **Post-submit**: Validation after integration.
- **Release candidate testing**: Broader checks before a release.
- **Culprit finding**: Identifying the change most likely to have introduced a failure.
- **Hermetic test**: A reproducible test with controlled dependencies.
- **TAP**: Google’s Test Automation Platform for large-scale continuous validation.
- **Failure management**: Triage, ownership, and recovery of broken checks.

## Mental Models

- Presubmit protects the author and reviewer; post-submit protects the repository and release.
- A CI system is a queueing system: latency, capacity, prioritization, and backpressure matter.
- “Green” is a social contract; a persistently broken build teaches people that failures are optional.
- Test logs are product UI for developers.

## Anti-patterns

- **Run everything presubmit**: Feedback becomes slow and developers bypass it.
- **Presubmit only**: Broad regressions, release behavior, and cross-platform risks remain unseen.
- **Indecipherable logs**: Engineers spend more time interpreting CI than fixing code.
- **No culprit ownership**: Failures remain red while every team assumes another caused them.
- **Uncontrolled environment**: CI results cannot be reproduced locally or trusted.

## Worked Example

The TAP model separates fast checks needed before commit from broader continuous validation. When a test fails, culprit finding identifies the likely change, a responsible owner receives actionable logs, and the system tracks recovery. Resource constraints are handled as scheduling and prioritization problems rather than by silently dropping important coverage.

## Code Examples

~~~text
presubmit: format + build + focused tests + high-confidence analysis
post-submit: full tests + cross-platform + integration + release checks
~~~

## Key Takeaways

1. Use different CI stages for different latency and fidelity needs.
2. Make feedback accessible, actionable, and owned.
3. Invest in hermeticity and reproducibility.
4. Treat broken builds as incidents in the development system.
5. Scale test selection and scheduling rather than abandoning coverage.

## Connects To

- **Chapter 11**: CI is the automated write-run-react loop.
- **Chapter 18**: Build determinism enables reliable CI scheduling and caching.
- **Chapter 24**: Continuous delivery uses CI feedback to ship safely.

