# Composing Full Architectures

## 1. The Orchestrator Pattern: The Pattern of Patterns

**Definition.** The Orchestrator coordinates every other pattern in this corpus into one coherent system: it takes the user's request, invokes the Planner to decompose it, loads relevant Memory, uses the Retriever for grounding (RAG), routes to Tools, applies Guardrails at each boundary, and runs Verification before returning a final response.

```
User
 ↓
Orchestrator
 ↓
Planner → Retriever → Memory → Tools → LLM(s) → Verification
 ↓
Response
```

The Orchestrator is not a 16th pattern bolted onto the other 15 — it's the composition layer that makes the other 15 into a system rather than a toolbox. This is why it closes the pattern list in the seed article and why this corpus gives it a dedicated chapter rather than folding it into [Chapter 5](chapter05-multi-agent-patterns.md)'s Supervisor pattern: a Supervisor coordinates *worker agents* within one team; the Orchestrator coordinates *pattern categories* (planning, memory, tools, safety, verification) across the whole system, and may itself contain multiple Supervisor-coordinated teams as sub-components.

```csharp
var plan = await planner.CreatePlanAsync(request);
var context = await memory.LoadAsync(userId);
var data = await retriever.SearchAsync(request);
var answer = await agent.ExecuteAsync(plan, context, data);
return answer;
```

## 2. A Reference Architecture

Putting every chapter's pattern together into one enterprise-shaped diagram:

```
                     User
                      │
                      ▼
               API Layer (ASP.NET Core / equivalent)
                      │
                      ▼
             AI Agent Orchestrator
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
     Planner      Memory Layer   Guardrails
        │             │              │
        │             │              ▼
        │        Short-term (Redis) +   Input/Output/Tool-stage
        │        Long-term (Vector DB)  checks (Ch. 6)
        │             (Ch. 3)
        ▼
  Tool / MCP Registry (Ch. 2, Ch. 5)
        │
 ┌──────┼─────────┬──────────────┐
 ▼      ▼         ▼              ▼
SQL   REST API   Search      External Systems
        │
        ▼
 Reflection & Self-Verification (Ch. 4)
        │
        ▼
  Final AI Response
```

Every box has a single responsibility, which is what makes the system testable, extensible, and debuggable in isolation — the direct opposite of the God Agent anti-pattern ([Chapter 10](chapter10-anti-patterns-failure-modes.md)), where every one of these responsibilities lives inside one undifferentiated prompt.

## 3. Where Multi-Agent Teams Fit Inside the Orchestrator

For genuinely complex domains, the "Tools" box above is not a flat list of function calls — it's itself a multi-agent team ([Chapter 5](chapter05-multi-agent-patterns.md)), reached via the Agent Registry and coordinated by its own Supervisor, communicating asynchronously over an event bus ([Chapter 7](chapter07-reactive-workflow-patterns.md)) rather than through direct synchronous calls. The Orchestrator's job at that point is to know *which* specialist team a sub-task belongs to and to hand off a well-formed, schema-validated request — not to know how that team does its work internally. This layering is what keeps the top-level Orchestrator's own prompt lean even as the system's total capability grows, which is the same "lean coordinator, bounded specialists" principle from [Chapter 5](chapter05-multi-agent-patterns.md) applied one level up.

## 4. Composing Frameworks Inside One Orchestrator

Because the Orchestrator's boxes are pattern categories, not framework-specific objects, nothing requires all of them to be built on the same framework. See [Chapter 8](chapter08-framework-landscape.md) for the concrete example of a LangGraph control room delegating planning to Google ADK and execution to a CrewAI team, connected via MCP and A2A rather than custom integration code. The architectural discipline that makes this work — explicit typed handoffs at every box boundary, checkpointed state rather than transient conversation history, and guardrails that run outside any single framework's reasoning loop — is exactly the discipline [Chapter 10](chapter10-anti-patterns-failure-modes.md) identifies as the difference between the ~13–59% of production multi-agent systems that don't fail and the majority that do.

## 5. A Build-Order Heuristic

The research doesn't prescribe a rigid build order, but the pattern dependencies imply one that avoids rework:

1. **Tool Calling** first — nothing else works without a reliable way to act on the world.
2. **RAG / Memory** next — grounding and state before adding reasoning complexity on top of an ungrounded agent.
3. **Planner** once single-step tool use is solid and the task genuinely needs decomposition.
4. **Guardrails** *before*, not after, any autonomous multi-step or multi-agent capability ships — retrofitting safety onto an already-deployed agent is strictly harder than designing it in.
5. **Reflection / Self-Verification** once you have a deterministic-enough check to make the extra pass worth its cost.
6. **Multi-Agent / Supervisor / Registry / Orchestrator** only once a single well-guarded agent has demonstrably outgrown its scope — not as a default starting architecture.
