# Topic 3: Ontologies and Semantic Standards

## Core Idea
Knowledge Graph Engineering (KGE) organizes structured and unstructured data into a machine-readable, logically consistent format by layering three W3C-family standards — OWL (formal logic/domain rules), SKOS (taxonomies/controlled vocabularies), and SHACL (structural validation) — over RDF triples. RDF 1.2's reification mechanism lets metadata attach directly to a fact, producing "Holons": self-contained, locally-meaningful statements that still cooperate inside a larger global graph. This semantic backbone is what lets LLMs be grounded against verifiable facts instead of free-floating text.

## Frameworks Introduced
- **OWL (Web Ontology Language)**: defines formal logic, classes, and property restrictions for a domain — the "zoning law" for what relationships are permitted between entity types.
  - When to use: when you need formal domain logic and the ability to infer new knowledge from existing facts.
  - How: define classes, properties, and restrictions; the reasoner can infer facts not explicitly stated, because OWL operates on an **open-world assumption** — missing information is "unknown," not "false."
- **SKOS (Simple Knowledge Organization System)**: manages taxonomies and controlled vocabularies, distinct from OWL's deep logical rules.
  - When to use: when the problem is conceptual hierarchy and synonym management, not formal inference — e.g. ensuring "AI" and "Artificial Intelligence" resolve to the same concept node, preventing fragmented data.
- **SHACL (Shapes Constraint Language)**: the validation layer; defines "shapes" the data must conform to, rejecting malformed relationships or structural violations before ingestion.
  - When to use: whenever data completeness and structural correctness must be actively enforced, not merely inferred.
  - How: SHACL operates on a **closed-world assumption** — anything not explicitly stated is considered false/invalid. If a `Person` shape requires a `Birthdate` and it's missing, SHACL flags an error; OWL, by contrast, would assume the birthdate exists but is simply not yet known.
- **RDF 1.2 / RDF-star Reification**: allows statements about statements — attaching metadata (confidence score, provenance, source chunk reference) directly to a triple rather than treating the triple as a bare, unqualified fact.
  - When to use: whenever a fact's trustworthiness or origin matters as much as the fact itself (e.g. LLM-extracted facts, facts merged from multiple sources).
  - How: instead of `(Company_A, acquired, Company_B)` as a bare fact, reification lets you attach a confidence score or source chunk to that exact triple, producing a **Holon** — a statement that is simultaneously a complete, independent unit of meaning and a cooperating part of the larger graph.

## Key Concepts
- **The Semantic Stack**: OWL (domain logic) → SKOS (vocabulary/taxonomy) → SHACL (structural validation) — three distinct jobs, often confused as interchangeable, that together govern a knowledge graph's semantic and structural integrity.
- **Open-World Assumption (OWL) vs. Closed-World Assumption (SHACL/CWA)**: OWL treats absence of information as "unknown" (good for inference, bad for completeness checking); SHACL treats absence as "false"/invalid (good for validation, not for inference). *(Note: this open-world/closed-world framing is standard semantic-web terminology used to explain the corpus's OWL/SHACL material; the corpus's own sources describe the two standards' roles but do not spell out the open-world/closed-world contrast in those exact terms.)*
- **Holon**: a self-contained unit of extracted meaning (via RDF 1.2 reification) that acts simultaneously as a complete independent statement and a cooperating part of the global knowledge graph.
- **Ontology-Guided Extraction**: constraining an LLM's extraction pipeline with a formal ontology schema (entity types, relationship types, domain/range constraints) injected directly into the prompt as a structured template, so extraction stays within the graph's defined vocabulary.
- **Entity Flattening**: a documented LLM extraction failure where an entity that should be a typed node (e.g. a manufacturer) is instead recorded as a simple string literal, destroying the relational mapping needed for a coherent graph (developed further in Topic 4).
- **Context Graph**: a temporary, bespoke subgraph built by traversing the RDF knowledge graph specifically to answer one user query — the retrieval mechanism underlying GraphRAG (see Topic 9).

## Mental Models
- **Ontologies are the rules of the world, not just documentation**: OWL/SKOS/SHACL aren't descriptive metadata bolted on after the fact — they are the enforced grammar that determines what the graph is even allowed to say, and that grammar is what makes LLM grounding possible.
- **Open-world for reasoning, closed-world for validation — pick the tool that matches the question you're asking**: "can I infer something new?" is an OWL question; "is this data complete and well-formed?" is a SHACL question. Using the wrong assumption for the wrong purpose produces either false confidence (treating missing SHACL data as merely unknown) or false rejections (treating OWL's open-world inference gaps as hard errors).
- **A Holon is a compromise between autonomy and cooperation**: reification lets a fact carry its own provenance/confidence without losing its place in the shared graph — this is the structural trick that lets a knowledge graph absorb uncertain, LLM-extracted facts without treating every fact as equally authoritative.
- **Grounding, not restriction, is the goal**: the point of ontology-driven design for AI is not to make LLMs less capable but to constrain their creative, sometimes unpredictable output using explicit, verifiable relational facts — turning free-floating generation into traceable traversal.

## Anti-patterns
- **Treating OWL's silence as SHACL's rejection (or vice versa)**: conflating open-world inference gaps with closed-world validation failures produces either graphs that silently tolerate incomplete data (should have been rejected by SHACL) or graphs that reject valid-but-incomplete facts that OWL would have correctly left as "unknown."
- **Skipping the semantic stack for "just SKOS" or "just SHACL"**: using only a taxonomy layer without formal validation (or vice versa) leaves either the vocabulary or the structural integrity of the graph unenforced.
- **Entity Flattening** (see Topic 4 for the full failure mode and mitigation): allowing LLM extraction to bypass ontology constraints, producing string literals where typed entity nodes were required.

## Code Examples
(omit — the source material does not include concrete OWL/SKOS/SHACL syntax examples; see Topic 4 for the JSON-LD/SHACL validation workflow description)

## Reference Tables
| Standard | Governs | Assumption | Failure Mode It Catches |
|---|---|---|---|
| OWL | Domain logic, classes, property restrictions | Open-world (missing = unknown) | Logical inconsistency; enables inference |
| SKOS | Taxonomies, controlled vocabularies | N/A (vocabulary management) | Fragmented synonyms (e.g. "AI" vs. "Artificial Intelligence") |
| SHACL | Structural validation ("shapes") | Closed-world (missing = false/invalid) | Malformed or incomplete triples before ingestion |

## Worked Example
An enterprise building a knowledge graph of its product catalog defines an OWL ontology stating every `Product` must have exactly one `manufacturedBy` relationship to a `Manufacturer` entity (not a string). SKOS is layered on top so that "Mfr.", "Manufacturer", and "Maker" as free-text labels all resolve to the same taxonomic concept. When an LLM extraction pipeline processes a new supplier's PDF spec sheet, it proposes a triple `(Product_X, manufacturedBy, "Acme Corp")` — a string literal, not a linked entity (Entity Flattening, see Topic 4). Before ingestion, a SHACL shape requiring `manufacturedBy` to point to a node of type `Manufacturer` rejects this triple under the closed-world assumption: the shape isn't satisfied, so the fact is invalid, full stop — regardless of what OWL might infer about missing manufacturer data elsewhere in the graph. The extraction pipeline is corrected to first resolve "Acme Corp" to an existing (or newly created, properly typed) `Manufacturer` node before the triple is accepted.

## Key Takeaways
1. OWL, SKOS, and SHACL are not redundant — each governs a distinct concern (logic, vocabulary, structure) and a mature knowledge graph typically needs all three.
2. The open-world (OWL) vs. closed-world (SHACL) assumption distinction determines whether "missing" means "unknown" or "invalid" — get this backwards and your validation logic is silently wrong.
3. RDF 1.2 reification (Holons) is what makes it possible to attach trust metadata (confidence, provenance) to individual facts, which matters enormously once facts start coming from LLM extraction rather than curated sources.
4. Ontology-guided extraction — injecting the formal schema into the LLM's prompt as a constraint — is the primary defense against ungrounded or malformed LLM output corrupting the graph.
5. The semantic stack exists specifically to make LLM grounding possible: verifiable, structured facts are what let a system constrain generative, stochastic reasoning.

## Connects To
- **Topic 2 (Graph Data Modeling)**: RDF triple stores as one of the two dominant graph data models, contrasted with property graphs.
- **Topic 4 (LLM-Assisted KGE)**: the concrete mechanics of Entity Flattening, Hierarchy Hallucination, and SHACL-based post-hoc validation of LLM output — the practical enforcement of the semantic stack introduced here.
- **Topic 9 (GraphRAG)**: Context Graphs and Holons as the retrieval/explainability mechanism built directly on this topic's semantic standards.
