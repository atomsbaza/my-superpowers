---
name: knowledge-graphs-ai-playbook
description: AI-actionable playbook for applying knowledge-graph and RAG techniques to an existing knowledge base
version: "1.0"
date: 2026-07-15
---

# Knowledge Graphs + AI: Executable Playbook

This file is written for an AI agent operating on an existing knowledge base (a
markdown folder, an Obsidian/Logseq vault, a vector store, or a code knowledge
graph). Apply the rules and recipes below mechanically. Do not re-derive theory —
cite the source docs in `## Source Documents` if justification is needed.

## Decision Rules

Evaluate in order. Each rule is a standalone IF/THEN check with a numeric threshold.

1. IF the query is single-hop and factual (one entity, one lookup) AND latency
   matters THEN use vector/dense retrieval only. GraphRAG adds ~2.3x latency
   (avg 7.37-9.03s) for only +0.47 pts average gain on single-hop benchmarks
   (NQ, PopQA, TriviaQA). Building graph structure here is not worth the cost.

2. IF the query chains 2+ entities or documents (e.g. "find X, then find X's Y")
   THEN add or use graph structure. Multi-hop benchmarks (HotpotQA, MuSiQue,
   2WikiMultiHopQA) show +27.23 avg pts lift from GraphRAG over dense retrieval.

3. IF the query references more than 5 distinct entities THEN do not rely on
   vector-only retrieval — accuracy collapses toward 0% past that point.
   GraphRAG stays stable through 10+ entities. Require graph traversal or a
   hybrid retrieval path.

4. IF construction budget or latency budget is constrained THEN prefer a
   relation-free / lazy construction method (LinearRAG, LazyGraphRAG,
   LightRAG) over full Microsoft-GraphRAG-style construction. LazyGraphRAG
   indexing cost is ~0.1% of full GraphRAG; LinearRAG is near-$0 vs. $13.19 per
   1M tokens for standard GraphRAG on NQ-scale corpora.

5. IF the knowledge base tracks facts that change over time (status, roles,
   relationships, ownership) THEN model edges with bi-temporal fields:
   `t_valid`/`t_invalid` (when the fact was true in the world) and
   `t_created`/`t_expired` (when the system learned it). Never delete a
   superseded fact — set `t_invalid`/`t_expired` and insert the new edge. This
   preserves "what did I believe on date X" queries and avoids silent
   overwrite errors.

6. IF the output feeds a high-stakes or regulated decision (healthcare,
   finance, legal, safety) THEN add a symbolic constraint/rule check as a
   post-retrieval gate before the answer is emitted. Neural retrieval alone
   cannot guarantee hard constraints ("never recommend X given contraindication
   Y"); a symbolic verifier layer is required.

7. IF an answer is wrong despite the correct evidence being present in the
   retrieved context THEN the defect is in reasoning/decomposition, not
   retrieval — do not rebuild the index. 73-84% of GraphRAG-Bench errors occur
   even though the gold answer was retrieved 77-91% of the time. Fix the
   agentic loop (query decomposition, verification step) instead.

8. IF the task is contextual summarization over fragmented/scattered sources
   (Level 3 per GraphRAG-Bench) THEN use GraphRAG for its stable connectivity;
   dense RAG alone tends to miss cross-document links ("lost in the middle").

9. IF the task requires inference beyond retrieved content, or creative
   synthesis under hard constraints (Level 4) THEN combine graph retrieval
   with a neuro-symbolic verification step (generate, then check against a
   rule/ontology layer) rather than trusting raw generation.

10. IF a candidate entity match has mid-range confidence (not a clear exact
    match, not clearly distinct) THEN do NOT auto-merge. Create a `SAME_AS`
    edge flagged for human review. Auto-merging on uncertain matches is a
    common source of silent identity-corruption in a KB.

11. IF the LLM backbone available is large (32B+ parameters) AND the task is
    borderline single/multi-hop THEN lean toward dense RAG — stronger models
    partially compensate for missing explicit structure via implicit
    reasoning, narrowing the graph's advantage.

## Recipes

### Recipe A: Add lightweight graph structure to an existing markdown/vault KB

1. Inventory the KB: list all notes/files, existing wikilinks/backlinks, and
   any existing frontmatter tags.
2. Run an entity-extraction pass over each note: extract named entities
   (people, projects, concepts, dates) using the LLM, one pass per note or
   batch of notes. Store extracted entities with source-note references.
3. Run entity resolution across the extracted set:
   a. Compare candidates via embedding similarity (semantic closeness).
   b. Cross-check with fuzzy string matching (surface-form closeness).
   c. Apply type constraints — only compare entities of compatible types
      (a "person" never merges with a "project").
   d. High-confidence matches (agreement across embedding + fuzzy + type) →
      merge into one canonical entity node.
   e. Mid-confidence matches → create a `SAME_AS` edge, flag for human
      review, do not merge (see Decision Rule 10).
4. Treat existing backlinks/wikilinks between notes as edges by default — they
   are free relational signal already present in the vault; no extraction
   needed for these.
5. Run community/cluster detection over the resulting entity+backlink graph
   (e.g. Leiden algorithm, or a simpler connected-components pass for small
   vaults) to surface topic clusters.
6. For each detected community, generate or update a MOC (Map of Content) note
   summarizing its members — this becomes the "global" query layer.
7. Persist the graph as either: (a) a sidecar file (e.g. `graph.json` with
   nodes/edges) alongside the vault, or (b) inline frontmatter fields
   (`entities:`, `related:`) per note, whichever matches the KB's existing
   conventions. Do not introduce a new storage paradigm without checking what
   the vault already uses.
8. Re-run steps 2-6 incrementally on new/changed notes only — do not rebuild
   the full graph on every update (see Recipe C for the general pattern).

### Recipe B: Decide vector vs. graph vs. hybrid retrieval for a given query

1. Classify the query into a GraphRAG-Bench complexity level:
   - Level 1 (Fact Retrieval): single entity, single fact lookup.
   - Level 2 (Complex Reasoning): chains 2+ knowledge points.
   - Level 3 (Contextual Summarization): synthesizes fragmented data across
     many sources.
   - Level 4 (Creative Generation): requires inference beyond retrieved
     content.
2. Count distinct entities referenced in the query.
3. Route:
   - Level 1 AND ≤5 entities → dense/vector retrieval only (Decision Rule 1).
   - Level 2, or any query with >5 entities → graph traversal or hybrid
     (vector for candidate seeding + graph for expansion) (Decision Rules 2-3).
   - Level 3 → graph retrieval, prefer community/global-summary mode if the
     underlying tool supports it (Decision Rule 8).
   - Level 4 → graph retrieval + symbolic/constraint verification pass
     (Decision Rule 9).
4. If budget-constrained at any level, substitute a lazy/relation-free graph
   method per Decision Rule 4 rather than skipping graph structure entirely.
5. Log the routing decision (level, entity count, chosen path) alongside the
   query — this log is the input to Recipe D's evaluation.

### Recipe C: Maintain the KB as agent memory over time

1. Maintain an episodic buffer: keep the last ~10 raw interaction turns or
   raw notes unconsolidated, for discourse coherence and immediate recall.
2. On a periodic cadence (e.g. end of session, or every N turns), run
   consolidation:
   a. Extract candidate facts from the episodic buffer via LLM extraction.
   b. Run contradiction detection against existing semantic-memory facts.
   c. On contradiction, resolve by temporal precedence: the newer fact
      supersedes, but do not delete the old one — invalidate it
      (`t_invalid`/`t_expired`, per Decision Rule 5) so historical queries
      remain answerable.
   d. Incrementally update the entity/profile graph — do not do a full
      rebuild; touch only affected nodes/edges.
3. Apply entity resolution (Recipe A step 3) to every newly extracted entity
   before writing it into semantic memory.
4. Apply forgetting-by-design, not as an afterthought: define explicit pruning
   rules (e.g. episodic turns older than the buffer window are dropped once
   consolidated; semantic facts below a relevance/recency threshold are
   archived, not silently lost). Forgetting must be a deliberate, logged
   decision, never a silent data loss.
5. Re-run Recipe A's community-detection pass periodically (not per-message)
   to keep MOC/summary nodes current as the KB grows.

### Recipe D: Evaluate whether graph investment paid off

1. Assemble a query set spanning at least Levels 1-3 (per Recipe B) drawn from
   real usage of the KB, not synthetic questions.
2. Run each query against both the plain vector baseline and the graph-enabled
   path.
3. Measure, per query and in aggregate:
   - Retrieval hit rate (is the needed fact/note actually retrieved).
   - Faithfulness (is the generated answer grounded in retrieved content, not
     invented).
   - Multi-hop accuracy specifically for Level 2+ queries.
   - Latency p95 per path.
4. Compare: if the graph path's accuracy gain on Level 2+ queries is small
   relative to its latency/build-cost overhead, and most queries in real usage
   are Level 1, downgrade to vector-only or a lazy-construction method
   (Decision Rule 4) rather than keeping full graph infrastructure live.
5. If errors persist despite high retrieval hit rate, diagnose per Decision
   Rule 7 — treat it as a reasoning-layer defect, not a retrieval-layer one,
   and do not "fix" it by adding more graph structure.
6. Re-run this evaluation whenever the KB's query mix or size changes
   materially — conclusions are workload-specific, not permanent.

## Tool Selection Matrix

| Scenario | Recommended tool/approach | Reason |
|---|---|---|
| General markdown/vault KB, want graph structure, no infra budget | Recipe A (in-file/sidecar graph, no DB) | Zero new infrastructure; backlinks are free edges |
| Need a production graph DB, general purpose | Neo4j | Market leader, most GraphRAG frameworks default to it |
| GraphRAG workload, latency-sensitive | FalkorDB | Up to 496x faster p50, 6x better memory efficiency than Neo4j on graph-retrieval queries |
| Need reference-implementation GraphRAG (community summaries, local/global/DRIFT modes) | Microsoft GraphRAG | Most mature, most benchmarked, ~29.8k stars |
| Cost-sensitive GraphRAG, want ~10x fewer tokens | LightRAG | Dual-level (local+global) retrieval at much lower token cost |
| Very tight indexing budget, near-zero construction cost acceptable | LazyGraphRAG or LinearRAG | Indexing cost ~0.1% of full GraphRAG / near-$0 vs. $13.19 per 1M tokens |
| Conversational agent memory with evolving/contradictory facts | Graphiti (Zep) | Bi-temporal model, P95 300ms, no query-time LLM call, beats GraphRAG on DMR (94.8% vs 93.4%) |
| Production system needing graph+vector+many connectors | Cognee | 30+ data connectors, supports FalkorDB/Neo4j/NetworkX |
| Prototyping only, no production hardening needed | nano-graphrag | Lightweight, minimal, thin docs — fine for a spike, not for production |
| Single-hop factual QA, high volume, cost-sensitive | Plain embeddings / dense vector RAG | GraphRAG adds 2.3x latency for +0.47 pts gain here — not worth it |
| Regulated/high-stakes output | Any of the above + a symbolic rule engine layer | Neural retrieval cannot enforce hard constraints reliably |

Do not pick **Kuzu** for new work (Apple-acquired, archived Oct 2025, no
corporate backing). Get legal review before adopting **Memgraph** (BSL 1.1,
~$25k/yr commercial). Note **Graphiti**'s temporal features are coupled to
Neo4j specifically — there is no backend-agnostic version.

## Anti-Patterns

- Do not build full GraphRAG (entity/relation extraction + community
  detection) for a KB whose queries are overwhelmingly single-hop factual
  lookups — the latency and construction cost are not repaid (Decision Rule 1).
- Do not auto-merge entities on mid-confidence matches. Always route uncertain
  matches to a `SAME_AS` review edge (Decision Rule 10).
- Do not delete or overwrite outdated facts when new information arrives.
  Invalidate them with temporal fields and keep the history queryable
  (Decision Rule 5).
- Do not assume a benchmark win (Microsoft GraphRAG, FalkorDB, Zep — all
  vendor-sourced) transfers directly to your workload. "When to Use Graphs in
  RAG" found GraphRAG frequently *underperforms* vanilla RAG on real-world
  tasks; many benchmark wins come from artificial, rule-constructed corpora
  that favor graph structure by design. Always validate against your own
  queries (Recipe D) before committing to graph infrastructure.
- Do not treat a wrong answer as a retrieval bug by default — check whether
  the gold context was actually retrieved first (Decision Rule 7); most
  GraphRAG-Bench failures (73-84%) are reasoning failures, not retrieval
  failures.
- Do not rebuild the entire graph/index on every KB update. Use incremental
  updates (Recipe A step 8, Recipe C step 2d) — full rebuilds do not scale and
  erase the cost advantage of lazy-construction methods.
- Do not skip the symbolic constraint check for regulated-domain answers just
  because retrieval and generation "look correct" — neural components cannot
  guarantee hard rule compliance (Decision Rule 6).

## Source Documents

- Theory (GraphRAG vs. dense vector RAG vs. KAG, neuro-symbolic convergence,
  agentic search, complexity matrix): `knowledge-graphs-ai-briefing.md`
- Practical (tooling ecosystem, KGs as agent memory, benchmarks/evaluation):
  `knowledge-graphs-ai-practical-supplement.md`
- Structured overview: `knowledge-graphs-ai-mindmap.json`

All three files live alongside this playbook in
`docs/research/knowledge-graphs/`. Re-derive nothing from memory — if a rule
here seems insufficient for a novel situation, consult the briefing or
supplement directly rather than guessing.
