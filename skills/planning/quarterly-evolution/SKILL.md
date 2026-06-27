---
model: sonnet
name: quarterly-evolution
description: >
  Structures a technical investment proposal as a quarterly evolution case instead of
  a 10-year roadmap. Software fights entropy and requires regular investment — the
  correct pitch is a focused, time-bounded improvement with a measurable business
  outcome, not a long-term architectural vision. Confidence in projections decays
  rapidly beyond 90 days. Trigger on /quarterly-evolution when proposing tech debt
  paydown, refactoring, infrastructure upgrades, or architecture migrations.
---

# Quarterly Evolution

Structure technical investment as a quarterly evolution, not a 10-year roadmap.
Software is evolved, not built. It fights entropy — accumulating leaks, drift,
and decay that require regular investment to manage.

The financial flaw of 10-year architecture plans: projection confidence decays
rapidly. A plan that sounds compelling at year 1 is speculation by year 3 and
fiction by year 5. Pitch quarterly evolutions with measured outcomes instead.

## When to invoke

- Proposing tech debt paydown or refactoring work for roadmap inclusion
- Pitching an infrastructure upgrade, migration, or platform change
- Responding to "why should we invest in this?" from product or leadership
- Turning a vague "we need to modernize X" into a fundable proposal
- `/quarterly-evolution` is typed

## The Quarterly Evolution Frame

A quarterly evolution proposal has four components:

1. **Entropy audit** — what has accumulated and is slowing the system down
2. **Targeted improvement** — one focused change, completable in one quarter
3. **Business outcome** — the measurable result the business cares about
4. **Deferral cost** — what gets worse each quarter this is not addressed

## Why quarterly, not annual or multi-year

- 90-day confidence is high: the codebase state is known, the team is known, the load
  is known. Predictions are grounded in observable reality.
- 1-year confidence is medium: depends on team stability, product direction, load growth
  — all of which change.
- 3-year confidence is low: product pivots, market changes, technology shifts, team
  turnover all compound. A 3-year architecture plan is largely fiction.
- Quarterly proposals are fundable: a VP can approve a quarter of investment against
  a measurable outcome. They cannot approve a 3-year plan whose ROI is theoretical.

## Workflow

### 1. Name the entropy
Describe what has accumulated concretely. Avoid abstract terms like "tech debt" or
"legacy code" — they do not make the cost legible to non-engineers.

Good: "Every new feature in the billing module requires touching 4 files and running
a manual regression test — adding a new payment provider took 3 engineer-weeks in Q3."

Bad: "The billing module has accumulated significant technical debt that is slowing
development."

### 2. Define the targeted improvement
State one specific, completable change. Resist the urge to bundle. A proposal that
says "modernize the entire data layer" will not be approved. A proposal that says
"migrate the billing module to the new payment abstraction" will.

- Scope it to one quarter of work (6–10 engineer-weeks)
- Name the specific component, module, or system being changed
- Name what will be different after (not "cleaner" — something observable)

### 3. Quantify the business outcome
Use the same frame as `/business-impact`:
- Features unblocked per quarter
- Engineer-hours saved per week (× weeks in a year)
- Incident reduction (fewer on-call pages × average incident cost)
- Onboarding speed (new engineers productive in X days instead of Y)

At least one number, even if approximate. Flag if it is an estimate.

### 4. State the deferral cost
What gets measurably worse each quarter this is not done?
- "Each quarter we add ~1 additional engineer-week per new payment provider"
- "Incident frequency has increased 20% quarter-over-quarter for the last 3 quarters"
- "Onboarding a new engineer to this module currently takes 2 weeks; complexity is
  growing faster than documentation can keep up"

This is the cost of inaction — critical for prioritization decisions.

### 5. Set the success condition
One measurable outcome that declares the evolution complete:
- "New payment provider integration takes < 3 days, down from 3 weeks"
- "Module test suite runs in < 2 minutes, enabling CI gating"
- "On-call pages from this subsystem drop to < 1/week"

Not: "the code is cleaner" or "the architecture is sound."

## Output format

```
## Quarterly Evolution Proposal

**System / component:** [name]
**Proposed quarter:** [Q1 / Q2 / Q3 / Q4 YYYY]

### Entropy audit
[2–4 sentences. Concrete, operational. What has accumulated and what does it cost
in measurable terms?]

### Targeted improvement
[1–2 sentences. One specific change, scoped to one quarter.]

### Business outcome
- [metric]: [current state] → [projected state after]
- [metric]: [current state] → [projected state after]

### Deferral cost
[What gets measurably worse each quarter this is deferred.]

### Success condition
[One measurable outcome that declares this complete.]

### Investment ask
[Engineer-weeks] over [timeframe] — no new headcount required / requires [X].
```

## Rules

- Never propose a multi-year roadmap through this skill. If the scope is multi-year,
  break it into quarterly increments and propose only the first one.
- Never use abstract framing: "technical debt," "modernization," "clean up," "refactor."
  Replace with concrete operational descriptions.
- The success condition must be measurable. "Better" is not measurable. "< 3 days
  to onboard a new payment provider" is measurable.
- If the deferral cost is zero (doing this now vs. next quarter makes no measurable
  difference), the proposal cannot be justified as urgent. Say so honestly — it may
  still be worth doing, just not urgently.
- One proposal per evolution. Bundling reduces approval probability and makes
  success conditions ambiguous.
