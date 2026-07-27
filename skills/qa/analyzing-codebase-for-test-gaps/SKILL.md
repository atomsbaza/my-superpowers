---
name: analyzing-codebase-for-test-gaps
description: >
  Scans the existing codebase to identify untested or undertested code paths.
  Finds controllers, service methods, and domain logic with no corresponding
  test files, exception handlers never exercised, and branches not covered by
  existing tests. Use when starting QA on an existing codebase, after a major
  refactor, or to prepare a coverage improvement plan. Trigger keywords:
  coverage gaps, untested code, missing tests, test coverage analysis,
  coverage report, uncovered branches, what is not tested, test gaps, codebase scan.
context: fork
---

## Purpose

Identify where the codebase has no or insufficient test coverage, prioritized by risk, so the team focuses testing effort where it matters most.

## Important: Use Grep and Glob for Scanning

Do NOT load entire source files into context. Use `grep` to extract method signatures and `find`/`Glob` to enumerate files. Load individual files only when a specific finding needs verification.

## Process

### Step 1 — Discover Structure

```bash
# List all production source files
find src -name "*.cs" -not -path "*/obj/*" -not -path "*/bin/*" -not -path "*/Migrations/*" | sort

# List all test files
find tests -name "*Tests.cs" -o -name "*Test.cs" | sort
```

### Step 2 — Find Source Files with No Corresponding Test File

For each file matching `*Service.cs`, `*Controller.cs`, `*Handler.cs`, `*Repository.cs` in `src/`, check whether a matching `*Tests.cs` exists in `tests/`.

```bash
# Extract names of service/handler/controller files
find src -name "*Service.cs" -o -name "*Handler.cs" -o -name "*Controller.cs" \
     -not -path "*/obj/*" | sort
```

For each file found, search for its test counterpart:
```bash
find tests -name "<FileName>Tests.cs" | wc -l
```

Flag files with zero test counterparts as **Gap: No Test File**.

### Step 3 — Find Untested Public Methods

For source files that DO have test counterparts, extract public method signatures:
```bash
grep -n "public.*Task\|public.*async\|public.*IEnumerable\|public.*IQueryable\|public.*List\|public.*void" \
     src/MyProject.Application/Services/OrderService.cs
```

Check whether each method name appears in the corresponding test file:
```bash
grep -c "PlaceOrder\|CancelOrder\|GetOrder" tests/Unit/OrderServiceTests.cs
```

Flag methods not appearing in tests as **Gap: Method Not Tested**.

### Step 4 — Identify Untested Exception Paths

```bash
# Find all catch blocks across source files
grep -rn "catch\s*(" src/ --include="*.cs" -l
```

For each file with catch blocks, check whether any test exercises the exception path:
```bash
grep -n "catch\|ThrowsAsync\|throws\|exception" tests/ -r --include="*.cs" -l
```

Flag catch blocks with no corresponding test as **Gap: Exception Path Not Tested**.

### Step 5 — Identify High-Density Branch Files (No Coverage Signal)

```bash
# Find files with many conditional branches
grep -c "if\s*(\|else\s*{\|switch\s*(\|case\s" src/**/*.cs | sort -t: -k2 -rn | head -20
```

Files with >15 branches and sparse test coverage are high-risk. Flag them.

### Step 6 — Check EF Core Query Coverage

```bash
# Find all EF Core query operations
grep -rn "\.Where\|\.FirstOrDefaultAsync\|\.ToListAsync\|\.FindAsync\|\.AnyAsync\|\.CountAsync" \
     src/ --include="*.cs"
```

For each query pattern found, check whether integration tests exercise that query:
```bash
grep -rn "FirstOrDefaultAsync\|ToListAsync" tests/Integration/ --include="*.cs"
```

Flag query patterns with no integration test as **Gap: Query Not Integration-Tested**.

### Step 7 — OceanBase-Specific Gaps

```bash
# Find partition-specific queries (PARTITION keyword)
grep -rn "PARTITION\|partition" src/ --include="*.cs"
```

Flag any partition-specific SQL with no corresponding integration test using a real OceanBase container (not `mysql:8.0`).

```bash
# Find any FOR SHARE usage (incompatible with OceanBase)
grep -rn "FOR SHARE\|WithLock" src/ --include="*.cs"
```

Flag `FOR SHARE` as a BLOCKER — OceanBase does not support it.

### Step 8 — Produce Gap Report

Write `test-coverage-gap-report.md`:

```markdown
# Test Coverage Gap Report
## Generated: <date>
## Codebase Root: <path>

## Summary
| Metric                              | Count |
|-------------------------------------|-------|
| Source files scanned                | N     |
| Files with no test file             | N     |
| Public methods not tested           | N     |
| Exception paths not tested          | N     |
| High-branch files (>15) sparse      | N     |
| EF Core queries not integration-tested | N  |
| OceanBase FOR SHARE (BLOCKER)       | N     |

## P0 Gaps — Test Immediately
| File                     | Method / Path           | Gap Type                   | Risk Reason                  |
|--------------------------|------------------------|----------------------------|------------------------------|
| OrderService.cs          | ProcessPayment()        | No test file               | Payment — data loss risk     |
| AuthController.cs        | RefreshToken()          | Exception path not tested  | Auth — security boundary     |

## P1 Gaps — Test This Sprint
...

## P2 Gaps — Test Before Release
...

## BLOCKERS (Fix Before Testing Can Proceed)
| File               | Line | Issue               | Fix Required                          |
|--------------------|------|---------------------|---------------------------------------|
| OrderRepo.cs       | 142  | FOR SHARE used      | Replace with IsRowVersion() optimistic concurrency |

## Recommended Next Steps
1. Run `generating-automation-scripts` for all P0 gaps
2. Add Testcontainers integration tests for all untested EF Core queries
3. Run Stryker.NET to establish mutation score baseline: `dotnet stryker`
4. Add OceanBase container integration tests for partition queries
```

### Step 9 — Update Workflow State

```json
{
  "stage": "gap_analysis_complete",
  "gap_report_file": "test-coverage-gap-report.md",
  "p0_gaps": 0,
  "p1_gaps": 0,
  "p2_gaps": 0,
  "blockers": 0,
  "error": null
}
```
