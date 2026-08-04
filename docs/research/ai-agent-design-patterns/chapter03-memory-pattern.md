# Memory Pattern

## 1. Why "Add a Vector Database" Is Not a Memory Architecture

Without memory, an agent forgets everything the moment a turn ends — a user states their name, and two turns later the agent asks for it again. Production-grade agentic systems treat memory as an **explicit, multi-tiered state strategy**, not a single mechanism. Distributing state across layers is required to preserve reasoning accuracy, manage token/cost budgets, and survive context-window limits. The baseline split used almost everywhere is:

* **Short-term memory** — conversation history and working state scoped to the current session, typically held in fast storage (Redis, application state, SQLite) for low latency.
* **Long-term (semantic) memory** — durable knowledge that persists and is retrieved across sessions, typically in a vector database (Azure AI Search, pgvector, Qdrant).

This separation improves scalability and lets an agent recall relevant knowledge across sessions without re-processing the entire history every turn. But "long-term memory" is not one mechanism — the research surfaces five architecturally distinct approaches in production use, each with different tradeoffs.

## 2. Five Memory Architectures

### MemGPT — OS-Inspired Virtual Context Management
Inspired by operating-system memory hierarchies, MemGPT gives the illusion of an infinite context window on top of a fixed-context model by treating the context window as **physical RAM (Main Context)** and external storage as **disk (External Context)**. Main Context splits into three segments: read-only *system instructions*, a read-write *working context* scratchpad for persistent variables, and a rolling *FIFO queue* of recent history. A **Queue Manager** pages content: at a memory-pressure threshold (roughly 70–90% of capacity) it warns the model to write critical facts out to working context or archival storage; at 100% it flushes and prepends a recursive summary. Critically, paging is **self-directed by the model** via explicit function calls ("heartbeats") — the model decides what to page in/out, which is powerful but expensive (many sequential tool-call hops per interaction).

### OpenAI Context Compaction
Built into the OpenAI Agents SDK's session primitive as an automated trimming mechanism rather than a self-directed one. Three modes: *automatic* (truncates as the active token footprint nears the context limit), *threshold-based* (`StaticCompactionPolicy`/`DynamicCompactionPolicy`), and *forced checkpoint* (`run_compaction(force=True)` at application-defined phase boundaries). On trigger, server-side compaction truncates history older than the most recent compaction marker while preserving system instructions, global variables, and recent frames. Much lower latency and cost than MemGPT-style paging, at the cost of being coupled to the OpenAI ecosystem.

### Google Memory Bank
A managed, long-term memory service native to the Gemini Enterprise Agent Platform (ADK, Agent Engine, Agent Runtime). Rather than manipulating context in-process, it **asynchronously** analyzes session histories out-of-band using Gemini models, extracting preferences, decisions, and account details into persistent profiles scoped by `USER_ID` and `APP_NAME`. The service consolidates and resolves contradictions in stored memories over time, and a new session automatically pulls relevant memories via semantic search into the agent's start state. Very low added latency in the request path (extraction happens off the critical path), but tightly coupled to GCP/Gemini.

### AWS AgentCore Memory
Part of the Amazon Bedrock AgentCore production runtime, launched late 2025. Separates transient session state from persistent cross-session insight explicitly, and adds **hierarchical namespaces** for multi-tenant isolation — a distinguishing feature for platforms serving multiple distinct agents or corporate tenants from one deployment. Session data is written to/restored from managed backends (DynamoDB, Aurora pgvector, OpenSearch Serverless) triggered by runtime events. Deeply coupled to AWS IAM/Bedrock.

### Vector-Database-Backed Long-Term Memory
The generic, most portable pattern: short-term memory in fast local storage, long-term memory as embedded chunks in a vector store (pgvector, Qdrant, Azure AI Search). Text is chunked (statically or semantically), embedded via a bi-encoder, and retrieved at query time by nearest-neighbor search (cosine similarity, HNSW indexes) over the top-K matches, which are appended to the prompt. This is the architecture most frameworks default to because it is model- and vendor-agnostic — and it inherits RAG's retrieval-quality failure modes (see §4 below and [Chapter 2](chapter02-foundational-patterns.md)).

### Tradeoff Summary

| Dimension | MemGPT | OpenAI Compaction | Google Memory Bank | AWS AgentCore Memory | Vector-DB LTM |
|---|---|---|---|---|---|
| Core mechanism | Self-directed paging via tool calls | Prompt truncation at compaction markers | Async out-of-band curation | Tiered session vs. cross-session state | Bi-encoder embedding + nearest-neighbor |
| Latency | High (multi-hop tool loops) | Very low | Ultra-low (off critical path) | Low–moderate | Moderate (embedding + index latency) |
| Cost | High (repeated reasoning loops) | Low | Moderate (background model calls) | Variable, capacity-based | Moderate (hosting + embedding) |
| Portability | High (model-agnostic) | Moderate (OpenAI ecosystem) | Low (GCP-coupled) | Low (AWS-coupled) | High (portable) |

## 3. Failure Modes of Poorly Designed Memory

**Context rot / decay.** As a session runs long, models exhibit uneven attention across long inputs (the "lost-in-the-middle" effect). A bloated, unsummarized memory buffer dilutes attention to the point that an instruction stated at turn 1 is silently ignored by turn 50. Naïve recursive summarization compounds this: critical "landmark" facts (a stated risk tolerance, a key variable assignment) get flattened into generic summaries and are effectively forgotten — functional amnesia despite the fact being technically "in memory" somewhere.

**Memory poisoning and overwrites.** Long-term memory that writes dynamically without validation is vulnerable to semantic contamination: a user's *temporary* correction ("just for this run, ignore the budget limit") gets promoted to a *permanent* rule if the write path doesn't distinguish scope. In multi-agent or parallel-session environments, concurrent writes to shared memory without transactional locks cause race conditions where one agent's update silently clobbers another's.

**Retrieval drift.** Flat vector search optimizes for semantic similarity, not logical or hierarchical relevance. Agents can retrieve conceptually "similar" but contextually wrong chunks, corrupting the context window with distracting text and forcing the model to reason over noise — which both inflates token cost and increases hallucination risk, especially on multi-hop queries where the needed answer spans chunks that were never retrieved together.

## 4. Design Guidance

* Default to the vector-store pattern unless you're already committed to one hyperscaler's agent platform — it's the most portable and has the widest framework support.
* Never let raw user corrections write directly to long-term memory without a validation/promotion step; distinguish "scoped to this run" from "durable preference."
* Summarize with landmark-preservation in mind — a compaction step that flattens everything equally will erase the facts that mattered most.
* If retrieval quality is degrading, suspect chunking (are document boundaries and headings being preserved?) before suspecting the embedding model.
