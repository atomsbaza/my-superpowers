---
name: reporting-test-results
description: >
  Analyzes test execution output and produces structured defect reports and
  test execution summaries in ISTQB-standard format. Reads TRX files, test
  output logs, console output, or raw failure descriptions. Produces individual
  defect tickets and an executive test summary with Go/No-Go recommendation.
  Trigger keywords: test results, defect report, bug report, test summary,
  execution report, test run results, failures analysis, test report,
  pass fail summary, test metrics, go no-go.
---

## Purpose

Transform raw test output into actionable defect reports that developers can act on, and an executive summary that stakeholders can use for release decisions.

## Input

Accept any of:
- TRX file path: `dotnet test --logger "trx;LogFileName=results.trx"`
- Console test output (paste or file path)
- Direct failure descriptions from the user

If no test output is provided, ask: "Please share the test results — TRX file path, console output, or paste the failure details."

## 3 Golden Rules for Reporting

1. **No rubber-stamps.** A summary that says "all tests passed" without stating what was tested is not a report. Always list what was verified.
2. **Cite or it didn't happen.** Every defect references the exact test that failed and the exact assertion that broke.
3. **Distinguish claim from verification.** "The test claims to cover X" and "I confirmed the test actually exercises X" are different — flag tests that pass trivially.

## Process

### Step 1 — Parse Test Results

For TRX files:
```bash
# Extract failed tests from TRX
grep -A10 'outcome="Failed"' test-results.trx | grep -E 'testName|Message|StackTrace'
```

For console output: identify lines with `FAIL`, `Error`, `Exception`, or `✗`.

### Step 2 — Defect Report Per Failure

For each failed test, produce an ISTQB-format defect report:

```markdown
## DEF-<NNN>: <Short, imperative title describing the defect>

| Field              | Value                                             |
|--------------------|---------------------------------------------------|
| ID                 | DEF-001                                           |
| Severity           | Critical / High / Medium / Low                    |
| Priority           | P0 / P1 / P2                                      |
| Status             | New                                               |
| Detection Method   | Automated test / Exploratory / Code review        |
| Test Case Ref      | TC_LOGIN_003 / LoginTests.Login_WithValidCredentials_RedirectsToDashboard |
| Environment        | Test / Staging / Local                            |
| Build              | v1.2.3 / commit abc1234                           |
| Reported Date      | <date>                                            |

### Steps to Reproduce
1. <Exact step — specific URL, data, action>
2. <Next step>
3. <Final action that triggers the defect>

### Actual Result
<Exactly what happened — paste the exception message or assertion failure>

### Expected Result
<What the test or requirement says should happen>

### Evidence
- **Test assertion:** `<failed assertion text>`
- **Stack trace:** `<first 3 relevant lines>`
- **Screenshot:** `<path if Playwright captured it>`

### Severity Rationale
<Why this severity — e.g., "Critical: auth_token not set means all authenticated requests will fail">

### Root Cause Hypothesis
<Based on stack trace analysis — be specific: "NullReferenceException at OrderService.cs:142 suggests the order entity is not loaded before access">

### Suggested Fix
<Concrete suggestion if determinable from the stack trace — one or two sentences>
```

### Step 3 — Severity Classification

Assign severity based on business impact:

| Severity | Criteria | Examples |
|---|---|---|
| **Critical** | System crash, data loss, security breach, auth failure | Payment fails, user data deleted, login broken |
| **High** | Core feature broken, no workaround | Order creation fails, search returns wrong results |
| **Medium** | Feature degraded, workaround exists | Pagination off by one, export slow |
| **Low** | Cosmetic, minor UX | Tooltip text wrong, minor alignment |

Priority maps to test priority: P0 test failure → P0 defect by default. Override if the failure is not business-critical.

### Step 4 — Executive Test Execution Summary

```markdown
# Test Execution Summary

| Field            | Value                  |
|------------------|------------------------|
| Feature / Sprint | <name>                 |
| Date             | <date>                 |
| Environment      | <env>                  |
| Build            | <version>              |
| Tester           | Automated + QA team    |

## Test Metrics

| Metric                          | Value   |
|---------------------------------|---------|
| Total test cases planned        | N       |
| Executed                        | N (X%)  |
| Passed                          | N (X%)  |
| Failed                          | N (X%)  |
| Blocked                         | N       |
| Not executed                    | N       |
| P0 pass rate                    | X%      |
| P1 pass rate                    | X%      |
| Mutation score (Stryker.NET)    | X%      |
| p95 response time               | Xms     |
| Performance NFR met?            | Yes / No|

## Defects Summary

| Severity | Open | Fixed | Deferred |
|----------|------|-------|----------|
| Critical | N    | N     | N        |
| High     | N    | N     | N        |
| Medium   | N    | N     | N        |
| Low      | N    | N     | N        |

## Exit Criteria Status

| Criteria                                   | Status      |
|--------------------------------------------|-------------|
| 100% of P0 test cases passing              | ✅ / ❌      |
| ≥95% of P1 test cases passing              | ✅ / ❌      |
| Zero open Critical defects                 | ✅ / ❌      |
| Zero open High defects without workaround  | ✅ / ❌      |
| p95 response time ≤ NFR target             | ✅ / ❌      |
| Mutation score ≥ 70%                       | ✅ / ❌      |

## What Was Verified

<!-- Satisfies Golden Rule 1: state what was tested -->
- Authentication flows (login, logout, refresh token)
- Order creation (valid, invalid, concurrent)
- OceanBase partition queries (RANGE p2026)
- Performance: 100 RPS steady-state, 2 minutes

## Go/No-Go Recommendation

**[GO / NO-GO]:** <One sentence rationale>

<!-- GO: All exit criteria met -->
<!-- NO-GO: State the specific criterion blocking release and the defect IDs -->
```

### Step 5 — Update Workflow State

```json
{
  "stage": "results_reported",
  "defect_count": 0,
  "critical_defects": 0,
  "high_defects": 0,
  "summary_file": "test-execution-summary-<date>.md",
  "defect_files": ["defects/DEF-001.md"],
  "go_nogo": "GO | NO-GO",
  "error": null
}
```

## Stryker.NET Results Interpretation

If a Stryker.NET HTML report is provided:
- **Mutation score < 60%:** HIGH risk — many code paths are not exercised. Flag as MAJOR gap.
- **Mutation score 60–79%:** MEDIUM — acceptable minimum before release.
- **Mutation score ≥ 80%:** GOOD — test suite is catching real code changes.

Note surviving mutants that are in P0 business logic paths — list them specifically.
