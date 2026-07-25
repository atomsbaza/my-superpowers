# Topic 11: Agent Workflows as Graphs

## Core Idea
Modeling AI agents as graphs means replacing a linear script ("do A, then B, then C") — a fragile "degenerate graph" where every node has exactly one edge in and out — with an explicit directed graph where nodes are bounded units of work with strict input/output contracts, and edges are data contracts that only exist when data actually moves across them. Because the orchestration layer (routing, merging, deduplication) is plain deterministic code rather than an LLM call, it costs zero model tokens — reserving expensive model reasoning strictly for nodes that require judgment.

## Frameworks Introduced
- **Degenerate Graphs**: a linear, unbranching chain (every node: one edge in, one edge out) is the default shape when developers first write multi-step agents as scripts. It is fragile (one stalled node blocks everything downstream) and forfeits parallelism. The first skill of graph engineering is breaking this chain apart to find independent, fan-out-able tasks.
- **Nodes as Bounded Work Units**: a node is a distinct, bounded unit of work — depending on the framework, a deterministic function, a single LLM call, a tool call, or an isolated subagent. The fundamental rule: nodes take exactly one input and produce exactly one output; nodes are where thinking/processing happens.
- **Node Input/Output Schema Contracts**: a node you cannot reason about is a node you cannot safely parallelize. Every node needs a strict contract — bounded input, bounded output, exactly one job.
  - How: bind nodes to strict JSON Schemas instead of free text, forcing structured-output tool calls. If the model hallucinates a format, the tool layer catches the mismatch and forces a retry, so downstream nodes always receive predictably shaped data.
- **Edges as Data Contracts**: an edge is not merely "Step B comes after Step A" — it's a promise that Node A produces a specific data shape and Node B is built to consume exactly that shape.
  - Critical design rule: *the edge only exists when data actually moves across it.* If no variable crosses between two nodes, they are independent and should not be chained sequentially — this is the concrete test for finding hidden parallelism in what looks like a sequential script.

## Key Concepts
- **Zero-Token Coordination**: in a properly engineered multi-agent graph, the coordination layer — routing, flattening lists, deduplicating data — lives entirely in plain deterministic code (JavaScript/Python), executed by the runtime rather than an LLM, costing zero model tokens.
- **"A Graph Paying Rent on Its Own Wiring"**: the named anti-pattern of spawning an AI agent simply to combine results or flatten an array — burning expensive tokens on basic data plumbing that deterministic code should handle for free.
- **Dynamic Task Graph**: a runtime representation of a multi-agent workflow as a DAG that constantly updates and adapts its vertices/edges as the task progresses (introduced in Topic 1, concretized here).

## Mental Models
- **"Does data actually cross this edge?" is the practical parallelism-finding test**: rather than reasoning abstractly about whether two steps "could" run in parallel, apply the edge's data-contract test directly — if Node B doesn't consume anything Node A produces, there is no reason for an edge between them, and they should run concurrently.
- **Determinism does the wiring, judgment does the thinking**: the load-bearing design discipline of this whole topic is keeping a hard line between "this needs an LLM to decide" (goes in a node) and "this is just data plumbing" (goes in deterministic edge/coordination code) — conflating the two is what produces "a graph paying rent on its own wiring."
- **A schema-bound node is a safely-parallelizable node**: the reason JSON Schema contracts matter isn't just output quality — it's that a node whose output shape you can't guarantee is a node whose downstream consumers you can't safely fan out to, because you can't reason about what they'll receive.
- **A degenerate graph is a starting point to be broken apart, not a design flaw to be ashamed of**: most agent systems start as linear scripts; the graph-engineering skill is specifically the practice of finding where that chain has no real edges (no data dependency) and splitting it into fan-out-able independent work.

## Anti-patterns
- **A graph paying rent on its own wiring**: using an AI agent call to perform deterministic data plumbing (combining results, flattening arrays) instead of plain code — wastes tokens on work that requires no judgment.
- **Free-text node output instead of schema-bound output**: asking an agent to return unstructured text that downstream code must "parse and pray over," instead of forcing a structured-output tool call against a JSON Schema.
- **Chaining nodes with no real data dependency**: leaving a degenerate, fully-sequential graph shape in place when no edge in the chain actually carries data between the connected nodes — forfeiting available parallelism.

## Code Examples
(omit — the source material describes the schema-contract and zero-token-coordination principles conceptually; see Topic 12 for concrete fan-out/fan-in and routing code)

## Reference Tables
| Concept | Lives In | Cost |
|---|---|---|
| Judgment / reasoning | Nodes (LLM calls, agents) | Model tokens |
| Routing, merging, deduplication, flattening | Edges / orchestration code | Zero tokens (deterministic code) |

## Worked Example
A team's first version of a document-processing agent is a linear script: "extract text, then classify document type, then extract entities, then summarize, then combine everything into a report." Applying the edge-as-data-contract test, they find that entity extraction and summarization both only depend on the classified document type and the extracted text — neither depends on the other's output. There's no real edge between them; the linear chain was an artifact of how the script was written, not a genuine data dependency. They restructure into a graph where classification produces one output consumed independently by an entity-extraction node and a summarization node running in parallel, with a final combine step (data plumbing — implemented as plain code, not an agent call) merging both outputs into the report. The result: two previously-sequential steps now run concurrently, and the "combine" step that used to be an implicit LLM responsibility is now a zero-token deterministic merge.

## Key Takeaways
1. A linear multi-step agent script is a degenerate graph — recognizing this is the entry point to finding hidden parallelism.
2. Nodes are bounded work units with strict one-input/one-output contracts; edges are data contracts, not mere sequencing markers.
3. "Does data actually cross this edge?" is the concrete, practical test for whether two steps genuinely need to be sequential.
4. Coordination logic (routing, merging, deduplication) belongs in deterministic code, not agent calls — this is what makes zero-token orchestration possible and avoids "paying rent on the graph's own wiring."
5. Schema-bound (JSON Schema) node output isn't just about correctness — it's the precondition for safely parallelizing downstream consumers.

## Connects To
- **Topic 1 (What Is Graph Engineering)**: the degenerate-graph framing and node/edge definitions introduced there, made concrete here.
- **Topic 12 (Orchestration Topologies)**: the Diamond Pattern, fan-out/fan-in, and conditional routing that build directly on nodes-as-work-units and edges-as-data-contracts.
- **Topic 13 (Verification and Reliability)**: verifier nodes as a specific, high-stakes instance of "a node with a strict contract."
