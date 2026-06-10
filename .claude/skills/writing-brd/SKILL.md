---
name: writing-brd
description: >
  Produces a Business Requirements Document (BRD) from stakeholder input,
  executive briefs, or business opportunity descriptions. Covers executive
  summary, business problem, goals with measurable success metrics,
  stakeholder map, in/out scope, constraints, assumptions, and risk register.
  Language- and technology-agnostic. Use when a business stakeholder has
  identified an opportunity or problem and needs a structured case before
  engineering starts. Trigger keywords: BRD, business requirements, business
  case, stakeholder requirements, business problem, business justification,
  why are we building this, business opportunity.
---

## Purpose

Document the "why" behind a product or feature — enough for a business stakeholder to approve funding and for engineering to understand the problem they are solving without being told the solution.

## Input

Accept any of:
- Executive brief or email
- Meeting notes or interview transcript
- Vision document (`docs/product/vision.md`)
- User description of a business opportunity

If nothing is provided, ask: "What is the business problem or opportunity this document should capture?"

## Process

### Step 1 — Identify Core Business Need

Extract or ask for:
1. What problem exists today?
2. Who is affected and how severely?
3. What happens if we do nothing? (cost of inaction)
4. What does success look like in measurable terms?

Do not propose a solution yet. The BRD documents the problem space.

### Step 2 — Build the Stakeholder Map

| Stakeholder | Role | Interest | Influence | Engagement Mode |
|---|---|---|---|---|
| [Name/Role] | Sponsor / Decision Maker / Affected User | [What they care about] | High/Medium/Low | Consult / Inform / Approve |

### Step 3 — Write the BRD

Follow this structure precisely:

```markdown
# Business Requirements Document: [Product / Initiative Name]

| Field | Value |
|---|---|
| Version | v1.0 |
| Date | [YYYY-MM-DD] |
| Author | Product Owner |
| Status | Draft / Under Review / Approved |
| Approvers | [Names and roles] |

---

## 1. Executive Summary

[2–3 sentences: the business problem, the proposed initiative, and the expected business outcome.]

---

## 2. Business Problem

### 2.1 Problem Statement
[Clear, solution-agnostic description of the pain. Who experiences it? How often? What is the impact?]

### 2.2 Cost of Inaction
[What happens if we do nothing? Quantify if possible: revenue at risk, churn rate, manual hours wasted.]

### 2.3 Current State
[How is the problem solved today? Why is the current solution insufficient?]

---

## 3. Business Goals and Success Metrics

| # | Goal | Success Metric | Baseline | Target | Timeframe |
|---|------|----------------|----------|--------|-----------|
| 1 | [Goal] | [KPI] | [Current value] | [Target value] | [When] |
| 2 | | | | | |

---

## 4. Stakeholder Map

| Stakeholder | Role | Interest | Influence | Engagement |
|---|---|---|---|---|
| [Name] | [Role] | [What they care about] | High/Med/Low | Consult/Inform/Approve |

---

## 5. Scope

### 5.1 In Scope
- [Business capability 1 that must be addressed]
- [Business capability 2]

### 5.2 Out of Scope
- [What we are explicitly NOT doing — prevents scope creep]
- [Adjacent problem we are deferring]

---

## 6. Business Requirements

> Business requirements state WHAT the business needs, not HOW to build it.
> Format: BR-NNN: [The system/process/capability shall…]

| ID | Requirement | Priority (MoSCoW) | Source / Rationale |
|---|---|---|---|
| BR-001 | [The capability that must exist] | Must | [Stakeholder / regulation / goal] |
| BR-002 | | Should | |
| BR-003 | | Could | |

---

## 7. Constraints

| Type | Constraint |
|---|---|
| Timeline | [Hard deadline and reason, e.g., "Regulatory compliance by Q3"] |
| Budget | [Budget ceiling or envelope] |
| Legal / Regulatory | [Applicable regulation] |
| Technical | [Platform, integration, or compatibility constraint] |
| Organizational | [Team, resource, or process constraint] |

---

## 8. Assumptions

> If any of these turn out to be false, the BRD must be revised.

| # | Assumption | Validation Method | Owner |
|---|-----------|------------------|-------|
| 1 | [Assumption the plan relies on] | [How to confirm] | [Who] |

---

## 9. Risks

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R-001 | [Risk description] | High/Med/Low | High/Med/Low | [Mitigation action] |

---

## 10. Dependencies

- [Dependency 1: system, team, vendor, or external event]
- [Dependency 2]

---

## 11. Approval

| Name | Role | Decision | Date |
|---|---|---|---|
| | Sponsor | Approved / Rejected / Deferred | |
| | Business Owner | | |

---

## Appendix

### Open Questions
- [ ] [Question that must be resolved before PRD]

### Change Log
| Version | Date | Change | Author |
|---------|------|--------|--------|
| v1.0 | [Date] | Initial draft | |
```

### Step 4 — Write Output File

Determine version: check `docs/requirements/` for existing BRD files for this product. Increment version number.

Save to `docs/requirements/brd-<product-slug>-v<N>.md`. Create directory if needed.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "brd",
  "last_artifact": "docs/requirements/brd-<product>-v1.md",
  "business_goals": ["goal 1 from BR table"],
  "open_questions": ["open questions from appendix"],
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Quality Check

Before finalizing, verify:
- [ ] Problem statement has no solution language
- [ ] Every business goal has a measurable metric and target
- [ ] Scope has both In and Out sections
- [ ] At least one risk documented
- [ ] Assumptions section exists and is non-empty
- [ ] BRD does not specify technology, architecture, or implementation approach
