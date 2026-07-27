# Topic 7: Distributed Graph Processing

## Core Idea
Distributed graph processing (Spark GraphX/GraphFrames) and native graph databases (Neo4j) solve fundamentally different problems and are not substitutes for each other: processing engines are for batch, whole-graph analytical computation (OLAP-style), while graph databases are for operational, real-time, local traversal (OLTP-style). Within Spark, GraphFrames (DataFrame-based) has succeeded GraphX (RDD-based) as the practical default because of its native Python support and declarative Motif-finding API.

## Frameworks Introduced
- **Apache Spark GraphX (RDD-based)**: optimized for batch iterative analytics.
  - How: partitions graphs using a **Vertex-cut** approach, letting high-degree vertices (super-nodes) span multiple machines to reduce network communication overhead; uses a **Triplet View** to logically join vertex and edge attributes.
  - Limitation: remains an "alpha" component and critically lacks first-class Python bindings — significant friction for PySpark-centric teams.
- **Apache Spark GraphFrames (DataFrame-based)**: the modern successor, built on Spark DataFrames with native APIs across Python, Scala, and Java.
  - When to use: any Spark-based distributed graph analytics workload, especially where Python is the primary language — GraphFrames integrates seamlessly into PySpark pipelines where GraphX does not.
  - How: installed as an external package (`--packages` option); a graph is instantiated from two DataFrames — `vertices` (unique identifiers) and `edges` (must contain `src`, `dst`, plus relationship attributes).
- **Motif Finding**: GraphFrames' declarative pattern-matching API for finding structural patterns (triangles, sequential chains) via a domain-specific language, replacing complex lower-level coding.
- **Pregel API / Bulk-Synchronous Parallel Messaging**: for complex iterative algorithms, Spark graph processing coordinates distributed nodes through discrete "super-steps" — all active elements process messages simultaneously and must finish before the next super-step begins, inspired by Google's Pregel system.

## Key Concepts
- **Built-in GraphFrames Algorithms**: PageRank (node importance/influence), Triangle Counting (tightly-knit clusters/cliques), Weakly Connected Components / WCC (partitions the graph into disjoint, unreachable subgraphs — enables "parallelism for free" by letting engineers process distinct components in isolation, e.g. for building Temporal CC Forests, see Topic 2/Topic 10).
- **Think-Like-a-Vertex vs. Think-Like-a-Graph** *(framing terms not present verbatim in the source corpus, used here to organize its content — treat as standard distributed-graph-processing vocabulary applied to the corpus's Pregel and Motif material, and verify independently if precision matters)*: Pregel-style processing has developers write logic from a single node's perspective (receive messages from incoming edges, update state, broadcast to outgoing edges); Motif finding instead lets engineers declare an entire topological pattern to match across the network at once, leaving the SQL optimizer to determine execution.
- **OLTP vs. OLAP for Graphs**: graph databases (Neo4j) serve OLTP-style workloads — operational storage, fast local traversals, real-time transactions, via index-free adjacency and constant-time traversal. Processing engines (GraphX/GraphFrames) serve OLAP-style workloads — batch iterative analytics and global algorithmic computation over the entire dataset at once.

## Mental Models
- **Ask "local neighborhood or whole graph?" before choosing a tool**: if the question is "explore from this specific starting node outward" (recommendation for one user, RBAC check for one request, shortest path between two nodes), reach for a graph database. If the question is "compute something over the entire topology at once" (PageRank across a billion-node network, global connected components, training an ML model on a full snapshot), reach for a distributed processing engine.
- **GraphX's RDD lineage is also its Python tax**: GraphX's partitioning sophistication (vertex-cut, triplet view) doesn't change the practical fact that it lacks first-class Python bindings — for PySpark-centric teams, this single limitation often decides the GraphFrames-vs-GraphX question before any algorithmic consideration does.
- **WCC as a pre-processing step, not just an algorithm**: running Weakly Connected Components isn't only for finding "the answer" (disjoint subgraphs) — it's frequently the first step in a larger pipeline, because once components are isolated, everything downstream can be processed in parallel independently, per component, for free.
- **Bulk-synchronous super-steps trade latency for correctness guarantees**: Pregel's barrier-per-superstep model (every node must finish before the next step begins) is deliberately conservative — it sacrifices the ability to let fast nodes race ahead, in exchange for a provably correct, deterministic iterative computation. This exact trade-off reappears in agent orchestration barriers (Topic 12).

## Anti-patterns
- **Choosing GraphX for a PySpark-first team without accounting for its Python binding gap**: leads to significant friction that a DataFrame-based GraphFrames approach avoids.
- **Using a graph database for whole-graph batch analytics**: forcing a Neo4j instance to compute global PageRank or full-graph community detection is the kind of workload that produces "Mammoth Transactions" (see Topic 6) — the wrong tool for the job.
- **Using a distributed processing engine for real-time, single-request traversal**: the batch/iterative nature of Spark graph processing is a poor fit for low-latency, per-request lookups that a native graph database's index-free adjacency handles natively.

## Code Examples
(omit — the source material describes the GraphFrames vertices/edges DataFrame API and `--packages` installation at a conceptual level without a reconstructable end-to-end code sample)

## Reference Tables
| Dimension | GraphX (RDD-based) | GraphFrames (DataFrame-based) |
|---|---|---|
| Data model | RDD | DataFrame |
| Python support | No first-class bindings | Native Python/Scala/Java |
| Partitioning | Vertex-cut | (DataFrame-native, not separately detailed) |
| Pattern matching | Triplet View (programmatic) | Motif Finding (declarative DSL) |
| Status | "Alpha" component | Modern successor, active use |

| Workload | Use | Why |
|---|---|---|
| Whole-graph analytics (PageRank, global WCC, ML training on full snapshot) | Spark GraphX/GraphFrames | Built for batch iterative computation across the entire dataset |
| Local traversal, real-time recommendation, RBAC check, shortest path | Graph database (Neo4j) | Index-free adjacency gives constant-time traversal from a specific starting node |

## Worked Example
A data platform team needs two things: (1) a nightly job computing PageRank across their entire 500-million-node citation network to rank papers by influence, and (2) a live API endpoint that, given a user ID, returns that user's accessible resources via an RBAC traversal in under 50ms. For (1), they use GraphFrames in PySpark — the DataFrame-native API fits their existing Python pipeline, and PageRank is a built-in algorithm running as a batch job with no latency requirement. For (2), GraphFrames would be entirely wrong — spinning up a Spark job per API request is far too slow. Instead they use Neo4j: the RBAC graph (Topic 5's Access Control Pattern) lives in a native graph database where index-free adjacency gives constant-time traversal from the specific user node outward, satisfying the real-time latency requirement.

## Key Takeaways
1. GraphFrames has effectively superseded GraphX for new work, primarily because of native Python support and the declarative Motif-finding API — not because GraphX's underlying techniques (vertex-cut partitioning) are inferior.
2. The OLTP/OLAP split for graphs maps directly onto graph databases vs. processing engines — this is the single most important tool-selection question in distributed graph engineering.
3. Weakly Connected Components is as much a parallelization enabler (isolate-then-process-independently) as it is an analytical result in its own right.
4. Pregel's bulk-synchronous super-step model is a deliberate latency-for-correctness trade-off that recurs conceptually in agent-orchestration barrier synchronization (Topic 12).
5. Forcing whole-graph analytics onto an operational graph database (rather than a processing engine) is a direct path to the Mammoth Transaction problem (Topic 6).

## Connects To
- **Topic 2 (Graph Data Modeling)**: non-native graph storage (GraphFrames as one option) introduced there, developed in full here.
- **Topic 6 (Query Optimization)**: the OLTP-side counterpart — why Mammoth Transactions happen when whole-graph workloads are forced onto an OLTP graph database instead of routed to a processing engine.
- **Topic 12 (Orchestration Topologies)**: barrier synchronization in agent graphs is the direct conceptual descendant of Pregel's bulk-synchronous super-step model introduced here.
