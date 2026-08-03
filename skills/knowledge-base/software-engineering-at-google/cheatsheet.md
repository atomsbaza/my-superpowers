# Cheatsheet

## Decide what to invest in

| If the software is… | Prefer… |
|---|---|
| Short-lived and local | Fast, lightweight programming practices |
| Long-lived or widely depended upon | Explicit contracts, tests, documentation, and upgrade paths |
| Used by many teams | Automation, canonical sources, shared head, and scalable policy |

## Before measuring

- If no outcome would change after a positive or negative result, do not measure.
- Start with a decision and a goal; derive signals and only then choose metrics.
- Cover QUANTS: Quality, Attention, iNtel­lectual complexity, Tempo/velocity, Satisfaction.
- If a number is easy to collect but cannot be traced to a goal, treat it as a smell.

## Before adding a rule

- Does it prevent danger, enforce a best practice, or create consistency?
- Is the benefit larger than the cost of learning, enforcing, and migrating?
- Can a formatter, checker, or suggested fix enforce it?
- If readers see inconsistent code, prefer the convention that lowers surprise.

## Before approving a change

1. Is the purpose narrow and the intent clear?
2. Are build, tests, formatting, and analysis automated?
3. Is the right owner reviewing it?
4. Would a future maintainer understand why it exists?
5. Is the review state and next action explicit?

## Choose a test

- Local behavior → small state-oriented unit test.
- Component boundary → medium test.
- Configuration, deployment, load, recovery, or emergent behavior → larger test.
- Real dependency is fast and deterministic → use it.
- Real dependency is too costly → use a tested fake.
- Stub only to control a narrow scenario; interaction-test only meaningful state-changing calls.

## Deprecate safely

owner → discover → replace → warn → migrate → prevent new use → remove

- A warning without discovery and migration tooling is not a deprecation plan.
- Do not remove the old path until consumer cost and replacement readiness are understood.
- Add a check that prevents backsliding.

## Manage versions and dependencies

- Prefer one current version and a shared head when coordination permits.
- Treat every dependency as an ongoing support contract.
- SemVer is a risk hint; CI is evidence.
- Version external inputs explicitly; never rely on unexamined “latest.”

## Scale change and delivery

- Broad migration → generate, shard, test, route owners, review, submit, prevent.
- Fast reliable checks → presubmit.
- Broad or slower checks → post-submit.
- Risky release → feature flag, staged rollout, observe, rollback or expand, then clean up.
- Production workload → classify batch/serving, externalize state, design for failure, rightsize, and autoscale.

## Fast smells

- Observable behavior with no test → future compatibility trap.
- One person owns all context → bus-factor or leadership bottleneck.
- Persistent CI red → feedback channel has lost authority.
- Many versions or long-lived branches → deferred integration cost.
- A static check users ignore → false-positive or workflow problem.
- A document with no owner/freshness → future misinformation.

