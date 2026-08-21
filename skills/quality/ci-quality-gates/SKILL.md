---
name: ci-quality-gates
description: Use when designing, reviewing, or debugging CI/CD quality gates, build pipelines, test pipelines, preview deployments, staged rollouts, or rollback plans. Prefer targeted checks for small changes and require evidence before calling a change ready.
---

# CI Quality Gates

Use this skill to make a change's readiness observable rather than relying on a green-looking summary. Adapt commands to the repository's actual stack; the sequence is a decision procedure, not a Node-specific template.

## 1. Define the change surface

Before choosing gates, identify:

- changed files and their runtime boundary
- user-visible paths, APIs, data migrations, and infrastructure touched
- the repository's documented commands and required checks
- whether the change is code, configuration, documentation, or a docs-only change

Choose the smallest test scope that can provide credible evidence, and record why broader gates are not applicable.

## 2. Order the gates by cost and signal

Use the cheapest reliable signal first:

1. formatting and lint/static analysis
2. type checking or compilation
3. focused unit tests for changed behavior
4. package/build validation
5. integration or contract tests when boundaries changed
6. E2E tests for critical user paths when the UI or end-to-end contract changed
7. security and dependency checks when inputs, permissions, secrets, or dependencies changed

For every gate, record its status as `required`, `conditional`, or `advisory`, plus the command, scope, owner, timeout, and artifact location. A missing artifact is `unverified`, not `passed`.

## 3. Handle failures without hiding them

When a gate fails:

- preserve the exact command, exit code, first useful error, and affected scope
- reproduce with the narrowest relevant check before running an expensive suite
- fix the cause or document an explicit, time-bounded exception with an owner
- never disable, skip, or weaken a check solely to turn a red pipeline green
- treat test-data, service-startup, timeout, and cleanup failures as distinct failure classes

A change is not ready while a required gate is failed or unverified. Cleanup failure overrides an otherwise passing result when it leaves a worktree, process, fixture, or report in an unknown state.

## 4. Separate verification from release actions

A pull-request pipeline should establish evidence for review. Staging and production deployment are separate transitions:

- use preview or staging validation before production
- keep production secrets out of CI test jobs and logs
- use feature flags or staged rollout for risky changes
- define a concrete rollback target and verification window before deployment
- require explicit approval for deploy, rollback, merge, push, or external publication

This skill can design or audit those gates; it does not silently deploy, push, merge, or change branch protection.

## 5. Keep evidence useful

The final gate summary must include:

- revision and environment identity
- commands and scopes that were run
- pass/fail/blocked/unverified status per gate
- test counts and coverage only when actually measured
- links or paths to logs, traces, screenshots, and build artifacts
- known limitations, skipped conditional gates, and the reason for each
- the exact next action for every failure or blocker

Do not claim a full-suite result from a targeted run. Do not call a deployment safe without a tested rollback path.

## 6. Optimize only after correctness

If CI is slow, optimize in this order:

- cache immutable dependencies using the repository's supported mechanism
- parallelize independent gates without sharing mutable state
- use path-aware selection for genuinely unrelated changes
- shard or schedule expensive suites while retaining a meaningful PR smoke gate
- remove redundant checks only after measuring overlap and preserving coverage

The completion criterion is a reproducible gate matrix with every required check evidenced, every exception owned and time-bounded, and no hidden failure or unapproved release action.
