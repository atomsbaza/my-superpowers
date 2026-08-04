# Framework Landscape

No framework implements every pattern equally well — each has a coordination model it was designed around, and that model determines which patterns are natural to build in it and which require fighting the framework. This chapter is a snapshot as of mid-2026 research sources; treat specific API names as a starting point to verify against current docs, not a stable contract.

## 1. Framework Comparison

| Framework | Core coordination model | Key strengths | Interop standards |
|---|---|---|---|
| **Semantic Kernel** (Microsoft) | Planner + plugin invocation | .NET-native, `FunctionCallingStepwisePlanner`, kernel/plugin abstraction maps cleanly onto Tool Calling and Planner patterns | MCP, Microsoft Agent Framework |
| **AutoGen** (Microsoft) | Conversation-driven, multi-party | Multi-agent deliberation and "swarms"; strong fit for Multi-Agent Collaboration's joint-deliberation mode | Microsoft Agent Framework |
| **Model Context Protocol (MCP)** | N/A — a tool/context interoperability standard, not an orchestration framework | Standardizes how any client discovers and invokes tools/resources/prompts across vendors | Consumed by nearly every framework in this table |
| **LangGraph** (LangChain) | Directed graphs with explicit, persistent state | Precise control over execution paths and cycles; first-class persistent checkpointing enables time-travel debugging and resumable workflows | LangChain ecosystem, MCP |
| **CrewAI** | Role-based "Crews," with CrewAI Flows for stateful control | Rapid prototyping via intuitive role/backstory definitions; Flows add explicit state for production use beyond simple sequential crews | CrewAI Flows |
| **OpenAI Agents SDK** | Agent + session + built-in compaction | Native context compaction (see [Chapter 3](chapter03-memory-pattern.md)), sandboxed tool execution | MCP |
| **Google ADK / Gemini Enterprise Agent Platform** | Graph-based / event-driven, managed runtime | Code-first agent definition, Memory Bank (async managed memory), Model Armor (guardrails), Agent Gateway | A2A (Agent-to-Agent), MCP |
| **AWS Bedrock AgentCore** | Orchestration loops on a managed runtime | Tight AWS ecosystem integration (IAM, VPC, Lambda), tiered/namespaced AgentCore Memory, Bedrock Guardrails | MCP, AgentCore SDK |

## 2. Reading the Table by Pattern

* **Planner** — most explicit in Semantic Kernel (a first-class object) and AutoGen; implicit in LangGraph and CrewAI, expressed as graph/flow structure instead.
* **Tool Calling** — universal, but MCP is the pattern's interoperability layer: a tool exposed via MCP is callable from any MCP-compliant client, not just the framework that defined it.
* **Memory** — where the platforms diverge most sharply (see [Chapter 3](chapter03-memory-pattern.md)): Google and AWS ship managed, opinionated memory services; LangGraph and the vector-store pattern stay portable but require more assembly.
* **Multi-Agent Collaboration / Supervisor** — AutoGen and CrewAI are purpose-built for this; LangGraph implements it via explicit graph topology (a supervisor node routing to worker nodes) rather than a dedicated abstraction.
* **Guardrail** — Google (Model Armor) and AWS (Bedrock Guardrails) ship first-party guardrail products; other frameworks generally expect you to bring your own (see [Chapter 6](chapter06-control-safety-patterns.md)).
* **Workflow / Event-Driven** — CrewAI Flows and LangGraph's state-graph model are both explicit fits; event-bus integration (Kafka, Service Bus) is typically layered on top of any framework rather than built in.

## 3. Multi-Framework Orchestration

A modern production architecture is not necessarily single-framework. A common composed pattern: **LangGraph** as the state-machine "control room" that owns durable, checkpointed execution state; it delegates planning to a **Google ADK** agent; which dispatches execution work to a **CrewAI** team of specialists. These otherwise-siloed frameworks are increasingly connected through two interoperability standards rather than custom glue code:

* **Model Context Protocol (MCP)** — standardizes tool/context exposure so a tool built for one framework is callable from another.
* **Agent-to-Agent (A2A)** — an emerging standard (led by Google) for agents built on different frameworks to discover and delegate to each other directly, complementing the Agent Registry pattern from [Chapter 5](chapter05-multi-agent-patterns.md).

**Design guidance.** Don't default to multi-framework composition — it adds an integration and versioning surface. It earns its cost when different parts of a system have genuinely different requirements a single framework doesn't serve well (e.g. a compliance-critical workflow needing LangGraph's checkpointing next to a rapid-iteration specialist team better expressed as a CrewAI crew). Standardizing tool exposure on MCP from the start keeps that option open even if you begin single-framework.
