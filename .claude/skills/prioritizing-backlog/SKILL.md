---
name: prioritizing-backlog
description: >
  Prioritizes a product backlog using RICE, WSJF, MoSCoW, or Kano frameworks.
  Selects the right framework based on context, scores all items, produces a
  ranked backlog with rationale, and flags items that need more information
  before scoring. Language- and technology-agnostic. Use when the team needs to
  decide what to build next, when backlog items need relative ranking, or when
  stakeholders need a structured priority decision. Trigger keywords: prioritize,
  RICE, WSJF, MoSCoW, Kano, rank features, what to build next, backlog ranking,
  backlog grooming, priority order, value vs effort, cost of delay.
---

## Purpose

Produce an objective, rationale-backed ranked backlog that the team can commit to and that stakeholders can understand.

## Input

Accept any of:
- List of features, epics, or stories (paste, table, or bullet list)
- Backlog file path (read it first)
- PRD with functional requirements (read and extract items)

Read `.po-workflow-state.json` for product context and business goals.

If nothing is provided, ask: "What items do you want prioritized? Paste a list or share a file path."

## Framework Selection

Choose the framework based on context:

| Context | Framework | Why |
|---|---|---|
| Quantitative data available (reach, usage metrics) | **RICE** | Produces defensible scores from data |
| SAFe environment, PI planning | **WSJF** | Standard SAFe prioritization method |
| Customer survey data available | **Kano** | Reveals customer delight vs basic expectations |
| Stakeholder alignment meeting, sprint scope decision | **MoSCoW** | Fast, collaborative, no scoring required |
| Quick decision with limited data | **Impact/Effort matrix** | Visual, fast, 2×2 quadrant |

When the user does not specify, ask: "Do you have usage data, are you in a SAFe environment, or do you want a quick prioritization? I'll pick the right framework."

## RICE Scoring

Formula: `Score = (Reach × Impact × Confidence) / Effort`

| Factor | Scale | Definition |
|---|---|---|
| **Reach** | Number of users/requests per time period | How many users are affected per quarter |
| **Impact** | 0.25 / 0.5 / 1 / 2 / 3 | Massive (3), High (2), Medium (1), Low (0.5), Minimal (0.25) |
| **Confidence** | 100% / 80% / 50% | How confident you are in Reach and Impact estimates |
| **Effort** | Person-months | Engineering estimate |

Output table:
```markdown
| Item | Reach | Impact | Confidence | Effort | RICE Score | Rank |
|---|---|---|---|---|---|---|
| [Feature A] | 1000 | 2 | 80% | 1 | 1600 | 1 |
```

## WSJF (SAFe) Scoring

Formula: `WSJF = Cost of Delay / Job Duration (Size)`

Cost of Delay = User/Business Value + Time Criticality + Risk Reduction / Opportunity Enablement

Fibonacci scale for each component: 1, 2, 3, 5, 8, 13, 20

Output table:
```markdown
| Item | User Value | Time Crit. | Risk/OE | CoD | Job Size | WSJF | Rank |
|---|---|---|---|---|---|---|---|
| [Feature A] | 8 | 5 | 3 | 16 | 3 | 5.3 | 1 |
```

## Kano Classification

Categories:
- **Must-be (Basic):** Absence causes dissatisfaction; presence is expected. No competitive advantage.
- **Performance (Linear):** More = more satisfaction. Core differentiators.
- **Delighters (Excitement):** Unexpected; cause delight when present; no dissatisfaction when absent.
- **Indifferent:** Neutral impact either way.
- **Reverse:** Presence causes dissatisfaction (over-engineering).

Allocation target: ~60% Must-be, ~30% Performance, ~10% Delighter.

Output table:
```markdown
| Item | Category | Rationale | Priority Recommendation |
|---|---|---|---|
| [Feature A] | Must-be | Industry-standard expectation | Deliver before launch |
```

## MoSCoW Classification

| Category | Definition | Limit |
|---|---|---|
| **Must** | Without this, the product/sprint fails | ≤ 60% of sprint capacity |
| **Should** | High value, can be deferred by one sprint | ≤ 20% of capacity |
| **Could** | Nice to have if time allows | ≤ 20% of capacity |
| **Won't** | Explicitly excluded from this scope | Documented, not forgotten |

Output table:
```markdown
| Item | MoSCoW | Rationale |
|---|---|---|
| [Feature A] | Must | Required for regulatory compliance |
```

## Impact/Effort Matrix (Quick)

Quadrants:
- **Quick Wins (High Impact, Low Effort):** Do first
- **Major Projects (High Impact, High Effort):** Schedule with capacity
- **Fill-ins (Low Impact, Low Effort):** Do when convenient
- **Time Sinks (Low Impact, High Effort):** Defer or eliminate

## Process

### Step 1 — Collect and Normalize Items

List all backlog items. For each, note:
- Item ID and title
- Known context (business value, customer request, technical debt, compliance)
- Any existing estimates

### Step 2 — Score All Items

Apply the selected framework. For items with missing data:
- Use a default conservative score
- Flag the item: "⚠️ Score based on assumption — validate with data"

### Step 3 — Rank and Write Output

```markdown
# Backlog Prioritization: [Product / Sprint / Quarter]

> **Framework:** [RICE / WSJF / MoSCoW / Kano / Impact-Effort]
> **Date:** [YYYY-MM-DD]
> **Scope:** [Sprint N / Q[N] / Release X]

## Ranking

| Rank | ID | Title | Score | Category / Priority | Rationale |
|---|---|---|---|---|---|
| 1 | [ID] | [Title] | [Score] | Must / P0 | [Why this is top] |

## Items Flagged for Clarification

| ID | Title | Missing Data | Recommended Action |
|---|---|---|---|
| [ID] | [Title] | [What's unknown] | [Stakeholder to ask] |

## Items Explicitly Deferred (Won't This Cycle)

| ID | Title | Reason for Deferral | Next Review |
|---|---|---|---|

## Prioritization Rationale

[2–3 sentences explaining the top priorities in relation to the business goals in `.po-workflow-state.json`]
```

### Step 4 — Write Output File

Save to `docs/product/backlog-prioritization-<date>.md`.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "prioritization",
  "last_artifact": "docs/product/backlog-prioritization-<date>.md",
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Quality Rules

1. **Every ranked item has a rationale.** "Higher priority because it has a higher score" is not a rationale — explain the business reasoning.
2. **Flag assumptions explicitly.** A score based on guessed data must be labeled.
3. **Deferred is not deleted.** Won't items are listed and dated for next review — not silently dropped.
4. **MoSCoW Must items must fit in sprint capacity.** If Must items exceed capacity, escalate to stakeholders — do not inflate sprint commitment.
