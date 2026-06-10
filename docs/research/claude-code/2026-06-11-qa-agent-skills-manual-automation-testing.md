# Research: Building a World-Class Claude Code QA Agent

> **Audience:** Dev team
> **Goal:** Build the QA agent and its skills
> **Scope:** All of it — make it the best of the best
> **Date:** 2026-06-11

---

## Executive Summary

A production-grade QA agent for the Claude Code ecosystem is built as a subagent defined in `.claude/agents/` with its domain skills stored as `SKILL.md` files in `.claude/skills/`. The agent's nine skills — from requirements analysis through workflow orchestration — are loaded via the Claude Agent SDK's filesystem mechanism, not via subagent frontmatter. The recommended stack for the target .NET/OceanBase environment is xUnit + Playwright (UI), Testcontainers with the generic OceanBase CE image (integration), Reqnroll (BDD, replacing the EOL SpecFlow), NBomber (performance), and Stryker.NET (mutation quality gate). A critical constraint: no official .NET Testcontainers module for OceanBase exists; the generic `ContainerBuilder` with `oceanbase/oceanbase-ce` is the correct approach, with an explicit caveat that partition-behavior validation requires a real OceanBase instance, not a MySQL proxy. The OpenObserve case study demonstrates that a six-phase specialized agent pipeline reduced test authoring from one hour to five minutes and cut flaky tests 85%.

---

## Key Findings

### Area 1 — Claude Code Agent SDK for QA Agents

**Confirmed subagent frontmatter fields:**
```yaml
name: qa-engineer
description: >
  Senior QA engineer for test generation, test planning, and defect analysis.
tools: Read, Write, Edit, Bash, Grep, Glob
model: claude-sonnet-4-6
effort: high
permissionMode: default
maxTurns: 80
```
Confirmed fields: `name`, `description`, `tools`, `model`, `effort` (low/medium/high), `permissionMode`, `disallowedTools`, `isolation`, `maxTurns`, `memory`.

**Critical: `skills:` is NOT a confirmed subagent frontmatter field.** Several blog posts assert this; it is not corroborated by official docs. Skills are loaded via the SDK's `settingSources` + `skills` option.

**SDK skill loading:**
```typescript
for await (const message of query({
  prompt: "Generate test cases from this PRD",
  options: {
    cwd: "/path/to/project",
    settingSources: ["user", "project"],
    skills: ["analyzing-requirements-for-qa", "generating-manual-test-cases"],
    allowedTools: ["Read", "Write", "Grep", "Bash"]
  }
})) { }
```

**`context: fork` for isolation:** A skill body can include `context: fork` in frontmatter to execute in its own isolated subagent context — appropriate for long codebase scanning steps.

### Area 2 — QA Methodology & Test Case Design

**ISTQB test case mandatory fields (2025):** Test Case ID, Title/Objective, Module/Feature, Preconditions, Test Steps (numbered), Test Data, Expected Result, Actual Result, Status, Priority (P0/P1/P2), Severity, Tester, Execution Date, Notes.

**Core design techniques:**
- **Equivalence Partitioning (EP):** Divide inputs into classes where behavior is identical; test one representative per class (valid + invalid)
- **Boundary Value Analysis (BVA):** Test at boundaries (min, min+1, max-1, max)
- **Decision Tables:** Capture combinations of conditions for business rules
- **State Transition Testing:** Draw state diagram, test valid + invalid transitions
- **Use Case Testing:** Basic flow (happy path) + alternative flows + exception flows

**Exploratory heuristics:**
- **SFDIPOT:** Structure, Function, Data, Integration, Platform, Operations, Time — ensures no coverage dimension is missed
- **FEW HICCUPPS:** Test oracles for recognizing defects through consistency checks

**Risk-based prioritization:** Risk = Probability × Impact (1–5 each). P0 = score 16–25, P1 = 9–15, P2 = 1–8.

### Area 3 — Automation Frameworks & Patterns

**SpecFlow is EOL (Dec 31, 2024) — use Reqnroll.** The community-maintained successor, forked by SpecFlow's original creator. Migration is a find-and-replace. Install: `Reqnroll.xUnit`.

**Playwright + xUnit** — primary UI automation. Inherit `PageTest` for per-test page isolation. Page Object Model pattern: locators live in POM classes, test methods call POM methods only.

**Testcontainers** — `IClassFixture<DatabaseFixture>` with `IAsyncLifetime`. Run EF Core migrations in `InitializeAsync`. Use `[Collection("Database")]` to share one container across test classes.

**Bogus (.NET Faker)** — `new Faker<T>().UseSeed(42)` for deterministic CI test data.

**NBomber** — .NET-native performance testing, protocol-agnostic, C# scenarios that can reuse application code directly. Preferred over k6 for .NET teams.

**Stryker.NET** — mutation testing. Config via `stryker-config.json`. Exclude `Migrations/*.cs`. Set `thresholds.break` to enforce quality gate.

**CI reporting:** `dotnet test --logger "trx"` → convert with `trx2junit` for GitHub Actions. Allure .NET adapter for rich dashboards with flakiness trends.

### Area 4 — Skills Architecture

See Recommended Blueprint below.

### Area 5 — OceanBase / .NET Specifics

**No official .NET Testcontainers module for OceanBase.** Use generic `ContainerBuilder` with `oceanbase/oceanbase-ce:4.2.2`. Port 2881. Wait for `"boot success!"` log message.

**`mysql:8.0` is NOT a valid substitute for OceanBase partition behavior validation.** OceanBase's partitioning model differs from MySQL. Use real OceanBase container for partition tests.

**Always set `utf8mb4_unicode_ci` charset** in EF Core `OnModelCreating` and connection string.

**Partition-specific test pattern:**
```csharp
// Requires real OceanBase container — mysql:8.0 will not validate this
await _db.Database.ExecuteSqlRawAsync(
    "INSERT INTO orders PARTITION (p2024) VALUES (@id, @dt)",
    new MySqlParameter("@id", Guid.NewGuid()),
    new MySqlParameter("@dt", new DateTime(2024, 6, 15)));
```

**Stryker.NET for OceanBase projects:** Exclude `**/Migrations/*.cs` from mutation to avoid false signals.

---

## Trade-offs / Caveats

- **SpecFlow is EOL.** Use Reqnroll for all new .NET BDD projects.
- **`skills:` frontmatter on subagents is unverified.** Use SDK `skills` option instead.
- **OceanBase Testcontainers is Java-only.** .NET uses generic `ContainerBuilder`.
- **NBomber vs k6:** NBomber is better for .NET teams embedded in CI. k6 is better for infra teams with separate tooling.
- **`context: fork` adds cold-start overhead.** Only use for genuinely long-running analysis skills (codebase scanning), not lightweight skills.

---

## Recommended QA Agent + Skills Blueprint

### Agent: `.claude/agents/qa-engineer.md`

```markdown
---
name: qa-engineer
description: >
  Senior QA engineer (10+ years, ISTQB Certified). Delegate here for any
  testing-related request: generating test cases from BRD or PRD documents,
  creating test plans, writing Gherkin/BDD scenarios, analyzing codebase
  coverage gaps, generating xUnit + Playwright automation scripts, building
  NBomber performance tests, reporting defects, or orchestrating a full QA
  workflow. Trigger keywords: test cases, test plan, acceptance criteria,
  Gherkin, automation, coverage gaps, performance test, defect report, QA.
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
effort: high
permissionMode: default
maxTurns: 80
---
```

### 9 Skills

| Skill | Triggers | Output |
|---|---|---|
| `analyzing-requirements-for-qa` | BRD, PRD, acceptance criteria, feature brief | `qa-requirements-analysis.md` + state |
| `creating-test-plan` | test plan, sprint QA, scope, entry/exit criteria | `test-plan-<feature>.md` + state |
| `generating-manual-test-cases` | manual test cases, test steps, expected result, ISTQB | `manual-test-cases-<feature>.md` + state |
| `generating-bdd-scenarios` | Gherkin, BDD, Given When Then, Reqnroll, feature file | `.feature` files + step definition stubs |
| `analyzing-codebase-for-test-gaps` | coverage gaps, untested code, missing tests | `test-coverage-gap-report.md` + state |
| `generating-automation-scripts` | automation script, Playwright, xUnit, Testcontainers | Test classes + POM classes |
| `generating-performance-tests` | NBomber, load test, RPS, p95, throughput | NBomber C# test files |
| `reporting-test-results` | test results, defect report, test summary, pass/fail | Defect reports + summary markdown |
| `orchestrating-qa-workflow` | full QA workflow, QA pipeline, end to end QA | All of the above, chained |

### Shared State: `.qa-workflow-state.json`

All skills read from and write to this file. Stage field drives orchestration:
`init → requirements_analyzed → test_plan_created → manual_test_cases_generated → bdd_scenarios_generated → gap_analysis_complete → automation_scripts_generated → performance_tests_generated → results_reported`

### Directory Layout

```
.claude/
├── agents/
│   └── qa-engineer.md
└── skills/
    ├── analyzing-requirements-for-qa/SKILL.md
    ├── creating-test-plan/SKILL.md
    ├── generating-manual-test-cases/SKILL.md
    ├── generating-bdd-scenarios/SKILL.md
    ├── analyzing-codebase-for-test-gaps/SKILL.md
    ├── generating-automation-scripts/SKILL.md
    ├── generating-performance-tests/SKILL.md
    ├── reporting-test-results/SKILL.md
    └── orchestrating-qa-workflow/SKILL.md

tests/
├── Unit/
├── Integration/Fixtures/DatabaseFixture.cs
├── E2E/Pages/ + Tests/
├── BDD/Features/ + Steps/
└── Performance/
```

---

## Sources

- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Agent Skills in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [agentic-qe — GitHub](https://github.com/proffesor-for-testing/agentic-qe)
- [OpenObserve — Autonomous QA Testing case study](https://openobserve.ai/blog/autonomous-qa-testing-ai-agents-claude-code/)
- [Exploratory Testing Skill — danashby/GitHub](https://github.com/danashby/Exploratory-Testing-Skill)
- [ISTQB Structured Approach to Test Case Definition (2025)](https://istqb.org/wp-content/uploads/2025/06/A_STRUCTURED_APPROACH_TO_TEST_CASE_DEFIN.pdf)
- [Risk-Based Testing — Testlio](https://www.testlio.com/blog/risk-based-testing)
- [FEW HICCUPPS — DevelopSense](https://developsense.com/blog/2012/07/few-hiccupps)
- [Playwright .NET Test Runners](https://playwright.dev/dotnet/docs/test-runners)
- [Reqnroll — GitHub](https://github.com/reqnroll/Reqnroll) (SpecFlow EOL Dec 2024)
- [Testcontainers Best Practices .NET](https://www.milanjovanovic.tech/blog/testcontainers-best-practices-dotnet-integration-testing)
- [Testcontainers OceanBase Module (Java-only)](https://testcontainers.com/modules/oceanbase/)
- [OceanBase CE — Docker Hub](https://hub.docker.com/r/oceanbase/oceanbase-ce)
- [OceanBase MySQL Compatibility](https://en.oceanbase.com/docs/common-oceanbase-database-10000000001714478)
- [Bogus — GitHub](https://github.com/bchavez/Bogus)
- [NBomber](https://nbomber.com/)
- [Stryker.NET Configuration](https://stryker-mutator.io/docs/stryker-net/configuration/)
- [Pact.NET — GitHub](https://github.com/pact-foundation/pact-net)
- [Beautiful .NET Test Reports — GitHub Actions](https://seankilleen.com/2024/03/beautiful-net-test-reports-using-github-actions/)
- [Skill Chaining — MindStudio](https://www.mindstudio.ai/blog/claude-code-skill-collaboration-chaining-workflows)
