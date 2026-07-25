# Topic 10: Graph ML and GNNs

## Core Idea
Graph Neural Networks learn from interconnected data by combining node attributes with network structure via **Message Passing** — nodes iteratively aggregate information from their local neighborhoods rather than being processed as isolated feature vectors. At web scale, this powers production systems from Pinterest's recommendation engine to Google's weather forecasting and route prediction, but feeding clean, leakage-free graph features into these models requires the same structural discipline (Temporal CC Forests, Linear Path Projection) developed for graph databases in Topics 2 and 5.

## Frameworks Introduced
- **Message Passing**: the core GNN mechanism — nodes iteratively aggregate information/features from immediate local neighbors, building deep structural understanding instead of treating data points in isolation.
- **Graph Convolutional Networks (GCNs)**: a GNN variant using spectral methods (graph Laplacian averaging).
  - Production example: Pinterest's **PinSage**, a web-scale GCN processing up to 3 billion nodes, combining random walks and GNN techniques to fuse visual content features (Pins) with the structural topology of user interactions — yielding a claimed 25% increase in impression rates via improved content disambiguation.
- **Spatial GNN Methods**: **GraphSAGE** (neighborhood sampling) and **GAT** (Graph Attention Networks — learned attention weights prioritizing specific structural connections).
  - When to use: when spectral methods (full-graph Laplacian computation) don't scale to your graph size or update frequency; spatial methods sample or attend over local neighborhoods instead.
- **Encoder-Processor-Decoder Architecture**: used by Google DeepMind's **GraphCast** to dominate global weather forecasting, delivering 10-day forecasts in under a minute.
- **Spatiotemporal Reasoning**: Google Maps applies GNNs to model "Supersegments," reducing ETA errors by 50%.
- **Molecular Engineering GNNs**: systems like **AlphaFold 3** predict protein-ligand interactions in minutes, compressing drug-discovery workflows that previously took years.

## Key Concepts
- **Preventing Future Leakage via Temporal CC Forests**: naively connecting historical data points in an ML pipeline can inadvertently give a model foresight into future events. The fix (introduced in Topic 2/Topic 5) is projecting chronological events with directed edges (e.g. `:SAME_CC_AS`) that strictly point forward in time, guaranteeing a model only ever trains on network state as it existed at that timestamp.
- **Avoiding Clique Explosion in Feature Engineering**: grouping entities by a shared trait (e.g. shared IP address) can create a fully-connected clique with O(degree²) edge complexity and massive memory bloat. The standard mitigation (Topic 2/Topic 5) is Linear Path Projection (O(degree) complexity), preserving reachability/connectivity for ML algorithms without the performance penalty.
- **Pre-computing Components (WCC) for "Parallelism for Free"**: running Weakly Connected Components first to partition the graph into disjoint subgraphs lets engineers isolate and process distinct components concurrently for feature extraction — this WCC-as-enabler mental model recurs from Topic 7 and Topic 8.
- **GNN-LLM Convergence (GraphRAG)**: GNN-learned embeddings are increasingly used to give LLMs structural context, helping disambiguate visually or linguistically similar but contextually different entities during GraphRAG traversals (Topic 9).

## Mental Models
- **Structure is a feature, not just a storage format**: the entire premise of GNNs is that the topology surrounding a node carries predictive signal that a flat feature vector for that node alone cannot capture — this is the ML-specific instantiation of "traversal-first thinking" from Topic 1.
- **Leakage prevention is a graph-modeling problem before it's an ML problem**: the discipline of forward-only temporal edges isn't a special ML technique bolted on afterward — it's the same Temporal CC Forest pattern used for correct graph modeling generally, applied specifically to keep training data honest about what a model could have "known" at prediction time.
- **The same anti-patterns that hurt query performance also hurt ML feature quality**: Clique Explosion degrades both traversal performance (Topic 5) and ML feature engineering (this topic) for the identical structural reason — O(degree²) edge blowup — reinforcing that these are general graph-modeling anti-patterns, not context-specific quirks.
- **Spectral vs. spatial is a scale/update-frequency trade-off, not a strict hierarchy**: GCNs' spectral approach and GraphSAGE/GAT's spatial approaches aren't "better vs. worse," they're suited to different graph sizes and how often the graph structure changes.

## Anti-patterns
- **Future leakage**: naively connecting historical events without a forward-only temporal constraint, letting a model implicitly train on information it wouldn't have had at prediction time. Fix: Temporal CC Forest pattern.
- **Clique explosion in feature graphs**: fully connecting every node sharing a trait for feature-engineering convenience, causing O(degree²) blowup. Fix: Linear Path Projection.
- **Skipping WCC pre-partitioning on large, naturally-disconnected graphs**: processing the whole graph as one unit when it's actually composed of many disjoint components forfeits free parallelism.

## Code Examples
(omit — the source material describes GNN architectures and feature-engineering patterns conceptually without a reconstructable training/inference code sample)

## Reference Tables
| System | GNN Type/Technique | Domain | Documented Outcome |
|---|---|---|---|
| Pinterest PinSage | GCN (spectral) + random walks | Content recommendation | Claimed 25% increase in impression rates |
| Google DeepMind GraphCast | Encoder-Processor-Decoder | Weather forecasting | 10-day forecasts in under a minute |
| Google Maps | Spatiotemporal GNN ("Supersegments") | ETA prediction | 50% reduction in ETA errors |
| AlphaFold 3 | Molecular GNN | Drug discovery | Protein-ligand interaction prediction in minutes vs. years |

| ML Feature-Engineering Risk | Graph-Modeling Fix | Also Prevents |
|---|---|---|
| Future leakage | Temporal CC Forest (forward-only edges) | — |
| Clique explosion | Linear Path Projection | Query performance degradation (Topic 5) |

## Worked Example
A fraud-detection team building a GNN-based transaction-risk model naively links every transaction sharing a device fingerprint into a fully-connected cluster for feature engineering — creating clique explosion (O(degree²) edges) once a popular shared device (e.g. a public kiosk) accumulates thousands of transactions. They refactor to a Linear Path Projection, chaining same-device transactions sequentially instead, cutting edge complexity to O(degree) while preserving the connectivity signal the GNN needs. Separately, they realize their initial training set connected each transaction to *all* other transactions from the same device regardless of timestamp — including transactions that happened after the one being scored, a future-leakage bug that made their offline validation metrics look artificially strong. They fix this by projecting a Temporal CC Forest: device-linked transaction edges strictly point forward in time, so a transaction's feature vector only ever reflects device history that existed before it, matching what the model will actually see in production.

## Key Takeaways
1. Message passing — aggregating neighbor information rather than treating nodes as isolated feature vectors — is the unifying mechanism across every GNN variant covered here.
2. Production-scale GNN systems (PinSage, GraphCast, Google Maps, AlphaFold 3) span recommendation, forecasting, routing, and molecular engineering — this is not a niche technique.
3. Temporal CC Forests and Linear Path Projection are not GNN-specific tricks; they are the general graph-modeling patterns from Topics 2 and 5, applied here to prevent ML-specific failure modes (future leakage, feature-graph clique explosion).
4. WCC pre-partitioning gives "parallelism for free" for feature extraction — reuse this Topic 7/8 technique whenever a large graph is actually composed of disjoint components.
5. GNN-learned embeddings are the structural-context mechanism behind GraphRAG's disambiguation capability (Topic 9) — graph ML and GraphRAG are not separate concerns.

## Connects To
- **Topic 2 (Graph Data Modeling) / Topic 5 (Graph DB Design Patterns)**: Temporal CC Forest and Linear Path Projection, the anti-patterns and fixes this topic directly reuses.
- **Topic 7 (Distributed Graph Processing)**: Weakly Connected Components as the shared pre-partitioning primitive.
- **Topic 8 (Industry Use Cases)**: PinSage's business outcome (25% impression-rate increase), developed at the technique level here.
- **Topic 9 (GraphRAG)**: GNN-learned embeddings as the disambiguation mechanism GraphRAG relies on.
