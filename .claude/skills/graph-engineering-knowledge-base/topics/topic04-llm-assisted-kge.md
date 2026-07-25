# Topic 4: LLM-Assisted Knowledge Graph Engineering

## Core Idea
LLMs can automate historically manual, labor-intensive KGE tasks — SPARQL generation, triple extraction, ontology drafting, entity resolution — but their stochastic nature introduces specific, documented failure modes (syntax errors, Entity Flattening, Hierarchy Hallucination). The mitigation is architectural, not prompt-level: constrain extraction with an injected ontology schema, then subject every generated triple to closed-world SHACL validation before it reaches the graph, so hallucinations are caught structurally rather than trusted.

## Frameworks Introduced
- **SPARQL Query Generation from Natural Language**: LLMs translate plain-language questions into syntactically correct SPARQL, lowering the barrier to querying RDF stores.
  - When to use: exposing knowledge graph query capability to non-expert users.
  - Limitation: LLMs are prone to subtle syntax errors or inconsistencies on complex, multi-join SPARQL queries — treat generated queries as a draft requiring validation, not a guaranteed-correct output.
- **Zero-Shot Triple Extraction / JSON-LD Population**: LLMs process unstructured or semi-structured text (e.g. spec-sheet PDFs) to identify key-value pairs and relationships, outputting directly into JSON-LD to populate a graph.
  - When to use: bootstrapping a knowledge graph from a corpus of unstructured documents where manual annotation would be prohibitively slow.
- **Automated Ontology Generation**: LLMs analyze relationships and patterns in existing data to assist in building or extending conceptual backbones (e.g. class/property hierarchies based on an existing ontology like DBpedia's), and can render these structures as Mermaid diagrams.
  - When to use: accelerating initial ontology drafts, not as a substitute for expert review — see Hierarchy Hallucination below.
- **Ontology-Guided Extraction with Schema Constraint Layers**: the primary mitigation architecture. Extraction is governed by a formal ontology schema — represented as a triplet constraint space defining allowed entity types, relationship types, and domain/range constraints — injected directly into the LLM's prompt as a structured template.
  - When to use: any production extraction pipeline that writes directly into a knowledge graph, i.e. essentially always.
  - How: constrain the prompt with the schema, generate triples, then validate every generated triple under a Closed World Assumption via SHACL (`NodeShape`/`PropertyShape`) before ingestion — see Worked Example below.

## Key Concepts
- **Entity Resolution (ER)**: determining which fragmented pieces of data relate to the same real-world entity. Graph databases are naturally suited to this; ML/AI models applied over the graph can spot patterns, predict links, and reconcile ambiguous entities or duplicates.
- **Entity Flattening**: an LLM extraction failure where an entity that should be a distinct, typed node (e.g. a product's manufacturer) is instead recorded as a plain string literal. A documented experiment found an LLM correctly *identifying* a 3D printer's manufacturer but inconsistently recording it as a string rather than linking it as a properly typed entity — destroying the relational mapping the graph depends on.
- **Hierarchy Hallucination**: when asked to generate or visualize ontology structures, LLMs risk hallucinating the actual depth, logical accuracy, or relationships of the conceptual hierarchy they produce.
- **Closed World Assumption (CWA) Validation**: post-extraction, generated triples pass through SHACL, which enforces `NodeShape` and `PropertyShape` constraints the data must match exactly — anything not explicitly conformant is rejected, not assumed valid.

## Mental Models
- **LLM output is a draft, the schema is the editor**: treat every LLM-generated triple, ontology fragment, or SPARQL query as a hypothesis to be checked against a fixed structural contract, never as ground truth to be ingested directly.
- **Constrain at the prompt, verify at the boundary — defense in depth**: ontology-guided extraction (constraining what the LLM is even allowed to propose) and SHACL post-hoc validation (catching what it proposed anyway) are complementary, not redundant — the first reduces the error rate, the second guarantees a hard floor on correctness regardless of what slips through.
- **Flattening is a symptom of the LLM defaulting to the easy structure**: when an LLM has a choice between emitting a properly typed entity reference (harder, requires resolving/creating a node) and a bare string (easier, always "works" syntactically), it will default to the string unless the schema explicitly forbids it — this is why schema constraints must be enforced structurally, not just requested in the prompt.

## Anti-patterns
- **Entity Flattening**: extracting what should be a typed entity node as a string literal, breaking the relational mapping. Fix: schema constraint layer requiring the field's type at extraction time, plus SHACL rejection of literal values where a node reference is required.
- **Hierarchy Hallucination**: trusting an LLM-generated ontology diagram or class hierarchy as authoritative without expert review of its depth and logical accuracy.
- **Trusting LLM-generated SPARQL/triples without validation**: treating fluent, syntactically-plausible output as semantically correct output — the two are not the same, especially on complex multi-join queries.

## Code Examples
(omit — the source material describes the JSON-LD/SHACL validation workflow at the architectural level without a reconstructable code sample)

## Reference Tables
| Capability | What LLMs Do Well | Documented Failure Mode | Mitigation |
|---|---|---|---|
| SPARQL generation | Simple, single-hop NL→SPARQL translation | Subtle syntax errors on complex multi-join queries | Validate/test generated queries before production use |
| Triple extraction (JSON-LD) | Identifying key-value pairs from unstructured text | Entity Flattening (typed entity → string literal) | Ontology-guided extraction + SHACL rejection |
| Ontology generation | Drafting class/property hierarchies from existing patterns | Hierarchy Hallucination (wrong depth/logic) | Expert review before adoption |
| Entity resolution | Applying ML/AI to spot links and reconcile duplicates | (not separately documented as high-risk) | — |

## Worked Example
A team ingests 3D-printer manufacturer spec sheets into a knowledge graph using an LLM extraction pipeline. The pipeline is given a schema (via prompt injection) stating that the `manufacturedBy` relationship must point to a `Manufacturer`-typed node, not a string. For one spec sheet, the LLM correctly identifies the manufacturer's name from the PDF text but — despite the schema instruction — emits it as a bare string literal (`"manufacturer": "Acme Corp"`) instead of a resolved entity reference: a live instance of Entity Flattening. Because the pipeline also runs every generated triple through SHACL validation under the Closed World Assumption, the malformed triple is caught at the boundary: the `PropertyShape` for `manufacturedBy` requires a node of type `Manufacturer`, the string literal doesn't satisfy that shape, and the triple is rejected before it can corrupt the graph. The extraction is retried (or routed to a resolution step that looks up/creates the `Manufacturer` node) rather than silently accepted.

## Key Takeaways
1. LLMs meaningfully accelerate KGE (SPARQL generation, extraction, ontology drafting, entity resolution) but introduce stochastic risk at every one of those steps.
2. Entity Flattening and Hierarchy Hallucination are the two named, documented failure modes to specifically design defenses against.
3. The correct architecture is two-layered: constrain extraction with an injected ontology schema *and* validate every output against SHACL under a closed-world assumption — prompt-level instruction alone is not sufficient.
4. SHACL's closed-world rejection is what actually catches flattening errors in production — it's the structural backstop, not the schema-in-prompt request.
5. Treat LLM-generated SPARQL, triples, and ontology fragments as drafts requiring validation, never as directly-ingestible ground truth.

## Connects To
- **Topic 3 (Ontologies and Semantic Standards)**: the OWL/SKOS/SHACL stack this topic's mitigation architecture is built on.
- **Topic 9 (GraphRAG)**: "when the graph is wrong, RAG is wrong" — Entity Flattening and other KGE quality failures propagate directly into GraphRAG hallucination risk.
- **Topic 13 (Verification and Reliability)**: the general pattern of structural/mechanical verification over LLM self-report, applied here specifically to knowledge graph ingestion.
