---
name: writing-user-stories
description: >
  Decomposes epics and features into INVEST-quality user stories using SPIDR
  splitting techniques. Produces story cards with persona (JTBD format), value
  statement, story points hint, and links to acceptance criteria. Language- and
  technology-agnostic. Works from PRD, BRD, or a direct feature description.
  Use when backlog items are too large to deliver in one sprint or when stories
  need to be groomed. Trigger keywords: user stories, decompose epic, split
  stories, backlog items, tickets, story writing, story cards, grooming,
  INVEST, SPIDR, story decomposition, write tickets.
---

## Purpose

Transform an epic, feature, or PRD into a backlog of INVEST-quality stories that a team can estimate, plan, and deliver in one sprint each.

## Input

Accept any of:
- PRD file path (read it first — extract requirements and personas)
- Epic description or feature request
- `.po-workflow-state.json` (read for existing context)
- Direct user description of a capability to decompose

If nothing is provided, ask: "What epic or feature do you want to decompose into user stories?"

## INVEST Criteria Checklist

Before finalizing any story, verify:
- **Independent:** Can be delivered without another story being delivered first
- **Negotiable:** Scope can be adjusted without losing core value
- **Valuable:** Delivers value to a user or the business on its own
- **Estimable:** Engineering can size it — if not, it needs splitting or clarification
- **Small:** Completable in one sprint (aim for ≤5 story points; anything ≥8 needs splitting)
- **Testable:** Acceptance criteria are verifiable (pass/fail)

## SPIDR Splitting Guide

Use the first technique that cleanly splits the story:

| Technique | When to Apply | Example |
|---|---|---|
| **Spike** | Too much uncertainty to estimate | "Research payment provider options" before "Integrate Stripe" |
| **Path** | Multiple user flows | Split happy path from error path |
| **Interface** | Multiple UIs or channels | Split web from mobile |
| **Data** | Different data types or sources | Split "import from CSV" from "import from API" |
| **Rules** | Business logic variations | Split simple pricing from complex discounted pricing |

## Process

### Step 1 — Identify Epics and Personas

From the input, list:
1. All functional areas that need stories (from PRD sections or feature domains)
2. All personas that interact with each area (use JTBD format)

### Step 2 — Decompose Into Stories

For each functional area, apply SPIDR to produce 2–8 stories per epic. Each story must be independently deliverable.

### Step 3 — Write Story Cards

Format for each story:

```markdown
## [US-NNN] [Short imperative title]

**As a** [persona — specific role or JTBD situation],
**I want to** [specific action or capability],
**so that** [measurable outcome or benefit].

**Story Points:** [1 / 2 / 3 / 5 / 8 — if 8 or above, split further]
**Priority:** [P0 / P1 / P2] — [MoSCoW: Must / Should / Could]
**Epic:** [Parent epic name]

### Context / Background
[1–2 sentences explaining why this story matters. Not required for obvious stories.]

### Acceptance Criteria
[Link to or inline the ACs — see writing-acceptance-criteria skill]
- [ ] Given [...], When [...], Then [...]

### Definition of Done
- [ ] Feature works as described in ACs
- [ ] Unit and integration tests pass
- [ ] Code reviewed and merged
- [ ] Deployed to staging and validated by PO

### Out of Scope for This Story
- [What is explicitly NOT included]

### Dependencies
- [Story ID or system this story depends on, if any]
```

### Step 4 — Apply Story Quality Rules

**Forbidden story patterns** — rewrite if you see these:

| Anti-pattern | Problem | Fix |
|---|---|---|
| "As an admin, I want a dashboard" | Too large, no single value | Split by dashboard widget or user task |
| "As a user, I want the system to be fast" | Not testable | Write as NFR: "p95 ≤ 500ms" |
| "As a developer, I want to refactor X" | No user value | Rephrase as enabler or technical story with business reason |
| "As a user, I want everything to work" | No scope | Split by specific workflow |
| Story with no acceptance criteria | Not testable | Add ACs before backlog entry |

### Step 5 — Write the Story File

Collect all stories into a single file.

Output format:
```markdown
# User Stories: [Epic Name]

> **Source:** [PRD or feature reference]
> **Date:** [YYYY-MM-DD]
> **Epic Owner:** Product Owner
> **Sprint Target:** [Sprint N or TBD]

## Summary Table

| ID | Title | Persona | Priority | Points |
|---|---|---|---|---|
| US-001 | [Title] | [Persona] | Must | 3 |

---

[Full story cards below]
```

Save to `docs/requirements/stories-<epic-slug>-<date>.md`. Create directory if needed.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "stories",
  "last_artifact": "docs/requirements/stories-<epic>-<date>.md",
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Story Count Guide

| Epic Complexity | Expected Story Count |
|---|---|
| Simple CRUD feature | 3–5 stories |
| Multi-persona workflow | 5–10 stories |
| Complex integration | 8–15 stories |
| Full product area | 15+ stories (consider further epic breakdown) |

If you produce more than 15 stories from a single epic, surface this to the user: the epic may need to be split into sub-epics.
