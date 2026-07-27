---
name: creating-test-plan
description: >
  Creates a formal, risk-based test plan document from requirements analysis or
  project context. Includes scope, test approach by layer, entry and exit
  criteria, environment needs, resource estimates, and risk mitigation. Use when
  starting a new feature, sprint, or release cycle. Trigger keywords: test plan,
  test strategy, QA plan, test scope, entry criteria, exit criteria, test
  approach, sprint QA plan, release test plan, testing strategy.
---

## Purpose

Produce a complete, executable test plan that answers: what will be tested, how, by whom, with what tools, and what "done" looks like.

## Input

- `.qa-workflow-state.json` → `output_file` (requirements analysis document)
- Any provided PRD, architecture doc, or previous test plans
- Direct user context if no state file exists

## Process

### Step 1 — Read Requirements Analysis

Read `.qa-workflow-state.json` to find the requirements analysis output file. Read that file for scope, risk scores, NFRs, and scenario counts.

If no state file, ask for the requirements document or feature description.

### Step 2 — Define Scope

**In scope:** Features explicitly mentioned in requirements with P0 or P1 risk rating.

**Out of scope:** Third-party integrations owned by external teams, features marked as future, infrastructure not changed by this release.

**Deferred:** P2 scenarios that require dedicated exploratory time, performance testing if NFRs are not yet defined.

### Step 3 — Test Approach by Layer

For each layer, specify tools, ownership, trigger, and expected coverage:

| Layer        | Tool/Framework                  | Owner      | Trigger          | Coverage Goal              |
|--------------|---------------------------------|------------|------------------|----------------------------|
| Unit         | xUnit + Moq/NSubstitute         | Dev        | Every commit     | ≥80% mutation score        |
| Integration  | xUnit + Testcontainers          | Dev/QA     | Every PR         | All DB operations, all API boundaries |
| E2E          | Playwright + xUnit (PageTest)   | QA         | Every PR (P0), nightly (full) | All P0 user flows |
| BDD          | Reqnroll + xUnit                | QA/BA      | Every PR         | All acceptance criteria     |
| Performance  | NBomber                         | QA/Platform| Pre-release      | All NFR targets met         |
| Contract     | Pact.NET                        | Dev/QA     | Every PR         | All service-to-service APIs |
| Exploratory  | Manual (SFDIPOT heuristic)      | QA         | Per sprint       | Risk-based charter          |
| Mutation     | Stryker.NET                     | Dev        | Weekly gate      | ≥70% mutation score         |

**OceanBase integration tests:** Use generic `ContainerBuilder` with `oceanbase/oceanbase-ce:4.2.2`. For basic CRUD, `mysql:8.0` is acceptable. For partition behavior, only real OceanBase container is valid.

### Step 4 — Entry Criteria

Testing may begin when ALL of the following are met:
- Code review approved and merged to feature branch
- Unit tests passing with ≥80% mutation score (Stryker.NET)
- Test environment deployed with latest build artifact
- EF Core migrations applied to test database
- Test data seeded (Bogus-generated fixtures with fixed seed)
- Feature flag enabled in test environment (if applicable)

### Step 5 — Exit Criteria (Release Gate)

Testing is complete and release is approved when ALL of the following are met:
- 100% of P0 test cases passing
- ≥95% of P1 test cases passing (remaining defects tracked with workaround)
- Zero open Severity 1 (Critical) defects
- Zero open Severity 2 (High) defects without approved workaround
- Performance NFRs met: p95 response time ≤ [stated target] at [stated RPS]
- Mutation score ≥70% for all modified service/handler files
- No security findings from automated scan (if applicable)

### Step 6 — Risk Register with Mitigation

List the top 5 risks ranked by score from the requirements analysis. For each:

| Risk Description              | Probability | Impact | Score | Mitigation Strategy               |
|-------------------------------|-------------|--------|-------|-----------------------------------|
| OceanBase partition query slow | 3           | 5      | 15    | Add partition key to all queries; perf test pre-release |

### Step 7 — Environment and Data

**Test environments needed:**
- `dev-integration`: Testcontainers (OceanBase CE, ephemeral per test run)
- `test`: Shared OceanBase test cluster, seeded with Bogus fixtures
- `staging`: Production-mirror, anonymized data

**Test data strategy:**
- Unit tests: Moq/NSubstitute mocks, no real data
- Integration tests: Bogus factories with `.UseSeed(42)` for reproducibility
- E2E tests: Pre-seeded test accounts in test environment (not shared with staging)
- OceanBase charset: All generated strings tested with utf8mb4 characters

### Step 8 — Output

Write `test-plan-<feature>-v1.md` with all sections above.

Update `.qa-workflow-state.json`:
```json
{
  "stage": "test_plan_created",
  "test_plan_file": "test-plan-<feature>-v1.md",
  "error": null
}
```
