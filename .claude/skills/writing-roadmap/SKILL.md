---
name: writing-roadmap
description: >
  Creates outcome-based product roadmaps using Now/Next/Later or quarterly OKR
  themes. Produces visual ASCII roadmaps, theme descriptions with business
  rationale, OKR connections, and explicit exclusions. Language- and
  technology-agnostic. Use when the team or stakeholders need to see product
  direction, when planning a quarter or PI, or when communicating priorities to
  leadership. Trigger keywords: roadmap, Now Next Later, product direction,
  quarterly plan, OKR roadmap, PI planning, product roadmap, strategic
  priorities, where are we going, what are we building next quarter.
---

## Purpose

Give stakeholders a shared, written view of where the product is going, why, and in what order — without committing to specific dates for distant items.

## Input

Accept any of:
- Vision document (`docs/product/vision.md`)
- BRD or PRD (read to extract goals)
- Prioritized backlog (`docs/product/backlog-prioritization-*.md`)
- `.po-workflow-state.json` for business goals
- Direct user description of product direction

If nothing is provided, ask: "What is the roadmap for? A product, a feature area, or a release? And what time horizon?"

## Roadmap Principles

1. **Outcome-based, not feature-list.** Each horizon has a business theme, not a delivery commitment.
2. **Honest about uncertainty.** "Now" is firm. "Next" is planned. "Later" is directional.
3. **Tied to OKRs or business goals.** Every theme explains why the business cares.
4. **Explicit about what is NOT on the roadmap.** Reduces stakeholder expectation drift.

## Roadmap Types

| Type | When to Use | Time Horizon |
|---|---|---|
| **Now/Next/Later** | Continuous flow, no fixed dates | Rolling quarters |
| **Quarterly OKR** | OKR-based planning cycle | 4 quarters |
| **PI Roadmap** | SAFe Program Increment | ~3 months per PI |
| **Release Roadmap** | Fixed-date releases | Specific versions |

Default to Now/Next/Later unless the user specifies otherwise.

## Process

### Step 1 — Extract Business Goals

From vision, BRD, or workflow state, identify:
- Top 3 business goals (with metrics)
- Key customer problems not yet solved
- Technical constraints that affect sequencing

### Step 2 — Define Roadmap Themes

For each horizon, define one primary theme:
- **Theme name:** 2–4 words (e.g., "Core Onboarding", "Growth Loops", "Enterprise Readiness")
- **Business rationale:** Why now / next / later?
- **Key epics or capabilities included**
- **Success metric:** How will we know this theme delivered value?

### Step 3 — Write the Roadmap

#### Now/Next/Later Format

```markdown
# Product Roadmap: [Product Name]

> **Version:** v1.0
> **Date:** [YYYY-MM-DD]
> **Owner:** Product Owner
> **Horizon:** [Rolling — Now = this quarter, Next = Q+1, Later = Q+2 and beyond]

---

## Vision
[One-sentence product vision]

## Business Goals This Roadmap Serves
1. [Goal 1 with metric]
2. [Goal 2 with metric]
3. [Goal 3 with metric]

---

## NOW — [Theme Name]
**Timeline:** [Month YYYY – Month YYYY]
**Business Rationale:** [Why this is the highest priority right now]
**OKR / Business Goal Connection:** [Which goal from above this serves]

### Key Epics / Capabilities
| Epic | Expected Outcome | Priority |
|---|---|---|
| [Epic 1] | [Business outcome] | Must |
| [Epic 2] | [Business outcome] | Should |

### Success Metrics
- [ ] [Metric: e.g., "Onboarding completion rate > 70%"]
- [ ] [Metric 2]

---

## NEXT — [Theme Name]
**Timeline:** [Month YYYY – Month YYYY (approximate)]
**Business Rationale:** [Why this follows from Now]
**OKR / Business Goal Connection:** [Goal]

### Key Epics / Capabilities
| Epic | Expected Outcome | Dependency on Now |
|---|---|---|
| [Epic 1] | | [Now theme deliverable required] |

### Success Metrics
- [ ] [Metric]

---

## LATER — [Theme Name]
**Timeline:** [H2 YYYY or "To be scheduled based on Now+Next outcomes"]
**Business Rationale:** [Why this is important but not yet]
**Prerequisite:** [What must be true before this starts]

### Direction (Not a Commitment)
- [Capability area 1]
- [Capability area 2]

---

## Explicitly NOT on the Roadmap

> These were considered and consciously excluded for this planning cycle.

| Item | Reason for Exclusion | Next Review Date |
|---|---|---|
| [Feature] | [Business or technical reason] | [Date or trigger] |

---

## Assumptions

| # | Assumption | If Wrong, Impact |
|---|-----------|-----------------|
| 1 | [Assumption the roadmap depends on] | [What changes in the roadmap] |

---

## Open Questions

- [ ] [Question that must be resolved to finalize Now theme]

---

## Change Log

| Version | Date | Change | Author |
|---------|------|--------|--------|
| v1.0 | [Date] | Initial roadmap | |
```

#### Quarterly OKR Format (Alternative)

```markdown
# Quarterly OKR Roadmap: [Product Name]

| Quarter | Objective | Key Results | Epics |
|---|---|---|---|
| Q1 | [Objective] | KR1: [Metric target] | [Epic 1, Epic 2] |
| Q2 | [Objective] | KR1: [Metric target] | [Epic 3, Epic 4] |
| Q3 | [Objective] | KR1: [Metric target] | [Epic 5] |
| Q4 | [Objective — directional] | KR1: [To be defined] | [TBD] |
```

### Step 4 — Write Output File

Save to `docs/product/roadmap-<date>.md`. Create directory if needed.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "roadmap",
  "last_artifact": "docs/product/roadmap-<date>.md",
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Quality Rules

1. **No feature lists masquerading as roadmaps.** If every entry is a specific feature, the roadmap is a sprint backlog in disguise. Rewrite as themes with business outcomes.
2. **Later must have a prerequisite.** "Later" items without a dependency condition are just wishes.
3. **Exclusions section is mandatory.** Stakeholders ask about every notable feature not on the roadmap — answer them proactively.
4. **Dates on Now only.** Dates on Later items are false precision. Use "H2 2026" or "after onboarding completion" instead.
5. **Tie every theme to a business goal.** A theme without a business rationale is a technology wish, not a product decision.
