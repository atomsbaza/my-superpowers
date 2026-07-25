# Topic 5: Graph Database Design Patterns

## Core Idea
Graph database design is a catalog of named, reusable patterns (Tree, Access Control, Time-Tree, Bitemporal Versioning, Temporal CC Forest) paired with named anti-patterns and their mitigations (Super-Node fan-out, Clique Explosion). Mastering this catalog — knowing which pattern fits which traversal shape, and which mitigation fits which bottleneck — is the practical core of "traversal-first thinking."

## Frameworks Introduced
- **Tree / Hierarchy Pattern**: models nested structures (org charts, category trees, folder structures) with bounded-depth traversal.
  - How: `MATCH (hq:Department {name: 'HQ'})-[:CHILD*1..5]->(sub) RETURN sub` — the `*1..5` bound is the critical performance discipline, preventing runaway unbounded traversal.
- **Access Control Pattern**: models RBAC, group permissions, and multi-tenancy by connecting users, roles, and resources as nodes.
  - How: `MATCH (u:User {id: 123})-[:HAS_ROLE]->(r:Role)-[:CAN_READ]->(res:Resource) RETURN res` — far cheaper than multi-join relational ACL tables because the traversal is index-free.
- **Time-Tree Pattern**: partitions time hierarchically (Year → Month → Day → Event) for fast range scans.
  - How: `MATCH (y:Year {val: 2025})-[:HAS_MONTH]->(m:Month {val: 7})-[:HAS_DAY]->(d:Day {val: 8})-[:HAS_EVENT]->(e:Event) RETURN e`
- **Bitemporal Versioning**: entities modeled as immutable historical records for domains needing strict audit trails.
  - When to use: any domain requiring "what did we believe was true, as of when" — compliance, finance, audit logs.
  - How: because Neo4j cannot `MERGE` on a `NULL` property (e.g. `EndDate = NULL`), the standard design uses a `Status` property (e.g. `"Active"`/`"Deleted"`) instead, ensuring deterministic merging.
- **Relationship Versioning**: when a relationship's attributes change, close the active relationship (set an end date, mark historical) and create a new one, rather than mutating the existing edge in place.
  - How: `MATCH (a)-->(b) WHERE r.valid_to IS NULL SET r.valid_to = $timestamp, r.status = 'HISTORICAL' CREATE (a)-[:DEPENDS_ON {valid_from: $timestamp, valid_to: NULL, status: 'ACTIVE'}]->(b)` — current-state queries stay fast via simple filters like `WHERE NOT n:Deleted` and `r.Status = 'Active'`.
- **Temporal CC Forest Pattern**: chronological events linked with edges (e.g. `:SAME_CC_AS`) that strictly point forward in time, preventing ML "future leakage" (see Topic 2, Topic 10).

## Key Concepts
- **Super-Node**: an entity with exceptionally high connectivity (a celebrity with millions of followers, a low-cardinality product category). Super-nodes cause traversal bottlenecks and write-lock contention.
- **Fan-Out Mitigation Strategies for Super-Nodes**:
  - *Exploiting relationship directionality*: if connectivity is asymmetric (e.g. 80M inbound edges, 121K outbound), querying the directed outbound path drastically restricts the search space.
  - *Planner join hints*: force the Cypher planner to evaluate independent paths and join at the super-node instead of traversing through it, via `USING JOIN ON`.
  - *Type segregation*: give super-nodes distinct labels/relationship types (e.g. `:Celebrity` + `-[:FAN]->` instead of `:User` + `-[:FOLLOWS]->`) so standard queries automatically bypass them.
  - *Node refactoring (cloning)*: physically clone the super-node into N nodes, distribute inbound relationships via hash-based routing, and link the clones with `-[:SAME_AS]->` to distribute lock contention.
  - *Sampling / edge limits*: cap the number of edges processed per query.
  - *Lucene relationship indexing*: full-text index relationship properties to filter without scanning every edge on the super-node.
- **Clique Explosion vs. Linear Path Projection**: see Topic 2 — the same fix applies here as the general anti-pattern mitigation.

## Mental Models
- **Bound every unbounded traversal on purpose**: `[:CHILD*1..5]` isn't a stylistic choice, it's the difference between predictable and catastrophic query performance — always ask "what's the worst case depth/fan-out here?" before shipping a traversal pattern.
- **Super-nodes are a structural fact of real networks, not a data-quality bug**: celebrities, popular categories, and shared attributes will always create high-degree nodes; the discipline is choosing the right mitigation (directionality, hints, segregation, cloning, sampling, indexing) for the specific bottleneck, not pretending they won't occur.
- **Versioning is append, not mutate**: both Bitemporal Versioning and Relationship Versioning share the same underlying move — close the old record/edge, open a new one — because graph databases (and Neo4j specifically) handle deterministic merging and audit trails far better with immutable historical records than with in-place mutation.

## Anti-patterns
- **Unbounded traversal**: omitting a depth bound on variable-length paths (`[:CHILD*]` instead of `[:CHILD*1..5]`), risking runaway execution over large graphs.
- **Super-node blind spots**: querying through a high-degree node without any of the six mitigation strategies, causing traversal bottlenecks and write-lock contention.
- **Clique Explosion**: see Topic 2 — connecting every node in a shared-trait group to every other node instead of chaining them.
- **`NULL`-based "current record" merging**: attempting to `MERGE` on a `NULL` end-date property in Neo4j, which fails deterministically; use a `Status` property instead.

## Code Examples
```cypher
// Planner join hint to route around a super-node
MATCH (me:User)-[:FRIENDS_WITH]->(f:User)-[:FOLLOWS]->(a:Artist)
MATCH (me)-[:FOLLOWS]->(a)
USING JOIN ON a
RETURN f
```
```cypher
// Relationship versioning — close old edge, open new one
MATCH (a)-->(b)
WHERE r.valid_to IS NULL
SET r.valid_to = $timestamp, r.status = 'HISTORICAL'
CREATE (a)-[:DEPENDS_ON {valid_from: $timestamp, valid_to: NULL, status: 'ACTIVE'}]->(b)
```

## Reference Tables
| Pattern | Problem It Solves | Key Discipline |
|---|---|---|
| Tree | Hierarchies, folder/org structures | Bound traversal depth |
| Access Control | RBAC, multi-tenancy | Traverse instead of multi-join ACL tables |
| Time-Tree | Event timelines, log trails | Hierarchical time partitioning |
| Bitemporal Versioning | Audit trails, compliance | `Status` property, not `NULL` |
| Relationship Versioning | Changing edge attributes over time | Close old edge, create new one |
| Temporal CC Forest | ML future-leakage prevention | Strictly forward-pointing edges |

| Super-Node Mitigation | Mechanism |
|---|---|
| Directionality exploitation | Query the low-cardinality direction |
| Planner join hints (`USING JOIN ON`) | Force independent-path evaluation, join at the super-node |
| Type segregation | Distinct labels/relationship types bypass default queries |
| Node cloning | Distribute inbound edges via hash routing across N clones |
| Sampling / edge limits | Cap edges processed per query |
| Lucene relationship indexing | Full-text filter without scanning all edges |

## Worked Example
A social platform models a celebrity account with 80 million followers as a `User` node like any other. Standard friend-of-friend queries that touch this node (`MATCH (me)-[:FOLLOWS]->(a)-[:FOLLOWS]->(fof)`) grind to a halt because the planner must expand millions of edges at the celebrity node. The team applies two mitigations together: first, type segregation — the celebrity's node is relabeled `:Celebrity` and its inbound edges retyped `-[:FAN]->` instead of `-[:FOLLOWS]->`, so ordinary `:User`-to-`:User` queries automatically skip it. Second, for the queries that do need to reason about celebrity connections, they exploit directionality: since the celebrity node has 80M inbound `FAN` edges but only 121K outbound `FOLLOWS` edges, queries anchor on the outbound direction, keeping the search space small regardless of the inbound fan-in.

## Key Takeaways
1. Bounded-depth traversal is a non-negotiable discipline for any recursive/variable-length pattern, not a nice-to-have.
2. Super-nodes are structurally inevitable in real networks; six named mitigation strategies exist and should be matched to the specific bottleneck (read fan-out, write contention, text filtering).
3. Versioning in graph databases is append-and-close, not in-place mutation — this is true for both entity state (Bitemporal Versioning) and relationship state (Relationship Versioning).
4. Neo4j's inability to `MERGE` on `NULL` properties is a concrete engineering constraint that shapes the standard versioning pattern (`Status` property over nullable end-dates).
5. Clique Explosion and Temporal CC Forest (Topic 2) reappear here as the connective tissue between data modeling and physical database design — the same anti-pattern, the same fix, at every layer.

## Connects To
- **Topic 2 (Graph Data Modeling)**: the foundational Tree, Tagged, Access Control, Time-Tree, and Temporal CC Forest patterns this topic builds on directly.
- **Topic 6 (Query Optimization)**: the `USING JOIN ON` planner hint and super-node bottlenecks here are developed further as query-tuning concerns.
- **Topic 10 (Graph ML and GNNs)**: Temporal CC Forests recur as the ML feature-engineering mechanism for preventing future leakage.
