# Appendix: Glossary

Alphabetized glossary of key terms used across this research set. Chapter references point to the chapter(s) where each term is introduced or discussed in depth.

---

**Architecture Decision Record (ADR)** — an immutable, append-only historical log capturing an architecturally significant design decision, its context, considered options, and accepted engineering consequences. (Ch. 3, 11)

**Authority Tier / Document Authority Hierarchy** — a 4-tier governance structure ranking documentation from Tier 1 (authoritative Source of Truth, read-only for AI) down to Tier 4 (Archive/non-authoritative), preventing AI models and developers from treating outdated notes as ground truth. (Ch. 2, 5, 7, 11)

**Business-to-Agent (B2A)** — a proposed role for an emerging machine-readable convention such as `llms.txt`, intended to route autonomous IDE agents and MCP servers. Test real consumer support rather than assuming it is canonical. (Ch. 7)

**BM25 (Okapi BM25)** — a lexical full-text ranking algorithm refining TF-IDF with term-frequency saturation and document-length normalization; optimal for exact symbols, SKUs, and error codes. (Ch. 6, 11)

**Bus Factor** — organizational risk metric describing how few people's absence would halt a project; elevated when tacit knowledge is uncodified and concentrated in individual minds. (Ch. 1)

**C4 Model** — a four-level hierarchical framework (System Context, Container, Component, Code) created by Simon Brown to visualize software architecture across varying levels of abstraction. (Ch. 3, 11)

**Code Wiki** — a workflow in which an AI agent proposes source-anchored Markdown patches from codebase analysis and Git commit pointers (`/generate-documentation-from-code`, `/doc-resync`). Generated changes are drafts pending checks and appropriate human review. (Ch. 4, 7, 11)

**Continuous Context** — a three-part framework classifying knowledge into Declared, Derived, and Observed Context, each with its own update mechanism and cadence, replacing calendar-based review with event-driven update loops. (Ch. 4, 5)

**Context Precision** — a retrieval evaluation metric measuring whether ground-truth relevant chunks appear at the highest ranks within the retrieved context window. (Ch. 6, 11)

**Context Recall** — a retrieval evaluation metric measuring the proportion of ground-truth statements directly attributable to retrieved context chunks. (Ch. 6, 11)

**Contextual Retrieval** — an ingestion technique that prepends document-level background context to a chunk before embedding. Anthropic reports improvements for its evaluated setup; test impact on representative local queries. (Ch. 6, 11)

**Cosine Similarity** — the geometric-proximity formula used to measure similarity between dense vector embeddings in semantic search: the dot product of two vectors divided by the product of their magnitudes. (Ch. 6)

**Cross-Encoder Reranker** — a neural model (e.g. monoBERT, duoBERT, Jina Reranker v2, Cohere Reranker) that jointly evaluates query-document pairs to re-score first-stage candidates. Tune the final context size on representative tasks. (Ch. 6, 11)

**Declared Context** — institutional human knowledge (business rules, domain ontologies, strategic intent) that cannot be derived from code and requires periodic human re-validation. (Ch. 5, 11)

**Derived Context** — summarized technical state (schemas, lineage, quality scores, incident histories) that can be automatically computed and updated from underlying system telemetry. (Ch. 5, 11)

**Diátaxis Framework** — an intent-focused documentation architecture (Daniele Procida) categorizing content into four non-overlapping quadrants along two axes (studying/working, practical/theoretical): Tutorials, How-To Guides, Reference, and Explanation. (Ch. 2, 3, 11)

**Directly Responsible Individual (DRI)** — a single named owner assigned to a document or service to guarantee explicit accountability for page accuracy and freshness, replacing committee ownership. (Ch. 5, 8, 11)

**Docbird** — Twitter's 2014 internal build platform, an early pioneer of Docs-as-Code that directly inspired Google's g3doc and Spotify's TechDocs. (Ch. 4, 9)

**Docs-as-Code** — a methodology treating documentation with the same engineering discipline as software: plain-text markup, version control co-location, peer review via PR, automated CI/CD linting, and automated publishing. (Ch. 3, 4, 11)

**Docusaurus** — Meta's React/MDX static site generator for documentation, with native versioning, localization, and search integrations. (Ch. 4)

**Dead Wiki (Abandoned Wiki)** — an anti-pattern in which a disconnected, unowned wiki space drifts out of sync with the codebase, becoming obsolete and misleading; fixed by a single named DRI, event-driven review triggers, and CI linters. (Ch. 5, 10)

**DORA Metrics / DORA Four Keys** — DevOps Research and Assessment performance metrics (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Failed Deployment Recovery Time / MTTR); accurate documentation directly compresses Lead Time for Changes and MTTR. (Ch. 1, 8)

**Faithfulness / Groundedness** — an evaluation metric measuring factual consistency of an LLM response against retrieved context passages. Set acceptance thresholds through local evaluation and risk-based review rather than treating published values as universal SLAs. (Ch. 6, 11)

**Folksonomy** — ad-hoc, user-generated tagging without a controlled vocabulary; frictionless initially but degrades into "tag explosion" as synonyms proliferate. (Ch. 2)

**g3doc** — Google's internal Docs-as-Code system co-locating Markdown next to source code inside its `google3` monorepo, establishing that code is the ultimate authority. (Ch. 4, 9)

**Golden Path** — a pre-configured software template (as used in Spotify's Backstage) that generates a standardized repository skeleton complete with default documentation directories and build pipelines. (Ch. 9)

**Hub-and-Spoke Model** — an information-architecture pattern combining PARA (hub of action) with Zettelkasten (spoke of insight), linking rather than moving files so permanent notes survive project archival. (Ch. 2)

**Hybrid Retrieval** — a search architecture fusing exact keyword matching (BM25) and dense vector semantic search, typically combined via Reciprocal Rank Fusion, to maximize precision and recall across mixed technical corpora. (Ch. 6, 11)

**Internal Developer Portal (IDP)** — a centralized catalog (e.g. Spotify Backstage, Port, Cortex) aggregating service ownership metadata, API schemas, scorecards, documentation, and self-service "golden paths." (Ch. 4, 8, 9)

**Johnny Decimal** — a numbered-hierarchy organizational framework (Johnny Noble) indexing content via a fixed 10×10 tree; low learning curve, suited to operations and archiving. (Ch. 2)

**Knowledge Silo** — an anti-pattern where tacit or documented knowledge is locked inside one team or individual's head, unreachable by the rest of the organization; addressed by onboarding fix-PRs, promotion incentives, and LLM Code Wikis. (Ch. 1, 8, 10)

**"Link-First" Rule** — an organizational communication norm requiring team members to answer inquiries by linking to canonical documentation, or opening a documentation PR first if the page does not exist. (Ch. 2, 5, 8, 9, 11)

**`llms.txt`** — an emerging machine-readable convention for a domain-root documentation index. Publish it only for target consumers and verify discovery, parsing, freshness, access control, and actual use. (Ch. 2, 4, 7, 11)

**`llms-full.txt`** — an optional concatenated Markdown export for AI consumption. Validate its size, freshness, access control, and target-consumer behavior before relying on it. (Ch. 2, 4, 7, 11)

**"Lost in the Middle" Phenomenon** — the tendency of LLMs to attend well to information at the beginning or end of a context window while overlooking facts placed in the middle. (Ch. 6, 11)

**`Lychee` / `Baler`** — fast, async link-checking tools scanning Markdown files in CI/CD workflows to detect broken internal paths, dead URLs, and expired domains. (Ch. 3, 4, 5, 11)

**MADR (Markdown Architectural Decision Records)** — an ADR template expanding the classic Nygard template with Decision Drivers, Considered Options, and Pros/Cons comparison matrices. (Ch. 2, 3)

**Map of Content (MOC)** — a fluid Markdown hub page aggregating links to atomic notes within a specific domain without enforcing rigid folder trees. (Ch. 2, 11)

**Markdoc** — Stripe's open-source Markdown-superset framework parsing content into a declarative Abstract Syntax Tree (AST) for static build-time validation and safe UI component rendering, without executing untrusted client-side JavaScript. (Ch. 3, 4, 7, 9, 11)

**`markdownlint`** — a static analysis linter enforcing Markdown syntax rules, heading hierarchies, list indentation, and formatting standards. (Ch. 3, 4, 5, 11)

**Markform** — a Markdown-extension framework using invisible HTML comments to define fields, instructions, and validation rules inside `.form.md` files for structured agent workflows. (Ch. 7)

**MkDocs / Material for MkDocs** — a fast, Python-based static site generator widely used for platform documentation. (Ch. 4)

**Nygard Template** — the classic 5-section ADR template (Title, Status, Context, Decision, Consequences) coined by Michael Nygard in 2011; a controlled comparison reported in an arXiv preprint found it outperformed more complex templates in readability and adoption speed — promising empirical evidence, not a universal mandate. (Ch. 2, 3)

**Observed Context** — inferred system behavior based on actual usage patterns (e.g. tables joined in most queries, silent deprecations), continuously inferred from telemetry and logs. (Ch. 5)

**Orphan Page** — an anti-pattern in which deeply nested, unlinked documents become unreachable by search or navigation; fixed by networked Zettelkasten links, Maps of Content, and `index.md` catalogs. (Ch. 2, 10)

**PARA Method** — an information-management framework (Tiago Forte) organizing workspace files into four top-down categories by actionability: Projects, Areas, Resources, Archives. (Ch. 2, 11)

**RAGAS / TruLens / DeepEval** — automated evaluation frameworks that isolate Retrieval Metrics from Generation Metrics for RAG systems, typically run as CI checks. (Ch. 6)

**Reciprocal Rank Fusion (RRF)** — a zero-shot rank-fusion algorithm combining lexical and semantic search ranks via a position-based formula. $k=60$ is a common starting value to tune on representative local queries. (Ch. 6, 11)

**Runbook** — a prescriptive, step-by-step operational guide executed by on-call engineers during system incidents to diagnose failures and minimize MTTR. (Ch. 1, 3, 11)

**Single Source of Truth (SSoT)** — an architectural rule mandating that every policy, API contract, or system configuration exists in exactly one authoritative location, preventing knowledge duplication and drift. (Ch. 1, 2, 8, 11)

**SPACE Framework** — a developer-productivity framework (Satisfaction, Performance, Activity, Communication & Collaboration, Efficiency & Flow); high-quality documentation directly boosts its Communication & Collaboration and Efficiency & Flow dimensions. (Ch. 1, 8)

**`START_HERE.md`** — a canonical repository entry point, readable in under 5 minutes by humans and entering AI agents, providing immediate project orientation. (Ch. 2, 3, 7, 11)

**Tacit Knowledge** — unwritten, highly contextual, experiential insight residing solely in developers' minds (debugging heuristics, undocumented dependencies); its opposite, Explicit Knowledge, is systematized and searchable. (Ch. 1)

**Tag Explosion** — an anti-pattern in which uncontrolled, ad-hoc folksonomy tagging accumulates synonyms and near-duplicates until tags stop being useful for discovery. (Ch. 2, 10)

**TechDocs / Backstage** — Spotify's Docs-as-Code solution integrated into its open-source Internal Developer Portal, unifying documentation with the service catalog, ownership metadata, and scorecards. (Ch. 3, 4, 9)

**User Profile** — per ISO/IEC/IEEE 26511, a unique attribute set (e.g. job function or clearance level) that a knowledge system uses to restrict or grant access to specific documentation spaces. (Ch. 5)

**`Vale`** — an open-source prose linter enforcing style guide compliance, active voice, terminology, and readability metrics (e.g. Flesch-Kincaid) across Markdown files. (Ch. 3, 4, 5, 11)

**Verification Tax** — the cognitive overhead engineers spend auditing AI-generated code or content that looks correct but contains subtle errors; grounded, machine-readable documentation reduces it. (Ch. 5)

**Zettelkasten Method** — a bottom-up knowledge system (Niklas Luhmann) built around atomic, self-contained Permanent Notes connected through explicit bidirectional links, alongside Fleeting and Literature Notes. (Ch. 2, 10, 11)

---

← [Index](README.md) | [Next: Cheatsheet](appendix-cheatsheet.md) →
