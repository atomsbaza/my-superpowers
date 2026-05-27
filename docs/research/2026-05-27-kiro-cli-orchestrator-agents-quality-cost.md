# Research: Kiro CLI — Orchestrator Agent Best Practices for Quality and Cost Routing

## Summary

Kiro CLI's subagent system (introduced in CLI v1.23, Jan 2026, expanded in v2.0 Apr 2026) supports multi-agent orchestration through a `subagent` built-in tool with `availableAgents` and `trustedAgents` access controls. Subagents run in isolated context windows (max 4 in parallel), return summaries to the orchestrator, and are individually configurable for model selection. Per-subagent credit tracking is a known gap (GitHub #6213). The `inclusion: always` steering-file-to-subagent injection bug (GitHub #7131) remains unfixed, but has a reliable workaround. No documented depth limit exists for nested orchestration, though single-level delegation is the implied architecture.

---

## Key Findings

### Q1 — Orchestrator Agent Configuration: Complete JSON Schema

The official configuration-reference page documents this schema for any agent acting as an orchestrator:

```json
{
  "name": "string",
  "description": "string — drives automatic routing; use 'Use when the user wants to...'",
  "prompt": "string or file:// URI",
  "model": "claude-haiku-4.5",
  "tools": ["read", "subagent", "todo"],
  "allowedTools": ["read", "subagent", "todo"],
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["builder", "validator", "test-*"],
      "trustedAgents": ["builder", "validator"]
    }
  },
  "resources": [
    "file://.kiro/steering/**/*.md",
    "skill://.kiro/skills/**/SKILL.md"
  ],
  "hooks": {
    "agentSpawn": [{ "command": "string" }],
    "preToolUse": [{ "matcher": "string", "command": "string" }],
    "postToolUse": [{ "matcher": "string", "command": "string" }],
    "stop": [{ "command": "string" }]
  },
  "includeMcpJson": false,
  "keyboardShortcut": "ctrl+o",
  "welcomeMessage": "string"
}
```

The `toolsSettings.subagent.availableAgents` and `toolsSettings.subagent.trustedAgents` fields are **not present in the official configuration-reference page** — they only appear documented on the subagents chat page and in community configs. This is a documentation gap, not a missing feature.

A pure routing orchestrator should have `tools: ["read", "subagent"]` only and no `write` access — the kiro-team pattern explicitly prevents orchestrators from modifying files directly.

Sources: [Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference/) | [Subagents Docs](https://kiro.dev/docs/cli/chat/subagents/) | [requix/kiro-team](https://github.com/requix/kiro-team)

---

### Q2 — `trustedAgents` vs `availableAgents`

These fields live under `toolsSettings.subagent`:

- **`availableAgents`**: Allowlist of agent names (or glob patterns like `test-*`) this agent is permitted to spawn. Agents not on the list cannot be delegated to.
- **`trustedAgents`**: Subset of available agents that run **without triggering user-approval prompts**. Agents in `availableAgents` but not `trustedAgents` require confirmation before executing.

The practical security implication: if `is_interactive` is `false` (e.g., CI/CD headless mode introduced in v2.0), and a subagent is not in `trustedAgents`, the subagent **fails fast** rather than hanging for approval. In headless pipelines, every spawnable subagent must be in `trustedAgents` or use `dangerously_trust_all_tools`.

Security caveat: hooks (`agentSpawn`, `preToolUse`, `postToolUse`) fire on the **orchestrator only**, not on subagents. Subagent-level security must be enforced via `toolsSettings.deniedCommands` and `allowedPaths` in each subagent's own config.

Sources: [Subagents Docs](https://kiro.dev/docs/cli/chat/subagents/) | [Kiro CLI 2.0 Blog](https://kiro.dev/blog/cli-2-0/) | [rommelporras/kiro-config](https://github.com/rommelporras/kiro-config)

---

### Q3 — Context Passing to Subagents

Subagents run in a **fully isolated context window**. They do not inherit the main agent's conversation history. The subagent's starting context is built from:

1. Its own agent config (`prompt`, `resources`, `model`)
2. An explicit task description passed by the orchestrator when invoking it
3. Any `relevant_context` the orchestrator explicitly includes in the invocation

**Conflict to note:** The official subagents doc page does not mention a `relevant_context` parameter. Community sources cite it as the primary mechanism for explicit context passing. This may be an IDE-vs-CLI surface difference, or the field exists in the tool invocation payload but is not exposed in the config schema. Treat `relevant_context` as available in practice but verify it is not IDE-only before relying on it.

On return: when a subagent finishes, it calls the built-in `summary` tool and returns its findings to the orchestrator. The orchestrator receives a **summary, not a raw context dump** — this prevents context bloat propagating back up.

To keep delegation cost-efficient: pass only a compressed task description, not the full upstream conversation. The orchestrator prompt should instruct the model to distill its routing decision into a focused task brief before invoking the subagent tool.

Sources: [Subagents Docs](https://kiro.dev/docs/cli/chat/subagents/) | [luizmachado.dev blog](https://luizmachado.dev/en/posts/utilizando-sub-agents-com-o-kiro-cli/)

---

### Q4 — Model Assignment Per Subagent

Each agent in the graph specifies its own `model` field independently. If `model` is omitted, the subagent inherits the **default model** from `~/.kiro/settings/cli.json` — a silent cost risk if the user's default is Opus.

Recommended tiering:

| Role | Model ID | Cost Multiplier |
|---|---|---|
| Routing orchestrator | `claude-haiku-4.5` | 0.4x |
| General specialist | `claude-sonnet-4.6` | 1.3x |
| High-quality specialist | `claude-opus-4.6` | 2.2x |
| Cost-aggressive specialist | `qwen3-coder-next` | 0.05x |

**Always specify `model` explicitly in every agent config** — never rely on default inheritance.

Community examples use `"claude-sonnet-4"` (no version suffix). Official docs list only versioned identifiers like `"claude-sonnet-4.6"`. Use full versioned IDs to avoid ambiguity.

Sources: [Models Docs](https://kiro.dev/docs/cli/models/) | [Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference/) | [requix/kiro-team](https://github.com/requix/kiro-team)

---

### Q5 — Steering Files in Subagent Context: Bug and Workaround

**The bug (GitHub #7131):** Workspace steering files with `inclusion: always` are **not automatically injected** into subagent context windows. Global rules — security constraints, coding standards — silently do not apply to subagents.

**Confirmed workaround:** Add an explicit `resources` glob to each subagent config:

```json
{
  "name": "builder",
  "resources": [
    "file://.kiro/steering/**/*.md",
    "file://~/.kiro/steering/**/*.md"
  ]
}
```

This forces the subagent to load steering files as part of its own context initialization, independent of the `inclusion:` metadata. No official fix timeline has been announced.

Sources: [GitHub Issue #7131](https://github.com/kirodotdev/Kiro/issues/7131) | [Creating Agents Docs](https://kiro.dev/docs/cli/custom-agents/creating/) | [rommelporras/kiro-config](https://github.com/rommelporras/kiro-config)

---

### Q6 — Cost Monitoring During Delegation

**Per-subagent credit attribution does not exist.** GitHub issue #6213 (opened March 2026, no official response) confirms that only the main agent's credit consumption is surfaced. Subagent credit consumption is not broken out anywhere — not in real-time, not in end-of-run summaries.

**Available visibility:**
- **Crew Monitor (Ctrl+G)** — introduced v2.0 (Apr 2026): real-time visibility into which subagents are active and their current tool calls. Activity monitoring only, not cost attribution.
- **`$AGENT_CONTEXT_OUT`** (v2.3, May 2026) — surface per-subagent shell output in tool result notes; can include token-count logging if instrumented.
- **`hooks.stop`** on each subagent config — emit a log line on completion to correlate with aggregate usage dashboard.
- **`/usage`** in-session — shows aggregate credits only, no per-agent breakdown.

Budget estimation for multi-agent workloads requires manual modeling based on expected model × context size per subagent.

Sources: [GitHub Issue #6213](https://github.com/kirodotdev/Kiro/issues/6213) | [CLI Changelog v2.0/v2.3](https://kiro.dev/changelog/cli/)

---

### Q7 — Multi-Level Orchestration (Nested Sub-Orchestrators)

**No documented depth limit exists.** A subagent can include `subagent` in its own `tools` array and thus act as a sub-orchestrator. However, the architecture is explicitly designed around **single-level delegation**.

GitHub issue #4262 (Dec 2025, still open) requests native sync/async subagent support with configurable depth limits — the fact that this is a feature request implies multi-level nesting currently has no rate-limit guardrails, making recursive or deep configurations a potential credit runaway risk.

Practical risks of going beyond single-level:
- Hooks do not fire inside subagents — security enforcement at levels 2+ requires redundant config in every intermediate agent
- Credit attribution gap (#6213) compounds at each nesting level
- Context summarization only happens at subagent completion — intermediate levels add latency without transparency

**Recommendation:** Keep orchestration flat (one orchestrator, direct specialists). If a specialist needs to coordinate subtasks, model those as parallel peers under the root orchestrator rather than a nested chain.

Sources: [Subagents Docs](https://kiro.dev/docs/cli/chat/subagents/) | [GitHub Issue #4262](https://github.com/kirodotdev/Kiro/issues/4262)

---

### Q8 — Parallel Delegation

Kiro CLI supports parallel subagent invocation with a hard limit of **4 concurrent subagents per orchestrator turn**. Additional tasks are batched in subsequent rounds.

As of v2.0 (Apr 13 2026), subagents support **task dependency graphs (DAGs)**: independent tasks at the same level run in parallel; tasks with declared dependencies wait for prerequisites. Graphs are planned upfront by the orchestrator and **cannot be modified during execution**.

Real-world benchmark from the community: 3 parallel agents (code review, docs generation, test execution) completed in ~45 seconds vs ~115 seconds sequential — 61% speedup.

Fan-out/fan-in: the orchestrator prompt must explicitly instruct the model to identify parallelizable subtasks, dispatch them simultaneously, and synthesize results. For tasks exceeding 4, the orchestrator prompt must include round-based batching logic.

Sources: [Subagents Docs](https://kiro.dev/docs/cli/chat/subagents/) | [dev.to parallel subagents](https://dev.to/aws-builders/aws-parallel-execution-of-tasks-using-kiros-custom-subagents-kiro-n77) | [CLI Changelog v2.0](https://kiro.dev/changelog/cli/)

---

### Q9 — Skills vs Subagents

| Dimension | Agent Skills | Dedicated Subagents |
|---|---|---|
| Activation | Auto-matched by description OR explicit `/skillname` | Orchestrator routes via delegation |
| Context loading | Progressive: name+description only until referenced | Full agent config + prompt loaded on spawn |
| Execution context | Stays inside main agent's context window | Isolated context window |
| Parallelism | No | Yes — up to 4 concurrent |
| Tool scope | Inherits main agent's tools | Own `tools`/`allowedTools` per config |
| Best for | Occasional domain knowledge that most requests don't need | Sustained domain roles, parallel execution, permission isolation |
| Cost profile | Lower for single-domain tasks (no spawn overhead) | Higher upfront per spawn but leaner main context |

**Decision rule:** If you need isolation, parallelism, or different tool permissions → use a subagent. If you just need the agent to know something domain-specific on demand without spawning overhead → use a skill. A cheap routing orchestrator (Haiku) can activate skills itself without spawning a Sonnet subagent for lookups.

Sources: [Agent Skills Docs](https://kiro.dev/docs/cli/skills/) | [Kiro 0.9 Blog](https://kiro.dev/blog/custom-subagents-skills-and-enterprise-controls/)

---

### Q10 — Real-World Community Configs and Patterns

**requix/kiro-team** — Team-lead orchestrator with `tools: ["read", "subagent", "todo"]`, explicit `trustedAgents` list, all specialists configured with independent `model` fields. Team-lead cannot write files — only reads, delegates, and tracks TODOs. [requix/kiro-team](https://github.com/requix/kiro-team)

**rommelporras/kiro-config** — Production config with 9 specialist agents, 3-layer security (hooks + denied paths + denied commands), a `devops-orchestrator` that handles config/markdown directly but delegates all code to specialists. Uses per-agent steering glob in `resources` (the `inclusion: always` workaround). [rommelporras/kiro-config](https://github.com/rommelporras/kiro-config)

**Patterns that have proven reliable:**
- Restrict orchestrator to `read + subagent` tools only — prevents "orchestrator writes directly and bypasses specialist context"
- Redundant `deniedCommands` in every specialist config since hooks don't cascade
- Explicit `model` field in every agent — never rely on default inheritance
- Steering glob in every subagent `resources` to work around #7131

**Patterns reported as fragile:**
- Subagents making autonomous tool choices beyond their task spec (agents generating more files than expected — stronger behavioral restrictions in subagent prompt needed)
- Any design that depends on `inclusion: always` propagating automatically to subagents — it does not
- Unversioned model identifiers like `"claude-sonnet-4"` — use full versioned IDs

---

## Trade-offs / Caveats

- **`relevant_context` parameter conflict:** The official subagents doc page does not mention it; community sources cite it as the primary explicit context-passing mechanism. This may be an IDE feature not yet in CLI, or an undocumented internal field. Verify experimentally before designing an orchestrator that depends on it.

- **Schema incompleteness:** `toolsSettings.subagent.availableAgents` and `trustedAgents` do not appear in the official configuration-reference schema page — only in the subagents feature page and community configs. Documentation lag, not a missing feature.

- **Cost attribution is broken for subagents:** As of May 2026, no per-subagent credit breakdown exists. Budget estimation requires manual modeling.

- **Multi-level nesting is architecturally discouraged but not blocked.** No depth limit documented. GitHub issue #4262 implies this area is not yet a first-class feature.

- **Task graph is immutable at runtime.** Once the orchestrator plans a DAG and begins execution, it cannot modify the graph mid-run. If a subagent discovers additional required work, the orchestrator must handle this in a subsequent turn.

- **Hooks do not cascade to subagents.** Security enforcement must be duplicated in every subagent config — `deniedCommands`, `allowedPaths`, `denyByDefault`.

---

## Complete Orchestrator + Specialist Example

### `~/.kiro/agents/orchestrator.json`
```json
{
  "name": "orchestrator",
  "description": "Main entry point. Routes every request to the right specialist. Use for all work.",
  "model": "claude-haiku-4.5",
  "tools": ["read", "subagent", "todo"],
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["sa", "coder", "reviewer", "chat"],
      "trustedAgents": ["sa", "coder", "reviewer", "chat"]
    }
  },
  "resources": [
    "file://.kiro/steering/**/*.md",
    "file://~/.kiro/steering/**/*.md"
  ],
  "prompt": "You are a router. Read the user's request and immediately delegate to the correct agent — do not answer yourself:\n- 'sa' for system design, architecture, ADRs, tech stack decisions\n- 'coder' for writing code, debugging, implementing features, tests\n- 'reviewer' for code review, PR review, security audits\n- 'chat' for quick questions, explanations, lightweight tasks\nDelegate with a focused task brief. Do not include full conversation history in the brief — summarize only what the specialist needs."
}
```

### `~/.kiro/agents/coder.json`
```json
{
  "name": "coder",
  "description": "Code implementation, debugging, multi-file changes, test writing",
  "model": "claude-sonnet-4.6",
  "tools": ["read", "write", "shell", "grep", "glob", "code"],
  "toolsSettings": {
    "shell": {
      "deniedCommands": ["rm -rf", "git push --force", "sudo"],
      "allowedPaths": ["./"]
    }
  },
  "resources": [
    "file://.kiro/steering/**/*.md",
    "file://~/.kiro/steering/**/*.md"
  ]
}
```

---

## Sources

- [Subagents — CLI Docs — Kiro](https://kiro.dev/docs/cli/chat/subagents/) — Primary reference for trustedAgents/availableAgents semantics, parallel limits, context isolation, and return mechanism
- [Agent Configuration Reference — CLI Docs — Kiro](https://kiro.dev/docs/cli/custom-agents/configuration-reference/) — Official JSON schema; incomplete on subagent-specific toolsSettings fields
- [Creating Custom Agents — CLI Docs — Kiro](https://kiro.dev/docs/cli/custom-agents/creating/) — Includes the resources glob pattern used as the steering file workaround
- [Models — CLI Docs — Kiro](https://kiro.dev/docs/cli/models/) — Full list of model IDs for per-agent assignment
- [Agent Skills — CLI Docs — Kiro](https://kiro.dev/docs/cli/skills/) — Progressive disclosure mechanism; skills vs subagents distinction
- [CLI Changelog — Kiro](https://kiro.dev/changelog/cli/) — v1.23 subagent intro, v2.0 DAG + Crew Monitor, v2.3 agent output side channels
- [Kiro CLI 2.0 Blog](https://kiro.dev/blog/cli-2-0/) — Headless mode implications for trustedAgents in CI/CD
- [Kiro 0.9 Blog — Custom Subagents, Skills, Enterprise Controls](https://kiro.dev/blog/custom-subagents-skills-and-enterprise-controls/) — Skills vs subagents comparison
- [Understanding Kiro Pricing and Usage Tracking](https://kiro.dev/blog/understanding-kiro-pricing-specs-vibes-usage-tracking/) — Aggregate credit attribution; confirms no per-agent breakdown
- [GitHub Issue #7131 — inclusion:always not injected into subagents](https://github.com/kirodotdev/Kiro/issues/7131) — Steering file bug; marked duplicate, no fix
- [GitHub Issue #6213 — Transparency on credits usage in subagents](https://github.com/kirodotdev/Kiro/issues/6213) — Per-subagent cost attribution gap; open, no official response
- [GitHub Issue #4262 — Multi-Agent Orchestration sync/async support](https://github.com/kirodotdev/Kiro/issues/4262) — Multi-level nesting not first-class; open since Dec 2025
- [requix/kiro-team — GitHub](https://github.com/requix/kiro-team) — Community reference: orchestrator + specialists with model assignment and trustedAgents
- [rommelporras/kiro-config — GitHub](https://github.com/rommelporras/kiro-config) — Production multi-agent config with 3-layer security and steering glob workaround
- [luizmachado.dev — Using Sub Agents with Kiro CLI](https://luizmachado.dev/en/posts/utilizando-sub-agents-com-o-kiro-cli/) — relevant_context usage, fan-out/fan-in patterns, 4-agent limit
- [dev.to — Parallel Execution of Tasks Using Kiro Custom Subagents](https://dev.to/aws-builders/aws-parallel-execution-of-tasks-using-kiros-custom-subagents-kiro-n77) — Real benchmark (61% speedup), fragile autonomous-decision patterns
