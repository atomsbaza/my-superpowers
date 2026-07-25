# Graph Engineering Patterns Reference

## PART A: Graph Data Patterns

### Tree Pattern
**Problem**: modeling nested structures — organizational hierarchies, category systems, folder structures — where naive recursive traversal risks unbounded execution.
**Solution**: model the hierarchy as `[:CHILD]` (or similar) relationships and always bound the traversal depth, e.g. `MATCH (hq:Department {name: 'HQ'})-[:CHILD*1..5]->(sub) RETURN sub`.
**When to use**: any parent/child, category/subcategory, or containment hierarchy.

### Tagged Pattern
**Problem**: applying flexible metadata across many different entity types without cumbersome relational join tables.
**Solution**: model tags as their own nodes, connected via a `TAGGED`-style relationship: `MATCH (t:Tag {name: 'Java'})<-[:TAGGED]-(p:Post) RETURN p`.
**When to use**: many-to-many categorical metadata (skills, topics, labels) shared across heterogeneous entity types.

### Access Control Pattern
**Problem**: modeling RBAC, group permissions, or multi-tenancy efficiently.
**Solution**: model users, roles, and resources as connected nodes; traverse from a user through role/group nodes to reachable resources: `MATCH (u:User {id: 123})-[:HAS_ROLE]->(r:Role)-[:CAN_READ]->(res:Resource) RETURN res`.
**When to use**: any access-control check that would otherwise require multi-join ACL tables in a relational schema.

### Time-Tree Pattern
**Problem**: fast filtering and range scans over event timelines or log trails.
**Solution**: partition time hierarchically (Year → Month → Day → Event): `MATCH (y:Year {val: 2025})-[:HAS_MONTH]->(m:Month {val: 7})-[:HAS_DAY]->(d:Day {val: 8})-[:HAS_EVENT]->(e:Event) RETURN e`.
**When to use**: temporal event data queried by date range far more often than by other predicates.

### Bitemporal Versioning
**Problem**: strict audit trails where both "what was true" and "when we believed it" must be reconstructable, without relying on nullable end-date properties (which Neo4j cannot `MERGE` on).
**Solution**: model entities as immutable historical records using a `Status` property (`"Active"`, `"Deleted"`) instead of `NULL` end-dates, for deterministic merge behavior.
**When to use**: compliance, finance, or any domain requiring a reconstructable audit history.

### Relationship Versioning
**Problem**: relationship attributes change over time, but you need to preserve the history of prior values.
**Solution**: close the active relationship (set `valid_to`, mark `status: 'HISTORICAL'`) and create a new active relationship, rather than mutating the edge in place.
**When to use**: any edge whose attributes (e.g. a dependency's strength, a subscription's tier) evolve and where history matters.

### Linear Path Projection
**Problem**: entities sharing a common trait (a device fingerprint, an IP address) tempt a "connect everyone to everyone" design, which produces Clique Explosion — O(degree²) edge complexity and severe performance/memory degradation.
**Solution**: project a Linear Path — chain the related nodes sequentially instead of fully connecting them — reducing complexity to O(degree) while preserving reachability and connectivity for downstream algorithms (e.g. Weakly Connected Components).
**When to use**: any shared-trait grouping pattern, especially before it feeds into fraud detection, entity resolution, or ML feature engineering.

### Temporal CC Forest Pattern
**Problem**: naively linking historical events for ML training can cause "future leakage" — a model implicitly seeing network state that didn't exist yet at the time being predicted.
**Solution**: link chronological events with edges (e.g. `:SAME_CC_AS`) that strictly point forward in time, guaranteeing a model only ever accesses the graph's state as it existed at that timestamp.
**When to use**: any ML pipeline training on graph-structured historical/event data.

### Super-Node Mitigation (six variants)
**Problem**: an entity with exceptionally high connectivity (a celebrity, a low-cardinality category) causes traversal bottlenecks and write-lock contention.
**Solution** (pick based on the specific bottleneck):
- *Directionality exploitation* — query the low-cardinality direction when connectivity is asymmetric.
- *Planner join hints* (`USING JOIN ON`) — force independent-path evaluation, joining only at the super-node.
- *Type segregation* — distinct labels/relationship types so default queries bypass the super-node automatically.
- *Node cloning* — split into N nodes, hash-route inbound edges, link clones with `:SAME_AS`.
- *Sampling/edge limits* — cap edges processed per query.
- *Lucene relationship indexing* — full-text index to filter without scanning every edge.
**When to use**: whenever a specific node's degree is orders of magnitude above the graph's typical degree.

## PART B: Agent Orchestration Patterns

### Fan-Out / Fan-In (Diamond Pattern)
**Problem**: a task decomposes into independent slices of work (auditing multiple files, querying multiple sources) that could run concurrently instead of sequentially.
**Solution**: split → dispatch identical agents concurrently via `parallel(thunks)` → merge results at a synthesis node, applying Null-Tolerant Collection (`.filter(Boolean)`) to drop individually-failed agents.
**When to use**: any batch of genuinely independent work items with an eventual synthesis step.

### Streaming Pipeline
**Problem**: forcing independent items through a synchronized barrier makes fast items idle behind slow ones (Barrier Abuse).
**Solution**: use `pipeline(items, ...stages)` to push each item through multiple stages independently, with no inter-stage barrier.
**When to use**: whenever the downstream steps don't need cross-item visibility — the default choice unless a barrier is specifically justified.

### Conditional / Self-Routing Edge
**Problem**: the correct next step depends on a runtime classification of the current state, not a fixed static path.
**Solution**: classify with an agent against a schema, then branch in deterministic code (`if (severity === 'high') {...} else {...}`); in LangGraph, `add_conditional_edges` evaluates a routing function against state.
**When to use**: any workflow where the path genuinely depends on intermediate results — keep the branching decision in code, not buried in an LLM's free-form judgment.

### Diamond Pattern with Model Tiering
**Problem**: uniform model selection wastes money on wide mechanical stages or under-provisions narrow high-stakes stages.
**Solution**: route wide, mechanical fan-out nodes to cheap/fast models; reserve narrow, high-stakes synthesis/merge nodes for premium models.
**When to use**: any fan-out/fan-in topology, as a default cost discipline.

### Reducer-Based State Merge
**Problem**: multiple parallel nodes writing to the same state key silently overwrite each other (last-write-wins, the Merge Problem).
**Solution**: annotate the state field with a reducer function (`operator.add` for list concatenation, `add_messages` for ID-deduplicated chat history) that defines how concurrent writes combine.
**When to use**: any parallel fan-out whose outputs need to accumulate into shared state rather than replace it.

### Verifier-on-Edge / Test Gate
**Problem**: allowing a worker agent's output to flow directly to production/final-output without an objective check risks propagating hallucinations or errors.
**Solution**: place a verifier node directly on the edge between the worker and its consumer; for mechanically-checkable domains, use an executed Test Gate (compiler, linter, test suite) instead of model judgment.
**When to use**: any edge carrying a consequential, hard-to-reverse, or high-stakes claim.

### Adversarial Verification (N-Skeptics)
**Problem**: agents rewarded for finding issues are prone to false positives; a single verifier can share the finder's blind spots or biases.
**Solution**: submit the finding to N (typically 3) independent, context-isolated skeptic agents prompted to refute it, defaulting to "false" under uncertainty; report only on majority vote.
**When to use**: any finding whose false-positive cost is high enough to justify the extra token spend.

### Perspective-Diverse Verification
**Problem**: N identical skeptics can unanimously miss the same class of failure because they share the same analytical blind spot.
**Solution**: assign each verifier a distinct lens (correctness, security, reproducibility) so the panel's coverage is a union of different examinations, not N repetitions of the same one.
**When to use**: complex findings where different failure classes require genuinely different expertise to catch.

### Judge Panel
**Problem**: for complex generative tasks (drafting a plan), picking a single "best" attempt from N candidates discards useful elements from the runners-up.
**Solution**: generate N attempts from different angles in parallel, score them against a rubric via judge agents, then have a synthesizer agent graft the best elements of runners-up onto the winning attempt.
**When to use**: high-value generative outputs (architecture plans, strategy documents) where combining strengths beats picking a single winner.

### Convergence Loop (Loop-Until-Dry)
**Problem**: discovery tasks of unknown size (sweeping a codebase for issues) can't be handled by a static, fixed-iteration plan.
**Solution**: iterate discovery rounds until K consecutive rounds surface nothing new, deduping every round against everything *seen* (confirmed and rejected), not just confirmed findings — the critical detail that prevents infinite loops.
**When to use**: open-ended discovery/sweep tasks where the total number of findings isn't known in advance.

### Null-Tolerant Collection (Failure Isolation)
**Problem**: in a large parallel fan-out, one agent's timeout or hallucination shouldn't crash the entire orchestrator run.
**Solution**: let failed agents resolve to `null`; drop them from the collected results with plain deterministic code (`.filter(Boolean)`) before fan-in synthesis.
**When to use**: any parallel fan-out at meaningful scale (tens to hundreds of concurrent agents).

### Composition Caps (Nested Workflow Governance)
**Problem**: a child sub-workflow spawning its own fan-out inside an already-fanned-out parent risks multiplying concurrency and token cost combinatorially.
**Solution**: the child graph shares the parent's concurrency cap, agent counter, and token budget rather than getting its own independent allotment.
**When to use**: any workflow architecture that allows sub-workflow composition/nesting.

### Dynamic Graph Generation (Self-Routing)
**Problem**: some jobs are too unpredictable to map out as a static workflow in advance.
**Solution**: give the LLM the objective and let it write its own deterministic orchestration script — decomposing the task, choosing fan-out scale, spawning subagents, and creating tailored verification pipelines for that specific run.
**When to use**: per the Workflow-vs-Loop decision framework (cheatsheet.md) — when the path, step stability, and branching can't be determined before the run starts.

## PART C: Knowledge Graph / Grounding Patterns

### Ontology-Guided Extraction
**Problem**: unconstrained LLM extraction from unstructured text produces malformed or inconsistent triples (Entity Flattening, Hierarchy Hallucination).
**Solution**: inject a formal ontology schema (allowed entity/relationship types, domain/range constraints) directly into the extraction prompt as a structured template, then validate every generated triple against SHACL under a closed-world assumption before ingestion.
**When to use**: any LLM-assisted knowledge graph population pipeline.

### Context Graph Construction (GraphRAG Retrieval)
**Problem**: flat vector similarity search can't natively connect facts scattered across many documents into a coherent multi-hop answer.
**Solution**: on each query, traverse the RDF/knowledge graph to dynamically assemble a bespoke, temporary Context Graph tailored to that specific question, providing both grounding and a traceable explanation path.
**When to use**: retrieval-augmented generation where answers depend on relationships between entities, not just semantic similarity of isolated chunks.
