# Appendix: Glossary

**A2A (Agent-to-Agent)** — An emerging interoperability standard (led by Google) letting agents built on different frameworks discover and delegate to each other directly.

**Agent Registry** — A pattern where agents register their capabilities so callers can discover and resolve the right agent dynamically at runtime, instead of hardcoding agent relationships.

**AgentCore Memory (AWS)** — AWS Bedrock's managed memory service, separating short-term session state from long-term cross-session insight, with hierarchical namespaces for multi-tenant isolation.

**Chunk-shredding** — A retrieval failure where document boundaries and headings are lost during chunking, so retrieved fragments lack the surrounding context needed to interpret them correctly.

**Compaction (context compaction)** — Automated trimming of an agent's active context (e.g. OpenAI Agents SDK sessions) that removes older history while preserving system instructions and recent frames, keeping long-running sessions within the model's context window.

**Confused deputy problem** — An MCP/OAuth vulnerability where a proxy server with broad, shared credentials is tricked into acting on behalf of an unauthorized user because it doesn't validate per-user token audience.

**Context rot** — Degradation of an agent's effective attention to earlier instructions as a long session's context window fills with unsummarized or poorly summarized content ("lost-in-the-middle").

**Critic / Evaluator pattern** — A dedicated agent or process that verifies another agent's output against ground truth or explicit criteria, rejecting and returning malformed output for correction.

**Event-Driven Agent pattern** — Agents triggered by messages on an event bus (Kafka, Service Bus, SQS) rather than invoked synchronously, decoupling agents temporally and containing failures.

**God Agent** — The anti-pattern of one agent carrying an entire system's workload (all tools, all memory, all planning) behind one overloaded prompt; degrades via context overflow, tool confusion, cascading state corruption, and debugging intractability.

**Guardrail pattern** — A safety layer enforced as deterministic checks outside the model's own reasoning loop, at input, tool/orchestration, and output stages.

**HITL (Human-in-the-Loop)** — A pattern where the agent pauses and persists state to await human approval before executing a consequential action.

**MAST (Multi-Agent System Failure) taxonomy** — An empirically derived classification of multi-agent failures into specification issues, inter-agent misalignment, and task verification failures.

**MCP (Model Context Protocol)** — A standard for how LLM clients discover and invoke external tools, resources, and prompts, enabling tool interoperability across frameworks.

**Memory Bank (Google)** — Gemini Enterprise's managed long-term memory service that asynchronously extracts and consolidates user preferences/decisions out-of-band from session histories.

**Memory poisoning** — Corruption of long-term memory when unvalidated writes (e.g. a scoped, temporary user correction) get promoted to permanent, contradictory rules.

**MemGPT** — An OS-inspired memory architecture that pages content between a model's active context ("RAM") and external storage ("disk"), self-directed by the model via explicit function calls.

**Orchestrator pattern** — The top-level pattern that composes planning, memory, retrieval, tools, guardrails, and verification into one coherent agent system.

**Planner pattern** — Decomposing a complex goal into a structured sequence of smaller, executable steps before acting.

**RAG (Retrieval-Augmented Generation)** — Grounding an agent's response in documents or records retrieved from an external knowledge source at query time, rather than relying solely on training data.

**Reflection pattern** — Having the agent (or a second pass) critique and improve its own draft output before returning it.

**Retrieval drift** — A RAG/memory failure where semantically "similar" but contextually irrelevant chunks are retrieved, corrupting the context with noise.

**Retry and Recovery pattern** — Automatic recovery from transient LLM/tool failures via retries, model/region fallback, cached responses, or escalation, rather than surfacing every failure to the user.

**Self-Verification pattern** — The agent validates its own output against a deterministic, checkable rule (schema, syntax, arithmetic) and retries on failure.

**Supervisor pattern** — A central agent that delegates sub-tasks to specialist worker agents and merges their outputs, within one coordinated team.

**Tool Calling pattern** — The LLM acts purely as a reasoning engine, emitting structured requests for a separate deterministic layer to execute (API calls, DB queries, calculations).

**Tool poisoning** — An MCP-specific attack where a compromised or manipulated tool description/schema tricks an LLM client into invoking the wrong tool or exfiltrating data.

**Workflow pattern** — A predefined, auditable sequence of agent steps, trading autonomy for predictability and compliance-friendly traceability.
