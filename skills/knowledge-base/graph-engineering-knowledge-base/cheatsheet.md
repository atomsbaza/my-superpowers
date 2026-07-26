# Graph Engineering Cheatsheet — Practitioner Judgment

## Decision Rules — Graph Data Engineering

| When... | Do... | Because... |
|---|---|---|
| You need formal inference / domain logic reasoning | Use RDF + OWL, query with SPARQL | OWL's open-world assumption lets you infer new knowledge; property graphs have no formal reasoning layer |
| You need fast, metadata-rich traversal and analytics | Use a Property Graph, query with Cypher/Gremlin | Nodes and edges natively hold properties; no reasoning overhead |
| You need to validate data completeness/structure | Use SHACL (closed-world) | Missing = invalid, not "unknown" — the right assumption for validation |
| A fact needs a confidence score or provenance attached | Use RDF 1.2 reification (Holons) | Lets metadata attach to a specific triple without breaking global graph cooperation |
| Modeling a hierarchy (org chart, folders, categories) | Tree Pattern, bounded depth (`*1..5`) | Predictable performance; prevents runaway traversal |
| Modeling RBAC / permissions | Access Control Pattern | Traversal beats multi-join ACL tables |
| Modeling event timelines / logs | Time-Tree Pattern | Fast range scans via time partitioning |
| Need an audit trail / compliance history | Bitemporal Versioning with a `Status` property | Neo4j can't `MERGE` on `NULL`; `Status` gives deterministic merging |
| A relationship's attributes change over time | Relationship Versioning (close old edge, create new) | Preserves history; current-state queries stay index-friendly |
| Feeding graph data into an ML pipeline with historical events | Temporal CC Forest (forward-only edges) | Prevents future leakage into training data |
| Tempted to fully connect every node sharing a trait | Use Linear Path Projection instead | Fully connecting = O(degree²) Clique Explosion; chaining = O(degree) |
| A node has millions of connections (super-node) | Directionality, `USING JOIN ON`, type segregation, cloning, sampling, or Lucene indexing | Six distinct mitigations for six distinct bottleneck shapes — pick the one matching your bottleneck |
| Need whole-graph batch analytics (PageRank, global WCC) | Spark GraphFrames/GraphX, not a graph database | Graph DBs risk Mammoth Transactions on whole-graph workloads |
| Need real-time, single-request local traversal | A graph database (Neo4j), not a processing engine | Index-free adjacency gives constant-time traversal; Spark is batch-oriented |
| LLM is extracting triples from unstructured text | Ontology-guided extraction + SHACL post-hoc validation | Prompt-level instruction alone doesn't catch Entity Flattening |
| Choosing an index for a query predicate | Match index type to predicate shape (Range/Text/Point/Full-Text/Vector) | Wrong index type silently falls back to a scan |
| A query has heavy aggregation or unindexed `ORDER BY` | Expect eager evaluation and a memory buffer | Eager operators must buffer all upstream rows before output |

## Decision Rules — Agent Graph Orchestration

| When... | Do... | Because... |
|---|---|---|
| Writing a multi-step agent as "do A, then B, then C" | Check whether each step's output is actually consumed by the next | A degenerate graph (linear chain) often hides parallelizable, non-dependent steps |
| Deciding whether two nodes need an edge | Ask "does data actually move across it?" | An edge that carries no data shouldn't force sequential execution |
| A step is pure data plumbing (combine, flatten, dedupe) | Do it in plain deterministic code, not an agent call | Zero-token coordination; avoids "paying rent on the graph's own wiring" |
| A downstream step needs to see all items in a batch | Use a barrier (`parallel()`) | Genuinely needs cross-item visibility (dedup, aggregate routing, judge panel) |
| A downstream step does NOT need to see the whole batch | Use a streaming `pipeline()`, not a barrier | Avoids idling fast items behind one slow item (Barrier Abuse) |
| Multiple parallel nodes write to the same state key | Annotate the field with a reducer | Default is last-write-wins (the Merge Problem) — silent data loss without one |
| Routing needs to branch based on agent output | Use deterministic code / conditional edges, not LLM judgment | Keeps orchestration reliable and auditable |
| Assigning models to nodes | Cheap/fast model on wide mechanical nodes; frontier model on narrow synthesis/verification nodes | Matches spend to cognitive demand; multi-agent handoffs already cost ~15x a single chat |
| A finding/claim needs to be trusted before acting on it | Route it through a Test Gate or N-skeptic adversarial panel | Model self-report is not evidence; structural rejection is |
| Skeptic panel keeps missing the same class of issue | Use perspective-diverse verification, not more identical skeptics | Identical skeptics share identical blind spots |
| Sweeping for an unknown number of issues (discovery) | Loop-Until-Dry, deduping against everything *seen* | Deduping only against *confirmed* findings causes infinite loops |
| A parallel fan-out has agents that might fail | Null-Tolerant Collection (`.filter(Boolean)`) | Isolates individual failure from the whole run |
| A child sub-workflow spawns its own fan-out | Share the parent's concurrency/token/agent caps | Prevents combinatorial capacity/cost blowup from nesting |
| The task's steps/branching can't be enumerated in advance | Use a dynamic/self-routing graph (LLM writes its own orchestration script) | Static workflows fail on genuinely unpredictable branching |

## Decision Trees

**RDF vs. Property Graph — which model?**
- Need formal domain logic and inference over missing data? → RDF + OWL (SPARQL)
- Need fast metadata-rich traversal for analytics/recommendations/fraud detection? → Property Graph (Cypher/Gremlin)
- Need both? → Layer SKOS/SHACL over RDF for vocabulary + validation, or maintain a property graph fed by an RDF-governed extraction pipeline (see Topic 4, Topic 9)

**Graph database vs. graph processing engine?**
- Question is "explore from this one node outward, right now"? → Graph database (Neo4j) — index-free adjacency
- Question is "compute something over the entire topology at once"? → Processing engine (Spark GraphFrames/GraphX) — batch/OLAP

**Barrier vs. Pipeline?**
- Does the next step need to see every item in the batch at once (dedup, aggregate count, judge comparison)? → Barrier
- Can each item proceed independently through the remaining stages? → Pipeline

**Is this graph orchestration problem a Workflow or a Loop?**
- Is the path known before the run starts? → Workflow
- Are the steps stable across different inputs? → Workflow
- Is the branching bounded and enumerable? → Workflow
- "No" to any of the above? → Agentic Loop (self-routing / dynamic graph generation)

## Trade-off Matrices

| Dimension | RDF Triple Store | Property Graph |
|---|---|---|
| Query language | SPARQL | Cypher / Gremlin |
| Strength | Formal semantic reasoning, inference | Fast traversal, rich node/edge metadata |
| Node/edge attributes | Requires separate literal nodes (unless reified) | Native properties on both nodes and edges |
| Validation model | OWL open-world | (property graphs have no built-in open/closed-world layer; SHACL is typically paired with RDF) |
| Best for | KGE, semantic standards, LLM grounding | Fraud detection, recommendations, RBAC, routing |

| Architecture | Cost | Latency | State Complexity |
|---|---|---|---|
| Pipeline (sequential, no barrier) | Low | High if truly sequential; low idle waste | Low (linear transitions) |
| Barrier (parallel) | High (concurrent tokens) | Low for the batch; idles on slowest worker | High (requires reducers/merging) |

| Verification Pattern | Purpose | Cost |
|---|---|---|
| Test Gate | Objective, mechanical acceptance check | Low (deterministic execution) |
| Adversarial N-skeptics | Reduce false positives from finder bias | High (N extra model calls per finding) |
| Perspective-diverse verification | Avoid shared blind spots | High (N extra calls, but diversified lenses) |
| Judge panel | Score + synthesize best-of-N generative attempts | Very high (N generations + N judgments + synthesis) |
| LLM-as-judge | Real-time gate before irreversible actions | Low-moderate (single extra call) |

## Thresholds & Defaults
- Multi-agent token premium: standard chat ≈ 1x, single-agent loop ≈ 4x, multi-agent system ≈ 15x (Anthropic study) — every agent handoff duplicates/re-establishes context.
- Clique Explosion vs. Linear Path: fully-connected group = O(degree²) edges; chained (Linear Path) = O(degree) edges — always prefer chaining for shared-trait groupings.
- Super-node asymmetry example from the corpus: 80M inbound edges vs. 121K outbound — exploit the low-cardinality direction.
- Mammoth Transaction throughput impact: up to 4.7x drop while short concurrent transactions wait.
- Adversarial verification panel size: typically N=3 skeptics, majority vote required, default to "false" under uncertainty.
- Concurrency caps: workflows commonly cap around the system's core count (e.g. ~16 active agents); hard backstop example: 1,000 agents per run.
- Bounded traversal default discipline: never ship a variable-length pattern (`[:REL*]`) without an explicit upper bound (`[:REL*1..5]`).
- PinSage / Pinterest scale: up to 3 billion nodes; claimed 25% increase in impression rates from GNN-based disambiguation.
- Google Maps Supersegments GNN: 50% reduction in ETA errors.
- Bun runtime Zig→Rust port: months of traditional work compressed to six days via dynamic fan-out + adversarial review + Test Gates.

## Tells & Smells (fast diagnosis)

| Symptom | Name | Fix |
|---|---|---|
| Query slows unpredictably as dataset grows on a shared-trait grouping | Clique Explosion | Linear Path Projection |
| Traversal chokes / write locks contend on one specific node | Super-Node bottleneck | Directionality, `USING JOIN ON`, type segregation, cloning, sampling, or Lucene indexing |
| LLM extracts an entity as a bare string instead of a linked node | Entity Flattening | Ontology-guided extraction + SHACL rejection |
| LLM-generated ontology diagram looks confidently wrong | Hierarchy Hallucination | Expert review before adoption |
| `EXPLAIN` shows `AllNodesScan` where you expected an index seek | Missing/mismatched index | Add the index type matching the predicate shape |
| `PROFILE` shows huge buffering before any output | Eager evaluation (aggregation/unindexed sort) | Add an index backing the sort, or paginate/pre-aggregate |
| Concurrent writes to a shared node keep deadlocking | Read Committed + pessimistic write locks | Restructure writes to reduce shared-node contention; consider the dummy-lock trick for conditional updates |
| One long read/write query stalls all other transactions | Mammoth Transaction | Move to offline/batch execution or a processing engine (Topic 7) |
| Fast items in a batch wait on one slow item unnecessarily | Barrier Abuse | Switch to a streaming `pipeline()` |
| Parallel agent outputs silently disappear from state | The Merge Problem | Add a reducer (`operator.add`, `add_messages`) |
| A discovery loop never terminates | Loop-Until-Dry deduping against confirmed-only | Dedupe against everything *seen*, not just confirmed |
| One agent timeout crashes the whole fan-out | Missing failure isolation | Null-Tolerant Collection (`.filter(Boolean)`) |
| An agent call exists purely to combine/flatten results | "Paying rent on the graph's own wiring" | Move to plain deterministic code |
| Team spends premium-model tokens on wide, mechanical extraction nodes | Flat model selection (no tiering) | Tier: cheap models wide, expensive models narrow/high-stakes |

## Root-Cause Note
Clique Explosion (Topic 2/5/10), Super-Node bottlenecks (Topic 5/6), and Mammoth Transactions (Topic 6) are structurally the same underlying disease across the data-engineering half of this corpus: **treating a many-to-many or high-fan-in relationship as if it were cheap to fully materialize or traverse in one pass.** On the orchestration half, Barrier Abuse, the Merge Problem, and "paying rent on the graph's own wiring" are the same underlying disease: **conflating deterministic coordination with something that needs a barrier or an agent call.** When you see any of these, ask first whether the structure (graph shape or graph topology) is honestly representing the actual dependency, not just whether the query/prompt needs tuning.
