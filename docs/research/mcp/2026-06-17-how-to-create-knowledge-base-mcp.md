# Research: Building a Knowledge Base MCP Server from Scratch

## Summary

The Model Context Protocol (MCP) provides a standardized JSON-RPC 2.0-based protocol for connecting AI assistants to external tools and data sources. Building a knowledge base MCP server for team knowledge transfer is well-supported by official TypeScript and Python SDKs, with mature patterns for exposing search and retrieval as MCP tools, documents as MCP resources, and guided query flows as MCP prompts. The best-fit stack for a self-hosted team knowledge base is the TypeScript SDK (v1.x) or Python SDK with SQLite + FAISS for small teams, upgrading to pgvector or Qdrant at scale, hybrid search (BM25 + dense embeddings), and a nomic-embed-text or OpenAI text-embedding-3-small model. Several open-source reference implementations exist that can be directly studied or forked. Integration with Claude Code takes under five minutes via a single CLI command or a JSON config file.

---

## Key Findings

### 1. MCP Server Architecture Fundamentals

MCP follows a client-server architecture: an **MCP Host** (e.g., Claude Code, Claude Desktop, VS Code) spawns or connects to one or more **MCP Servers** through a per-server **MCP Client** connection. All message exchange uses JSON-RPC 2.0 regardless of transport. [Official MCP Architecture Docs](https://modelcontextprotocol.io/docs/concepts/architecture)

**Transports:**

- **stdio** — The host spawns the server as a child process and communicates over stdin/stdout. Zero network overhead, best performance, ideal for local single-developer or per-machine deployments. This is the default for Claude Code. [MCP Transport Concepts](https://modelcontextprotocol.io/legacy/concepts/transports)
- **Streamable HTTP** — The modern remote transport (replaced standalone SSE as of spec version 2025-06-18). Uses HTTP POST for client-to-server messages, with optional Server-Sent Events for streaming. Required for team-shared or cloud-hosted knowledge bases. Supports OAuth, bearer tokens, and API keys. [Streamable HTTP vs stdio comparison](https://kirkryan.co.uk/stdio-vs-streamable-http-choosing-the-right-mcp-transport/)
- **SSE (legacy)** — Deprecated as of the 2025-06-18 spec. Avoid for new builds. [Roo Code MCP Transport Docs](https://docs.roocode.com/features/mcp/server-transports)

**Three server-side primitives, all relevant to knowledge bases:**

- **Tools** — Model-invoked, executable functions. Use for `search_knowledge`, `add_document`, `ask_question`. These are what Claude calls during reasoning. [MCP Server Patterns](https://dev.to/webbywisp/mcp-server-patterns-tools-vs-resources-vs-prompts-when-to-use-each-5bgp)
- **Resources** — Read-only data the host application fetches for context. Use to expose individual documents at `kb://<collection>/<doc-id>` URIs so Claude can retrieve raw source material. Discovery via `resources/list`, retrieval via `resources/read`. [MCP Tools vs Resources vs Prompts](https://www.rapidevelopers.com/mcp-tutorial/mcp-tools-vs-resources-vs-prompts)
- **Prompts** — User-selectable reusable templates. Use to provide guided interaction patterns like "Summarize onboarding docs for a new engineer" or "What does our runbook say about incident X?" [MCP Capabilities: Tools, Resources, Prompts](https://www.getknit.dev/blog/mcp-architecture-deep-dive-tools-resources-and-prompts-explained)

The practical split for a knowledge base: expose **search and write operations as tools**, expose **individual documents as resources**, expose **common workflows as prompts**.

---

### 2. Official SDKs

Three official SDKs are maintained under the `modelcontextprotocol` GitHub organization:

- **TypeScript SDK** (`@modelcontextprotocol/sdk`, npm) — Most feature-complete. Ships server and client packages, framework adapters for Express/Hono, full Streamable HTTP + stdio support. Use v1.x for production; v2 (pre-alpha) is on `main` and targets Q3 2026 stable. [TypeScript SDK GitHub](https://github.com/modelcontextprotocol/typescript-sdk) | [npm package](https://www.npmjs.com/package/@modelcontextprotocol/sdk)
- **Python SDK** — Equally official, widely used. Preferred if your retrieval pipeline uses Python-native tools (LangChain, LlamaIndex, txtai, FAISS, sentence-transformers). [MCP GitHub Org](https://github.com/modelcontextprotocol)
- **.NET, Java, Rust** — Available via the `microsoft/mcp-for-beginners` curriculum but less mature for production knowledge base use. [Microsoft MCP for Beginners](https://github.com/microsoft/mcp-for-beginners/)

**Recommendation:** Use the **Python SDK** if you want direct access to the full ML retrieval ecosystem (sentence-transformers, FAISS, LangChain, txtai). Use the **TypeScript SDK** if your team is JS/TS-first and you want to co-locate the MCP server with a Node.js API.

A minimal TypeScript server skeleton:
```typescript
import { McpServer } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';

const server = new McpServer({ name: 'knowledge-base', version: '1.0.0' });

server.registerTool('search_knowledge', {
  description: 'Semantic search across team knowledge base',
  inputSchema: z.object({ query: z.string(), top_k: z.number().default(5) })
}, async ({ query, top_k }) => {
  const results = await vectorSearch(query, top_k);
  return { content: [{ type: 'text', text: JSON.stringify(results) }] };
});

await server.connect(new StdioServerTransport());
```

---

### 3. Storage Backend Options

| Backend | Type | Best For | Notes |
|---|---|---|---|
| Local Markdown files | Flat files | Prototyping, no infra | No indexing; must parse/chunk at query time |
| SQLite + FAISS | Embedded | Small–medium teams, local | txtai and jeanibarz/kb-mcp-server use this; O(n) cosine or HNSW for ~100K chunks |
| SQLite + HNSW | Embedded | Tens of thousands of chunks | O(log n) ANN, still no server process needed |
| pgvector | PostgreSQL extension | Teams already using Postgres | 471 QPS at 99% recall on 50M vectors (11x faster than Qdrant in May 2025 benchmark) |
| Qdrant | Dedicated vector DB | Teams needing filtering + scale | Rust-native, strong payload filtering; 1,321 GitHub stars on MCP server |
| Chroma | Embedded/server | Fast prototyping in Python | Simplest API; single-process, no sharding |
| Pinecone / Weaviate | Hosted | Zero-ops teams | Managed, adds cloud cost and data egress |

Sources: [Vector DB comparison 2026 — DEV Community](https://dev.to/ayinedjimi-consultants/chromadb-vs-qdrant-vs-weaviate-vs-pgvector-vector-database-shootout-2026-14n7) | [Best Vector DBs — Firecrawl](https://www.firecrawl.dev/blog/best-vector-databases) | [Vector DB MCP Servers — ChatForest](https://chatforest.com/guides/best-vector-database-mcp-servers/)

**Recommendation for team knowledge transfer:** Start with **SQLite + FAISS** (zero ops, ships in a single binary alongside your MCP server). Migrate to **pgvector** when you need concurrent writes from multiple team members or exceed ~100K chunks.

---

### 4. Retrieval Strategies

**Three approaches, in order of sophistication:**

**Keyword / BM25** — TF-IDF-weighted term matching. Fast, no GPU needed, excellent for exact terminology (error codes, product names, acronyms). Libraries: `rank-bm25` (Python), Elasticsearch, Typesense.

**Semantic / Dense Embeddings** — Text is encoded into a high-dimensional vector; queries retrieve by cosine similarity. Captures meaning, synonyms, and paraphrase. Requires an embedding model.

**Hybrid (BM25 + Dense) with RRF** — Run both in parallel, merge results with **Reciprocal Rank Fusion (RRF)**. Best empirical performance for enterprise knowledge bases — preserves keyword precision while adding semantic recall. [Hybrid Search RAG — Meilisearch](https://www.meilisearch.com/blog/hybrid-search-rag) | [Hybrid Retrieval BM25 + FAISS — Chitika](https://www.chitika.com/hybrid-retrieval-rag/)

**Practical embedding models:**

| Model | Dims | Context | Mode | Notes |
|---|---|---|---|---|
| `nomic-embed-text-v1` | 768 | 8,192 tokens | Local (Ollama) | 86.2% top-5 accuracy; best open-source for long docs |
| `nomic-embed-text-v2` | variable | 8,192 tokens | Local (Ollama) | MoE architecture, multilingual, 100+ languages |
| `text-embedding-3-small` | 1536 | 8,192 tokens | OpenAI API | Low cost ($0.02/1M tokens), strong general performance |
| `all-MiniLM-L6-v2` | 384 | 512 tokens | Local (sentence-transformers) | Fastest; good for resource-constrained environments |

Sources: [Best Open-Source Embedding Models — BentoML](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models) | [Embedding Model Comparison — Ailog RAG](https://app.ailog.fr/en/blog/guides/choosing-embedding-models)

**Recommendation:** Use `nomic-embed-text` via Ollama for fully local/private deployments. Use `text-embedding-3-small` via OpenAI API if cloud is acceptable. Implement hybrid BM25 + dense from day one.

---

### 5. Practical Implementation Patterns

**Chunking strategies for team knowledge docs:**

1. **Markdown-header-aware splitting** — Split at `#`, `##`, `###` boundaries first using `MarkdownHeaderTextSplitter` (LangChain), preserving section context. Then apply `RecursiveCharacterTextSplitter` on any remaining oversized chunks.
2. **Chunk size** — 256–512 tokens (roughly 100–200 words) with 20–30% overlap. Supported by 2025 benchmarking across 36 segmentation methods. [Chunking strategies arxiv 2025](https://arxiv.org/html/2603.06976)
3. **Metadata tagging** — Embed per-chunk metadata: `{ source_file, section_title, doc_type: "onboarding|runbook|adr", author, last_updated, team }`. This enables filtered search by document type and team.

**Exposing knowledge as MCP primitives:**

- **Tools** — Minimum viable tools: `search_knowledge(query, top_k, filters?)`, `get_document(doc_id)`, `list_collections()`. Optionally: `add_document(content, metadata)`, `ask_knowledge(question)`.
- **Resources** — Expose individual documents at stable URIs (`kb://onboarding/day-one-guide`). Clients can browse the knowledge base structure independently of retrieval.
- **Prompts** — Pre-define use-case-specific prompts: "Summarize onboarding guide for role X", "Find all ADRs related to topic Y", "What does our incident runbook say about Z?"

---

### 6. Open-Source Reference Implementations

| Project | Language | Storage | Retrieval | Noteworthy |
|---|---|---|---|---|
| [kb-mcp-server (Geeksfino)](https://github.com/Geeksfino/kb-mcp-server) | Python | SQLite+FAISS or pgvector (via txtai) | Hybrid (semantic + keyword), knowledge graph, causal boosting | Portable `.tar.gz` KB bundles; plug-and-play |
| [knowledge-base-mcp-server (jeanibarz)](https://github.com/jeanibarz/knowledge-base-mcp-server) | Python | FAISS per-model index | Hybrid BM25 + dense + cross-encoder reranking | Exposes both tools and resources; mutation audit log; multi-KB support |
| [mjm.local.docs](https://dev.to/markjackmilian/mjmlocaldocs-open-source-local-knowledge-base-with-mcp-3711) | .NET | SQLite / SQLite+HNSW / SQL Server | Dense semantic | Web UI + MCP; document versioning; pluggable embeddings (Ollama/OpenAI/Azure) |
| [AWS Knowledge MCP Server](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server) | — | AWS Bedrock | Managed | Reference for remote/hosted pattern |
| [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners/) | Multi-language | — | — | Best starter curriculum; TypeScript, Python, .NET, Java, Rust examples |

The `kb-mcp-server` (Geeksfino) is the most production-ready Python option: install via `pip install kb-mcp-server`, build a KB with `kb-build --input /docs`, and point the server at the resulting archive.

---

### 7. Registering and Integrating with Claude Code

**Three scope levels:**

| Scope | Storage | Shared? |
|---|---|---|
| `local` (default) | Per-project private user state | No |
| `project` | `.mcp.json` at project root | Yes — committed to git, shared with team |
| `user` | `~/.claude.json` | Yes — across all your projects |

CLI commands:
```bash
# Add a local stdio server (for your machine only)
claude mcp add knowledge-base --scope local -- node /path/to/kb-server/index.js

# Add a project-level server (committed to .mcp.json, shared with team)
claude mcp add knowledge-base --scope project -- node /path/to/kb-server/index.js

# Verify
claude mcp list

# Remove
claude mcp remove knowledge-base
```

For a remote Streamable HTTP server (team-shared):
```bash
claude mcp add knowledge-base --transport http --url https://kb.yourteam.com/mcp
```

**Claude Desktop (JSON config):**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "node",
      "args": ["/absolute/path/to/kb-server/index.js"],
      "env": {
        "KB_PATH": "/path/to/knowledge-base"
      }
    }
  }
}
```

**Team sharing pattern:** Run the server as a shared HTTP service (Streamable HTTP transport) and register it at `--scope project` in `.mcp.json`. Every developer who clones the repo automatically gets the knowledge base server registered.

---

## Trade-offs / Caveats

- **SSE deprecation:** The standalone SSE transport was deprecated in MCP spec 2025-06-18. Tutorials older than mid-2025 may reference SSE-only patterns — avoid.
- **TypeScript SDK v2 instability:** The `main` branch of the TypeScript SDK is v2 pre-alpha. Production builds must pin to v1.x until Q3 2026 stable release.
- **Vector DB MCP ecosystem immaturity:** As of early 2026, the vector DB MCP space is described as "young and fragmented." You may need to write the MCP wrapper yourself for your chosen DB.
- **pgvector benchmark caveat:** The 11x QPS advantage over Qdrant cited from May 2025 benchmarks used pgvectorscale, not pgvector alone. Vanilla pgvector performance will be lower.
- **Chunking sensitivity:** A 2025 arxiv study across 36 segmentation methods found even large embedding models are sensitive to suboptimal chunking. Structure-aware markdown splitting consistently outperforms fixed-size splitting for documentation corpora.
- **Security note for team use:** When exposing write tools (`add_document`, `reindex_knowledge_base`), gate them behind an environment flag and implement mutation audit logging. Do not commit embedding model API keys into `.mcp.json`.
- **Ollama dependency:** Running `nomic-embed-text` via Ollama requires the Ollama daemon running locally. For teams that prefer cloud, `text-embedding-3-small` has no local dependency.

---

## Recommended Approach

For a developer building a team knowledge base MCP server from scratch:

1. **Language:** Python SDK. Direct access to `txtai`, `sentence-transformers`, `rank-bm25`, FAISS, and LangChain's `MarkdownHeaderTextSplitter`.

2. **Storage:** Start with **SQLite + FAISS** (txtai bundles both). Migrate to **pgvector** when the team grows or you need concurrent writers.

3. **Retrieval:** Implement hybrid BM25 + dense from the start using **Reciprocal Rank Fusion**. Use `nomic-embed-text` via Ollama for local/private deployments; fall back to OpenAI `text-embedding-3-small` if privacy is not a constraint.

4. **Chunking:** Use `MarkdownHeaderTextSplitter` first, then `RecursiveCharacterTextSplitter` for oversized sections. Target 256–512 token chunks with ~20% overlap. Tag every chunk with `{ source, section, doc_type, team, last_updated }`.

5. **MCP surface:** Expose `search_knowledge`, `get_document`, `list_collections` as tools. Expose individual documents as resources at stable `kb://` URIs. Add 2–3 prompts for the most common use cases (onboarding lookup, incident runbook search, ADR retrieval).

6. **Transport:** stdio for local dev. Streamable HTTP for team sharing — run as a shared Docker container and register at `--scope project` in `.mcp.json` so every developer gets it automatically on clone.

7. **Reference implementation to fork:** Start from [kb-mcp-server (Geeksfino)](https://github.com/Geeksfino/kb-mcp-server). Study [jeanibarz/knowledge-base-mcp-server](https://github.com/jeanibarz/knowledge-base-mcp-server) for multi-KB, hybrid search, resource-exposure, and audit-log patterns.

---

## Sources

- [MCP Architecture Overview — modelcontextprotocol.io](https://modelcontextprotocol.io/docs/concepts/architecture)
- [MCP Transport Concepts (legacy) — modelcontextprotocol.io](https://modelcontextprotocol.io/legacy/concepts/transports)
- [stdio vs Streamable HTTP — kirkryan.co.uk](https://kirkryan.co.uk/stdio-vs-streamable-http-choosing-the-right-mcp-transport/)
- [Roo Code MCP Server Transports](https://docs.roocode.com/features/mcp/server-transports)
- [TypeScript SDK — GitHub](https://github.com/modelcontextprotocol/typescript-sdk)
- [TypeScript SDK — npm](https://www.npmjs.com/package/@modelcontextprotocol/sdk)
- [MCP Server Patterns: Tools vs Resources vs Prompts — DEV Community](https://dev.to/webbywisp/mcp-server-patterns-tools-vs-resources-vs-prompts-when-to-use-each-5bgp)
- [MCP Tools vs Resources vs Prompts — RapidDev](https://www.rapidevelopers.com/mcp-tutorial/mcp-tools-vs-resources-vs-prompts)
- [MCP Architecture Deep Dive — getknit.dev](https://www.getknit.dev/blog/mcp-architecture-deep-dive-tools-resources-and-prompts-explained)
- [Vector DB Shootout 2026 — DEV Community](https://dev.to/ayinedjimi-consultants/chromadb-vs-qdrant-vs-weaviate-vs-pgvector-vector-database-shootout-2026-14n7)
- [Best Vector Databases 2026 — Firecrawl](https://www.firecrawl.dev/blog/best-vector-databases)
- [Best Vector Database MCP Servers 2026 — ChatForest](https://chatforest.com/guides/best-vector-database-mcp-servers/)
- [Hybrid Search for RAG — Meilisearch](https://www.meilisearch.com/blog/hybrid-search-rag)
- [Implementing Hybrid BM25 + FAISS — Chitika](https://www.chitika.com/hybrid-retrieval-rag/)
- [Hybrid RAG in the Real World — NetApp](https://community.netapp.com/t5/Tech-ONTAP-Blogs/Hybrid-RAG-in-the-Real-World-Graphs-BM25-and-the-End-of-Black-Box-Retrieval/ba-p/464834)
- [RAG with Hybrid Search: BM25 — Towards Data Science](https://towardsdatascience.com/rag-with-hybrid-search-how-does-keyword-search-work/)
- [Document Chunking for RAG — LangCopilot](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide)
- [Chunking and Embedding — Mastra Docs](https://mastra.ai/docs/rag/chunking-and-embedding)
- [Systematic Investigation of Chunking Strategies — arxiv 2025](https://arxiv.org/html/2603.06976)
- [Best Open-Source Embedding Models — BentoML 2026](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models)
- [Embedding Model Comparison — Ailog RAG](https://app.ailog.fr/en/blog/guides/choosing-embedding-models)
- [kb-mcp-server — Geeksfino (GitHub)](https://github.com/Geeksfino/kb-mcp-server)
- [knowledge-base-mcp-server — jeanibarz (GitHub)](https://github.com/jeanibarz/knowledge-base-mcp-server)
- [mjm.local.docs — DEV Community](https://dev.to/markjackmilian/mjmlocaldocs-open-source-local-knowledge-base-with-mcp-3711)
- [AWS Knowledge MCP Server](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server)
- [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners/)
- [Connect Local MCP Servers — modelcontextprotocol.io](https://modelcontextprotocol.io/docs/develop/connect-local-servers)
- [Connect Claude Code to MCP — code.claude.com](https://code.claude.com/docs/en/mcp)
- [Claude Code MCP Servers — builder.io](https://www.builder.io/blog/claude-code-mcp-servers)
- [Adding MCP Servers to Claude Code — MCPcat](https://mcpcat.io/guides/adding-an-mcp-server-to-claude-code/)
