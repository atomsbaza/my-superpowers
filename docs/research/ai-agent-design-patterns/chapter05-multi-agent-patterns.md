# Multi-Agent Patterns

## 1. Multi-Agent Collaboration

**Definition.** Instead of one generalized agent handling an entire workload, a task is split across a team of specialized agents, each with a narrow role, scoped toolset, and focused system prompt — analogous to a software team where a researcher, coder, and tester each own a distinct responsibility rather than one person doing all three.

**Execution modes.** *Sequential* (linear handoff, output of one agent becomes input to the next), *Hierarchical* (a manager agent delegates to and consolidates from workers), and *Joint Deliberation* (multiple agents reason together, e.g. AutoGen-style multi-party conversation).

**Why it exists.** The dominant motivation, confirmed repeatedly across the failure-mode research, is that a single "God Agent" carrying every responsibility degrades on four fronts as it scales: context window overflow, exponential tool-selection confusion, cascading state corruption, and debugging intractability (full detail in [Chapter 10](chapter10-anti-patterns-failure-modes.md)). Splitting into specialized agents with a lean system prompt (well under 1,000 tokens) and a small toolset (3–4 tools) directly counters all four.

**Production tradeoff.** Coordination is not free — it replaces one hard problem (an overloaded single agent) with another (keeping multiple agents' understanding of shared state consistent). This tradeoff is only favorable once a single agent's scope has actually become unmanageable; splitting a genuinely simple task across multiple agents adds coordination overhead without a corresponding reliability gain.

```csharp
var researcher = await researchAgent.RunAsync(task);
var developer = await codingAgent.RunAsync(researcher);
var tester = await testingAgent.RunAsync(developer);
```

## 2. Supervisor / Orchestrator Pattern

**Definition.** One central agent supervises a team of worker agents: it interprets the overall objective, delegates sub-tasks to the appropriate specialist(s), and merges their outputs into a final result. (Note: this "Supervisor" pattern is the local coordination mechanism within a multi-agent team; [Chapter 9](chapter09-composing-architectures.md) covers the broader "Orchestrator" pattern that composes *all* pattern categories — planning, memory, tools, guardrails — into a full system architecture. The two share a name in casual usage but operate at different scopes.)

**When to use it.** Large workflows that benefit from parallel execution across specialists and a single point of synthesis — e.g. fanning out sales, finance, and HR analysis agents and merging into one report.

**Production tradeoff.** Simplifies debugging and gives a clear responsibility chain (every delegation and merge passes through one place), but creates a single point of failure and a potential bottleneck at the supervisor. The supervisor's own prompt must stay lean and focused purely on routing/aggregation — the moment it starts doing domain work itself, it re-introduces the God Agent problem at the coordination layer.

```csharp
var tasks = new[] { salesAgent.RunAsync(), financeAgent.RunAsync(), hrAgent.RunAsync() };
await Task.WhenAll(tasks);
var report = await managerAgent.MergeAsync(tasks);
```

## 3. Agent Registry Pattern

**Definition.** Instead of hardcoding which agents an application talks to, agents register their capabilities in a registry, and the application (or another agent) discovers and resolves the appropriate agent dynamically at runtime.

**When to use it.** Enterprise platforms with many specialized agents (HR, Finance, Legal, Sales, …) where hardwiring every possible caller-to-agent relationship doesn't scale, and new specialist agents need to be added without redeploying every consumer.

**Benefit.** Enables organization-wide discovery and reuse of specialized agents, and is a natural complement to interoperability standards like the Model Context Protocol (MCP) and the emerging Agent-to-Agent (A2A) protocol, which let a registry resolve not just *which* agent to call but *how* to call it across framework boundaries (see [Chapter 8](chapter08-framework-landscape.md)).

```csharp
IAgent agent = registry.Resolve("Finance");
var result = await agent.ExecuteAsync("Generate monthly report");
```

## 4. Coordination Overhead Is Structural, Not Incidental

A systems-theoretic finding worth internalizing before building a multi-agent system: in a flat, unbrokered mesh topology of N agents that all talk directly to each other, communication complexity scales quadratically (C = N(N-1)/2). This is why every pattern in this chapter routes communication through a small number of coordination points (a supervisor, a registry, an event bus — see [Chapter 7](chapter07-reactive-workflow-patterns.md)) rather than letting agents call each other peer-to-peer. Mesh topologies are the structural root of the "communication breakdown" and "state synchronization lag" failure categories documented in the MAST taxonomy ([Chapter 10](chapter10-anti-patterns-failure-modes.md)).
