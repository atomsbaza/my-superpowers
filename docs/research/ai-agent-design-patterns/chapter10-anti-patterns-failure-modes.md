# Anti-Patterns & Failure Modes

## 1. The Headline Numbers

Empirical research into production multi-agent LLM systems (2025–2026 deployments) reports failure rates of **41–87%** — a wide range, but consistently high, indicating agents that succeed reliably in isolated demos degrade sharply under real production entropy: real users, real latency, real partial failures.

The more actionable finding is *why*: **79% of these failures trace back to specification and coordination issues, not low-level code bugs.** Within that, **coordination failures alone account for 37%** — communication breakdowns, state-synchronization lag between parallel agents, and conflicting objectives caused by agents operating on mismatched semantic definitions of shared data (e.g. a Finance agent and a Compliance agent computing different answers because they don't agree on what "revenue" means in a given context). Treat these as source-reported figures from the underlying studies, not independently re-derived numbers — but treat the *direction* of the finding (failures are architectural, not syntactic) as the load-bearing conclusion, since it recurs across multiple independent sources in this corpus.

## 2. The MAST Taxonomy

The Multi-Agent System Failure (MAST) taxonomy, built from analyzing 7 popular multi-agent frameworks across 200+ tasks, classifies failures into three structural categories:

```
                    MAST FAILURE TAXONOMY
                            │
      ┌─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
SPECIFICATION        INTER-AGENT           TASK VERIFICATION
   ISSUES             MISALIGNMENT             FAILURES
 • Poor task        • Communication       • Incorrect self-
   decomposition       breakdowns            verification
 • Inadequate       • Inconsistent goal   • Incomplete quality
   role definitions   execution             checks
 • Unclear target   • Memory failures     • 13.48% of all
   specifications   • Protocol drift        MAST failures
```

1. **Specification issues** — rooted in how tasks are formulated and assigned: coarse-grained or non-verifiable decomposition (see the Planner pattern's failure mode, [Chapter 2](chapter02-foundational-patterns.md)), vague role/backstory definitions that dilute an agent's focus, unclear objectives.
2. **Inter-agent misalignment** — rooted in runtime interaction: communication breakdowns, downstream agents misinterpreting upstream intent, memory management failures (context pollution, amnesia — [Chapter 3](chapter03-memory-pattern.md)), and coordination-protocol violations.
3. **Task verification failures** — 13.48% of all observed MAST failures: incorrect self-verification, incomplete verification processes, insufficient quality control (the exact gap the Self-Verification and Critic/Evaluator patterns in [Chapter 4](chapter04-reflection-verification.md) exist to close).

## 3. A Systems-Theoretic View: Five Subsystems, Five Failure Classes

A complementary framework decomposes any autonomous agent into five interacting functional subsystems and maps failure modes to each:

| Subsystem | Failure modes |
|---|---|
| **Reasoning & World Model** | World-model inconsistency (internal representation diverges from reality); planning drift (brittle or hallucinated plans); counterfactual reasoning deficit (leaning on stale parametric knowledge over fresh retrieved facts) |
| **Perception & Grounding** | Poor cognitive data quality (favoring stale training bias over fresh context); context window pollution ([Chapter 3](chapter03-memory-pattern.md)); stale state replay (historical errors get replayed, corrupting new trajectories) |
| **Action Execution** | Tool parameter hallucination (invalid schemas — [Chapter 2](chapter02-foundational-patterns.md)); inadequate error recovery (stuck in expensive infinite tool loops on transient failure) |
| **Learning & Adaptation** | Catastrophic forgetting of earlier instructions when adapting to new task experience; value/alignment decay over long-running sessions |
| **Inter-Agent Communication** | Quadratic communication overhead in mesh topologies; state synchronization lag; cascading error propagation (one agent's error or injected instruction silently poisons the whole fleet's state) |

## 4. The God Agent Anti-Pattern

The single most cited production design error: one generalized agent carrying the entire system's workload — all business logic, all memory management, all planning, every tool, every output format — behind one increasingly bloated system prompt.

```
                  [ THE GOD AGENT ]
             (1 Agent, 20 attached Tools)
         ┌───────────────────────────┐
         │   System Prompt (vague,   │
         │      4,000+ tokens)       │
         └─────────────┬─────────────┘
                        │
  ┌──────────┬──────────┼──────────┬──────────┐
  ▼          ▼          ▼          ▼          ▼
read_db   write_api  send_eml   run_bash   query_crm
```

It degrades on four fronts:

1. **Context window overflow and attention decay.** Each attached tool needs a schema, docstring, and often few-shot examples — 20 tools can consume 3,000–5,000 tokens before the user even speaks. Combined with the "lost-in-the-middle" attention effect, constraints defined early in a long session get silently pushed out of effective attention and ignored by later turns.
2. **Exponential tool confusion.** The combinatorial space of possible tool sequences explodes with tool count. Benchmarks cited in the research show tool-selection accuracy dropping sharply once an agent has more than roughly **10–15 tools** available simultaneously — the model starts picking "close enough" tools or hallucinating parameters.
3. **Cascading failures and silent state corruption.** With zero isolation of state in one context window, a transient error at step 3 of a 7-step chain pollutes the conversation history with raw error dumps, forcing steps 4–7 to reason over corrupted context — the agent often completes with high confidence and a completely wrong answer.
4. **Debugging and testing intractability.** A monolithic agent's failure can't be isolated to one component; engineers comb through one massive multi-turn log. The system can't be unit-tested component by component — only run as expensive, non-deterministic end-to-end integration tests.

## 5. Anti-Patterns Checklist

* **The God Agent** — one agent, too many tools, an overloaded prompt. (§4 above)
* **Ungrounded tool access** — letting the LLM hit databases or external systems directly with no tool abstraction layer, risking unauthorized reads/writes. (See Tool Calling, [Chapter 2](chapter02-foundational-patterns.md), and Guardrails, [Chapter 6](chapter06-control-safety-patterns.md).)
* **Missing memory** — no separation of short-/long-term memory, causing the agent to "forget" context it was already given. (See [Chapter 3](chapter03-memory-pattern.md).)
* **No guardrails / prompt-only safety** — trusting system-prompt instructions as the sole safety mechanism, which shares the model's own attention space with untrusted input and is bypassable. (See [Chapter 6](chapter06-control-safety-patterns.md).)
* **Single-model, no fallback** — no retry or fallback strategy when a specific model deployment hits latency, rate limits, or an outage. (See [Chapter 6](chapter06-control-safety-patterns.md).)
* **Unformatted inter-agent handoffs** — agents exchanging free-form natural language instead of typed, validated schemas, letting a hallucination in one agent silently propagate to the next uncaught.
* **Unbounded loops** — reflection, retry, or verification loops with no step budget, which convert a correctness safeguard into a silent cost sink instead of escalating to a human.

## 6. Concrete Mitigations

* **Bounded specialization** — decompose into specialist agents with a small toolset (3–4 tools) and a lean (<800-token) system prompt each, coordinated by a lean orchestrator/supervisor that does no domain work itself. ([Chapter 5](chapter05-multi-agent-patterns.md))
* **Trust boundaries and least privilege** — isolate agents that process untrusted input from agents with write/execute privileges; sandbox execution tools (ephemeral containers, workspace-only filesystem, resource limits); enforce per-user token passthrough rather than a shared privileged service account. ([Chapter 6](chapter06-control-safety-patterns.md))
* **Explicit, persistent state** — checkpoint every state mutation (Postgres/Redis-backed), enabling deterministic rollback and replay: roll back to the last good step instead of replaying (and re-billing) an entire multi-step run on failure.
* **Event-driven coordination over synchronous chains** — decouple agents via an event bus so one agent's outage doesn't cascade into the whole system's outage. ([Chapter 7](chapter07-reactive-workflow-patterns.md))
* **Rigid schema enforcement between agents** — typed, validated handoff contracts (Pydantic or equivalent) at every agent boundary, with a Critic/Evaluator loop rejecting and routing back malformed output. ([Chapter 4](chapter04-reflection-verification.md))
* **Step budgets** — hard-cap autonomous loops (`max_iter`); on exhaustion, roll back and raise a Human-in-the-Loop exception rather than looping indefinitely. ([Chapter 6](chapter06-control-safety-patterns.md))
