# Appendix: Cheatsheet

Quick-reference tables assembled from the chapters. Use this page when you need an answer fast; follow the chapter links for the reasoning behind each row.

---

## 1. Tool Architecture Selection (Chapter 4)

| Dimension | Git-Backed (Docs-as-Code) | Database-Backed (Wikis) |
|:--- |:--- |:--- |
| **Source of Truth** | Markdown/MDX files co-located with code inside Git repositories. | Centralized relational or document database (e.g., PostgreSQL, custom JSON blocks). |
| **Authoring Workflow** | Developers write locally in IDEs (VS Code, Neovim) using plain text. | Rich-text WYSIWYG editors, drag-and-drop block interfaces. |
| **Governance & Quality** | Pull/Merge Requests, automated CI/CD linting (`markdownlint`, `Vale`, `lychee`). | Manual page reviews, permission groups, or external plugin bots. |
| **Versioning & Releases** | Branches, commits, and tags mirror exact software release versions. | Page revision history, space-level backups. |
| **Primary Advantage** | Documentation evolves synchronously with code changes, eliminating drift. | Extremely low barrier to entry for non-technical PMs, HR, and business leads. |
| **Primary Weakness** | High technical barrier for non-developers; requires Node/Python build pipelines. | High tendency for search decay, stale pages, and disconnection from live code. |

**Selection guidance:**

| Criterion | Evaluation Guidance |
|:--- |:--- |
| **Team Size** | Small teams (5–20): low-overhead static sites (MkDocs, Docusaurus) or lightweight Git vaults. Medium (20–100): hybrid systems (GitBook, Slite) balancing Git-sync with cross-departmental editing. Large enterprises (100+): standardized Internal Developer Portals (Backstage) or Jira-connected wikis (Confluence). |
| **Technical vs. Non-Technical** | 100% engineer-authored content → Git-backed Markdown. PM/HR/business co-authors needed → database-backed UI tools (Confluence, Notion) or Git-sync tools (GitBook). |
| **Search Quality** | Use lexical (BM25) for exact parameter/symbol matches; compare lexical, dense, and hybrid retrieval on representative queries before selecting a default. |
| **Integrations** | Deep integration with issue trackers (Jira/GitHub Issues), CI/CD pipelines (`lychee`, `markdownlint`, `Vale`), and Slack bots to prevent drift. |
| **Pricing** | Self-hosted OSS (MkDocs, Docusaurus, Outline, Backstage): zero licensing cost, platform-engineering overhead. Commercial SaaS (GitBook, Slite, Confluence, Fern): per-seat fees. |

---

## 2. Diátaxis Quadrants (Chapter 3)

| Quadrant | Orientation | Reader's Need | Example |
|:--- |:--- |:--- |:--- |
| **Tutorials** | Learning-oriented, practical | "Teach me, hold my hand" | Getting-started walkthrough |
| **How-To Guides** | Goal-oriented, practical | "Show me how to solve this problem" | "How to rotate an API key" |
| **Reference** | Information-oriented, theoretical | "Tell me the facts, precisely" | API parameter tables |
| **Explanation** | Understanding-oriented, theoretical | "Help me understand why" | Architecture rationale doc |

## C4 Diagram Levels (Chapter 3)

| Level | Diagram Name | Primary Audience | Core Elements Shown |
|:--- |:--- |:--- |:--- |
| **1** | System Context | Non-technical & technical stakeholders, PMs | System boundaries, personas, external dependencies |
| **2** | Container | Architects, developers, ops engineers | Deployable units (apps, services, DBs, queues) & protocols |
| **3** | Component | Developers & component architects | Internal modules, controllers, repositories, interfaces |
| **4** | Code | Software engineers | Class diagrams, interfaces, functions (optional, auto-generate) |

---

## 3. RAG Calibration Guide (Chapter 6, 11)

All numeric settings below are starting hypotheses. Build a labeled, representative query set and choose settings from retrieval and answer quality, latency, and cost.

| Pipeline Stage | Starting hypothesis | Validate locally |
|:--- |:--- |:--- |
| **Chunking — prose** | Test 500–800 tokens, 50-token overlap | Retrieval/answer quality, latency, cost, relevant-sentence density |
| **Chunking — source code** | Test 200–400 tokens, split along AST boundaries | Retrieval/answer quality, latency, cost |
| **Chunking — dense reference/regulatory text** | Test 800–1200 tokens | Retrieval/answer quality, latency, cost |
| **Chunking — data tables** | Test 1 row per chunk, with injected header | Table question accuracy and context cost |
| **Enrichment** | Test contextual retrieval with a 50–100 token summary | Compare to a no-enrichment baseline; source-reported percentage improvements vary |
| **Hybrid Fusion** | Compare BM25 + dense vector; start RRF at k=60 | Exact-identifier and conceptual-query recall against single-mode baselines |
| **First-stage retrieval** | Test 12–20 candidates (and larger sets if needed) | Recall versus reranker latency/cost |
| **Reranking** | Test a Cross-Encoder with 5–10 final chunks | Answer quality and context budget |
| **Evaluation** | RAGAS / DeepEval plus task-specific human review | Calibrated, risk-appropriate thresholds |

**When to use which search mode:** exact symbols/SKUs/error codes → BM25 lexical. Conceptual/natural-language/multi-lingual queries → dense vector semantic search. Mixed, entity-heavy engineering corpora → Hybrid Retrieval (BM25 + vector via RRF).

---

## 4. Continuous Context Model (Chapter 5)

| Context Type | Definition | Update Mechanism |
|:--- |:--- |:--- |
| **Declared Context** | Institutional human knowledge, business rules, domain ontologies, strategic intent | Cannot be computed from code; periodic human re-validation |
| **Derived Context** | Summaries from technical state (schemas, lineage, incident histories, freshness) | Computed automatically via pipeline integrations |
| **Observed Context** | Inferred system behavior from actual usage (e.g. tables joined in most queries) | Inferred continuously from telemetry, logs, query patterns |

## KB Health Metrics (Chapter 5)

| Maintenance Dimension | Best Practice | Key Target Metric / Tool |
|:--- |:--- |:--- |
| **Freshness Engine** | Event-driven updates triggered on Jira/PR close events | Reviewable update proposals, including Code Wiki `/doc-resync` drafts |
| **Ownership** | Single named owner (DRI) in frontmatter schema | 100% of Tier 1/2 docs with named owner |
| **Linting Pipeline** | Automated syntax, style, and link checking in CI | `markdownlint`, `Vale`, `Lychee` |
| **Stale Content** | De-index active-search copies of archived files; apply a 4-tier authority hierarchy | Confirm archives are absent from active indexes and any published AI manifests |
| **Onboarding** | Assign new hires a Week 1 "Fix-PR" task on setup guides | First production commit in ~3–5 days |

**Automated docs review impact (illustrative, source-/case-specific):**

| Illustrative, Source-/Case-Reported Metric | Before | After |
|:--- |:--- |:--- |
| Avg. Review Cycles per Docs PR | 2.4 cycles | 1.4 cycles |
| Time to First Feedback | 1–3 days | Instant (inline PR comments) |
| Style-Related Review Comments | ~60% of human review time | ~10% |
| Broken Links Shipped to Prod | Monthly occurrences | Rare |

---

## 5. IF/THEN Decision Rules, Condensed (Chapter 11)

| If… | Then… |
|:--- |:--- |
| KB primarily serves developers | Docs-as-Code (Git-backed), co-located with source |
| Non-technical stakeholders must co-author | Database-backed wiki or hybrid (GitBook-style two-way Git sync) |
| Enterprise, 100+ devs, microservices | Internal Developer Portal (Backstage TechDocs, Cortex) |
| Need interactive UI without executing client-side JS | Markdoc (AST-based), not raw MDX |
| Structuring by reader intent | Diátaxis: Tutorials / How-To / Reference / Explanation |
| Mixing sprint execution + long-term insight | PARA (execution) + Zettelkasten (insight) in a Hub-and-Spoke model |
| Need a repo entry point | Root `START_HERE.md`, readable in under 5 minutes |
| Naming files/ADRs | Lowercase hyphenated, imperative present tense (e.g. `0007-use-postgres.md`) |
| Docs prone to drift/decay | Single named DRI owner in frontmatter, not a team/committee |
| Someone asks a question answerable by docs | "Link-First" rule: reply with canonical URL, or PR the page first |
| Ticket touches infra/API/runbooks | Doc updates mandatory in Definition of Done, block merge until done |
| Automating CI quality gates | `markdownlint` (syntax) + `Vale` (style) + `Lychee`/`Baler` (links) |
| Doc becomes outdated | Archive it, banner it non-authoritative, de-index from search/AI |
| Searching exact symbols/SKUs/error codes | Lexical BM25 |
| Searching conceptual/natural-language queries | Dense vector semantic search |
| Querying mixed entity-heavy corpora | Compare lexical, dense, and hybrid retrieval; start RRF at k=60 and validate locally |
| Setting RAG chunk sizes | See calibration table above (§3); select from local evaluation |
| Configuring first-stage RAG retrieval | Start at 12–20 candidates and 5–10 final chunks; tune for quality, latency, and cost |
| Making docs discoverable to AI agents/MCP servers | Consider emerging `/llms.txt` + optional `/llms-full.txt`; test actual target-consumer use |
| Preventing AI hallucination/conflicting answers | 4-Tier Document Authority Hierarchy, Tier 1 read-only for AI |
| Structuring ADRs for coding agents | `applies_to` glob, RFC 2119 keywords, <200 line budget, automated `verify` command |
| Maintaining docs as code evolves | Anchored Code Wiki draft proposals with checks, `TODO-VERIFY`/`CONTRADICTION`, and appropriate human review |

---

← [Prev: Glossary](appendix-glossary.md) | [Index](README.md)
