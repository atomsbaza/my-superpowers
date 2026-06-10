---
name: analyzing-requirements-for-qa
description: >
  Reads BRD, PRD, or user story documents and extracts all testable scenarios,
  acceptance criteria, risk areas, and edge cases for QA planning. Use when you
  have requirements documents and need to understand what to test before writing
  test cases. Outputs a structured analysis to workflow-state.json for downstream
  QA skills. Trigger keywords: analyze requirements for testing, extract test
  scenarios, testable conditions, acceptance criteria, BRD for QA, PRD for QA,
  user story testing, feature spec analysis, what to test.
---

## Purpose

Transform unstructured requirements text into a structured testing inventory with risk scores, so the QA team knows exactly what to test and in what order.

## Input

Accept requirements as any of:
- File path(s) to BRD, PRD, feature spec, or user story documents
- Pasted text in the conversation

If nothing is provided, ask: "Please share the BRD, PRD, or feature specification — file path or pasted text."

## Process

### Step 1 — Ingest the Document

Read all provided files. Extract every section that describes system behavior, business rules, acceptance criteria, or constraints.

### Step 2 — Identify Testable Units

For each section or user story, extract:
- **Functional requirements** — what the system must do (look for "shall", "must", "will")
- **Non-functional requirements** — performance targets, availability, security constraints, scalability
- **Business rules** — validation logic, calculation rules, state machine transitions
- **Explicit acceptance criteria** — Given/When/Then if present
- **Implicit acceptance criteria** — derive from requirement statements where Given/When/Then is not written

Flag any requirement that is ambiguous or untestable as `[AMBIGUOUS]`.

### Step 3 — Risk Scoring

Score each testable unit:
- **Probability of failure** (1–5): How likely is this to have a defect?
- **Business impact of failure** (1–5): What is the cost if this fails in production?
- **Risk Score** = Probability × Impact

Priority assignment:
- Score 16–25 → **P0** (critical — must test before any release)
- Score 9–15 → **P1** (high — test in every sprint)
- Score 1–8 → **P2** (medium/low — test before major releases)

Default to P1 when the document does not provide enough context to score.

### Step 4 — Edge Case Enumeration via SFDIPOT

For each testable unit, apply SFDIPOT to ensure no dimension is missed:

- **Structure:** Data model constraints, schema rules, referential integrity
- **Function:** Each function's happy path + every stated error condition
- **Data:** Empty, null, zero, minimum value, maximum value, max string length, special characters (especially emoji and non-BMP Unicode for OceanBase utf8mb4), SQL injection patterns, whitespace-only
- **Integration:** External service dependencies, API contracts, message queue payloads, webhook formats
- **Platform:** Browser/OS combinations (for UI), .NET runtime versions, OceanBase tenant compatibility
- **Operations:** Concurrent users, high-volume data, bulk import/export, pagination edge cases
- **Time:** Date/time boundaries (DST transitions, year-end, leap year Feb 29), expired tokens, session timeouts, delayed processing

### Step 5 — Produce Requirements Analysis Document

Write `qa-requirements-analysis.md` with:

```markdown
# Requirements Analysis for QA
## Document: <filename>
## Analysis Date: <date>

## Testable Scenarios Inventory
| ID      | Scenario Description               | Type          | Priority | Risk Score |
|---------|-----------------------------------|---------------|----------|------------|
| REQ-001 | User login — valid credentials     | Functional+   | P0       | 20         |
| REQ-002 | User login — invalid email         | Functional-   | P1       | 12         |
| REQ-003 | Login form — empty submission      | Negative      | P1       | 9          |

## Risk Register
| Requirement | Risk Description                | Probability | Impact | Score |
|-------------|--------------------------------|-------------|--------|-------|

## Non-Functional Requirements
| NFR Type     | Requirement                    | Measurable Target        |
|-------------|--------------------------------|--------------------------|

## Derived Acceptance Criteria
<!-- For requirements without Given/When/Then, derive them -->
### REQ-001: User Login — Valid Credentials
- Given a registered user exists with email "user@test.com"
- When the user submits valid credentials
- Then the user is redirected to /dashboard
- And an auth_token cookie is set with HttpOnly and Secure flags

## Edge Cases Identified (SFDIPOT)
| Category    | Edge Case                                | Mapped Requirement |
|-------------|------------------------------------------|--------------------|

## Gaps and Ambiguities Requiring Clarification
| ID  | Requirement Text Quote          | Issue                          | Priority |
|-----|--------------------------------|--------------------------------|----------|
| G-1 | "fast response time"           | No measurable target specified | BLOCKER  |
```

### Step 6 — Update Workflow State

Write or update `.qa-workflow-state.json`:
```json
{
  "stage": "requirements_analyzed",
  "source_document": "<path or inline>",
  "output_file": "qa-requirements-analysis.md",
  "scenario_count": 0,
  "p0_count": 0,
  "p1_count": 0,
  "p2_count": 0,
  "ambiguous_count": 0,
  "error": null,
  "history": [{"stage": "requirements_analyzed", "at": "<ISO timestamp>"}]
}
```

## Validation Before Finishing

- Every `[AMBIGUOUS]` requirement has a corresponding entry in the Gaps table
- At least one P0 scenario exists for any feature involving auth, payments, or data mutations
- NFRs are extracted even if not explicitly stated (mark as `[INFERRED]`)
- SFDIPOT Data dimension always includes utf8mb4 special character test for OceanBase targets
