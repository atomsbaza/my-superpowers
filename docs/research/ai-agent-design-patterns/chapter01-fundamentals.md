# Fundamentals

## 1. What Makes Something an Agent, Not a Chatbot

A single call to a chat completion API — prompt in, text out — is not an agent. It has no memory beyond the current context window, cannot act on the world beyond generating text, cannot check its own work, and cannot recover from a bad step except by being re-prompted by a human. Production AI agents are distinguished by a specific set of capabilities layered on top of that base call:

* They **remember** across turns and sessions, not just within one context window.
* They **use tools** — calling APIs, databases, and external systems rather than hallucinating an answer.
* They **retrieve** grounding information instead of relying solely on parametric (trained-in) knowledge.
* They **collaborate** with other agents when a task exceeds one agent's effective scope.
* They **recover from failure** — transient errors, rate limits, malformed output — without a human intervening every time.
* They **verify their own work** before returning it.
* They **execute workflows** — multi-step, often auditable sequences — rather than answering in one shot.
* They **learn from and adapt to** previous interactions within a session and, in more advanced systems, across sessions.

Each of these capabilities corresponds to one or more of the design patterns in this corpus. None of them is free — each has an implementation cost, a latency/cost tradeoff, and a specific way it fails when done poorly. Market analysts (Gartner) project that a large share of enterprise applications will embed task-specific agents by 2026, which is exactly why the engineering discipline around these patterns — not prompt engineering — is becoming the differentiator between a demo and a production system.

## 2. Why Patterns, Not Prompts, Are the Unit of Reliability

A recurring theme across the research is that reliability comes from **imposing structure and constraints on a fundamentally non-deterministic model**, sometimes described in the sources as "graph engineering" — not a new idea, but the current name for a well-established systems-engineering discipline applied to LLM-based systems. The practical implication: every pattern in this corpus exists to remove some class of decision from the model's free-form reasoning and replace it with deterministic, testable structure — a state machine, a schema, a retry policy, an approval gate — while still using the model for what it is uniquely good at (language understanding, flexible reasoning, tool selection).

This reframes "prompt engineering" as one input to a much larger system design problem. A well-crafted prompt on top of a monolithic, tool-overloaded, memory-less, unguarded agent will still fail in production; a mediocre prompt on top of a properly decomposed, memory-tiered, guarded, and verified architecture will often succeed. The patterns in this corpus are, collectively, the structure that makes that difference.

## 3. The 15-Pattern Taxonomy and How This Corpus Groups It

The seed article identified 15 recurring patterns in production .NET agent architectures. This corpus keeps all 15, verifies and deepens each against a much broader (framework-agnostic) source set, and groups them into thematic chapters so related patterns can be read together:

| # | Pattern | Chapter |
|---|---|---|
| 1 | Planner | [Ch. 2 — Foundational Patterns](chapter02-foundational-patterns.md) |
| 2 | Tool Calling | [Ch. 2 — Foundational Patterns](chapter02-foundational-patterns.md) |
| 3 | Retrieval-Augmented Generation (RAG) | [Ch. 2 — Foundational Patterns](chapter02-foundational-patterns.md) |
| 4 | Memory | [Ch. 3 — Memory Pattern](chapter03-memory-pattern.md) |
| 5 | Reflection | [Ch. 4 — Reflection & Self-Verification](chapter04-reflection-verification.md) |
| 6 | Multi-Agent Collaboration | [Ch. 5 — Multi-Agent Patterns](chapter05-multi-agent-patterns.md) |
| 7 | Supervisor | [Ch. 5 — Multi-Agent Patterns](chapter05-multi-agent-patterns.md) |
| 8 | Human-in-the-Loop | [Ch. 6 — Control & Safety Patterns](chapter06-control-safety-patterns.md) |
| 9 | Event-Driven Agent | [Ch. 7 — Reactive & Workflow Patterns](chapter07-reactive-workflow-patterns.md) |
| 10 | Workflow | [Ch. 7 — Reactive & Workflow Patterns](chapter07-reactive-workflow-patterns.md) |
| 11 | Self-Verification | [Ch. 4 — Reflection & Self-Verification](chapter04-reflection-verification.md) |
| 12 | Retry and Recovery | [Ch. 6 — Control & Safety Patterns](chapter06-control-safety-patterns.md) |
| 13 | Guardrail | [Ch. 6 — Control & Safety Patterns](chapter06-control-safety-patterns.md) |
| 14 | Agent Registry | [Ch. 5 — Multi-Agent Patterns](chapter05-multi-agent-patterns.md) |
| 15 | Orchestrator | [Ch. 9 — Composing Full Architectures](chapter09-composing-architectures.md) |

Chapter groupings reflect why the pattern exists, not just what it's called: **foundational** patterns are what turns a chatbot into an agent at all; **memory** gets its own chapter because "memory" turned out to be five genuinely different architectures with different failure modes, not one; **quality** patterns (Reflection, Self-Verification) trade cost/latency for correctness; **coordination** patterns (Multi-Agent, Supervisor, Registry) trade simplicity for scale; **control** patterns (HITL, Guardrail, Retry) are the non-negotiable safety layer; **reactive/workflow** patterns govern how and when an agent runs at all; and the **Orchestrator** is the pattern that composes every other pattern into one coherent system, which is why it gets a dedicated composition chapter rather than a short standalone entry.
