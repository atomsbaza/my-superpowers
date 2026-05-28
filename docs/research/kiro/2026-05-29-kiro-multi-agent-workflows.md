# Research: Multi-Agent Workflows in Kiro

## Summary

Kiro's multi-agent system — called **subagents** — lets a main orchestrating agent delegate focused tasks to isolated child agents that run in parallel or in a dependency-ordered sequence (DAG). Built-in subagents handle context-gathering and general parallelism automatically. Custom subagents, introduced in Kiro IDE v0.9 and Kiro CLI v1.23, let teams define specialized agents (code reviewers, security analyzers, test runners, etc.) via markdown files with YAML frontmatter. The system's principal advantages over single-agent workflows are context isolation per task, parallel throughput, and repeatable specialist behavior — at the cost of higher credit usage, a hard cap of 4 concurrent subagents, and several hook/spec limitations that restrict automated governance.

---

## Key Findings

### 1. What Multi-Agent Workflows Are in Kiro

Multi-agent workflows in Kiro are built on a **subagents model**: a primary (main) agent acts as orchestrator and can spawn child agents, each of which executes in its own isolated context window. The main agent waits for all active subagents to complete before incorporating their results and proceeding. Each subagent starts clean — distinct from a single long conversation that accumulates context.

The official conceptual framing: the main agent "decides what to delegate, fires off the subagents, waits for results, and consolidates everything into a coherent response."

Source: [Subagents — IDE Docs](https://kiro.dev/docs/chat/subagents/), [Kiro 0.9 Blog](https://kiro.dev/blog/custom-subagents-skills-and-enterprise-controls/)

---

### 2. How They Work — Architecture and Execution Model

**Built-in subagents (IDE):** Kiro ships two built-in subagents without any configuration required:
- A **context-gathering subagent** — explores a project to collect relevant context (e.g., codebase structure, dependency trees)
- A **general-purpose subagent** — used by the main agent to parallelize independent tasks

**DAG Task Graph (IDE + CLI):** For complex tasks, the main agent plans a **directed acyclic graph (DAG)** of subtasks upfront before any subagent is launched. Independent nodes execute in parallel; dependent nodes wait for their prerequisites. The graph is fixed at planning time — it cannot be modified mid-execution.

**Parallel cap:** A maximum of **4 subagents** can run simultaneously.

**Context isolation:** Each subagent has its own context window. The main agent's context is never polluted by a subagent's execution history.

**Results return:** Subagents automatically return their results to the main agent on completion.

Source: [Subagents — IDE Docs](https://kiro.dev/docs/chat/subagents/), [Subagents — CLI Docs](https://kiro.dev/docs/cli/chat/subagents/), [CLI Changelog 1.23](https://kiro.dev/changelog/cli/1-23/)

---

### 3. How to Set Them Up — Configuration

#### IDE (Custom Subagents — introduced in v0.9)

Create a markdown file in one of:
- `~/.kiro/agents/<agent-name>.md` — global, available across all workspaces
- `<workspace>/.kiro/agents/<agent-name>.md` — workspace-scoped

The file body is the system prompt. YAML frontmatter sets metadata and constraints:

```yaml
---
name: code-reviewer
description: Expert code review assistant that checks for correctness, security, and performance
tools:
  - read_file
  - list_directory
model: claude-sonnet-4-5
mcpServers:
  - my-linting-server
---

You are a strict code reviewer. When given a diff or set of files, you check for:
- Logic bugs
- Security vulnerabilities
- Missing error handling
- Performance anti-patterns

Return findings as a structured list with file, line, severity, and a concrete fix.
```

**Supported YAML frontmatter fields:**

| Field | Purpose |
|---|---|
| `name` | Display name / identifier |
| `description` | Used by the main agent for **automatic agent selection**; write it precisely |
| `tools` | List of tools the agent can access (scope-limiting) |
| `model` | Override the model for this specific agent |
| `mcpServers` | MCP servers available to this agent |
| `prompt` | Alternative to body — supports `file://` URI to an external file |

Kiro **automatically selects** the appropriate custom agent based on its `description` field when spawning subagents, or you can invoke one explicitly.

Source: [Kiro 0.9 Changelog](https://kiro.dev/changelog/ide/0-9/), [Subagents — IDE Docs](https://kiro.dev/docs/chat/subagents/)

#### CLI (Custom Agents — available separately)

The CLI uses a JSON configuration file approach with `toolsSettings.subagent` for permission control:

```json
{
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["reviewer", "tester", "analyzer", "docs-*"],
      "trustedAgents": ["reviewer", "tester"]
    }
  }
}
```

- `availableAgents` — restricts which agents a main agent can delegate to; glob patterns supported
- `trustedAgents` — agents that run without interactive permission prompts
- `dangerously_trust_all_tools` — disables permission prompts entirely (use with caution)

Source: [Agent Configuration Reference — CLI](https://kiro.dev/docs/cli/custom-agents/configuration-reference/), [Managing Tool Permissions — CLI](https://kiro.dev/docs/cli/chat/permissions/)

---

### 4. Agent Roles and Types

Kiro does not prescribe fixed agent roles — you define them. Documented community patterns and official examples include:

| Role | Responsibility | Example description field |
|---|---|---|
| Architect | Designs system structure, breaks tasks into sub-tasks | "Plans technical approach and decomposes requirements into subtasks" |
| Coder | Implements features in a specific language/framework | "Expert React frontend developer" or "Python backend implementer" |
| Code Reviewer | Reviews diffs for correctness, security, performance | "Expert code review assistant" |
| Security Analyzer | Checks IAM policies, security groups, S3 configs, CloudFormation | "AWS security specialist reviewing for Well-Architected compliance" |
| Tester | Writes or executes tests, formats results | "Test runner that generates structured output" |
| Docs Writer | Generates or updates documentation | "Technical documentation author" |

The `description` field drives auto-selection, so write it to unambiguously distinguish agents.

Source: [AWS Builders — DEV Community](https://dev.to/aws-builders/aws-parallel-execution-of-tasks-using-kiros-custom-subagents-kiro-n77), [Kiro 0.9 Blog](https://kiro.dev/blog/custom-subagents-skills-and-enterprise-controls/)

---

### 5. Orchestration Patterns

#### Pattern A: Parallel Fan-Out
Main agent receives a task, decomposes it into N independent sub-tasks (up to 4), fires them simultaneously, waits, and merges results. Best for tasks with no data dependencies between them.

*Example:* Security audit of an AWS deployment — IAM, networking, S3, and CloudFormation reviewed in parallel.

#### Pattern B: DAG with Dependencies
Main agent builds a full task graph upfront. Independent tasks run in parallel; dependent tasks wait for prerequisite subagents to finish.

*Example:* Analyze codebase → (parallel) refactor module A + refactor module B → run tests → generate PR summary.

#### Pattern C: Player / Coach
A 3-agent pattern: an **orchestrator** dispatches work to a **player** subagent, which produces output and then invokes a **coach** subagent to review and provide feedback. The player incorporates the feedback and returns a refined result to the orchestrator. Creates a self-correcting quality loop without human review at each step.

Reference implementation: [GitHub — kiro-player-coach](https://github.com/094459/kiro-player-coach)

#### Pattern D: Spec-Driven Multi-Repo
Main agent uses Kiro's Spec workflow to define requirements, then spawns subagents per repository to apply changes in parallel. Used for large-scale migrations across several repos simultaneously.

---

### 6. Practical Use Cases

- **Multi-language monorepo:** React frontend + Python backend — split into two custom subagents, each with access only to the tools relevant to their stack. Prevents context window bloat from loading all tools at once.
- **Cloud security audits:** 4 parallel subagents covering IAM, networking, object storage, and infrastructure-as-code simultaneously.
- **Cross-repo migrations:** Spec-driven changes applied in parallel across multiple repositories via custom subagents.
- **Technical content generation:** Research, drafting, and review as 3 separate specialized agents — documented as reducing hours of sequential work to ~15 minutes.
- **Repeated structured tasks:** Any task with a fixed procedure, consistent toolset, and well-defined output format (e.g., CDK code review against the Well-Architected Framework).

---

### 7. What Propagates Into Subagents vs What Does Not

| Feature | Works in Subagents? |
|---|---|
| Steering files (`.kiro/steering/`) | Yes |
| MCP servers | Yes |
| Agent Skills | No — custom agents do not load skills by default |
| Specs (`.kiro/specs/`) | No |
| Hooks (Pre/Post Tool Use) | No |
| Power steering (`POWER.md`) | No (open GitHub issue #7758) |

Source: [Subagents — IDE Docs](https://kiro.dev/docs/chat/subagents/), [GitHub Issue #7755](https://github.com/kirodotdev/Kiro/issues/7755), [GitHub Issue #7758](https://github.com/kirodotdev/Kiro/issues/7758)

---

### 8. Comparison: Single-Agent vs Multi-Agent Workflows

| Dimension | Single Agent | Multi-Agent (Subagents) |
|---|---|---|
| Context window | Accumulates all task history | Each subagent starts clean |
| Throughput | Sequential | Up to 4 tasks simultaneously |
| Specialization | One generalist prompt | Distinct system prompts per agent type |
| Tool scope | All tools loaded at once | Per-agent tool restriction possible |
| Hook governance | Hooks fire on all tool calls | Hooks do NOT fire in subagents |
| Spec access | Main agent can read Specs | Subagents cannot access Specs |
| Credit cost | Lower per task | Higher — 4.3x observed vs one-shot for comparable work |
| Setup overhead | None | Requires markdown file authoring, description precision |
| DAG orchestration | Not applicable | Dependency-ordered execution with parallel branches |

---

## Trade-offs / Caveats

- **Hooks do not fire in subagents (open issue):** Active gap — [GitHub Issue #7755](https://github.com/kirodotdev/Kiro/issues/7755). If your team relies on Pre Tool Use hooks for safety gates or governance, those gates are bypassed for all tool calls made inside a subagent.
- **Power steering does not propagate (open issue):** `POWER.md` and power-scoped steering files are not inherited by subagents — [GitHub Issue #7758](https://github.com/kirodotdev/Kiro/issues/7758).
- **Model field in IDE subagents — partial support:** The `model` field in IDE custom agent frontmatter may not be honored when auto-selected by the main agent — [GitHub Issue #6637](https://github.com/kirodotdev/Kiro/issues/6637).
- **Task graph is fixed at planning time:** Mid-execution course correction is not possible without restarting.
- **4-concurrent-subagent cap:** Planning graphs with more than 4 independent tasks at the same level will serialize the excess.
- **Credit cost:** One community report measured 4.3 credits per multi-agent workflow iteration vs under 1 credit for a single-agent approach on comparable work. Budget accordingly for automated or CI-triggered workflows.
- **Custom agents do not load Agent Skills by default:** If a Skill encodes a workflow your subagent needs, inline that guidance into the subagent's system prompt directly.
- **IDE vs CLI distinction matters:** `toolsSettings.subagent`, `availableAgents`, `trustedAgents`, and `dangerously_trust_all_tools` are CLI-only configuration. IDE agents use markdown frontmatter. Do not mix up the two surfaces.
- **Version availability:** IDE subagents appeared in v0.8 (general) and v0.9 (custom); CLI subagents in v1.23.

---

## Sources

- [Subagents — IDE Docs](https://kiro.dev/docs/chat/subagents/)
- [Subagents — CLI Docs](https://kiro.dev/docs/cli/chat/subagents/)
- [Agent Configuration Reference — CLI](https://kiro.dev/docs/cli/custom-agents/configuration-reference/)
- [Custom Agents (CLI) — Overview](https://kiro.dev/docs/cli/custom-agents/)
- [Creating Custom Agents — CLI Docs](https://kiro.dev/docs/cli/custom-agents/creating/)
- [Kiro 0.9 Release Blog](https://kiro.dev/blog/custom-subagents-skills-and-enterprise-controls/)
- [Kiro Changelog IDE 0.9](https://kiro.dev/changelog/ide/0-9/)
- [CLI Changelog 1.23](https://kiro.dev/changelog/cli/1-23/)
- [Managing Tool Permissions — CLI](https://kiro.dev/docs/cli/chat/permissions/)
- [AWS Builders: Parallel Execution with Custom Subagents — DEV Community](https://dev.to/aws-builders/aws-parallel-execution-of-tasks-using-kiros-custom-subagents-kiro-n77)
- [Player/Coach Workflow — DEV Community](https://dev.to/aws/implementing-playercoach-workflow-with-kiro-cli-subagents-2gf3)
- [GitHub — kiro-player-coach](https://github.com/094459/kiro-player-coach)
- [Kiro Showcase: Multi-Repo Spec + Subagents — DEV Community](https://dev.to/dvddpl/kiro-showcase-automating-changes-across-several-repos-with-spec-driven-development-and-custom-8bo)
- [GitHub Issue #7755 — Hooks should trigger in subagents](https://github.com/kirodotdev/Kiro/issues/7755)
- [GitHub Issue #7758 — Power steering not propagated to subagents](https://github.com/kirodotdev/Kiro/issues/7758)
- [GitHub Issue #6637 — model field not honored when subagent invoked programmatically](https://github.com/kirodotdev/Kiro/issues/6637)
- [GitHub — requix/kiro-team](https://github.com/requix/kiro-team)
- [arXiv — When Single-Agent with Skills Replace Multi-Agent Systems](https://arxiv.org/pdf/2601.04748)
