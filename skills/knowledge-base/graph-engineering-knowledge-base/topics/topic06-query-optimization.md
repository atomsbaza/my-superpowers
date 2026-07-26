# Topic 6: Query Optimization

## Core Idea
Optimizing graph queries requires reasoning at four levels simultaneously: reading the query plan (EXPLAIN/PROFILE, DB Hits, lazy vs. eager evaluation), understanding the planner and runtime engines (cost-based planning, Interpreted/Slotted/Pipelined/Parallel runtimes), choosing the correct index type for the predicate shape, and respecting the database's transactional/locking model — including its most severe documented weakness, "Mammoth Transactions."

## Frameworks Introduced
- **EXPLAIN vs. PROFILE**: the two primary Cypher plan-inspection commands.
  - `EXPLAIN`: generates the logical plan and estimated row counts without executing the query — zero database hits, used to verify index usage before running anything.
  - `PROFILE`: executes the physical plan and records real performance metrics — actual rows, memory, and **DB Hits** (the abstract unit of storage-engine work: reading a property, traversing a relationship). Minimizing DB Hits is the primary tuning goal.
  - How to read a plan: bottom-up — data flows from leaf operators (e.g. `NodeIndexSeek`, finding start anchors) up through unary/binary operators (`Expand(All)`, `Filter`) to the root operator (`ProduceResults`).
- **Lazy vs. Eager Evaluation**: most Cypher operators are lazy, piping rows to the next step immediately. Aggregation (`count()`, `collect()`) or unindexed `ORDER BY` force eager evaluation, which must buffer all upstream rows before producing output — a memory barrier with high heap cost.
- **Cost-Based Query Planner**: Neo4j assigns a cost to alternative plans using database statistics (label counts, relationship counts, index selectivity tracked in the count store) and picks the cheapest.
- **Execution Runtimes**: Interpreted (nested iterator tree, one record at a time) → Slotted (memory-slot allocation, faster/leaner) → Pipelined/Compiled (fused operators, default for supported queries in Enterprise Edition) → Parallel (distributes pipeline execution across worker threads).
  - When to use: generally let the planner choose; understand the hierarchy to explain unexpected performance differences between similar-looking queries.

## Key Concepts
- **Index Types (Search-Performance — used automatically by the planner)**:
  - *Range Indexes*: the default; optimized for equality, inequality, sorting; can be composite across multiple properties.
  - *Text Indexes*: trigram-based (breaking strings into 3-character chunks), making substring `CONTAINS`/`ENDS WITH`/`STARTS WITH` fast without full scans.
  - *Point Indexes*: spatial querying (distances, bounding boxes).
  - *Token Lookup Indexes*: automatic schema indexes for node labels and relationship types (speeds up `MATCH (n:Person)`).
- **Index Types (Semantic — approximate matching & scoring, not auto-invoked)**:
  - *Full-Text Indexes*: Apache Lucene-powered, tokenized with analyzers (e.g. stop-word removal), returns proximity scores; must be explicitly invoked via `db.index.fulltext.queryNodes()`.
  - *Vector Indexes*: stores high-dimensional float arrays via HNSW (Hierarchical Navigable Small World) graphs; k-NN via cosine/Euclidean distance; queried via the `SEARCH` clause. Modern hybrid-search architectures fuse full-text, vector, and standard graph traversal for superior retrieval context.
- **Read Committed Isolation**: Neo4j's default transaction isolation level — reads are unblocked, but writes use pessimistic locking (exclusive locks on nodes/relationships being modified).
- **Deadlocks**: because modifying a relationship requires locking both its source and target nodes, highly concurrent writes to a shared node frequently deadlock; the deadlock detector aborts the "victim" transaction and rolls it back.
- **Conditional Update Anomaly**: under Read Committed isolation, a `MATCH` followed by a conditional `SET` (e.g. find-then-decrement a counter) can double-apply under concurrent transactions.
- **Mammoth Transactions**: long-running read/write queries spanning huge portions of the graph (cascading GDPR deletes, community-detection scoring). They hold vast numbers of locks, starving concurrent short transactions — throughput can drop up to 4.7x.

## Mental Models
- **Read plans bottom-up, optimize DB Hits, not wall-clock intuition**: the leaf operators tell you what anchors the query; a high DB Hit count on an intermediate operator, not just total query time, is the actionable signal for where to add an index or restructure the query.
- **Eager operators are memory cliffs, not just "slower"**: an `ORDER BY` without a backing index or a `collect()` doesn't just cost more time — it silently converts a streaming query into a fully-buffered one, which is the difference between constant memory and memory proportional to result-set size.
- **Choosing an index is choosing a predicate shape, not "turning indexing on"**: Range vs. Text vs. Point vs. Full-Text vs. Vector each serve structurally different query predicates; picking the wrong index type means the planner silently falls back to a scan even though "an index exists."
- **The dummy-lock trick is a workaround for a systemic isolation gap, not a best practice to reach for by default**: `SET n._dummy_ = true` before a conditional read-then-write manually forces exclusive locking to avoid the conditional update anomaly — useful, but a sign that the isolation model doesn't natively give you serializable semantics for this pattern.
- **Mammoth Transactions are an unsolved problem, not a tuning target**: the corpus is explicit that current graph databases offer little out-of-the-box support for very large read/write transactions — the practical response is architectural (stop-the-world offline execution, application-level workarounds), not query tuning.

## Anti-patterns
- **Unbounded traversals**: `MATCH (a)-[*]->(b)` without a depth bound can traverse massive portions of the dataset. Fix: bound the pattern, e.g. `[:CHILD*1..5]`.
- **Cartesian products**: matching multiple unconnected node sets without aggregating generates pairwise cross-products. Fix: aggregate with `COLLECT()`.
- **Literal values instead of parameters**: hardcoding `{name: 'Alice'}` prevents plan caching (Neo4j must re-parse the AST every time). Fix: use parameters (`{name: $actorName}`) so the cached plan is reused.
- **Super-node bottlenecks**: querying through millions-of-connections nodes without directionality/hints/segregation/cloning (see Topic 5).
- **Trusting model-based self-report over PROFILE output**: assuming a query is fast because it "looks simple" instead of measuring actual DB Hits.

## Code Examples
```cypher
// EXPLAIN — logical plan only, zero DB hits, verifies index usage
EXPLAIN MATCH (n:Person {name: $name}) RETURN n

// PROFILE — executes and records actual DB Hits / memory / rows
PROFILE MATCH (n:Person {name: $name}) RETURN n
```
```cypher
// Dummy-lock trick — force deterministic serialization for a conditional update
MATCH (n:Post {id: $id})
SET n._dummy_ = true
WITH n
MATCH (n)-[r:UPVOTED]-(u:User {id: $userId})
SET n.upvotes = n.upvotes - 1
DELETE r
```

## Reference Tables
| Index Type | Category | Best For |
|---|---|---|
| Range | Search-performance (auto) | Equality, inequality, sorting; composable |
| Text (trigram) | Search-performance (auto) | Substring `CONTAINS`/`STARTS WITH`/`ENDS WITH` |
| Point | Search-performance (auto) | Spatial distance/bounding-box queries |
| Token Lookup | Search-performance (auto) | Label/relationship-type matching |
| Full-Text (Lucene) | Semantic (manual invoke) | Proximity-scored text search within content |
| Vector (HNSW) | Semantic (manual invoke) | k-NN similarity search |

| Runtime | Mechanism | Notes |
|---|---|---|
| Interpreted | Nested iterator tree, one record at a time | Baseline |
| Slotted | Memory-slot allocation for streamed records | Faster interpreted |
| Pipelined/Compiled | Fused operator pipelines | Default in Enterprise Edition for supported queries |
| Parallel | Multi-threaded pipeline execution | Highest throughput where applicable |

## Worked Example
A team notices a Cypher query that "looks fine" is timing out under load: `MATCH (u:User)-[:PURCHASED]->(p:Product) WHERE p.category = 'electronics' RETURN u, count(p) ORDER BY count(p) DESC`. Running `PROFILE` shows the `Filter` operator on `p.category` has a huge DB Hit count relative to rows returned — no index is backing `Product.category`, so it's a full scan. They add a Range index on `Product.category`; `EXPLAIN` now shows a `NodeIndexSeek` leaf operator instead of an `AllNodesScan`. Separately, `PROFILE` reveals the `count(p)`/`ORDER BY` combination forces eager evaluation — the entire result set is buffered before sorting, which is fine at current scale but flagged as a future memory risk if the purchase volume grows an order of magnitude, at which point they'd consider paginating or pre-aggregating instead.

## Key Takeaways
1. `EXPLAIN` (free, no execution) and `PROFILE` (executes, gives real DB Hits) are complementary — use EXPLAIN to verify plan shape before running, PROFILE to find the actual bottleneck.
2. Eager operators (aggregation, unindexed sort) are memory-scaling risks, not just slower steps — recognize them in a plan by the buffering behavior they force.
3. Index selection must match predicate shape: Range for equality/sorting, Text/trigram for substring matching, Point for spatial, Full-Text/Vector for semantic — picking the wrong type silently degrades to a scan.
4. Neo4j's Read Committed isolation plus pessimistic write locking makes deadlocks and the conditional update anomaly real, addressable risks in concurrent-write workloads — the dummy-lock trick is the documented (if inelegant) fix for the latter.
5. Mammoth Transactions are an acknowledged, largely unsolved weakness of current graph database transactional models — plan around them architecturally (offline execution, application-level chunking), don't expect a query-tuning fix.

## Connects To
- **Topic 5 (Graph DB Design Patterns)**: super-node mitigation strategies and the `USING JOIN ON` hint developed further here as query-tuning mechanics.
- **Topic 7 (Distributed Graph Processing)**: the OLTP/OLAP distinction — this topic covers OLTP query tuning; Topic 7 covers the OLAP alternative for whole-graph analytics that would otherwise become a Mammoth Transaction.
- **Topic 9 (GraphRAG)**: Vector Indexes and hybrid search (full-text + vector + graph traversal) as the retrieval mechanism underlying GraphRAG systems.
