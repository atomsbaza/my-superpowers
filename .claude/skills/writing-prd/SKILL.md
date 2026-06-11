---
name: writing-prd
description: >
  Produces a Product Requirements Document (PRD) from a BRD, executive brief,
  or feature description. Covers product overview, goals, user personas (JTBD),
  user journeys, functional requirements (MoSCoW-tagged and numbered), NFRs,
  out-of-scope, open questions, and success metrics. Language- and
  technology-agnostic — describes what to build, not how. Use when engineering
  needs a precise specification to design and estimate. Trigger keywords: PRD,
  product spec, feature specification, product requirements, feature doc,
  product requirements document, what to build, functional requirements.
---

## Purpose

Translate business requirements into a precise, engineering-ready specification that answers: What will the product do? Who will use it and how? How will we know it's done?

## Input

Accept any of:
- BRD file path (read it first)
- Business problem or feature description
- Executive brief or stakeholder notes

Read `.po-workflow-state.json` to pick up existing product context.

If nothing is provided, ask: "What feature or product should this PRD specify?"

## Process

### Step 1 — Establish Scope and Context

From the input, identify:
- **Feature or product name**
- **Problem being solved** (copy or adapt from BRD if available)
- **Primary and secondary user personas** (use JTBD — avoid demographic labels)
- **Success metrics** (what changes in user behavior or business outcome)

### Step 2 — Map User Journeys

For each primary persona, write one happy-path journey:

```
[Persona] wants to [achieve goal].

Current state: [How they do it today — pain points]

New state: [How the product improves their journey, step by step]
1. User [action]
2. System [response]
3. User [next action]
4. User [achieves outcome]
```

Also list failure paths: what happens when the journey breaks?

### Step 3 — Write Functional Requirements

Number requirements in groups by domain: AUTH-001, ORDER-001, etc.

Tag each with MoSCoW priority.

Requirement format: "[The system] shall [observable behavior] when [condition]."

Never write: "The system should be fast" or "The UI should be user-friendly." All requirements must be testable.

### Step 4 — Write the PRD

```markdown
# Product Requirements Document: [Feature / Product Name]

| Field | Value |
|---|---|
| Version | v1.0 |
| Date | [YYYY-MM-DD] |
| Author | Product Owner |
| Status | Draft / Under Review / Approved |
| Related BRD | [Path or "N/A"] |
| Approvers | [Names] |

---

## 1. Overview

### 1.1 Problem Statement
[2–3 sentences: what user problem does this solve? Copy and adapt from BRD if available.]

### 1.2 Proposed Solution
[2–3 sentences: what the product will do — no implementation details.]

### 1.3 Success Metrics
| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|--------------------|
| [KPI] | [Current] | [Goal] | [How measured] |

---

## 2. Goals

### 2.1 User Goals
- [What the user will be able to do that they can't do today]

### 2.2 Business Goals
- [How this feature moves the business metrics from the BRD]

### 2.3 Non-Goals (Explicitly Out of Scope)
- [What this feature will NOT do — prevents scope creep]

---

## 3. User Personas

### 3.1 Primary Persona
**Name:** [Persona name]
**JTBD:** When [situation], I want [motivation], so I can [outcome].
**Frequency:** [How often they encounter this scenario]
**Pain Points:** [Current friction]

### 3.2 Secondary Persona (if applicable)
**Name:** [Persona name]
**JTBD:** When [situation], I want [motivation], so I can [outcome].

---

## 4. User Journeys

### 4.1 [Primary Persona] — Happy Path
[Step-by-step journey: user action → system response]

### 4.2 [Primary Persona] — Failure Paths
| Failure Scenario | System Behavior | Recovery Path |
|---|---|---|
| [e.g., Network error during submit] | [Error message shown] | [User can retry] |

---

## 5. Functional Requirements

> Format: [Domain-NNN]: [The system] shall [behavior] when [condition].
> Testable = specific enough that a QA engineer can write a pass/fail test.

### 5.1 [Domain Area 1, e.g., Authentication]

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| AUTH-001 | The system shall [requirement] | Must | |
| AUTH-002 | | Should | |

### 5.2 [Domain Area 2]

| ID | Requirement | Priority | Notes |
|---|---|---|---|
| [DOM]-001 | | Must | |

---

## 6. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-001 | Performance | Response time (p95) | ≤ 500ms under normal load |
| NFR-002 | Availability | Uptime | 99.9% per month |
| NFR-003 | Security | Authentication | All mutations require valid auth token |
| NFR-004 | Scalability | Concurrent users | Support N concurrent users |
| NFR-005 | Accessibility | WCAG compliance | WCAG 2.1 Level AA |

---

## 7. UI/UX Requirements

> Describe behavior and constraints, not visual design (leave that to design).

- [Behavior constraint 1, e.g., "Form must validate inline, not on submit"]
- [Behavior constraint 2]
- [Accessibility requirement]

---

## 8. Data Requirements

| Data Element | Source | Format | Retention | Sensitivity |
|---|---|---|---|---|
| [Field name] | [User input / API / database] | [Type] | [Duration] | PII / Non-PII |

---

## 9. Integration and Dependency Requirements

| System | Type | What Is Needed |
|---|---|---|
| [System name] | API / Database / Event | [What data or capability is required] |

---

## 10. Out of Scope

> Explicit exclusions agreed with stakeholders.

- [Capability or feature NOT included in this PRD]

---

## 11. Open Questions

| # | Question | Owner | Due Date | Status |
|---|---------|-------|----------|--------|
| Q-001 | [Question that must be resolved] | [Owner] | [Date] | Open |

---

## 12. Acceptance Criteria Summary

> High-level acceptance that confirms requirements are met. Detailed ACs live in user stories.

- [ ] [Criterion 1: observable behavior]
- [ ] [Criterion 2]

---

## Appendix

### Glossary
| Term | Definition |
|------|-----------|
| | |

### Change Log
| Version | Date | Change | Author |
|---------|------|--------|--------|
| v1.0 | [Date] | Initial draft | |
```

### Step 5 — Write Output File

Determine version: check `docs/requirements/` for existing PRD files for this feature. Increment version number.

Save to `docs/requirements/prd-<feature-slug>-v<N>.md`. Create directory if needed.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "prd",
  "last_artifact": "docs/requirements/prd-<feature>-v1.md",
  "open_questions": ["open questions from PRD"],
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Quality Check

Before finalizing, verify:
- [ ] Every functional requirement is testable (no vague language)
- [ ] Non-Goals section explicitly states what is excluded
- [ ] NFRs have measurable targets (numbers, not adjectives)
- [ ] All user journeys include at least one failure path
- [ ] Open questions are numbered and assigned an owner
- [ ] No technology stack or implementation details in requirements
