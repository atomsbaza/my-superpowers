# Topic 2: Graph Data Modeling

## Core Idea
Graph data modeling shifts the architectural focus from structured, isolated tables to interconnected networks, prioritizing relationships between data points. Two dominant models — RDF triple stores and property graphs — serve different purposes (semantic reasoning vs. analytics/traversal), and within property graphs, a family of named design patterns (Tree, Tagged, Access Control, Time-Tree, Temporal CC Forest) and anti-pattern mitigations (Linear Path Projection vs. Clique Explosion) form the practical toolkit for traversal-first design.

## Frameworks Introduced
- **RDF Triple Stores (Knowledge Graphs)**: governed by Semantic Web standards; models data as subject-predicate-object "triples," queried with SPARQL, governed by OWL/SKOS/SHACL (see Topic 3).
  - When to use: domains requiring formal semantic reasoning, inference, and strict domain logic (see Topic 3's decision framework).
  - How: every fact is a triple; RDF 1.2 reification lets metadata (confidence, provenance) attach to a triple itself, producing "Holons."
- **Property Graphs (Labeled Property Graph model)**: optimized for analytics and traversal; queried via Cypher or Gremlin; nodes and edges natively hold key-value properties.
  - When to use: fraud detection, network routing, recommendation engines — anywhere rich per-node/per-edge metadata and fast traversal matter more than formal inference.
  - How: nodes have an identifier, a label (role, e.g. `User`), and properties; edges have an identifier, a type, and (unlike RDF) can also natively carry properties (e.g. a flight-route edge holding distance and duration) without needing a separate literal node for every attribute.
- **Directed vs. Undirected Edges**: edges either indicate one-way flow (e.g. "sent an email") or bidirectional/mutual relationships (e.g. "friends with").
  - When to use: choose based on the real-world semantics of the relationship being modeled — directionality affects which traversal directions are cheap (see Topic 5's directionality mitigation for super-nodes).
- **Native vs. Non-Native Graph Storage**: native storage (e.g. Neo4j) uses index-free adjacency and direct memory pointers for constant-time traversal; non-native approaches run graph abstractions atop other storage.
  - When to use non-native: Apache Spark GraphFrames (DataFrame-based, good for distributed bulk algorithms — see Topic 7) or PuppyGraph (query-time projection engine executing graph queries directly over existing SQL warehouses like Iceberg/Snowflake, without a separate storage layer or data duplication) when you don't want to stand up and duplicate data into a dedicated graph database.

## Key Concepts
- **Schema-on-Read vs. Schema-on-Write**: relational databases require rigid schema-on-write (costly migrations — recreating tables, casting types, updating views); graph databases offer flexible schema models closer to schema-on-read, letting relationships and properties be added, modified, or removed dynamically without system-wide downtime. (Note: the source material describes this flexibility directly; "schema-on-read" is the standard industry term applied to it, not a phrase the sources used verbatim.)
- **Tree Pattern**: models organizational hierarchies or folder structures via a bounded-depth relationship traversal.
- **Tagged Pattern**: applies flexible metadata across different entity types without relational join tables.
- **Access Control Pattern**: models RBAC natively; traversing the graph to find a user's accessible resources beats querying multi-join ACL tables.
- **Time-Tree Pattern**: partitions time hierarchically (Year → Month → Day → Event) for fast temporal filtering and range scans.
- **Clique Explosion**: the anti-pattern of connecting every node sharing a trait (e.g. a shared IP address) directly to every other node in that group, producing O(degree²) edge complexity and severe performance degradation.
- **Linear Path Projection**: the standard mitigation for clique explosion — chain the related nodes sequentially instead of fully connecting them, reducing complexity to O(degree) while preserving reachability/connectivity for analysis.
- **Temporal CC Forest Pattern**: in ML pipelines, naively connecting historical events risks "future leakage" (a model implicitly seeing the future). The fix is chronological linear chains (e.g. `:SAME_CC_AS` edges) that strictly point forward in time, so a model only ever sees graph state as it existed at a given timestamp.

## Mental Models
- **Traversal-first thinking**: design the graph around the paths and queries you need to walk efficiently, not around normalized tabular structure — the query pattern should drive the model, not the other way around.
- **The relationship is the payload, not the join key**: in property graphs, an edge itself can carry rich data (distance, duration, weight, confidence); this is a structural inversion of the relational mindset where a relationship is just a foreign key with no attributes of its own.
- **Pick RDF vs. property graph by what you need to prove, not by habit**: RDF/SPARQL when you need formal inference and interoperable semantics; property graphs/Cypher when you need fast, metadata-rich traversal and analytics (full decision framework in Topic 3 and cheatsheet.md).
- **Fully-connected is a trap, not a feature**: the instinct to directly link every node sharing a trait feels natural but is the single most common structural anti-pattern in graph modeling (clique explosion); chaining beats meshing whenever reachability, not pairwise adjacency, is the actual requirement.

## Anti-patterns
- **Clique Explosion**: directly connecting every node in a shared-trait group to every other node, causing O(degree²) edge growth and severe query/memory degradation. Fix: Linear Path Projection (O(degree)).
- **Ignoring schema-on-read flexibility and over-normalizing**: importing relational normalization habits into a graph model defeats the point of native property storage on nodes/edges.
- **Naive historical linking causing future leakage**: connecting events without a forward-only temporal constraint lets ML pipelines "see the future." Fix: Temporal CC Forest pattern with strictly forward-pointing edges.

## Code Examples
```cypher
// Tree Pattern — bounded-depth hierarchy traversal
MATCH (hq:Department {name: 'HQ'})-[:CHILD*1..5]->(sub)
RETURN sub
```
```cypher
// Tagged Pattern — flexible metadata without join tables
MATCH (t:Tag {name: 'Java'})<-[:TAGGED]-(p:Post)
RETURN p
```

## Reference Tables
| Model | Query Language | Optimized For | Governing Standards |
|---|---|---|---|
| RDF Triple Store | SPARQL | Semantic reasoning, inference | OWL, SKOS, SHACL |
| Property Graph | Cypher / Gremlin | Analytics, traversal | (schema-flexible, no formal standard body) |

| Storage Architecture | Mechanism | Best For |
|---|---|---|
| Native (e.g. Neo4j) | Index-free adjacency, direct memory pointers | Fast local/operational traversal |
| Non-native: Spark GraphFrames | DataFrame abstraction, bulk-synchronous messaging | Distributed batch algorithms |
| Non-native: PuppyGraph | Query-time projection over existing SQL warehouses | Avoiding data duplication / new storage layer |

## Worked Example
A logistics company wants to model its delivery network. Using a property graph: `Warehouse` and `DeliveryHub` nodes carry properties (capacity, region); `ROUTE` edges between them carry properties directly (distance, average duration, cost) — no separate "distance" node or join table needed. To model the org chart of hub managers, they use the Tree Pattern with a bounded-depth traversal (`[:MANAGES*1..4]`) so a query can never runaway-traverse an unexpectedly deep or cyclic structure. To track shipment events over time, they use a Time-Tree (Year→Month→Day→Shipment) so "all shipments delayed on 2026-07-20" is an indexed range scan, not a full table scan.

When they later want to flag shipments that share a common risk factor (e.g. same customs broker under investigation), the naive approach — connecting every shipment that used that broker directly to every other such shipment — would clique-explode as the broker's volume grows. Instead they chain the shipments sequentially with a Linear Path (`:SAME_BROKER_AS`), preserving the ability to find "all shipments connected to this one via the broker" (a graph traversal / connected-components query) without the O(degree²) blowup.

## Key Takeaways
1. RDF and property graphs solve different problems — choose based on whether you need formal semantic inference (RDF) or fast, metadata-rich traversal (property graph).
2. Property graphs let both nodes *and* edges carry properties natively — a structural advantage over RDF's triple-only model, at the cost of RDF's formal reasoning guarantees.
3. Schema-on-read flexibility is a real architectural advantage of graph databases over relational schema-on-write, not just marketing language.
4. Named design patterns (Tree, Tagged, Access Control, Time-Tree) are the working vocabulary for traversal-first modeling — know them before inventing bespoke structures.
5. Clique Explosion is the single most important anti-pattern to recognize early; Linear Path Projection is its standard, low-cost fix.
6. Temporal correctness (Temporal CC Forest, forward-only edges) is not optional in ML-feeding graphs — it is the mechanism that prevents future leakage from corrupting model training.

## Connects To
- **Topic 3 (Ontologies and Semantic Standards)**: the deeper mechanics of RDF, OWL, SKOS, SHACL, and reification/Holons referenced here at a summary level.
- **Topic 5 (Graph DB Design Patterns)**: the full pattern catalog (including super-node mitigations) that builds directly on the Tree/Tagged/Access Control/Time-Tree/Temporal CC Forest patterns introduced here.
- **Topic 7 (Distributed Graph Processing)**: GraphFrames as a non-native storage/processing approach, developed in depth.
- **Topic 10 (Graph ML and GNNs)**: the Temporal CC Forest and Clique Explosion mitigations recur directly as ML feature-engineering concerns.
