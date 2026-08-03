# Decision Rules and Glossary

## Part 1: IF/THEN Decision Rules for Knowledge Base Work

### 1. Tooling Choice & Architecture
* **IF** your knowledge base primarily serves developers and technical execution **THEN** adopt a **Docs-as-Code (Git-backed)** architecture co-locating Markdown files directly in source code repositories so documentation branches, reviews, and releases evolve synchronously with code changes.
* **IF** non-technical stakeholders (product managers, HR, business leads) must actively co-author content **THEN** deploy a database-backed wiki (e.g., Confluence, Notion, Slite) or a hybrid platform featuring two-way Git synchronization (e.g., GitBook).
* **IF** building a knowledge platform for an enterprise with 100+ developers and microservice architectures **THEN** integrate documentation into an **Internal Developer Portal (IDP)** like Spotify Backstage (TechDocs) or Cortex, linking docs directly to software catalogs, service owners, and scorecards.
* **IF** you need to render interactive UI components without executing arbitrary client-side JavaScript **THEN** adopt **Markdoc** (Stripe’s AST-based Markdown superset) rather than raw MDX.

### 2. Information Architecture & File Structure
* **IF** structuring technical documentation based on reader intent **THEN** implement the **Diátaxis framework**, strictly separating content into four quadrants: *Tutorials* (learning-oriented), *How-To Guides* (goal-oriented recipes), *Reference* (terse, factual descriptions), and *Explanation* (understanding-oriented background).
* **IF** managing both deadline-driven sprint work and long-term architectural knowledge **THEN** combine **PARA** (Projects, Areas, Resources, Archives) for execution with **Zettelkasten** (atomic, bidirectionally linked Permanent Notes) for insight in a **Hub-and-Spoke model**.
* **IF** creating an entry point for a repository **THEN** maintain a root `START_HERE.md` file readable in under 5 minutes containing the project overview, team roster, sprint state, critical architecture pointers, and environment/credential links.
* **IF** naming physical Markdown files and ADRs **THEN** use lowercase alphanumeric characters separated by hyphens (e.g., `0007-use-postgres.md`) and imperative present-tense verb phrases.

### 3. Governance & Quality Maintenance
* **IF** documentation is prone to drift or "dead wiki" decay **THEN** assign a **single named Directly Responsible Individual (`owner`)** in every file's YAML frontmatter schema rather than relying on team/committee ownership.
* **IF** a team member asks a technical question in chat or code review **THEN** enforce the **"Link-First" rule**: reply with the canonical SSoT documentation URL, or open a Pull/Merge Request to add the page first if it doesn't exist.
* **IF** an engineering ticket touches infrastructure, API schemas, or operational runbooks **THEN** mandate documentation updates in the **Definition of Done (DoD)** and block pull request merges until docs are updated in the same PR.
* **IF** automating quality gates in CI/CD pipelines **THEN** enforce syntax formatting with `markdownlint`, style guide and active voice rules with `Vale`, and link integrity with `Lychee` or `Baler`.
* **IF** a document becomes outdated or superseded **THEN** archive it, prepend a non-authoritative banner, and **de-index it from search and AI manifests** rather than letting stale docs sit in search indexes.

### 4. Search & Retrieval (RAG & Vector Search)
* **IF** searching for exact symbols, SKUs, error codes (`ERR_CONN_REFUSED`), or API parameters **THEN** use **lexical full-text search (BM25)** rather than pure vector search.
* **IF** searching for high-level conceptual questions, natural language queries, or multi-lingual matches **THEN** use **dense vector semantic search**.
* **IF** querying mixed, entity-heavy engineering documentation **THEN** compare lexical, dense, and **Hybrid Retrieval** modes; RRF with $k=60$ is a common starting value, and any recall lift must be measured on representative local queries.
* **IF** setting chunk sizes for RAG ingestion **THEN** begin by testing **500–800 tokens** (50-token overlap) for prose, **200–400 tokens** along AST boundaries for source code, **800–1200 tokens** for dense reference text, and **1 row per chunk** with an injected header for data tables; choose from retrieval and answer metrics, latency, and cost.
* **IF** configuring first-stage candidate retrieval in RAG **THEN** start with **12–20 candidates** and **5–10 final chunks** via a Cross-Encoder reranker, then tune and evaluate rather than assuming those values eliminate retrieval errors.

### 5. AI-Readiness & Agentic Workflows
* **IF** making technical documentation discoverable for identified AI coding assistants or MCP servers **THEN** consider the emerging `/llms.txt` convention and optional `/llms-full.txt` export; test discovery, parsing, access control, freshness, and real consumer use before relying on them.
* **IF** preventing AI agents from giving conflicting or hallucinated answers **THEN** enforce a **4-Tier Document Authority Hierarchy** where Tier 1 (Source of Truth) is read-only for AI.
* **IF** structuring ADRs for coding agents **THEN** attach an `applies_to` frontmatter file glob, use normative RFC 2119 keywords (`MUST`/`SHOULD`), enforce a <200 line budget, and include an automated `verify` check command.
* **IF** maintaining documentation as a codebase evolves **THEN** use a Code Wiki workflow to produce anchored draft proposals (`/generate-documentation-from-code` and `/doc-resync`); require human approval for Tier 1/2 changes and risk-based review for Tier 3 while retaining unresolved `TODO-VERIFY` or `CONTRADICTION` markers.

---

## Part 2: Glossary of Key Terms

1. **Architecture Decision Record (ADR)**: An immutable, append-only historical log capturing an architecturally significant design decision, its context, considered options, and accepted engineering consequences.
2. **C4 Model**: A four-level hierarchical framework (System Context, Container, Component, Code) created by Simon Brown to visualize software architecture across varying levels of abstraction.
3. **Code Wiki**: A workflow in which an AI agent proposes source-anchored documentation patches from codebase analysis and Git commit pointers; generated changes remain drafts pending checks and appropriate human review.
4. **Context Precision**: A retrieval evaluation metric measuring whether ground-truth relevant chunks appear at the highest ranks within the retrieved context window.
5. **Context Recall**: A retrieval evaluation metric measuring the proportion of ground-truth statements that are directly attributable to retrieved context chunks.
6. **Contextual Retrieval**: An ingestion technique that prepends document-level background context to a chunk before embedding. Test its effect locally; published reductions in retrieval failures are setup-specific.
7. **Cross-Encoder Reranker**: A neural model that jointly evaluates query-document pairs to re-score first-stage candidates. The final context size is a locally calibrated setting, not a universal 5–10-chunk rule.
8. **Declared Context**: Institutional human knowledge (business rules, domain ontologies, strategic intent) that cannot be derived from code and requires periodic human re-validation.
9. **Derived Context**: Summarized technical state (schemas, lineage, quality scores, incident histories) that can be automatically computed and updated from underlying system telemetries.
10. **Diátaxis Framework**: An intent-focused documentation architecture that categorizes content into four distinct quadrants based on user needs: Tutorials, How-To Guides, Reference, and Explanation.
11. **Directly Responsible Individual (DRI)**: A single named owner assigned to a document or service to guarantee explicit accountability for page accuracy and freshness.
12. **Docs-as-Code**: A methodology where documentation is written in plain text (Markdown), co-located in version control alongside source code, and verified via automated CI/CD pipelines.
13. **Document Authority Hierarchy**: A 4-tier governance structure ranking documentation from Tier 1 (authoritative Source of Truth) down to Tier 4 (Archive), preventing AI models and developers from treating outdated notes as ground truth.
14. **Faithfulness / Groundedness**: An evaluation metric measuring the factual consistency of an LLM's generated response against retrieved context passages.
15. **Hybrid Retrieval**: A search architecture that fuses exact keyword matching (BM25) and dense vector semantic search to maximize both precision and recall across mixed technical corpora.
16. **"Link-First" Rule**: An organizational communication norm requiring team members to answer inquiries by linking to canonical documentation, or submitting a documentation PR first if the page does not exist.
17. **`llms.txt`**: An emerging machine-readable convention for a domain-root documentation index. Verify that each intended AI consumer discovers and uses it.
18. **`llms-full.txt`**: An optional concatenated Markdown export for AI consumption; validate size, access controls, freshness, and consumer behavior before relying on it.
19. **"Lost in the Middle" Phenomenon**: The tendency of large language models to attend well to information at the beginning or end of a context window while overlooking facts placed in the middle.
20. **`Lychee`**: A fast, async link-checking tool that scans Markdown files in CI/CD workflows to detect broken internal paths, dead URLs, and expired domains.
21. **Map of Content (MOC)**: A fluid Markdown hub page that aggregates and outlines links to atomic notes within a specific domain without enforcing rigid folder trees.
22. **Markdoc**: Stripe's open-source Markdown-superset framework that parses content into a declarative Abstract Syntax Tree (AST) for static build-time validation and safe UI component rendering.
23. **`markdownlint`**: A static analysis linter that enforces Markdown syntax rules, heading hierarchies, list indentation, and formatting standards.
24. **PARA Method**: An information management framework developed by Tiago Forte that organizes workspace files into four top-down categories based on actionability: Projects, Areas, Resources, and Archives.
25. **Reciprocal Rank Fusion (RRF)**: A zero-shot rank-fusion algorithm that combines lexical (BM25) and semantic search ranks. $k=60$ is a common starting value to tune on representative local queries.
26. **Runbook**: A prescriptive, step-by-step operational guide executed by on-call engineers during system incidents to diagnose failures and minimize MTTR.
27. **Single Source of Truth (SSoT)**: An architectural rule mandating that every policy, API contract, or system configuration exists in exactly one authoritative location to prevent knowledge duplication and drift.
28. **`START_HERE.md`**: A canonical repository entry point designed to be read in under 5 minutes by humans and entering AI agents to provide immediate project orientation.
29. **`Vale`**: An open-source prose linter used in CI/CD pipelines to enforce style guide compliance, active voice, terminology, and readability metrics across Markdown files.
30. **Zettelkasten Method**: A bottom-up knowledge system developed by Niklas Luhmann built around atomic, self-contained notes connected through explicit bidirectional links.

---

← [Prev: Anti-Patterns](chapter10-anti-patterns.md) | [Index](README.md) | [Next: Implementation Roadmap](chapter12-implementation-roadmap.md) →

## Related chapters
- [chapter01-fundamentals](chapter01-fundamentals.md) — background on the terms defined here
- [chapter04-tooling-landscape](chapter04-tooling-landscape.md) — the tools referenced in the tooling decision rules
- [chapter05-maintenance-governance](chapter05-maintenance-governance.md) — the governance rules referenced here
- [chapter06-search-retrieval-rag](chapter06-search-retrieval-rag.md) — the retrieval rules referenced here
- [chapter07-ai-ready-kb](chapter07-ai-ready-kb.md) — the AI-readiness rules referenced here
- [chapter10-anti-patterns](chapter10-anti-patterns.md) — anti-patterns these rules prevent
