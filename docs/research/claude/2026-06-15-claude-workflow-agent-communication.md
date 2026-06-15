# Research: Claude Multi-Agent Orchestration — Inter-Agent Communication

## Disambiguation: "Claude Workflows" Maps to Three Distinct Systems

The phrase "Claude Workflows" is used loosely across Anthropic's documentation. For an integration team, the label resolves to three mechanisms with *different integration models*. Understanding which applies determines every implementation decision:

| Mechanism | What it is | Integration model | Relevance |
|---|---|---|---|
| **Managed Agents Multiagent API** | Hosted agent sessions with coordinator/subagent threading via the `managed-agents-2026-04-01` API | Build against Anthropic's SDK; agent logic defined via API | **Primary focus for integrating into an existing project** |
| **Claude Code Dynamic Workflows** | JavaScript scripts that orchestrate up to 1,000 subagents, written and run inside Claude Code | Claude Code CLI/Desktop tool; script runtime is Anthropic-managed | Relevant only if your team's workflow is Claude-Code-based |
| **Agent Teams / Claude Cowork** | End-user multi-app automation surface with third-party connectors | End-user product, not developer API | Not directly integrable; deprioritize |

This report focuses on the **Managed Agents API** (which is the developer-facing integration surface) and documents **Dynamic Workflows** where its patterns diverge in instructive ways.

---

## Summary

Anthropic's Managed Agents API (launched April 2026, beta header `managed-agents-2026-04-01`) is the primary integration surface for teams embedding multi-agent orchestration into their own projects. It implements a strict two-level coordinator/subagent model where agents communicate through isolated session threads using a typed event stream. Agent-to-agent message payloads carry text content and agent identity, but tools, MCP server access, and conversation context are explicitly not shared between agents — only the filesystem and vault credentials are. Claude Code's Dynamic Workflows (May 2026) is a separate system with a different architecture: the orchestration plan lives in a JavaScript script rather than in the model's context, intermediate results live in script variables, and there is no shared state between subagents at all. Both systems support parallel subagent execution within phase-level synchronization boundaries. Anthropic's own production research system recommends artifact-based outputs (agents write to external storage, then return lightweight references) to prevent context pollution across agents.

---

## Key Findings

### 1. How Agents Pass Information to Each Other

**Managed Agents API:** Agent-to-agent communication is mediated through the session event stream. When a subagent completes work, the event `agent.thread_message_received` fires on the primary thread, carrying `from_session_thread_id`, `from_agent_name`, and a `content` payload. When the coordinator delegates to a subagent, `agent.thread_message_sent` fires with `to_session_thread_id`, `to_agent_name`, and `content`. The coordinator synthesizes subagent outputs into its own context; **individual subagents do not communicate peer-to-peer**. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Tools, MCP, and context are NOT shared.** Each agent uses only the tools, MCP servers, and system prompt declared in its own agent definition. Agents cannot see each other's conversation history. The only shared surfaces are the sandbox filesystem and vault credentials (which are session-scoped, not agent-scoped). This is load-bearing for integration design: you cannot assume a subagent can access a tool the coordinator has unless you declared it in the subagent's configuration. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Dynamic Workflows:** Intermediate results live in script variables, not in any agent's context window. There is no shared state between agents. The script itself is what holds the plan, the branching logic, and accumulated results across phases. [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows)

**Anthropic's production pattern:** In their own multi-agent research system, agents write outputs to external storage (Memory/filesystem) and pass lightweight references back to the coordinator. This prevents the "game of telephone" problem where full results accumulate in the coordinator's context and degrade quality. [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

### 2. How Orchestrator Agents Delegate to Subagents

**Managed Agents API — configuration-time roster:** The coordinator is created with a `multiagent` field declaring the exact agents it can delegate to. Delegation at runtime is autonomous — the coordinator (Claude) decides which agents to invoke based on its system prompt and incoming task.

```json
{
  "multiagent": {
    "type": "coordinator",
    "agents": [
      {"type": "agent", "id": "<agent_id>"},
      {"type": "agent", "id": "<agent_id>", "version": "<pinned_version>"},
      {"type": "self"}
    ]
  }
}
```

The roster is snapshotted at coordinator creation time. Referenced agents are version-pinned and do **not** automatically pick up later updates. To delegate to a newer agent version, you must update the coordinator explicitly. The coordinator can include `{"type": "self"}` to spawn copies of itself. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Delegation is one level deep only.** Depth greater than 1 is ignored by the API. Subagents cannot spawn their own subagents. A maximum of 20 unique agents can be listed in `multiagent.agents`, but the coordinator can call multiple copies of the same agent. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Dynamic Workflows — code-based delegation:** Claude writes a JavaScript script that calls the Task tool for each subagent invocation. The script controls the loop, concurrency, and branching; the model is not involved in orchestration decisions after the script is written. Claude Code's Agent SDK and headless mode run the script without any per-run approval prompt. [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows)

### 3. Data Structures for Inter-Agent Communication

**Managed Agents API — event types (primary thread):**

| Event type | Key fields | When it fires |
|---|---|---|
| `session.thread_created` | `session_thread_id`, `agent_name` | Coordinator spawned a thread |
| `session.thread_status_running` | `session_thread_id` | Thread started working |
| `session.thread_status_idle` | `session_thread_id`, `stop_reason` | Thread awaiting input or requires action |
| `session.thread_status_terminated` | — | Thread archived or encountered terminal error |
| `agent.thread_message_received` | `from_session_thread_id`, `from_agent_name`, `content` | Subagent returned a result |
| `agent.thread_message_sent` | `to_session_thread_id`, `to_agent_name`, `content` | Coordinator sent a task |

[Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Tool permission and custom tool result routing:** When a subagent is blocked on a tool confirmation or custom tool call, `session.thread_status_idle` fires on the primary thread with `stop_reason: {type: "requires_action", event_ids: [...]}`. Your client responds by posting `user.tool_confirmation` (with `tool_use_id`) or `user.custom_tool_result` (with `custom_tool_use_id`) to the session event endpoint. The server routes the response to the correct thread automatically.

```json
{
  "type": "session.thread_status_idle",
  "session_thread_id": "sth_01DEF...",
  "agent_name": "code-reviewer",
  "stop_reason": {
    "type": "requires_action",
    "event_ids": ["toolu_01XYZ..."]
  }
}
```

[Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Dynamic Workflows — no inter-agent message schema.** Results live in JavaScript variables within the script. The `args` global accepts structured input at invocation time (arrays, objects — no parsing required). There is no documented inter-agent message format because the script is the sole coordination artifact. [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows)

**Anthropic's research system — no formal schema documented.** The engineering blog describes structured task descriptions ("objective, output format, guidance on tools, task boundaries") but does not publish a schema. Early attempts with vague one-line task strings failed because subagents misinterpreted assignments and duplicated work. [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

### 4. How to Handle Results Returned from Subagents

**Managed Agents API:** The primary thread event `agent.thread_message_received` carries the subagent's result in a `content` array (same structure as an `agent.message` event from a single-agent session — text blocks, tool results, etc.). You consume this from your application by subscribing to `/v1/sessions/:id/events/stream`. To drill into a specific subagent's full reasoning and tool call trace, stream or list events from its session thread at `/v1/sessions/:id/threads/:thread_id/events`. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Thread lifecycle management:** Completed threads consume capacity against a hard limit of 25 concurrent threads per session. Archive a completed thread (`POST /v1/sessions/:id/threads/:thread_id/archive`) to free a slot. Archive only succeeds on `idle` threads; interrupt a running or blocked thread first, then archive. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Threads are persistent:** The coordinator can send follow-up messages to an agent it called earlier, and that agent retains its prior conversation history. This enables multi-turn delegation to the same subagent across a session. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Dynamic Workflows:** Results are cached per-agent for the duration of the run. If a run is paused and resumed in the same session, agents that already completed return their cached results without re-executing. Exiting Claude Code between runs discards the cache and restarts the workflow from scratch. [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows)

### 5. Best Practices for Building Reliable Multi-Agent Pipelines

**Use artifact-based outputs, not context-passing.** Anthropic's production system passes lightweight references (file paths, storage keys) between the coordinator and subagents rather than embedding full subagent outputs in the coordinator's context. Full results accumulate as token overhead and degrade synthesis quality. [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

**Write detailed subagent task descriptions.** Each subagent invocation should specify: a concrete objective, an expected output format, which tools or sources to use, and explicit task boundaries to prevent work duplication. One-sentence descriptions consistently produced misinterpreted or duplicated work in Anthropic's research system. [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

**Specialize agents; do not stack all capabilities onto the coordinator.** Use `specialization` routing — domain-focused system prompts and scoped tool sets per agent — rather than granting every agent every tool. MCP servers are agent-scoped; vault credentials are session-scoped. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Pin agent versions explicitly.** Agent roster entries default to the latest version at coordinator creation time and do not auto-update. In production pipelines, pin specific versions (`"version": "<version>"`) to avoid silent behavior changes when subagent definitions are updated. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Add tools to your allowlist before long runs.** Shell commands, web fetches, and MCP tools not in the tool allowlist will trigger interactive confirmation prompts mid-run. In headless or SDK-based pipelines, pre-approve tools to prevent blocking. [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows)

**Archive completed threads.** The 25-thread concurrent limit is a hard cap. Pipelines that fan out to many agents must archive idle threads to remain under the limit. Build thread archival into your result-handling loop. [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent)

**Use parallelization within synchronous phase boundaries.** Anthropic's own production orchestrator runs subagents in parallel batches but waits for all agents in a batch to complete before the coordinator synthesizes and proceeds to the next phase. The simpler synchronous boundary trades some throughput for dramatically reduced coordination bugs. [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

**Use simpler primitives first.** The Building Effective Agents guidance (Dec 2024) notes that the most reliable production systems are built with the simplest composition that handles the task, not the most general framework. Reduce abstraction layers as you move toward production. [Building Effective AI Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)

---

## Trade-offs and Caveats

**Parallel execution vs. synchronous coordination — a documented conflict.** The Managed Agents API and Dynamic Workflows both emphasize parallel fan-out. Anthropic's engineering blog on their research system, however, reports that their *production* lead agents run subagents *synchronously* — waiting for a full batch to complete before proceeding — because it simplifies coordination at the cost of some throughput. The resolution is that parallel fan-out and synchronous phase boundaries are not in conflict: you fan out agents *within* a phase, then wait for the phase before synthesizing. Neither approach is wrong; the tradeoff is throughput vs. coordination complexity. [How we built our multi-agent research system — Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

**"Managed Agents handles state sharing" is imprecise.** Several secondary sources describe the API as providing "state sharing." The primary documentation is more specific: the *filesystem* and *vault credentials* are shared; *tools, MCP servers, and context* are explicitly not shared. Integration designs that assume a subagent can call a tool the coordinator has will fail unless that tool is independently declared in the subagent's definition.

**One-level delegation only.** The current API enforces a flat coordinator/worker hierarchy. Any design requiring hierarchical subagents (subagents spawning their own subagents) is not supported and depth > 1 is silently ignored.

**Beta API status.** The Managed Agents API requires the `managed-agents-2026-04-01` beta header. Beta APIs can have breaking changes without the same deprecation window as stable APIs. Monitor Anthropic's changelog before production promotion.

**Source staleness.** The "Building Effective Agents" blog post is from December 2024 — more than 18 months old as of June 2026. It predates both the Managed Agents API and Dynamic Workflows. Its orchestrator-worker pattern descriptions are still conceptually valid but do not reflect the current API surface. Treat it as background context, not implementation reference.

**Data structure documentation gaps.** The Managed Agents API documents event types and fields. It does not publish a formal JSON schema for `content` payloads within inter-agent events beyond noting they match the structure of `agent.message` content blocks. Dynamic Workflows has no documented inter-agent message format — the script is the communication medium.

---

## Sources

- [Multiagent sessions — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/multi-agent) — Primary reference: complete API for coordinator/subagent configuration, event types, thread management, vault/MCP scoping, and tool permission routing
- [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows) — Primary reference: Dynamic Workflows architecture, subagent spawning via script, context/result model, concurrency limits, and agent comparisons table
- [How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system) — Anthropic's own production multi-agent system: task description patterns, artifact-based output strategy, parallel execution within synchronous phase boundaries
- [Building Effective AI Agents — Anthropic Research](https://www.anthropic.com/research/building-effective-agents) — Dec 2024, 18+ months old: foundational orchestrator-worker and parallelization patterns; conceptually valid but predates current API products
- [Claude Managed Agents Deep Dive — DEV Community](https://dev.to/bean_bean/claude-managed-agents-deep-dive-anthropics-new-ai-agent-infrastructure-2026-3286) — Secondary source; confirmed absence of detailed inter-agent schema in community-level documentation
- [Anthropic launches dynamic workflows in Claude Code — ITBrief](https://itbrief.news/story/anthropic-launches-dynamic-workflows-in-claude-code) — Contextual: Dynamic Workflows launch announcement, May 2026
- [Claude Code Dynamic Workflows vs Agent Teams vs Sub-Agents — MindStudio](https://www.mindstudio.ai/blog/claude-code-dynamic-workflows-vs-agent-teams-vs-sub-agents) — Secondary: comparisons across Claude's multi-agent primitives
