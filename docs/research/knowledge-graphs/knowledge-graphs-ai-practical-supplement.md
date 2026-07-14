# Knowledge Graphs and AI: Practical Supplement (2025-2026)

This document complements `knowledge-graphs-ai-briefing.md`, which covers the theoretical landscape (GraphRAG vs. dense vector RAG vs. KAG, neuro-symbolic convergence, and agentic search). Where that briefing addresses *why* and *when* to reach for graph structure, this supplement addresses the *practical* side: which tools implement these ideas today, how knowledge graphs are used as agent memory, and how the field actually measures whether any of this works.

---

## 1. Tooling Ecosystem

### Graph databases
**Neo4j** remains the market leader — general-purpose, mature ecosystem, largest community — and is the default backing store for most GraphRAG frameworks ([arcadedb.com](https://arcadedb.com/blog/neo4j-alternatives-in-2026-a-fair-look-at-the-open-source-options/)). **FalkorDB** is purpose-built for GraphRAG workloads: sparse adjacency-matrix representations give it up to 496x faster p50 latency and 6x better memory efficiency than Neo4j on graph-retrieval queries, and it ships a `GraphRAG-SDK` for direct LLM integration ([falkordb.com](https://www.falkordb.com/blog/falkordb-vs-neo4j-for-ai-applications/)). **Memgraph** is in-memory-first and tuned for real-time analytics with low query latency, but it is licensed under BSL 1.1 (not FOSS), commercial licensing runs roughly $25k/year, and users report stability issues ([memgraph.com](https://memgraph.com/blog/neo4j-vs-memgraph)). **Kuzu** was acquired by Apple and archived in October 2025 — community forks exist but lack corporate backing, making it a risky long-term bet. **NebulaGraph** shows little recent development activity.

### Frameworks
**Microsoft GraphRAG** (github.com/microsoft/graphrag, ~29.8k stars) is the reference implementation: an indexing stage (entity/relation extraction plus Leiden community detection) paired with three query modes — global (community summaries), local (entity-level), and DRIFT (a hybrid). Reported benchmarks show 80% correct answers vs. 50.83% for traditional RAG; the GraphRAG 1.0 release (December 2024) cut startup time by 74x and storage by 43% ([articsledge.com](https://www.articsledge.com/post/graphrag-retrieval-augmented-generation)). **LightRAG** (October 2024) targets cost: roughly 10x fewer tokens than GraphRAG for comparable accuracy, using dual-level (local + global) retrieval ([medium.com/@claudiubranzan](https://medium.com/@claudiubranzan/from-llms-to-knowledge-graphs-building-production-ready-graph-systems-in-2025-2b4aff1ec99a)). **LazyGraphRAG** (June 2025) pushes further, claiming indexing cost of just 0.1% of full GraphRAG at comparable quality by deferring most graph construction to query time.

**Graphiti** (from Zep AI) is a temporal knowledge graph layer built on Neo4j, designed for incremental updates rather than batch re-indexing — it answers queries in P95 300ms without requiring an LLM call at query time, and beats GraphRAG on the Deep Memory Retrieval (DMR) benchmark, 94.8% vs. 93.4% ([neo4j.com](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)). Graphiti's temporal model and its role as agent memory are covered in more depth in Section 2.

Orchestration layers **LangChain** (`LLMGraphTransformer`) and **LlamaIndex** (property graphs with dynamic schema inference) are not standalone GraphRAG systems but glue code for building graphs from documents and wiring them into retrieval pipelines ([memgraph.com](https://memgraph.com/blog/improved-knowledge-graph-creation-langchain-llamaindex)). **Cognee** is a more production-oriented option — combines graphs and vectors, ships 30+ data connectors, and supports FalkorDB, Neo4j, or NetworkX as backends. **nano-graphrag** is a lightweight, minimal reimplementation with thin documentation, useful for prototyping but not hardened for production.

### Managed offerings
Fully managed GraphRAG-as-a-service is still limited: Microsoft Discovery (Azure), Zep's hosted offering, Fluree, and Amazon Neptune (AWS-native) are the notable options. Most teams instead self-host an open-source framework on top of a managed graph database — FalkorDB Cloud, Neo4j AuraDB, or Memgraph Cloud.

### Caveats
Kuzu's archival makes it a poor new choice regardless of its technical merits. Memgraph's licensing terms need legal review before commercial use. The GraphRAG-vs-LightRAG choice is a real trade-off between reasoning depth and cost, not a strict upgrade path — pick per workload. Graphiti's temporal capabilities are coupled to Neo4j; there's no backend-agnostic version.

---

## 2. Knowledge Graphs as Agent Memory

A separate and increasingly important application of KGs is as long-term memory for conversational or task-executing agents, distinct from GraphRAG's use over static document corpora.

### The bi-temporal model
Graphiti's core design tracks two independent time axes: *when a fact was true in the world* (`t_valid`/`t_invalid`) and *when the system learned about it* (`t_created`/`t_expired`). This separation lets an agent answer "what did I believe on date X" as well as "what is true now," and lets it resolve contradictions (a user's job change, say) without silently overwriting or discarding the earlier fact ([neo4j.com](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)).

### Benchmark evidence for temporal KG memory
The Zep paper reports DMR accuracy of 94.8% (using gpt-4-turbo) vs. 93.4% for MemGPT, and a larger gap on LongMemEval: +18.5% accuracy alongside a 90% latency reduction, driven by shrinking the context an agent needs to load from ~115k tokens down to ~1.6k ([arxiv.org/2501.13956](https://arxiv.org/html/2501.13956v1)). A separate comparison on LongMemEval found Mem0 (a vector-based memory system) at 49.0% accuracy vs. Zep (temporal KG) at 63.8% under GPT-4o ([vectorize.io](https://vectorize.io/articles/mem0-vs-zep)) — a substantially larger margin than GraphRAG's edge over dense RAG in document-retrieval settings (see Section 3), suggesting temporal/relational structure matters even more for tracking an evolving conversation than for static corpus QA.

### Episodic + semantic memory split
Recent agent-memory architectures pair two stores: an *episodic buffer* holding the last ~10 raw conversation turns for discourse coherence, and a *semantic (neocortical) memory* that consolidates facts more slowly, growing at roughly 3 tokens per message. This mirrors the complementary-learning-systems idea from cognitive science — fast, volatile episodic recall alongside slow, stable semantic consolidation ([arxiv.org/2605.17625](https://arxiv.org/html/2605.17625)).

### Consolidation pipeline
A common three-stage async pipeline turns raw dialogue into durable graph memory: (1) LLM-based extraction plus contradiction detection, (2) conflict resolution using temporal precedence (newer facts supersede older ones unless marked otherwise), and (3) incremental update of an entity/user profile rather than a full rebuild.

### Entity resolution
Matching new mentions to existing graph entities uses multi-layer matching: embedding similarity, fuzzy string matching, and type constraints (only compare entities of compatible types). Crucially, mid-confidence matches don't auto-merge — they create a `SAME_AS` edge flagged for human review, avoiding silent identity-merging errors ([neo4j.com/labs](https://neo4j.com/labs/agent-memory/explanation/resolution-deduplication/)).

### Forgetting
Memory systems increasingly treat forgetting as a first-class design goal rather than a failure mode: selective retention, pruning, mitigation of catastrophic forgetting, and context-triggered forgetting are framed as "forgetting-by-design," a resource-optimization technique rather than an accident ([arxiv.org/2602.06052](https://arxiv.org/pdf/2602.06052)).

### Caveats
Several of the strongest numbers above (Zep's DMR/LongMemEval results) are vendor-sourced and merit independent replication. Vector-only memory remains competitive for simple semantic recall (not everything needs a graph). Entity resolution in high-stakes domains is still partially manual by design (the `SAME_AS` human-review step). Forgetting mechanisms across the field are mostly heuristic rather than principled.

---

## 3. Evaluation & Benchmarks

### Purpose-built GraphRAG benchmarks
**GraphRAG-Bench** (ICLR 2026) is the most comprehensive dedicated benchmark: 1,018 college-level questions spanning 16 CS disciplines and 5 question formats, evaluating the full pipeline — construction, retrieval, and reasoning — with dedicated rationale-quality metrics (R Score, AR Metric) rather than just final-answer accuracy ([arxiv.org/2506.02404](https://arxiv.org/abs/2506.02404)).

### Multi-hop vs. single-hop performance
Across standard multi-hop QA benchmarks (HotpotQA, MuSiQue, 2WikiMultiHopQA), GraphRAG shows a large average lift of +27.23 points over dense retrieval, compared to only +0.47 on single-hop benchmarks (NQ, PopQA, TriviaQA) — strong confirmation that graph structure earns its cost specifically on multi-hop tasks, not general QA ([arxiv.org/2604.09666](https://arxiv.org/html/2604.09666v1)). The same analysis found a striking gap between retrieval and reasoning: in 77–91% of cases the gold answer is actually present in the retrieved context, yet final accuracy is only 35–78% — meaning 73–84% of errors are reasoning failures downstream of retrieval, not retrieval failures themselves. This cautions against assuming a retrieval upgrade (e.g., adding a graph) alone will fix accuracy problems.

### Enterprise / entity-dense benchmarks
Diffbot's KG-LM benchmark found GraphRAG at 56.2% accuracy vs. vector-only RAG at 16.7% (a 3.4x gap) on enterprise KPI queries; a 2025 FalkorDB evaluation reported 90%+ on schema-bound queries. On entity-dense queries specifically, vector RAG accuracy collapses to 0% once more than 5 entities are involved, while GraphRAG stays stable through 10+ entities — the sharpest documented case for graph structure paying off ([falkordb.com](https://www.falkordb.com/blog/graphrag-accuracy-diffbot-falkordb/)).

### Standard evaluation metrics
Beyond task-specific benchmarks, the field converges on a common metric set: accuracy/F1, faithfulness (is the answer grounded in retrieved context), context recall/precision, and latency at p50/p95/p99 ([braintrust.dev](https://www.braintrust.dev/articles/rag-evaluation-metrics)). Hierarchical/dense-structure approaches (RAPTOR, HippoRAG) exceed 72% on GraphRAG-Bench overall, though math, programming, and ethics-reasoning question types remain hard for every approach tested ([emergentmind.com](https://www.emergentmind.com/topics/graphrag-bench)).

### Caveats
The paper "When to Use Graphs in RAG" is an important counterweight: it finds GraphRAG frequently *underperforms* vanilla RAG on real-world tasks, and argues that many benchmarks showing GraphRAG wins are artificial — rule-constructed questions over short corpora that favor graph structure by design ([arxiv.org/2506.05690](https://arxiv.org/abs/2506.05690)). The same analysis shows agentic dense RAG narrows the multi-hop gap to +26.59 (from the +27.23 above), and that GraphRAG's latency (averaging 7.37–9.03s) and infrastructure cost are commonly underreported in commercial marketing claims.

---

## How the pieces fit together

The theory in the companion briefing predicts that graph structure earns its keep on multi-hop, relational, or entity-dense tasks and struggles to justify its cost on single-hop fact lookup — and the benchmark data in Section 3 bears this out almost exactly (+27.23 multi-hop lift vs. +0.47 single-hop; 3.4x accuracy gain on entity-dense enterprise queries but potential *underperformance* on vanilla real-world tasks per the "When to Use Graphs" critique). The tooling landscape in Section 1 reflects this same split: frameworks like LightRAG and LazyGraphRAG exist specifically to claw back the cost side of that trade-off, while FalkorDB and Graphiti optimize the latency side. Section 2's agent-memory use case is the strongest empirical case for graph structure found across all three reports — the temporal-KG-vs-vector gap (63.8% vs. 49.0% on LongMemEval) is wider than anything seen in document-corpus GraphRAG benchmarks, likely because tracking an evolving, contradiction-prone conversation benefits even more from explicit relational/temporal structure than static-document QA does. The throughline for practitioners: match the tool to the task complexity level from the briefing's complexity matrix, expect real latency and engineering cost wherever a graph is added, and treat vendor-reported benchmark wins (Zep, FalkorDB, Microsoft GraphRAG) as directionally useful but not a substitute for testing against your own workload.

---

## Sources

- Neo4j vs. open-source alternatives — https://arcadedb.com/blog/neo4j-alternatives-in-2026-a-fair-look-at-the-open-source-options/
- FalkorDB vs. Neo4j for AI applications — https://www.falkordb.com/blog/falkordb-vs-neo4j-for-ai-applications/
- Memgraph vs. Neo4j — https://memgraph.com/blog/neo4j-vs-memgraph
- GraphRAG overview and benchmarks — https://www.articsledge.com/post/graphrag-retrieval-augmented-generation
- LLMs to knowledge graphs, production graph systems 2025 — https://medium.com/@claudiubranzan/from-llms-to-knowledge-graphs-building-production-ready-graph-systems-in-2025-2b4aff1ec99a
- Graphiti: knowledge graph memory (Neo4j/Zep) — https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/
- LangChain/LlamaIndex knowledge graph creation — https://memgraph.com/blog/improved-knowledge-graph-creation-langchain-llamaindex
- Zep: temporal knowledge graph architecture (arXiv) — https://arxiv.org/html/2501.13956v1
- Episodic/semantic agent memory (arXiv) — https://arxiv.org/html/2605.17625
- Neo4j Labs: agent memory entity resolution & deduplication — https://neo4j.com/labs/agent-memory/explanation/resolution-deduplication/
- Forgetting-by-design in agent memory (arXiv) — https://arxiv.org/pdf/2602.06052
- Mem0 vs. Zep comparison — https://vectorize.io/articles/mem0-vs-zep
- GraphRAG-Bench (ICLR 2026, arXiv) — https://arxiv.org/abs/2506.02404
- Multi-hop vs. single-hop GraphRAG performance (arXiv) — https://arxiv.org/html/2604.09666v1
- Diffbot/FalkorDB GraphRAG accuracy benchmark — https://www.falkordb.com/blog/graphrag-accuracy-diffbot-falkordb/
- RAG evaluation metrics — https://www.braintrust.dev/articles/rag-evaluation-metrics
- GraphRAG-Bench analysis (Emergent Mind) — https://www.emergentmind.com/topics/graphrag-bench
- "When to Use Graphs in RAG" (arXiv) — https://arxiv.org/abs/2506.05690
