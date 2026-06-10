---
name: generating-manual-test-cases
description: >
  Generates ISTQB-format manual test cases from requirements, acceptance
  criteria, or an existing requirements analysis. Applies equivalence
  partitioning, boundary value analysis, decision tables, and state transition
  techniques. Produces test case documents with ID, objective, preconditions,
  numbered steps, expected results, priority, and severity. Trigger keywords:
  manual test cases, test case document, test steps, expected result, test case
  template, ISTQB test cases, write test cases, create test cases, test case design.
---

## Purpose

Generate comprehensive, executable manual test cases that cover all risk areas identified in requirements analysis. Minimum ratio: 2 negative test cases per positive for every P0 scenario.

## Input

- `.qa-workflow-state.json` → `output_file` (requirements analysis)
- Direct requirements or acceptance criteria from the user
- Feature description for on-demand generation without prior analysis

## Test Design Technique Selection

Apply the right technique based on scenario type:

| Scenario Type | Technique | When to Use |
|---|---|---|
| Input fields, form validation | EP + BVA | Any input with valid/invalid ranges |
| Business rules with conditions | Decision Tables | Multiple independent input conditions |
| Wizard, cart, order lifecycle | State Transition | Defined states + transition rules |
| User-facing features | Use Case Testing | BRD/PRD has user stories or use cases |
| Everything else | SFDIPOT heuristic | Default when no clear structure |

## Process

### Step 1 — Read Requirements Analysis

Read the analysis file from workflow state. For each scenario in the testable inventory (sorted P0 → P1 → P2):

1. Identify the scenario type
2. Select the design technique
3. Generate positive test cases (happy path)
4. Generate negative test cases (invalid inputs, error conditions, boundaries)
5. Generate edge cases from SFDIPOT Data + Time dimensions

### Step 2 — ISTQB Test Case Format

Generate every test case in this format:

```markdown
### TC_<MODULE>_<NNN>: <Concise imperative title>

| Field          | Value                                                   |
|----------------|---------------------------------------------------------|
| ID             | TC_LOGIN_001                                            |
| Module         | Authentication                                          |
| Priority       | P0                                                      |
| Severity       | Critical                                                |
| Type           | Functional / Positive                                   |
| Technique      | Use Case Testing — Basic Flow                           |
| Preconditions  | User has registered account. Application is running.    |
| Test Data      | email: user@test.com  password: ValidPass1!             |

**Steps:**
1. Navigate to /login
2. Enter "user@test.com" in the Email field
3. Enter "ValidPass1!" in the Password field
4. Click the "Sign In" button

**Expected Result:**
- User is redirected to /dashboard
- Welcome banner displays "Welcome, Test User"
- `auth_token` cookie is set with `HttpOnly` and `Secure` flags
- Session expires after 30 minutes of inactivity
```

### Step 3 — Decision Table Test Cases (for business rules)

When multiple conditions combine:

```
Condition Matrix:
  C1: Email valid?     Y  Y  N  N
  C2: Password valid?  Y  N  Y  N
  -------
  Action: Login        ✓  ✗  ✗  ✗
  Action: Show error   -  ✓  ✓  ✓

→ Generate one test case per column (4 test cases, 1 positive + 3 negative)
```

### Step 4 — State Transition Test Cases

Draw the state model from the feature description:
```
Draft → Submitted → Approved → Fulfilled
              └──→ Rejected
```

Generate test cases for:
- Every valid transition (forward flows)
- Every invalid transition (attempt to skip states)
- Re-entry to same state (idempotency)

### Step 5 — BVA Test Cases for Input Fields

For each numeric or string input:
- Min − 1 (invalid) → expect validation error
- Min (valid) → expect success
- Min + 1 (valid) → expect success
- Typical middle value (valid) → expect success
- Max − 1 (valid) → expect success
- Max (valid) → expect success
- Max + 1 (invalid) → expect validation error

For OceanBase string fields — always include:
- Value containing emoji (🧪) → verify utf8mb4 storage
- Value at exact `varchar(N)` length limit
- Value exceeding the limit by 1 character

### Step 6 — Output

Write `manual-test-cases-<feature>.md` containing:
1. **Summary table:** total count, breakdown by priority and type
2. **All test cases** in ISTQB format, grouped by module
3. **Traceability matrix:** TC_ID → Requirement ID

Update `.qa-workflow-state.json`:
```json
{
  "stage": "manual_test_cases_generated",
  "test_cases_file": "manual-test-cases-<feature>.md",
  "total_cases": 0,
  "p0_cases": 0,
  "p1_cases": 0,
  "p2_cases": 0,
  "error": null
}
```

## Quality Check Before Finishing

- Every P0 scenario has ≥1 positive and ≥2 negative test cases
- Every `[AMBIGUOUS]` scenario from requirements analysis is flagged in the test cases as `[BLOCKED — needs clarification]`
- At least one test case exists for each SFDIPOT dimension that applies
- Test data is concrete (specific values, not "valid email") except where variation is the point
