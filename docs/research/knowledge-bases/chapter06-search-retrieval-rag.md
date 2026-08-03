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
Choosing the right chunk size is a major lever in retrieval quality. Oversized chunks dilute the semantic vector with irrelevant prose, while undersized chunks lose surrounding context.

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

1. **Standard Prose & Technical Guides**: **500–800 tokens with a 50-token sliding overlap**.
2. **Source Code & API Specs**: **200–400 tokens** split strictly along syntax/AST boundaries (functions, classes) using Tree-sitter parsers.
3. **Dense Reference & Regulatory Specifications**: **800–1,200 tokens**, as surrounding definitions are required to preserve the reference frame.
4. **Data Tables**: **1 row per chunk** with the table header row prepended/injected into every chunk.

#### Advanced Chunking Mechanics
* **Recursive / Structural Chunking**: Recursively applies a list of separators (e.g., `["#", "\n\n", "\n", " "]`) to respect Markdown heading hierarchies.
* **Late Chunking (JinaAI)**: Embeds the entire document at once using a long-context transformer (e.g., 8,192 tokens) to generate token-level representations, and then pools those tokens into chunks. This allows every chunk to retain document-wide context.
* **Late Interaction (ColBERT / ColPali)**: Computes and stores token-level embeddings separately without pooling, performing fine-grained **MaxSim** token-to-token alignment at query time for high precision.

### C. Metadata Enrichment & Contextual Retrieval
* **Frontmatter Metadata**: Injecting queryable fields (`owner`, `applies_to`, `authority_tier`, `status`) allows hard filtering before vector search.
* **Anthropic's Contextual Retrieval**: Prepending 50–100 tokens of document-level background context to each chunk prior to embedding (e.g., *"This chunk discusses user authentication for the tenant-db service..."*). This reduces retrieval failures by **49%** (and by **67%** when combined with reranking).

### D. Multi-Stage Retrieval & Candidate Expansion
* **Candidate Set ($K$)**: First-stage retrieval retrieves $K = 12\text{--}20$ candidates (or $K = 200\text{--}500$ in large corpora) to guarantee high recall.

### E. Precision Reranking
First-stage candidates are passed through a **Cross-Encoder reranker** (e.g., `monoBERT`, `duoBERT`, `Jina Reranker v2`, `Cohere Reranker`). Cross-encoders perform joint self-attention across the query and candidate chunk simultaneously, re-scoring candidates down to the top **5–10 most relevant chunks** for the LLM context window.

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
 1. Doc B (Score: 0.0315)
 2. Doc A (Score: 0.0322)
 3. Doc C (Score: 0.0320)
```

* **Smoothing Constant ($k$)**: Set to **$k = 60$** as the industry standard. Lower $k$ values favor top-ranked items (precision); higher $k$ values favor consensus across lists (recall).
* **Alpha ($\alpha$) Parameter**: Controls hybrid weighting:
 * $\alpha = 0.0$: Pure lexical / keyword search.
 * $\alpha = 0.5$: Equal weighting between BM25 and Dense Vector search.
 * $\alpha = 1.0$: Pure dense vector semantic search.
* **Performance Lift**: Deploying hybrid RRF retrieval recovers exact identifier hits while retaining semantic discovery, delivering a **10–20% recall lift** on entity-heavy technical corpora.

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
 * **Production SLA Threshold**: Faithfulness below **70%** is unsafe for production. High-performing engineering systems target **$>90\%$ Faithfulness**.
2. **Answer Relevance**: Quantifies how directly the response addresses the prompt by generating candidate questions from the answer and measuring their mean cosine similarity to the original user query.

---

## Summary Architectural Checklist

| Pipeline Stage | Recommended Configuration | Source Benchmark / SLA |
|:--- |:--- |:--- |
| **Chunking** | Prose: 500–800 tokens + 50 overlap. Code: 200–400 tokens / AST. | 40–60% relevant-sentence density per chunk. |
| **Enrichment** | Contextual Retrieval (prepend 50–100 token doc summary). | Cuts retrieval failure rates by 49–67%. |
| **Hybrid Fusion** | BM25 + Dense Vector fused via RRF ($k=60$). | 10–20% recall lift on entity/code queries. |
| **Reranking** | Multi-stage: Candidate $K=12\text{--}20 \rightarrow$ Cross-Encoder $\rightarrow$ Top 5–10. | Eliminates context noise before generation. |
| **Evaluation** | RAGAS / DeepEval automated CI checks. | Target $>90\%$ Faithfulness, $>80\%$ Context Recall. |

---

← [Prev: Maintenance & Governance](chapter05-maintenance-governance.md) | [Index](README.md) | [Next: AI-Ready Knowledge Bases](chapter07-ai-ready-kb.md) →

## Related chapters
- [chapter07-ai-ready-kb](chapter07-ai-ready-kb.md) — structuring documents so this retrieval pipeline works well
- [chapter10-anti-patterns](chapter10-anti-patterns.md) — RAG/retrieval failure modes and their fixes
- [chapter11-decision-rules](chapter11-decision-rules.md) — IF/THEN rules for chunking and retrieval choices
