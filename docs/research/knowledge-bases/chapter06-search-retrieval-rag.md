# Search, Retrieval, and RAG

An end-to-end **Search and Retrieval Architecture** over an engineering knowledge base bridges static documentation and real-time developer (and AI agent) query execution. Building an enterprise-grade retrieval pipeline requires balancing exact lexical string matching, semantic vector search, chunking strategies, multi-stage reranking, and rigorous quality evaluation.

---

## 1. Full-Text (Lexical) vs. Semantic Search

Modern technical search engines must accommodate two fundamentally different query patterns: exact symbol/identifier lookups and high-level conceptual questions.

```
 SEARCH & RETRIEVAL DUALITY
 ┌──────────────────────────────────┬──────────────────────────────────┐
 │ Full-Text / Lexical Search │ Semantic Search │
 │ (BM25 / TF-IDF) │ (Dense Vector Embeddings) │
 ├──────────────────────────────────┼──────────────────────────────────┤
 │ • Exact token matching │ • Meaning & intent matching │
 │ • Inverted index lookup │ • Cosine similarity in vector space│
 │ • Handles SKUs, code symbols, │ • Handles paraphrasing, natural │
 │ error codes, & API endpoints │ language, & multi-linguality │
 └──────────────────────────────────┴──────────────────────────────────┘
```

### Full-Text / Lexical Search (BM25)
* **Mechanics**: Matches exact tokens using inverted indices. Algorithms like **Okapi BM25** refine traditional TF-IDF by adding term frequency saturation ($k_1$) and document length normalization ($b$):
 $$\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$
 Typical parameter defaults are $1.2 \le k_1 \le 2.0$ and $b \approx 0.75$.
* **Optimal Use Cases**: SKUs, error codes (`ERR_CONN_REFUSED`), proper nouns, API endpoints (`/v2/tenants`), function signatures, legal clauses, and domain-specific jargon.
* **Failure Modes**: Vocabulary mismatch—fails completely if the user query uses synonyms or paraphrasing that does not appear verbatim in the document.

### Semantic (Dense Vector) Search
* **Mechanics**: Neural encoder models (e.g., SentenceBERT, Transformers) map queries and text passages into a continuous high-dimensional vector space (typically 768 or 1024 dimensions). Similarity is measured via geometric proximity, such as **Cosine Similarity**:
 $$\text{Cosine Similarity}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$
* **Optimal Use Cases**: Exploratory natural language questions, conceptual queries, multi-lingual matching, and paraphrased intent.
* **Failure Modes**: "Out-of-domain" data. Dense models struggle with rare codes, arbitrary serial numbers, or newly added internal codenames that were absent from their pre-training corpus.

---

## 2. Embeddings & Vector Stores

### Sparse vs. Dense Embeddings
* **Sparse Embeddings (TF-IDF, BM25, SPLADE)**: High-dimensional vectors (tens of thousands of dimensions) where the vast majority of values are zero. Dimensions correspond to specific tokens or vocabulary terms.
* **Dense Embeddings (SBERT, OpenAI `text-embedding-3`, BGE, Jina)**: Compact, lower-dimensional vectors (384 to 1536 dimensions) where nearly all values are non-zero floats encoding deep semantic context.

### Storage Architectures: Vector Databases vs. Vector Libraries

| Dimension | Vector Databases (Milvus, Pgvector, Pinecone, Weaviate, Qdrant) | Vector Libraries (FAISS) |
|:--- |:--- |:--- |
| **Data Persistence** | Full disk/cloud database with durable storage and ACID transaction support. | In-memory index structures written in C++ with Python wrappers. |
| **CRUD Capabilities** | Full real-time Create, Read, Update, and Delete operations on individual vectors. | Volatile; modifying or deleting single items requires recreating or re-indexing the entire index. |
| **Filtering & Scale** | First-class metadata filtering alongside vector indexing at massive scale. | High-speed similarity search optimized for static, local, or research workloads. |

---

## 3. RAG Architecture over Internal Documentation

```
 END-TO-END RAG PIPELINE
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ Parsing & │ ──► │ Chunking & │ ──► │ Hybrid │ ──► │ Cross-Encoder│ ──► LLM
 │ Metadata │ │ Contextual │ │ Retrieval │ │ Reranking │ Generation
 │ Extraction │ │ Enrichment │ │ (BM25+Dense) │ │ (Top 5-10) │
 └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### A. Ingestion & Document Parsing
Raw documentation (Markdown, PDF, HTML, OpenAPI specs) is extracted alongside structural metadata (headers, tables, timestamps, access levels, and file globs).

### B. Chunking Strategies & Sizing Guidance
Choosing the right chunk size is a major lever in retrieval quality. Oversized chunks can dilute the semantic vector with irrelevant prose, while undersized chunks can lose surrounding context. The ranges below are starting hypotheses, not portable defaults: validate them with labeled, representative queries from the corpus and tune for retrieval quality, answer quality, latency, and cost.

```
 CHUNK SIZE BY CONTENT TYPE
 ┌────────────────────────────────────────────────────────┐
 │ Prose & General Wiki (500–800 tokens, 50-token overlap)│
 ├────────────────────────────────────────────────────────┤
 │ Code & AST Units (200–400 tokens / function boundary) │
 ├────────────────────────────────────────────────────────┤
 │ Reference & Regulatory (800–1200 tokens) │
 ├────────────────────────────────────────────────────────┤
 │ Data Tables (1 Row per chunk + Injected Header) │
 └────────────────────────────────────────────────────────┘
```

1. **Standard Prose & Technical Guides**: Start by testing **500–800 tokens with a 50-token sliding overlap**.
2. **Source Code & API Specs**: Start by testing **200–400 tokens** split along syntax/AST boundaries (functions, classes) using Tree-sitter parsers.
3. **Dense Reference & Regulatory Specifications**: Start by testing **800–1,200 tokens**, where surrounding definitions may be needed to preserve the reference frame.
4. **Data Tables**: **1 row per chunk** with the table header row prepended/injected into every chunk.

#### Advanced Chunking Mechanics
* **Recursive / Structural Chunking**: Recursively applies a list of separators (e.g., `["#", "\n\n", "\n", " "]`) to respect Markdown heading hierarchies.
* **Late Chunking (JinaAI)**: Embeds the entire document at once using a long-context transformer (e.g., 8,192 tokens) to generate token-level representations, and then pools those tokens into chunks. This allows every chunk to retain document-wide context.
* **Late Interaction (ColBERT / ColPali)**: Computes and stores token-level embeddings separately without pooling, performing fine-grained **MaxSim** token-to-token alignment at query time for high precision.

### C. Metadata Enrichment & Contextual Retrieval
* **Frontmatter Metadata**: Injecting queryable fields (`owner`, `applies_to`, `authority_tier`, `status`) allows hard filtering before vector search.
* **Contextual Retrieval**: Test prepending a 50–100 token document-level summary to each chunk before embedding (e.g., *"This chunk discusses user authentication for the tenant-db service..."*). Anthropic reports 49% fewer retrieval failures for its evaluated setup, and 67% when combined with reranking; treat those results as source-reported, not as an expected local outcome.

### D. Multi-Stage Retrieval & Candidate Expansion
* **Candidate Set ($K$)**: Start by evaluating $K = 12\text{--}20$ candidates (or a larger range such as $K = 200\text{--}500$ in large corpora). Choose the final value from recall, reranker quality, latency, and cost measurements; no candidate count guarantees recall.

### E. Precision Reranking
First-stage candidates can be passed through a **Cross-Encoder reranker** (e.g., `monoBERT`, `duoBERT`, `Jina Reranker v2`, `Cohere Reranker`). Cross-encoders perform joint self-attention across the query and candidate chunk simultaneously. Start by testing a final context of **5–10 chunks**, then tune it against representative tasks and the target model's context budget.

### F. Response Generation & Context Placement
To avoid the **"Lost in the Middle"** phenomenon—where LLMs reliably attend to information at the very beginning or end of a prompt but overlook facts placed in the middle—the retriever orders the top chunks so that the highest-confidence evidence is placed at the boundaries of the prompt.

---

## 4. Hybrid Retrieval & Reciprocal Rank Fusion (RRF)

Because BM25 term scores and dense vector cosine similarities operate on completely different mathematical scales, they cannot be directly added together. Platforms use **Reciprocal Rank Fusion (RRF)**, a zero-shot fusion algorithm that ignores raw scores and merges documents based purely on their rank positions across both result lists:

$$RRF\_Score(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

```
 RECIPROCAL RANK FUSION (RRF)
 BM25 Ranking (Exact Terms) Dense Ranking (Semantic Intent)
 1. Doc A 1. Doc B
 2. Doc B 2. Doc C
 3. Doc C 3. Doc A
 │ │
 └───► RRF ◄─────┘
 (k = 60)
 │
 ▼
 Fused Final Rank:
 1. Doc A (Score: 0.0322)
 2. Doc C (Score: 0.0320)
 3. Doc B (Score: 0.0315)
```

* **Smoothing Constant ($k$)**: **$k = 60$** is a common starting value, not an industry-wide optimum. Lower values favor top-ranked items; higher values favor consensus across lists. Tune it with the same labeled evaluation set.
* **Alpha ($\alpha$) Parameter**: Controls hybrid weighting:
 * $\alpha = 0.0$: Pure lexical / keyword search.
 * $\alpha = 0.5$: Equal weighting between BM25 and Dense Vector search.
 * $\alpha = 1.0$: Pure dense vector semantic search.
* **Performance Lift**: Hybrid RRF can recover exact-identifier hits while retaining semantic discovery. Reported recall lifts (including 10–20% figures) are corpus- and setup-specific; measure the lift on representative local queries before adopting it.

---

## 5. Knowledge Graphs vs. Flat Docs for Retrieval

```
 RETRIEVAL STRUCTURAL PARADIGMS
 ┌───────────────────┬───────────────────┬───────────────────┐
 │ Flat Chunking │ Hierarchical RAG │ Knowledge Graph │
 │ (RAG) │ (RAPTOR / HiQA) │ (GraphRAG) │
 ├───────────────────┼───────────────────┼───────────────────┤
 │ Independent vector│ Tree: Doc -> Sec │ Entity-relation │
 │ text blocks │ -> Paragraph │ triples & nodes │
 └───────────────────┴───────────────────┴───────────────────┘
```

### Flat Docs (Standard RAG)
* **Mechanics**: Documents are chopped into uniform chunks and indexed independently.
* **When It Wins**: Fast, cheap, and effective for localized, single-fact QA ("What is the timeout limit for Service X?").
* **Failure Modes**: Breaks down on multi-hop questions requiring sequential evidence chaining across separate files.

### Hierarchical RAG (RAPTOR, HiQA, Tree-Organized)
* **Mechanics**: Clusters atomic text chunks recursively using Gaussian Mixture Models (GMMs) or document structures, summarizing clusters to form a multi-level tree (Document $\rightarrow$ Section $\rightarrow$ Paragraph).
* **When It Wins**: High-level thematic questions ("Summarize our entire authentication migration strategy across all services").

### Knowledge Graphs (GraphRAG / Context Graphs)
* **Mechanics**: Extracts explicit entity-relation-entity triples (`(AuthService) -[DEPENDS_ON]-> (PgBouncer)`) into a graph database.
* **When It Wins**: Complex dependency resolution, impact analysis ("If we deprecate DB V1, which downstream teams and services break?"), and multi-hop entity reasoning.

---

## 6. Retrieval Quality Evaluation & Metrics

Evaluating a RAG system requires isolating **Retrieval Metrics** from **Generation Metrics** using frameworks like RAGAS, TruLens, or DeepEval.

```
 RAG EVALUATION TRIAD
 ┌────────────────────────────────────────────────────────┐
 │ RETRIEVAL METRICS │
 │ • Context Precision: Are relevant chunks ranked top? │
 │ • Context Recall: Did we fetch all needed facts? │
 │ • Context Relevance: Is there noise in the context? │
 ├────────────────────────────────────────────────────────┤
 │ GENERATION METRICS │
 │ • Faithfulness / Groundedness: Are claims in context? │
 │ • Answer Relevance: Does output answer user query? │
 └────────────────────────────────────────────────────────┘
```

### Retrieval Metrics
1. **Context Precision**: Evaluates whether all ground-truth relevant chunks appear at the highest ranks ($k=1, 2$) in the context window rather than buried at the bottom:
 $$\text{Context Precision@K} = \frac{\sum_{k=1}^{K} (\text{Precision@k} \times v_k)}{\text{Total relevant items in top K}}$$
2. **Context Recall**: Measures the proportion of ground-truth statements attributable to the retrieved context:
 $$\text{Context Recall} = \frac{|\text{Ground-Truth Sentences Attributable to Context}|}{|\text{Total Sentences in Ground-Truth}|}$$
3. **Context Relevance**: Measures the ratio of relevant sentences to total sentences inside the retrieved context blocks:
 $$\text{Context Relevance} = \frac{\text{Number of Relevant Sentences}}{\text{Total Sentences in Retrieved Context}}$$

### Generation Metrics
1. **Faithfulness / Groundedness**: Measures factual consistency by verifying if every claim in the LLM's answer can be inferred directly from the context:
 $$\text{Faithfulness Score} = \frac{\text{Number of Claims Inferable from Context}}{\text{Total Claims in Generated Answer}}$$
 * **Acceptance threshold**: Set a risk-appropriate threshold from a labeled evaluation set and human review. Values such as **$>90\%$ faithfulness** or **$>80\%$ context recall** are starting hypotheses, not universal production SLAs; high-impact tasks need stricter review and escalation paths.
2. **Answer Relevance**: Quantifies how directly the response addresses the prompt by generating candidate questions from the answer and measuring their mean cosine similarity to the original user query.

---

## Summary Architectural Checklist

| Pipeline Stage | Starting hypothesis | Validate locally |
|:--- |:--- |:--- |
| **Chunking** | Prose: test 500–800 tokens + 50 overlap. Code: test 200–400 tokens / AST. | Retrieval/answer metrics, latency, cost, and relevant-sentence density. |
| **Enrichment** | Test contextual retrieval with a 50–100 token document summary. | Compare against a no-enrichment baseline on labeled queries. |
| **Hybrid Fusion** | Test BM25 + dense vectors fused via RRF (start at $k=60$). | Exact-identifier and conceptual-query recall against single-mode baselines. |
| **Reranking** | Test Candidate $K=12\text{--}20 \rightarrow$ Cross-Encoder $\rightarrow$ 5–10 final chunks. | Retrieval gain versus latency and cost. |
| **Evaluation** | Use RAGAS / DeepEval plus task-specific human review. | Calibrated acceptance thresholds for faithfulness, recall, and task risk. |

---

← [Prev: Maintenance & Governance](chapter05-maintenance-governance.md) | [Index](README.md) | [Next: AI-Ready Knowledge Bases](chapter07-ai-ready-kb.md) →

## Related chapters
- [chapter07-ai-ready-kb](chapter07-ai-ready-kb.md) — structuring documents so this retrieval pipeline works well
- [chapter10-anti-patterns](chapter10-anti-patterns.md) — RAG/retrieval failure modes and their fixes
- [chapter11-decision-rules](chapter11-decision-rules.md) — IF/THEN rules for chunking and retrieval choices
