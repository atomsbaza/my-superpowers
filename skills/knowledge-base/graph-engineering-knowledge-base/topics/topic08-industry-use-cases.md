# Topic 8: Industry Use Cases

## Core Idea
Across fraud detection, recommendation systems, and Customer-360/entity resolution, the common structural move is the same: shift the "unit of analysis" from the isolated record (a transaction, a click, a permission entry) to the interconnected network topology, then run graph-native analytics (structural pattern detection, GNN-based recommendation, entity resolution algorithms) that would be prohibitively expensive or simply invisible in a relational model.

## Frameworks Introduced
- **Fraud Detection and AML (Anti-Money Laundering)**: modeled in graph databases (Neo4j, TigerGraph) by making users/businesses/accounts nodes and transactions/shared attributes edges — shifting analysis from isolated transactions to network topology.
  - When to use: any domain where illicit activity manifests as a *pattern* across multiple entities rather than a property of any single record.
  - Key analytical patterns: **Smurfing** (identifying large deposits fragmented into smaller, less suspicious ones across the network) and **Circular Flows** (tracking funds round-tripped through multiple accounts to obscure origin).
  - Measurable outcome: topological network signals (vs. isolated rule-based logic) significantly reduce the "95% false positive" problem typical of legacy AML systems.
- **Recommendation Systems — Pinterest PinSage**: models data as a web-scale graph (up to 3 billion nodes) tightly coupling visual content features (Pins) with the structural topology of user interactions.
  - How: PinSage uses Graph Neural Networks and random walks to process recommendations across the graph.
  - Measurable outcome: disambiguating visually similar but contextually different content yields a claimed 25% increase in impression rates.
- **Customer-360 / Entity Resolution (Insurance — Simply Business)**: builds a "360° customer view" graph tracking an individual's complete journey, modeling 500+ disparate data points (backend application data, website clicks, marketing events, purchases, completed forms) as nodes and edges.
  - How: primary analytical workload is Entity Resolution — determining which fragmented data pieces relate to the same real-world entity — using **Node Similarity** (weighted connections determining equality via thresholds) and **Weakly Connected Components** (detecting isolated subgraphs belonging to one customer).
  - Measurable outcome: cleaner, deduplicated, reconciled data enabling faster response to customer actions, better-targeted marketing, and earlier detection/resolution of customer issues.

## Key Concepts
- **Unit-of-Analysis Shift**: the defining move across every use case in this topic — from the isolated record to the network topology surrounding it. This is the practical, applied form of the "traversal-first thinking" mental model from Topic 1/Topic 2.
- **Smurfing** and **Circular Flows**: the two named structural fraud signatures detectable via graph traversal but effectively invisible to record-by-record rule engines.
- **Node Similarity** and **Weakly Connected Components (WCC)**: the two named Neo4j Graph Data Science algorithms doing the heavy lifting in entity resolution — WCC recurs here from Topic 7 as an applied technique, not just a distributed-processing primitive.

## Mental Models
- **Graph value scales with how "hidden" the pattern is in a flat view**: fraud rings, entity duplicates, and content disambiguation all share the property that no single record reveals the pattern — only the shape of connections does. This is the litmus test for whether a use case is a good graph fit: "is the signal in the relationships, not the rows?"
- **Measurable outcomes anchor the business case, not just the technical elegance**: each documented use case pairs a graph technique with a quantified business result (95% false-positive reduction, 25% impression-rate increase) — when pitching graph adoption, lead with the outcome the pattern produces, not the pattern itself.

## Anti-patterns
(omit — this topic catalogs applied use cases rather than named engineering anti-patterns; see Topic 2/Topic 5 for the structural anti-patterns, e.g. Clique Explosion, that these use cases must still avoid at scale)

## Code Examples
(omit — not code-heavy; this topic is an applied-outcomes survey)

## Reference Tables
| Use Case | Graph Modeled As | Key Analytics | Measurable Outcome |
|---|---|---|---|
| Fraud/AML | Users/accounts as nodes, transactions/shared attributes as edges | Smurfing detection, Circular Flow tracking | Reduces the "95% false positive" problem in legacy AML |
| Recommendations (Pinterest) | Pins + user interactions, up to 3B nodes | PinSage (GNN + random walks) | Claimed 25% increase in impression rates |
| Customer-360 (Simply Business) | 500+ data points per customer as nodes/edges | Node Similarity, Weakly Connected Components | Faster response to customer actions; better targeting; earlier issue detection |

## Worked Example
A bank's AML system currently flags transactions using isolated rule thresholds ("flag any single deposit over $10,000"), producing overwhelming false-positive volume because most large legitimate deposits trigger the same rule as a single fragment of a smurfing scheme. Migrating to a graph model, the bank represents accounts as nodes and transactions as edges, then runs pattern-matching specifically for Smurfing (many small deposits from related accounts converging on one destination just under the reporting threshold) and Circular Flows (funds that traverse a loop of accounts back toward their origin). Because these patterns are topological rather than record-level, the same underlying rule-threshold logic that used to flag every large individual transaction now only fires on transactions that are structurally part of a suspicious network shape — directly targeting the "95% false positive" problem the corpus attributes to legacy rule-based AML systems.

## Key Takeaways
1. The common thread across fraud, recommendations, and Customer-360 is the same structural move: shift analysis from the isolated record to the network topology surrounding it.
2. Named structural fraud patterns (Smurfing, Circular Flows) are graph-traversal-detectable and rule-engine-invisible — this is the concrete justification for graph adoption in AML.
3. Entity Resolution in Customer-360 contexts leans on the same Weakly Connected Components algorithm introduced as a distributed-processing primitive in Topic 7 — it is a general-purpose graph technique, not fraud- or recommendation-specific.
4. Every use case in this topic pairs a technique with a quantified business outcome — a discipline worth carrying into any internal graph-adoption pitch (see the `business-impact` skill for the broader framing).
5. Two commonly-cited graph use cases — Uber Eats' recommendation graph and BloodHound-style Active Directory attack-path graphs — are **not present in the underlying research corpus for this skill**; treat any claims about them (including plausible-sounding ones) as needing independent verification, not as sourced from this knowledge base.

## Connects To
- **Topic 2 (Graph Data Modeling)**: the Tagged/Access Control/Tree patterns that would concretely implement several of these use cases (e.g. Access Control Pattern for security modeling).
- **Topic 7 (Distributed Graph Processing)**: Weakly Connected Components as a shared primitive between distributed batch processing and applied entity resolution.
- **Topic 10 (Graph ML and GNNs)**: PinSage's GNN/random-walk mechanics, developed in full as a graph ML technique.
