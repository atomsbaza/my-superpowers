# AI Agent Design Patterns — Research

**Provenance:** NotebookLM deep research — 211 processed sources (framework documentation, arXiv preprints, engineering blog posts from Anthropic/OpenAI/Google/Microsoft/AWS, and practitioner articles), collected 2026-08-05. Seeded from the Medium article ["15 AI Agent Design Patterns Every .NET Architect Should Know"](https://medium.com/@mohsho10/15-ai-agent-design-patterns-every-net-architect-should-know-36078bf3908c) by Mohammad Shoeb, then expanded beyond its .NET/Semantic Kernel framing into a framework-agnostic survey. This is a mixed-evidence synthesis, not a single authoritative source — treat specific statistics (failure rates, effectiveness percentages, latency numbers) as source-reported unless independently verified.

**Evidence interpretation:** arXiv papers are preprints unless peer review is independently established. Vendor claims (e.g. guardrail block rates, hallucination-detection accuracy) come from the vendor's own published benchmarks. Medium posts and practitioner blogs are engineering experience reports, not controlled studies. Framework capabilities described here (Semantic Kernel, LangGraph, CrewAI, AutoGen, OpenAI Agents SDK, Google ADK, AWS Bedrock AgentCore) reflect each framework's state as of mid-2026 research sources and will drift — verify against current docs before depending on a specific API.

---

## Executive Summary

The shift from LLM-wrapped chatbots to production AI agents is an architecture problem, not a prompting problem. A chatbot answers; an agent decomposes goals, calls tools, retrieves grounding context, remembers across turns, critiques its own output, and — increasingly — coordinates with other agents. None of that is free: every one of those capabilities is a design pattern with its own tradeoffs, failure modes, and framework support, and skipping the pattern doesn't remove the risk, it just moves the failure into production.

The research converges on a small set of foundational patterns (Planner, Tool Calling, RAG, Memory) that almost every serious agent needs, layered with quality patterns (Reflection, Self-Verification) that trade latency and cost for correctness, coordination patterns (Multi-Agent Collaboration, Supervisor/Orchestrator, Agent Registry) that trade simplicity for scale, and control patterns (Human-in-the-Loop, Guardrail, Retry/Recovery) that are non-negotiable the moment an agent can take a consequential action. An Orchestrator pattern composes all of the above into a coherent system — it is the pattern that turns a pile of patterns into an architecture.

The most consequential finding in the research is empirical, not theoretical: studies of production multi-agent systems report failure rates of **41–87%**, and **79% of those failures trace back to specification and coordination problems, not code bugs** — vague task decomposition, misaligned agent roles, and inconsistent shared state, not stack traces. The dominant anti-pattern behind this is the **"God Agent"** — one agent, too many tools, an overloaded system prompt — which degrades via context window pollution, exponential tool-selection confusion past roughly 10–15 tools, and cascading, hard-to-debug state corruption. The MAST (Multi-Agent System Failure) taxonomy and a complementary systems-theoretic framework both converge on the same prescription: bounded specialization, explicit typed handoffs between agents, persistent checkpointed state, event-driven decoupling instead of synchronous call chains, and validation loops that catch bad output before it propagates.

Memory deserves its own treatment because "add a vector database" is not a memory architecture. Production systems separate short-term (session-scoped) from long-term (cross-session) memory and choose among genuinely different mechanisms — MemGPT's OS-inspired paging, OpenAI's context compaction, Google's asynchronously curated Memory Bank, AWS AgentCore's tiered/namespaced memory, or a plain vector-store RAG loop — each with different latency, cost, and portability tradeoffs, and each vulnerable to a distinct failure mode (context rot, memory poisoning, retrieval drift).

Safety is likewise a systems problem, not a prompt problem: guardrails work only when they execute as deterministic checks *outside* the model's reasoning loop, at three control points (input, tool/orchestration, output), because a jailbroken or injected model cannot be trusted to guard itself. The Model Context Protocol (MCP), which is rapidly becoming the standard for tool integration across frameworks, brings its own security surface — tool poisoning via manipulated tool descriptions, and the "confused deputy" problem in shared OAuth proxies — that a generic prompt-injection guardrail does not cover.

The closing chapters translate this into a framework landscape (which of Semantic Kernel, AutoGen, MCP, LangGraph, CrewAI, OpenAI Agents SDK, Google ADK, and AWS Bedrock AgentCore implements which pattern), a chapter on composing patterns into a full architecture, a dedicated anti-patterns/failure-modes chapter, and a condensed decision-rule cheatsheet — so the corpus works both as a reference (read any chapter standalone) and as a design checklist before building an agent.

---

## Table of Contents

### Chapters

1. [Fundamentals](chapter01-fundamentals.md) — what makes something an agent rather than a chatbot; the 15-pattern taxonomy and how the chapters group it.
2. [Foundational Patterns](chapter02-foundational-patterns.md) — Planner, Tool Calling, and Retrieval-Augmented Generation (RAG): the patterns almost every agent needs.
3. [Memory Pattern](chapter03-memory-pattern.md) — short-term vs. long-term memory; MemGPT paging, OpenAI compaction, Google Memory Bank, AWS AgentCore Memory, vector-store RAG; context rot, memory poisoning, retrieval drift.
4. [Reflection & Self-Verification](chapter04-reflection-verification.md) — critique-and-improve loops, self-checking output, and the Critic/Evaluator pattern.
5. [Multi-Agent Patterns](chapter05-multi-agent-patterns.md) — Multi-Agent Collaboration, Supervisor/Orchestrator delegation, and the Agent Registry pattern for dynamic discovery.
6. [Control & Safety Patterns](chapter06-control-safety-patterns.md) — Human-in-the-Loop approval, the Guardrail pattern (prompt injection, PII, content safety, output validation, authorization), and Retry/Recovery.
7. [Reactive & Workflow Patterns](chapter07-reactive-workflow-patterns.md) — Event-Driven agents and the (more constrained, more auditable) Workflow pattern.
8. [Framework Landscape](chapter08-framework-landscape.md) — Semantic Kernel, AutoGen, MCP, LangGraph, CrewAI, OpenAI Agents SDK, Google ADK, AWS Bedrock AgentCore: coordination model, strengths, interop standards (MCP, A2A).
9. [Composing Full Architectures](chapter09-composing-architectures.md) — the Orchestrator pattern as the pattern of patterns; a reference architecture; multi-framework composition via MCP/A2A.
10. [Anti-Patterns & Failure Modes](chapter10-anti-patterns-failure-modes.md) — the God Agent; the 41–87% production failure-rate research; the MAST taxonomy; the systems-theoretic failure framework; concrete mitigations.

### Appendices

- [Appendix: Glossary](appendix-glossary.md) — definitions of every pattern and technical term used across the chapters.
- [Appendix: Cheatsheet](appendix-cheatsheet.md) — condensed pattern-selection table, framework comparison table, and an IF/THEN decision-rule catalog.
