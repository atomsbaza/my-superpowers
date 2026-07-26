---
name: reviewing-code
description: >
  Performs a structured code review using principal engineer standards with
  BLOCKER, MAJOR, and NIT severity levels. Use when the user asks for a code
  review, PR review, review of changes, feedback on code, quality review, or
  to review before merging. Reads changed files and their tests, applies an
  OceanBase-aware checklist, distinguishes new findings from pre-existing issues,
  and outputs a markdown report without modifying any files.
---

## Operating Rules (3 Golden Rules)

These are non-negotiable. Violating them produces reviews that feel thorough but miss real bugs.

1. **No rubber-stamps.** "LGTM" is not output. If you genuinely find nothing, state exactly which code paths you traced and what you checked — so the author can judge whether your coverage was sufficient.
2. **Cite or it didn't happen.** Every finding must reference a specific `file:line`. No finding of the form "this might break under load" without naming the exact condition and the exact code location that exposes it.
3. **Distinguish claim from verification.** "The PR says X" and "I traced X through the code and confirmed it produces X" are different statements. Keep them separate in findings. A comment or docstring claiming it handles error Y does not mean it handles error Y — trace it.

## Purpose

Give the author actionable, high-confidence findings. Every finding must have a concrete impact on users or developers. Never invent findings to appear thorough. Zero findings is acceptable.

## Input

- Changed files: read them all before reviewing
- Related test files: check if tests exist for changed code
- `workflow-state.json` → `implementation` for context on what was built

If reviewing a PR, ask for the diff or file list. If reviewing "the current branch", run:
```bash
git diff main --name-only
```
Then read each changed file.

## Severity Definitions

- **BLOCKER** — Must be fixed before merge. Correctness bugs, data loss risk, security vulnerabilities, missing critical error handling, broken migrations.
- **MAJOR** — Should be fixed before merge. Performance problems, missing test coverage for critical paths, error states not handled, silent failures, design mismatches.
- **NIT** — Optional improvement. Naming, style, minor readability. Only report if project rules require it or it creates a real maintenance burden.

## Review Checklist

Load `reference/review-checklist.md` for the full item list. Apply every item.

### Correctness

- [ ] All code paths return a value or throw — no implicit `null` returns
- [ ] Async methods always `await` or explicitly fire-and-forget with a comment
- [ ] Nullable reference types respected — no unchecked `!` bang operators without justification
- [ ] No integer overflow in arithmetic on user-controlled values
- [ ] Collection iteration does not modify the collection in-place

### Error Handling

- [ ] No empty catch blocks
- [ ] No swallowed exceptions (`catch (Exception) { }` or `catch { }`)
- [ ] No misleading success state (method returns `true` when it silently failed)
- [ ] Background work has logging, retry, or user-visible error recovery
- [ ] Multi-step operations handle partial failure or make partial state observable

### Security

- [ ] No secrets, tokens, or connection strings in code or logs
- [ ] User input validated at system boundary before use
- [ ] SQL built with parameterized queries (EF Core LINQ / `FromSqlInterpolated`) — no string concatenation
- [ ] No PII logged
- [ ] Authorization enforced on all endpoints that mutate data

### .NET-Specific

- [ ] Cancellation tokens present on all `async` method signatures in service and repository layers
- [ ] `ConfigureAwait(false)` in library code (not in ASP.NET request handlers)
- [ ] `IDisposable` / `IAsyncDisposable` disposed (prefer `using` declarations)
- [ ] No synchronous `Result` or `.Wait()` on async calls — deadlock risk
- [ ] `ILogger` structured logging (message templates, not string interpolation)

### OceanBase-Specific

- [ ] No `SELECT FOR SHARE` — must use optimistic concurrency (`IsRowVersion()`)
- [ ] All GUID/string columns explicitly configured with `utf8mb4` in Fluent API
- [ ] Queries on partitioned tables include the partition key in WHERE clause (partition pruning)
- [ ] Partitioning DDL applied via `migrationBuilder.Sql(...)` — not via EF Core table fluent API
- [ ] `ServerVersion` hardcoded — not `AutoDetect()`
- [ ] Connection string uses `CharSet=utf8mb4`

### Testing

- [ ] Every changed behavior has at least one corresponding test
- [ ] New failure paths have a test covering the error case
- [ ] No tests that always pass (`Assert.True(true)`, assertions inside `if` blocks)
- [ ] Integration tests use Testcontainers — not in-memory providers for EF Core
- [ ] Test names follow `MethodName_Scenario_ExpectedBehavior` convention

### OceanBase Migration Checklist (for schema changes)

- [ ] Migration `Up()` includes partition DDL for new large tables
- [ ] Migration `Down()` removes partitioning before dropping the table
- [ ] No `ascii` charset in generated migration DDL
- [ ] Migration is idempotent (can be re-run without error)

### Security Baseline

- [ ] New parameters validated before use — untrusted input does not reach SQL, file paths, HTTP calls, or deserialization without sanitization
- [ ] New endpoints have `.RequireAuthorization()` — no internal logic reachable from external callers without auth
- [ ] No new secrets hardcoded — all secrets read from environment variables or `IConfiguration` (Key Vault, Secret Manager)
- [ ] No secrets, tokens, PII (email, phone, name) logged on happy path or error path (check exception handlers and stack trace serialization)
- [ ] New NuGet packages are pinned to a specific version — not floating (`Version="*"`)
- [ ] Error responses use Problem Details format — no stack traces, DB error text, or internal paths returned to external callers
- [ ] File paths constructed from user input are sanitized against directory traversal

### Observability

- [ ] New behaviors are observable after deploy — key decision points (which branch taken, which value resolved) are logged with CorrelationId
- [ ] Log messages use structured message templates, not string interpolation: `LogInformation("Order {OrderId} created", id)` not `LogInformation($"Order {id} created")`
- [ ] No PII in log messages (email, phone, name, address, national ID)
- [ ] Errors logged at the correct level: `Error` for operation failures requiring investigation, `Warning` for recoverable unexpected state
- [ ] Background jobs and worker services log start, success, and failure with enough context to diagnose without a debugger

### Rollback & Blast Radius

- [ ] If this includes a DB migration: can the previous code version run against the new schema? Is rollback a no-op or does it require a `Down()` migration?
- [ ] Are there consumers of a changed API contract (HTTP, event schema, queue message shape)? If yes, is the change backward-compatible or do all consumers deploy simultaneously?
- [ ] Can this change be deployed dark (feature flag, per-tenant config) before going live? If not, state why.
- [ ] What is the blast radius if this breaks? One queue consumer, one tenant, or every request?

## Finding Format

```
### [SEVERITY] Short title

**File:** `path/to/file.cs`, line NN
**Impact:** Who is affected and how (data loss, error, performance hit, test gap)
**Issue:** Precise description of the problem
**Fix:**
```csharp
// suggested replacement
```
**Note:** Why existing guards do not prevent this (for BLOCKER/MAJOR)
```

## Pre-existing Issues

Findings in *unchanged* lines are tracked separately at the end of the report under:
```
## Pre-existing Issues (Not Introduced by This Change)
```
These are informational — the author is not obligated to fix them in this PR, but should be aware.

## Output Format

```markdown
# Code Review — [Feature / PR Name]

## What Was Reviewed
[List the files read and the code paths traced — satisfies Golden Rule 1: no rubber-stamps]

## Findings

### [BLOCKER] Short title
**File:** `path/to/file.cs:NN`
**Claim:** [what the code says it does]
**Verification:** [what the trace actually shows — satisfies Golden Rule 3]
**Impact:** [concrete consequence for users or data]
**Fix:** [minimal concrete change]

### [MAJOR] ...
### [NIT] ...

## Pre-existing Issues (Not Introduced by This Change)
[findings or "None identified"]

## Verdict
[ ] ✅ Approved — no blockers or majors
[ ] ⚠️  Approved with comments — address MAJORs before merge
[ ] ❌ Changes requested — fix BLOCKERs before re-review
```

Do not modify any files. Output is a report only.

Update `workflow-state.json`:
```json
{
  "stage": "reviewed",
  "review": {
    "blockers": 0,
    "majors": 0,
    "nits": 0,
    "verdict": "approved | approved_with_comments | changes_requested"
  }
}
```
