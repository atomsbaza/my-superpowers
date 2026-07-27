# Topic 12: Orchestration Topologies

## Core Idea
The shape of a multi-agent graph — pipeline vs. barrier, fan-out/fan-in, the Diamond Pattern, conditional routing — is the single biggest lever on latency and cost. Barriers are only justified when a downstream step genuinely needs cross-item visibility; unjustified barriers create measurable latency waste ("Barrier Abuse"), and every handoff between agents carries a documented token premium, making topology choice and model tiering the primary cost/latency control surface.

## Frameworks Introduced
- **The Diamond Pattern (Fan-Out / Fan-In)**: split → work → merge. When a task decomposes into independent slices (auditing multiple files, querying multiple sources), the orchestrator fans out to identical agents concurrently via a `parallel(thunks)` construct, then merges results at a synthesis node.
  - When to use: any task with genuinely independent, decomposable slices of work.
  - How: `const raw = await parallel(SOURCES.map((s) => () => agent(s.prompt, { schema: ITEM_SCHEMA })));` then apply Null-Tolerant Collection: `const collected = raw.filter(Boolean);` — dropping casualties from individual agent failures without crashing the whole run.
- **Streaming Pipelines (`pipeline()`)**: pushes each item through multiple stages independently with no inter-stage barrier, as the default alternative to unjustified `parallel()` barriers.
  - When to use: whenever items can progress through stages at their own pace without needing to wait for the slowest sibling — e.g. a 5-minute complex file shouldn't stall the verification stage for 199 fast files running through the same pipeline.
- **Conditional Runtime Edge Routing**: inspects an agent's output and determines the downstream path at runtime, executed as deterministic code (not LLM judgment) for strict operational control.
  - How: classify with an agent against a schema, then branch in plain code (`if (severity === 'high') { await parallel(...) } else { await agent(...) }`). In LangGraph, this is `add_conditional_edges`, evaluating a routing function against current state to dynamically pick the next node(s).
- **LangGraph Reducers**: annotate state fields with reducer functions so parallel node writes merge safely instead of last-write-wins overwriting.
  - How: `Annotated[list, operator.add]` concatenates parallel worker outputs into one list; `Annotated[list[AnyMessage], add_messages]` appends chat messages and deduplicates by ID (so an updated/corrected message replaces the old version rather than duplicating history).
- **Dynamic Parallelization (Map-Reduce)**: LangGraph's `Send` API spawns a variable number of worker nodes dynamically at runtime; workers execute in parallel and combine outputs in the parent graph via a reducer.

## Key Concepts
- **Barrier Justification Test**: a barrier (like `parallel()`) forces every execution slot to idle until the slowest worker finishes — only justified when a downstream step requires cross-item visibility (deduplicating across a full result set, an early-exit decision based on an aggregate count, a multi-agent judge panel comparing outputs).
- **Barrier Abuse**: using barriers where independent pipelines would suffice, creating a "staircase effect" in execution traces where downstream nodes unnecessarily queue behind unrelated slow tasks.
- **The Merge Problem**: LangGraph's default behavior when multiple parallel nodes write to the same state key is last-write-wins, silently overwriting earlier nodes' data — the reason reducers exist.
- **The Multi-Agent Premium**: a documented Anthropic study finding that a standard chat costs 1x tokens, a single-agent loop costs ~4x, and a multi-agent system costs ~15x, because context must be duplicated, summarized, or re-established across every agent boundary.
- **Model Routing / Tiering**: assigning models to nodes by difficulty — wide, mechanical fan-out stages (data extraction, file reading) route to cheap/fast models (Haiku, Gemini Flash); narrow, heavily-constrained merge/synthesis nodes at the bottom of the diamond use expensive frontier models.
- **Concurrency Caps**: workflows cap concurrent agents around the system's core count (e.g. ~16 active agents), queueing excess; hard backstops cap total agents per run (e.g. 1,000); composition caps mean a child sub-workflow **shares** its parent's concurrency cap, agent counter, and token budget — preventing multi-level nesting from exponentially multiplying capacity.

## Mental Models
- **Ask "does the next step need to see everyone, or just me?" before reaching for a barrier**: this single question distinguishes justified barriers (dedup, aggregate routing, judge panels — genuinely need cross-item visibility) from Barrier Abuse (forcing independent items to synchronize when a pipeline would let each proceed at its own pace).
- **The multi-agent premium means every additional handoff is a deliberate spend, not a free abstraction**: at ~15x token cost for multi-agent systems vs. 1x for standard chat, topology decisions (how many agents, how many handoffs, how much context re-establishment) are cost decisions on the same order of magnitude as model selection — treat them with the same rigor.
- **Model tiering follows the shape of the diamond, not a flat policy**: wide parts of the graph (many parallel, mechanical nodes) want cheap models; narrow parts (the few high-stakes synthesis/verification nodes) want expensive ones — a uniform "always use the best model" or "always use the cheapest model" policy wastes money or quality at one end of the diamond.
- **Composition caps exist because nested capacity multiplication is a real risk, not a theoretical one**: without a shared cap between parent and child workflows, a sub-workflow spawning its own fan-out inside an already-fanned-out parent could multiply concurrent agents and token spend combinatorially — the shared-cap rule is the deliberate guardrail against that.

## Anti-patterns
- **Barrier Abuse**: using `parallel()`-style synchronization where independent `pipeline()` stages would suffice, producing a staircase-effect latency penalty in traces.
- **Ignoring the Merge Problem**: writing parallel node outputs to shared state without a reducer, silently losing data to last-write-wins.
- **Uniform model selection across the whole diamond**: not tiering models to node difficulty, over-spending on wide mechanical stages or under-provisioning narrow synthesis stages.
- **Unbounded nested composition**: allowing child sub-workflows to spawn fan-out without inheriting the parent's concurrency/token caps, risking combinatorial cost/capacity blowup.

## Code Examples
```javascript
// Diamond Pattern — fan-out with parallel(), Null-Tolerant Collection on fan-in
const raw = await parallel(SOURCES.map((s) => () => agent(s.prompt, { schema: ITEM_SCHEMA })));
const collected = raw.filter(Boolean); // drops nulls from failed agents
```
```javascript
// Conditional runtime edge routing — deterministic branch on agent classification
const { severity } = await agent("Classify risk...", { schema: SEVERITY_SCHEMA });
if (severity === 'high') {
    await parallel(...); // heavy path: full parallel audit
} else {
    await agent(...);    // light path: one quick pass
}
```
```python
# LangGraph reducer — list accumulation across parallel writes
Annotated[list, operator.add]
# Chat history — appends and deduplicates by message ID
Annotated[list[AnyMessage], add_messages]
```

## Reference Tables
| Topology | When to Use | Cost/Latency Profile |
|---|---|---|
| Pipeline (sequential, no barrier) | Items can progress independently through stages | Low cost, but high latency if truly sequential; avoids idle waiting on siblings |
| Barrier (`parallel()`) | Downstream step needs cross-item visibility (dedup, aggregate routing, judge panel) | High concurrent token cost, low latency for the batch, but idles on the slowest worker |
| Diamond (fan-out → fan-in) | Independent decomposable slices needing eventual synthesis | Concurrent cost during fan-out; requires reducers for safe state merging |

| Node Position | Model Tier |
|---|---|
| Wide, mechanical fan-out (extraction, formatting, routing) | Cheap/fast (Haiku, Gemini Flash) |
| Narrow, high-stakes synthesis/verification | Premium, high-reasoning frontier models |

## Worked Example
A code-review orchestrator processes 200 changed files. The naive design fans out 200 review agents in a single `parallel()` barrier, then waits for all 200 before any downstream step runs — but one file with a complex diff takes 5 minutes while the other 199 finish in 10 seconds, so the whole batch idles for 5 minutes (Barrier Abuse, staircase effect). The team restructures: a `pipeline()` pushes each file through review → verification independently, so fast files complete and report results without waiting on the slow one. They keep exactly one barrier — after all reviews complete, a deduplication step needs cross-item visibility to merge overlapping findings across files, which genuinely requires seeing the full result set. Model tiering: the 200 per-file review nodes (wide, mechanical) run on a cheap fast model; the single cross-file deduplication/synthesis node (narrow, high-stakes) runs on a frontier model. Total structure: pipeline for the wide part of the diamond, one justified barrier at the narrow synthesis point.

## Key Takeaways
1. Topology shape (pipeline vs. barrier, fan-out/fan-in) is the primary latency/cost lever in multi-agent systems — bigger than most individual model or prompt choices.
2. A barrier is only justified when the downstream step needs genuine cross-item visibility; anything else is a candidate for `pipeline()` instead, to avoid Barrier Abuse.
3. Parallel writes to shared state need reducers, or the Merge Problem (last-write-wins data loss) will silently corrupt results.
4. The documented ~15x multi-agent token premium (vs. 1x for standard chat) means every additional agent handoff is a deliberate cost decision.
5. Model tiering follows the diamond's shape: cheap models at the wide, mechanical parts; expensive models at the narrow, high-stakes synthesis/verification parts.
6. Composition caps (shared concurrency/token budget between parent and child workflows) are the guardrail against combinatorial cost blowup from nested fan-out.

## Connects To
- **Topic 11 (Agent Workflows as Graphs)**: the node/edge-as-data-contract foundations this topic's topologies are built from.
- **Topic 13 (Verification and Reliability)**: judge panels as a specifically justified use of the barrier pattern.
- **Topic 7 (Distributed Graph Processing)**: Pregel's bulk-synchronous super-step model as the conceptual ancestor of barrier synchronization here.
