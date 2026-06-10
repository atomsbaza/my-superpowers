---
name: planning-sprint
description: >
  Creates a sprint plan from a prioritized backlog. Defines the sprint goal,
  selects stories to commit based on velocity and capacity, identifies
  dependencies and risks, and outputs a sprint plan document. Language- and
  technology-agnostic. Use at the start of a sprint planning session or when
  the team needs to decide what fits in the next sprint. Trigger keywords:
  sprint plan, sprint goal, sprint backlog, velocity, capacity, sprint
  planning, what fits in the sprint, sprint commitment, sprint N.
---

## Purpose

Produce a sprint plan that the team can commit to: a clear sprint goal, a realistic story selection within capacity, identified risks, and explicit acceptance criteria for the sprint as a whole.

## Input

Accept any of:
- Prioritized backlog file path (read it first)
- List of candidate stories with point estimates
- Velocity and team capacity information
- `.po-workflow-state.json` for product context

If nothing is provided, ask: "What sprint number is this, what is the team's velocity, and what stories are candidates?"

## Key Concepts

**Velocity:** Average story points completed per sprint (use last 3-sprint average when available).

**Capacity:** Actual available person-days this sprint, accounting for holidays, PTO, and non-development time.

**Sprint Goal:** A single sentence that describes the business value the team will deliver. All committed stories must contribute to the sprint goal.

**Commitment:** Stories the team commits to complete. Not a "stretch goal" list.

## Process

### Step 1 — Establish Capacity

Ask for or calculate:
```
Team size: N people
Sprint length: N weeks (usually 2)
Working days per person: N days/sprint
Non-development time (meetings, reviews): N days/person
Available development days = (Team size × Working days) − Non-development days
Velocity (story points): [last 3-sprint average or team estimate]
```

### Step 2 — Define the Sprint Goal

The sprint goal must:
- Be a single sentence
- State business value (what the user or business gains)
- Be achievable given the selected stories
- Allow the team to make trade-off decisions during the sprint

Format: "By the end of Sprint N, [who] will be able to [what], enabling [business outcome]."

Example: "By the end of Sprint 12, customers will be able to reset their password via email, reducing support tickets for account access issues."

### Step 3 — Select Stories

Apply these rules:
1. Start from the top of the prioritized backlog
2. Select stories until committed points reach velocity − 10% buffer
3. Every committed story must contribute to the sprint goal
4. Stories > 5 points must be split before commitment
5. Stories without acceptance criteria must be written before commitment (invoke `writing-acceptance-criteria` if needed)

### Step 4 — Identify Risks and Dependencies

For each committed story, check:
- Does it depend on another team, system, or story?
- Is there a technical blocker that must be resolved first?
- Is the scope clear enough to start on day 1?

Flag anything that could derail the sprint goal.

### Step 5 — Write the Sprint Plan

```markdown
# Sprint [N] Plan

| Field | Value |
|---|---|
| Sprint | [N] |
| Start Date | [YYYY-MM-DD] |
| End Date | [YYYY-MM-DD] |
| Sprint Length | [N weeks] |
| Team Velocity | [N story points] |
| Committed Points | [N story points] |

---

## Sprint Goal

> "[By the end of Sprint N, [who] will be able to [what], enabling [outcome].]"

---

## Sprint Backlog

### Committed Stories

| Priority | ID | Title | Points | Owner | Acceptance Criteria |
|---|---|---|---|---|---|
| 1 | US-001 | [Title] | [N] | [Dev] | [Link or inline ref] |
| 2 | US-002 | | | | |

**Total committed:** [N] points (velocity: [N] — [N]% utilized)

### Stretch Goals (if capacity allows)
| ID | Title | Points | Condition |
|---|---|---|---|
| US-XXX | [Title] | [N] | Start only if committed stories are complete by Day 7 |

---

## Capacity Summary

| Team Member | Available Days | Sprint Role | Focus Area |
|---|---|---|---|
| [Name] | [N] | Dev / QA / Lead | [Stories] |
| [Name] | [N] | | |

**Non-development time:** [N days total — sprint planning, daily standups, review, retro]

---

## Dependencies and Risks

| ID | Risk / Dependency | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R-001 | [Risk or dependency] | High/Med/Low | High/Med/Low | [Action] |

---

## Sprint Entry Criteria

- [ ] All committed stories have acceptance criteria written
- [ ] All committed stories are ≤ 5 story points
- [ ] Dependencies identified and owners notified
- [ ] Sprint goal agreed by team and Product Owner
- [ ] Environment and access ready for all stories

---

## Sprint Exit Criteria (Definition of Done)

- [ ] All committed stories pass acceptance criteria
- [ ] All code reviewed and merged to main branch
- [ ] Tests (unit + integration) passing in CI
- [ ] Sprint goal achieved
- [ ] Sprint demo ready for stakeholders

---

## Sprint Review Agenda

1. Demo: [Story US-001 — Name of demonstrator]
2. Demo: [Story US-002 — Name of demonstrator]
3. Metrics: Velocity, burndown
4. PO acceptance: Pass / Fail per story
5. Stakeholder Q&A

---

## Open Blockers

| # | Blocker | Owner | Escalation Path |
|---|---------|-------|-----------------|
| | | | |
```

### Step 6 — Write Output File

Save to `docs/sprints/sprint-<N>-plan.md`. Create directory if needed.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "sprint_plan",
  "last_artifact": "docs/sprints/sprint-<N>-plan.md",
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Sprint Planning Quality Rules

1. **Sprint goal is not a list of stories.** "Complete US-001, US-002, US-003" is a to-do list, not a goal. Rewrite as business value.
2. **Never commit to more than velocity.** Optimism is not velocity. Use the 3-sprint average.
3. **Never commit a story without ACs.** If ACs don't exist, write them or don't commit the story.
4. **Never hide blockers.** If a story has an unresolved dependency, it is a risk — surface it explicitly.
5. **Stretch goals are not commitments.** They are worked on only when committed stories are complete.
