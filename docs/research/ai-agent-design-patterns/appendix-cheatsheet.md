# Appendix: Cheatsheet

## 1. Pattern Selection Table

| Pattern | Use when | Skip / defer when |
|---|---|---|
| Planner | The goal genuinely implies an ordered, variable set of sub-tasks | The task is single-step or the decomposition is always the same (use Workflow instead) |
| Tool Calling | The agent needs to act on the world or do precise computation | Never skip — this is foundational the moment an agent does more than talk |
| RAG | The answer depends on current, private, or frequently changing information | The model's training data is sufficient and stable for the domain |
| Memory | The agent needs continuity across turns or sessions | A single-shot, stateless request with no follow-up expected |
| Reflection | Open-ended output where a second critical pass plausibly catches errors | Latency/cost-sensitive paths where the first-pass error rate is already low |
| Self-Verification | A deterministic check exists (schema, syntax, arithmetic) | No mechanical check is possible — falls back to Reflection or human review |
| Multi-Agent Collaboration | A single agent's scope has become unmanageable (tools, context, responsibilities) | The task is simple enough for one well-scoped agent — don't default to multi-agent |
| Supervisor | Multiple specialists need centralized delegation and result merging | A flat pipeline (Workflow) already captures the necessary structure |
| Agent Registry | Many specialist agents must be discoverable/reusable across an org | A small, fixed, known set of agents — hardcoding is simpler and sufficient |
| Human-in-the-Loop | The action is consequential/irreversible/costly if wrong | Low-stakes, easily-reversible actions where a delay costs more than the risk |
| Event-Driven | Work arrives asynchronously, or agents would otherwise chain synchronously | A simple, low-latency request/response interaction |
| Workflow | Predictability and auditability outrank flexibility (compliance, audits) | The process genuinely varies per request (use Planner) |
| Guardrail | Any agent that can be exposed to untrusted input or take a real-world action | Never skip in production — even "just a chatbot" faces prompt injection |
| Retry and Recovery | Any production call to an external model or service | Never skip — treat transient failure as certain, not exceptional |
| Orchestrator | Composing more than 2–3 of the above patterns into one system | A single pattern in isolation doesn't need a composition layer |

## 2. Framework Quick-Pick

| If you need… | Consider |
|---|---|
| .NET-native planning + tool calling | Semantic Kernel |
| Multi-party agent deliberation ("swarms") | AutoGen |
| Cross-framework tool interoperability | MCP (pair with any framework) |
| Explicit, checkpointed state machines / resumable workflows | LangGraph |
| Fast prototyping of role-based agent teams | CrewAI (Flows for production state) |
| Built-in context compaction, sandboxed execution | OpenAI Agents SDK |
| Managed memory + guardrails on GCP | Google ADK / Gemini Enterprise |
| Deep AWS IAM/VPC integration, managed memory + guardrails | AWS Bedrock AgentCore |
| Cross-framework agent-to-agent delegation | A2A (pair with a registry) |

## 3. IF/THEN Decision Rules

- IF an agent has more than ~10–15 tools attached → THEN split it into specialists with 3–4 tools each before shipping; tool-selection accuracy degrades sharply past that range.
- IF an agent's system prompt exceeds ~800–1,000 tokens of role/tool description → THEN treat it as a signal the agent's scope is too broad.
- IF any agent can process untrusted external content (web pages, emails, uploaded files) AND has write/execute tool access → THEN separate those two capabilities into different agents with a trust boundary, not just a prompt caveat.
- IF an agent writes to long-term memory → THEN validate/scope the write (session-only vs. durable) before persisting; never let a raw user statement become a permanent rule unchecked.
- IF two or more agents need to coordinate → THEN route them through a supervisor, registry, or event bus — never a flat peer-to-peer mesh (communication overhead scales quadratically with agent count).
- IF an agent can take a consequential, hard-to-reverse action → THEN gate it behind Human-in-the-Loop approval, regardless of how confident the model appears.
- IF a reflection, retry, or verification loop exists → THEN bound it with an explicit step budget and escalate to a human on exhaustion; never loop unbounded.
- IF a production deployment relies on a single model with no fallback → THEN treat that as an outage waiting to happen, not a cost optimization.
- IF inter-agent handoffs pass free-form natural language → THEN replace with typed, schema-validated payloads before scaling the team further.
- IF safety currently lives only in the system prompt → THEN that is not a guardrail; add deterministic checks outside the model's reasoning loop at input, tool, and output stages.
