---
name: orchestrating-qa-workflow
description: >
  Orchestrates the complete end-to-end QA workflow from requirements through
  results: analyzing requirements, creating test plan, generating manual test
  cases, generating BDD scenarios, analyzing codebase gaps, generating
  automation scripts, generating performance tests, and reporting results.
  Use when you want to run the full QA pipeline, do end-to-end QA from a
  document, or resume a paused QA workflow. Trigger keywords: full QA workflow,
  end to end QA, run all QA steps, complete testing pipeline, QA pipeline,
  orchestrate testing, start QA from scratch, QA from BRD, QA from PRD.
---

## Purpose

Chain all QA skills in sequence using `.qa-workflow-state.json` to persist progress, enable resume after interruption, and enforce quality gates between stages.

## Workflow Stages

```
[START]
    │
    ▼
[1] analyzing-requirements-for-qa
    └─► stage = "requirements_analyzed"
    │
    ▼
[2] creating-test-plan
    └─► stage = "test_plan_created"
    │
    ▼
[3] generating-manual-test-cases
    └─► stage = "manual_test_cases_generated"
    │
    ├──► [4a] generating-bdd-scenarios   (parallel)
    │         └─► stage = "bdd_scenarios_generated"
    │
    └──► [4b] analyzing-codebase-for-test-gaps   (if codebase path provided)
              └─► stage = "gap_analysis_complete"
    │
    ▼
[5] generating-automation-scripts
    └─► stage = "automation_scripts_generated"
    │
    ▼ (if NFRs present)
[6] generating-performance-tests
    └─► stage = "performance_tests_generated"
    │
    ▼ (after test execution)
[7] reporting-test-results
    └─► stage = "results_reported"
    │
    ▼
[DONE — feature ready for release decision]
```

## State File: `.qa-workflow-state.json`

Full schema:
```json
{
  "stage": "init",
  "feature": "<feature name>",
  "started_at": "<ISO timestamp>",
  "source_document": null,
  "codebase_path": null,
  "output_file": null,
  "scenario_count": 0,
  "p0_count": 0, "p1_count": 0, "p2_count": 0,
  "test_plan_file": null,
  "test_cases_file": null,
  "total_cases": 0,
  "feature_files": [],
  "step_definition_stubs": [],
  "gap_report_file": null,
  "p0_gaps": 0, "p1_gaps": 0, "p2_gaps": 0, "blockers": 0,
  "test_files_created": [],
  "pom_files_created": [],
  "fixture_files_created": [],
  "performance_test_files": [],
  "nfr_thresholds": {},
  "defect_count": 0,
  "critical_defects": 0,
  "summary_file": null,
  "go_nogo": null,
  "error": null,
  "history": []
}
```

## Quality Gates (Enforced — Not Skipped)

| From Stage | Gate Condition | If Not Met |
|---|---|---|
| → Test Plan | `scenario_count > 0` and no BLOCKER ambiguities | Stop, ask user to resolve ambiguities |
| → Manual Test Cases | `test_plan_file` exists | Re-run test plan stage |
| → Automation Scripts | `test_cases_file` exists | Re-run manual test cases stage |
| → Performance Tests | NFRs present in requirements | Skip performance stage if no NFRs |
| → Results Report | Test output file exists | Ask user to run tests and provide output |

BDD generation and codebase gap analysis run after manual test cases are complete. They do not block each other.

## Process

### Step 1 — Initialize or Resume

```bash
cat .qa-workflow-state.json 2>/dev/null || echo '{"stage":"init"}'
```

If `stage != "init"`, resume from the last completed stage — skip all completed steps.

If `error` is non-null:
- Print: "Stage `<stage>` failed with: `<error>`"
- Ask: "Retry (r), skip (s), or abort (a)?"
- Honor the user's choice and clear or preserve the error in state.

### Step 2 — Collect Inputs

Ask once (if not already in state):
1. "What is the feature name?"
2. "Do you have a BRD/PRD/requirements document? (file path or paste)"
3. "Do you have a codebase to scan for gaps? (src/ path, or skip)"
4. "Are there performance NFRs? (response time targets, RPS requirements, or skip)"

### Step 3 — Run Each Stage

For each stage in the workflow:

1. Announce the stage: `Starting stage: [stage name]`
2. Invoke the skill (by describing what it should do)
3. Confirm the stage name is written to `workflow-state.json` before proceeding
4. Print a one-line status update: `✅ Stage complete: <stage> — <brief summary>`

If any skill writes `"error": "<message>"` to state, stop and surface it immediately.

### Step 4 — Conditional Routing

After `requirements_analyzed`:
- **BDD route:** Always run `generating-bdd-scenarios`
- **Gap analysis route:** Run `analyzing-codebase-for-test-gaps` only if `codebase_path` is set
- **Performance route:** Run `generating-performance-tests` only if NFRs exist in the analysis
- **OceanBase route:** If OceanBase is the persistence layer, ensure `generating-automation-scripts` uses `ContainerBuilder` with `oceanbase/oceanbase-ce:4.2.2`, not `MySqlBuilder`

### Step 5 — Final Summary

After all stages complete, print:

```markdown
## QA Workflow Complete

### Feature: <feature name>

| Stage                    | Status | Key Output                              |
|--------------------------|--------|-----------------------------------------|
| Requirements Analysis    | ✅     | qa-requirements-analysis.md             |
| Test Plan                | ✅     | test-plan-<feature>-v1.md               |
| Manual Test Cases        | ✅     | manual-test-cases-<feature>.md (N cases)|
| BDD Scenarios            | ✅     | tests/BDD/Features/ (N scenarios)        |
| Codebase Gap Analysis    | ✅     | test-coverage-gap-report.md (N P0 gaps) |
| Automation Scripts       | ✅     | N test files generated                   |
| Performance Tests        | ✅     | tests/Performance/ (NBomber)             |
| Test Results Report      | ⏳     | Run tests first, then invoke reporting   |

### Metrics
- Total manual test cases: N (P0: N, P1: N, P2: N)
- P0 coverage gaps found: N
- Automation files generated: N

### Recommended Next Steps
1. Run `dotnet test` and share output to invoke `reporting-test-results`
2. Run `dotnet stryker` to validate mutation score ≥70% on changed files
3. Resolve N ambiguous requirements before finalizing test cases
```

## Error Handling Policy

- Never silently continue past a failed stage
- Never skip quality gates unless the user explicitly says to
- If a stage writes an error, surface it with the full error text
- If the state file becomes corrupted, offer to reset to `init` stage
