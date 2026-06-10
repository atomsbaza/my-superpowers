# Research: Building a Claude Code Principal Software Engineer Agent

> **Audience:** Dev team  
> **Goal:** Build the agent and its skills using Claude Code agent SDK  
> **Stack:** C# .NET 6/8/10, OceanBase database  
> **Date:** 2026-06-11

---

## Executive Summary

Claude Code has a mature, well-documented skill and subagent system (as of 2025–2026) that can be used to build a persistent principal software engineer persona. Skills (SKILL.md files) provide on-demand expertise loaded by semantic matching, while subagents (`.claude/agents/` markdown files) run in isolated context windows for heavier delegated tasks. A principal-engineer agent is best built as a subagent with a strong system prompt persona, backed by a library of SKILL.md files covering BRD/PRD intake, ADR authoring, C# .NET implementation patterns, testing, code review, and database design. OceanBase operates in MySQL-compatible mode, which means MySqlConnector and Pomelo EF Core work against it — but OceanBase-specific DDL features (partitioning, tablet groups) must be handled outside EF Core's schema migrations. .NET 6 reached end-of-life in November 2024; new builds should target .NET 8 (LTS, supported until November 2026) or .NET 10 (LTS, supported until November 2028).

---

## Key Findings

### Area 1 — Claude Code Agent SDK and Skills System

**Skills (SKILL.md) are filesystem-first, on-demand capabilities.** Each skill lives at `.claude/skills/<skill-name>/SKILL.md` (project-shared via git) or `~/.claude/skills/<skill-name>/SKILL.md` (user-personal). Only the `name` and `description` frontmatter fields load at startup; the full body is read on demand.

**The SKILL.md YAML frontmatter has exactly two required fields with strict validation rules:**
- `name`: max 64 chars, lowercase letters/numbers/hyphens only, no XML tags, cannot contain "anthropic" or "claude"
- `description`: max 1024 chars, non-empty, no XML tags, written in third person, must state both what the skill does and when to trigger it

**The `allowed-tools` frontmatter field in SKILL.md only applies when using Claude Code CLI directly; it is ignored when using Skills through the Agent SDK.** In SDK mode, tool access is controlled exclusively through the `allowedTools` option on the query call.

**Subagents are defined at `.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md` (user).** The YAML frontmatter supports: `name` (required), `description` (required, triggers automatic delegation), `tools` (allowlist), `disallowedTools` (denylist), `model` (`sonnet`, `opus`, `haiku`, `inherit`, or full model ID), `memory`, `skills`, `maxTurns`, `permissionMode`, `hooks`. The markdown body becomes the system prompt.

**Skills discovery is governed by `settingSources` (TypeScript) / `setting_sources` (Python).** Valid values are `"user"` and `"project"`. Skills in every parent directory up to the repository root are discovered when `cwd` is set. The `skills` query option accepts `"all"`, a named list, or `[]` to disable.

**For a senior engineering persona, the subagent system prompt structure should:** open with a role definition sentence, enumerate a decision-making framework, list preferred patterns and anti-patterns, specify output format for each output type (ADR, design doc, PR review), and close with constraints. Effective descriptions use "Use this agent when..." phrasing and include trigger keywords.

**SKILL.md body should stay under 500 lines.** Supporting materials (design templates, reference schemas, ADR format) belong in sibling files (`TEMPLATES.md`, `reference/`) referenced with one level of indirection from SKILL.md. Deeper nesting causes Claude to use `head -100` partial reads and miss content.

---

### Area 2 — Skill Design for the Principal Engineer Workflow

**BRD/PRD intake skill should structure output as:** bounded context identification → non-functional requirements extraction → open questions list → recommended ADRs to author. The description field should include trigger terms: "requirements document", "BRD", "PRD", "business requirements", "product specification".

**ADR skills should use low-freedom mode (exact templates) since ADRs are append-only and architectural.** The MADR (Markdown Architectural Decision Records) format is the most widely used .NET-ecosystem standard. Microsoft's Well-Architected Framework guidance recommends ADRs capture: context, decision drivers, considered options with pros/cons, decision outcome, and consequences.

**For C# .NET implementation skills, target .NET 8 or .NET 10 only.** .NET 6 reached end-of-life November 12, 2024. .NET 8 (LTS) is supported until November 10, 2026. .NET 10 (LTS, released November 2025) is supported until November 14, 2028.

**xUnit is the modern default for .NET testing (used by Microsoft internal teams); NUnit remains strong for data-driven test migrations.** Key patterns: AAA (Arrange/Act/Assert) structure, Testcontainers for integration testing against real dependencies, Moq or NSubstitute for mocking at stable boundaries.

**The `dotnet-adr` CLI tool (`endjin/dotnet-adr`) provides a .NET-native global tool** for creating and managing ADRs, co-located with code in the same repository.

---

### Area 3 — OceanBase Database Patterns for .NET

**OceanBase operates in MySQL-compatible tenant mode.** The MySQL-mode tenant uses the standard MySQL wire protocol, meaning MySqlConnector and Pomelo.EntityFrameworkCore.MySql connect to OceanBase with no driver changes. The connection format uses `Username@TenantName#ClusterName` syntax or `ClusterName:TenantName:Username` in the user field, with port 2881 as the default OBProxy port.

**Pomelo.EntityFrameworkCore.MySql 9.0.0 is the recommended EF Core provider for .NET 8/10 projects against OceanBase.** It targets EF Core 9.x and MySqlConnector 2.4.0+. Configuration uses:
```csharp
UseMySql(connectionString, new MySqlServerVersion(new Version(8, 0, 29)))
```
Specify MySQL 8.0.x as the server version since OceanBase MySQL mode is approximately compatible with MySQL 8.0. Do **not** use `ServerVersion.AutoDetect()` against OceanBase in production: the auto-detection query can expose compatibility gaps.

**Known OceanBase/Pomelo incompatibility: OceanBase does not support the `ascii` character set.** EF Core migrations for GUID-type columns (which Pomelo generates with `ascii` charset by default) will fail. Workaround: configure EF Core to use `utf8mb4` charset globally or override the column type for GUID columns explicitly. (Pomelo issue #1918)

**OceanBase does not support `SELECT ... FOR SHARE` statements** and lacks several MySQL functions including `LOAD_FILE()`, `GET_LOCK()`, `RELEASE_LOCK()`, and spatial types. EF Core features that rely on pessimistic concurrency must be redesigned with optimistic concurrency (`[Timestamp]` / `rowversion` pattern) or application-level locking.

**OceanBase partitioning is a DDL-level concern that EF Core migrations cannot express natively.** OceanBase supports RANGE, HASH, LIST, and composite (subpartitioning) strategies. For large event/log tables, RANGE partitioning on a datetime column with monthly intervals is the standard recommendation. HASH partitioning on the primary key evenly distributes writes across nodes. These partition clauses must be applied via raw SQL in EF Core migration's `Up()` method using `migrationBuilder.Sql(...)` after `migrationBuilder.CreateTable(...)`.

**MySqlConnector connection pool best practices for OceanBase production deployments:**
```
MaximumPoolSize=200         // OceanBase is distributed; higher parallelism is safe
MinimumPoolSize=10          // keep warm connections to OBProxy
ConnectionIdleTimeout=300   // prevents stale connections from OBProxy load-balancing
ConnectionLifeTime=1800     // recycle connections before OBProxy forcibly closes them
ConnectionReset=true        // ensures session state is clean on checkout (default)
DefaultCommandTimeout=60    // increase beyond 30s default for complex distributed queries
```

---

### Area 4 — Skill Composition and Chaining

**CLAUDE.md, skills, and subagents serve distinct roles in a multi-skill system:**
- `CLAUDE.md`: always-on context (project facts, coding conventions)
- Skills: on-demand specialized procedures (loaded when topic-relevant)
- Subagents: isolated workers in separate context windows (for heavy tasks that would pollute the main context)

**The canonical context-passing pattern is a shared JSON state file.** Each skill reads only the fields it needs from a centralized `workflow-state.json`, writes its outputs back with structured fields, and updates a `stage` field that the orchestrator reads to determine the next skill. Free-text handoffs between skills lead to extraction failures.

**Four orchestration patterns for the principal engineer workflow:**
1. **Sequential chain** — BRD analysis → ADR authoring → schema design → implementation → test generation
2. **Fan-out/merge** — generate multiple ADR options in parallel, merge into a decision
3. **Conditional routing** — if requirements include distributed data, route to OceanBase-partitioning skill; otherwise route to standard schema design skill
4. **Iterative loop** — code review → fix → re-review until no blockers (always define max iteration count)

**Skills should produce and consume a loose contract.** Define required output fields; let skills include additional fields freely; downstream skills only read declared fields. This makes individual skills replaceable without rewriting the chain.

**Run skills in a subagent for heavy research tasks** (e.g., "analyze this 200-page BRD") to preserve the main context window. The subagent reads the document, produces a structured summary, and returns only the summary to the main conversation.

---

## Trade-offs / Caveats

- **.NET 6 is end-of-life** (November 12, 2024). Building new production workloads on .NET 6 is not recommended. Skills that claim to support .NET 6 should add a deprecation warning section. Default to .NET 8 or .NET 10.

- **OceanBase-specific .NET documentation is sparse.** Official OceanBase documentation covers Java, Python, Go, and C — but not .NET/C#. All .NET guidance in this report is extrapolated from OceanBase's MySQL-mode compatibility guarantee plus MySqlConnector/Pomelo docs. Validate against your specific OceanBase version and run Pomelo migrations against a staging OceanBase instance before production rollout.

- **The OceanBase `ascii` charset issue with Pomelo** (GitHub issue #1918) may be fixed in newer OceanBase releases. Verify against your target OceanBase version (4.3.3+ is most current). The workaround of forcing `utf8mb4` is safe in all versions.

- **`ServerVersion.AutoDetect()` against OceanBase is unreliable in production.** OceanBase's version string during connection handshake may not match what Pomelo expects. Hard-code `new MySqlServerVersion(new Version(8, 0, 29))` as a stable baseline.

- **The `allowed-tools` frontmatter field in SKILL.md is a CLI-only feature.** If the principal engineer agent is built on the SDK (Python/TypeScript), tool control must be managed via `allowedTools` in the query options, not in SKILL.md.

- **Skills cannot be registered programmatically via the Agent SDK API.** They must be filesystem artifacts. If you want to dynamically inject skills, the only supported path is writing SKILL.md files to disk before invoking `query()`.

- **Pomelo.EntityFrameworkCore.MySql version alignment:** 9.0.0 targets EF Core 9.x. If the project targets .NET 8 with EF Core 8.x, use Pomelo 8.0.x instead.

---

## Recommended Agent + Skills Blueprint

### Core Agent Definition

**File:** `.claude/agents/principal-engineer.md`

```markdown
---
name: principal-engineer
description: >
  A senior principal software engineer with 20+ years of experience.
  Use this agent when requirements documents, system design decisions,
  architecture reviews, C# .NET implementation tasks, code reviews,
  or database schema work are needed. Use proactively whenever the
  user presents a BRD, PRD, feature brief, or asks for technical
  architecture guidance.
tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
model: opus
skills: all
---
You are a principal software engineer with 20+ years of experience
building large-scale distributed systems in C# and .NET.

Your decision-making framework:
1. Understand the business problem before proposing technical solutions.
2. Make architecture decisions explicit with ADRs before writing code.
3. Design for operability: observability, graceful degradation, and rollback first.
4. Prefer boring technology for infrastructure; reserve complexity for business logic.
5. Reject requirements that are not testable; push back and clarify.

Coding standards: C# 12+, .NET 8 (default) or .NET 10 (if greenfield),
xUnit for all new test code, Testcontainers for integration tests,
Pomelo EF Core for MySQL/OceanBase, minimal APIs for new endpoints.

Output format:
- For designs: produce a structured design doc and at least one ADR.
- For implementations: produce production-quality code with XML doc comments.
- For reviews: use BLOCKER / MAJOR / NIT severity tags per finding.
- For schemas: include partitioning strategy rationale when OceanBase is the target.
```

---

### Skills Library (8 Skills)

#### 1. `analyzing-requirements`
Consumes a BRD or PRD document (file path or pasted text) and produces a structured intake artifact. Extracts functional scope, non-functional requirements (performance, availability, security, scalability), bounded contexts with suggested service ownership, explicit ambiguities as a numbered open-questions list, and a list of ADRs recommended for authoring. Output is written to `workflow-state.json` under key `requirements_analysis`. Invoked at the start of every engagement where a requirements document exists.

**Description trigger keywords:** "BRD", "PRD", "requirements document", "business requirements", "product specification", "feature brief", "intake analysis"

---

#### 2. `authoring-adrs`
Produces Architecture Decision Records in MADR format. Loads an ADR template from `reference/adr-template.md` and applies the principal engineer's decision-making framework. Outputs one `.md` file per ADR into `docs/decisions/`. Each ADR covers: context and problem statement, decision drivers, considered options with pros/cons table, chosen option with rationale, and positive/negative consequences. Invoked whenever an architecturally significant or hard-to-reverse decision is being made.

**Description trigger keywords:** "architecture decision", "ADR", "design decision", "technology choice", "architectural trade-off"

---

#### 3. `designing-systems`
Transforms a requirements analysis artifact into a system design document covering: component diagram (C4 or ASCII), data flow, API contracts (OpenAPI sketch), database entity model, deployment topology, and cross-cutting concerns (auth, caching, rate-limiting, observability). Reads `workflow-state.json` for requirements context and writes to `docs/design/system-design.md`. Includes OceanBase partitioning strategy section whenever distributed persistence is in scope.

**Description trigger keywords:** "system design", "architecture", "component design", "design document", "C4 diagram", "data flow", "deployment topology"

---

#### 4. `implementing-dotnet`
Generates production-quality C# .NET 8/10 code from a design document or explicit specification. Enforces conventions: minimal API or controller-based endpoints, record types for DTOs, `IOptions<T>` for configuration, `ILogger<T>` for structured logging, cancellation tokens on all async methods, `ConfigureAwait(false)` in library code, nullable reference types enabled. References `reference/patterns.md` for repository pattern, mediator (MediatR), outbox pattern, and domain event implementations. Flags .NET 6 EOL status if detected.

**Description trigger keywords:** "implement", "write code", "C# implementation", ".NET code", "feature implementation", "generate code", "coding"

---

#### 5. `designing-database-schema`
Produces database schema DDL and EF Core entity configurations for OceanBase (MySQL-mode) targets. Generates entity configurations using Fluent API, index definitions, composite primary keys, and raw SQL migration snippets for OceanBase partitioning (RANGE on datetime columns for event tables, HASH on primary key for high-write tables). Explicitly overrides GUID column charset to `utf8mb4` (avoids Pomelo issue #1918). Recommends hardcoded `ServerVersion(8, 0, 29)` and cautions against `AutoDetect()`. Contains `reference/oceanbase-ddl.md` with partitioning DDL examples.

**Description trigger keywords:** "database schema", "schema design", "EF Core migration", "entity configuration", "OceanBase", "partitioning", "DDL", "table design"

---

#### 6. `writing-tests`
Generates comprehensive test suites for C# .NET code across three layers: unit tests (xUnit, Moq/NSubstitute, AAA pattern, parallel-safe), integration tests (xUnit with `IClassFixture<WebApplicationFactory<T>>` or Testcontainers for database-dependent tests), and contract tests for external API boundaries. For OceanBase integration tests, generates a Testcontainers setup using the MySQL container image with an OceanBase-compatible startup SQL script. Enforces naming convention: `MethodName_Scenario_ExpectedBehavior`.

**Description trigger keywords:** "write tests", "unit tests", "integration tests", "test coverage", "xUnit", "NUnit", "testing", "test generation"

---

#### 7. `reviewing-code`
Performs a structured code review using the principal engineer's standards. Reports findings grouped by severity: BLOCKER (correctness bugs, security issues, data loss risk), MAJOR (performance problems, missing error handling, test coverage gaps), NIT (style, naming, minor readability). Distinguishes findings in changed lines from pre-existing issues in unchanged code. Review checklist (`reference/review-checklist.md`) covers: null safety, cancellation token propagation, logging sensitive data, connection disposal, migration idempotency, and OceanBase-specific patterns (partition key in queries for pruning, FOR SHARE avoidance). Does not modify files; output is a markdown report only.

**Description trigger keywords:** "code review", "review this code", "PR review", "review changes", "feedback on code", "quality review"

---

#### 8. `orchestrating-workflow`
The meta-skill that chains BRD → design → implementation → test → review into a full end-to-end principal engineer workflow. Manages `workflow-state.json` as the shared state backbone, initializing required keys and validating stage transitions. Uses sequential chain by default and conditional routing when OceanBase partitioning or specific compliance requirements are detected. Enforces that no implementation begins before at least one ADR is authored, and no PR is considered complete without a code review pass. Logs each stage transition to `workflow-state.json` under a `history` array for auditability.

**Description trigger keywords:** "full workflow", "end-to-end", "from requirements to code", "full SDLC", "complete feature", "orchestrate"

---

## Sources

- [Agent Skills in the SDK](https://code.claude.com/docs/en/agent-sdk/skills) — SKILL.md format, SDK configuration, settingSources, skills option
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills) — SKILL.md authoring guide: frontmatter fields, progressive disclosure, directory structure
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — YAML field validation rules, description authoring, naming conventions
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents) — subagent frontmatter fields, file locations, system prompt structure
- [Equipping agents for the real world with Agent Skills - Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — progressive disclosure design rationale
- [Claude Code Skill Collaboration: How to Chain Skills](https://www.mindstudio.ai/blog/claude-code-skill-collaboration-chaining-workflows) — skill chaining patterns, JSON state file contract
- [How to Build a Skill System in Claude Code](https://www.mindstudio.ai/blog/how-to-build-skill-systems-claude-code) — four orchestration patterns
- [.NET Support Policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core) — .NET 6 EOL Nov 2024, .NET 8 LTS until Nov 2026, .NET 10 LTS until Nov 2028
- [Maintain an architecture decision record (ADR) - Microsoft Learn](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record) — MADR format guidance
- [GitHub - endjin/dotnet-adr](https://github.com/endjin/dotnet-adr) — .NET-native global CLI tool for ADR management
- [NuGet Gallery - Pomelo.EntityFrameworkCore.MySql 9.0.0](https://www.nuget.org/packages/Pomelo.EntityFrameworkCore.MySql) — version targeting
- [Pomelo Issue #1918](https://github.com/PomeloFoundation/Pomelo.EntityFrameworkCore.MySql/issues/1918) — OceanBase ascii charset incompatibility with GUID migrations
- [OceanBase MySQL Compatibility V4.3.3](https://en.oceanbase.com/docs/common-oceanbase-database-10000000001714478) — unsupported MySQL features
- [OceanBase Partitioned Tables](https://en.oceanbase.com/docs/enterprise-oceanbase-database-en-10000000000829358) — RANGE/HASH/LIST partitioning
- [MySqlConnector Connection Options](https://mysqlconnector.net/connection-options/) — pool configuration parameters
- [.NET Unit Testing Best Practices](https://scand.com/company/blog/net-unit-testing/) — xUnit/NUnit comparison, Testcontainers patterns
