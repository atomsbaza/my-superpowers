# Information Architecture

## 1. Organizational Paradigms: Hierarchical vs. Networked vs. Tag-Based

Information Architecture (IA) governs how developers and automated agents navigate a technical knowledge base. Selecting the appropriate organizational model depends on the nature of the information, its rate of change, and its primary usage pattern.

```
 ORGANIZATIONAL PARADIGMS
 ┌───────────────────┬───────────────────┬───────────────────┐
 │ Hierarchical │ Networked/Linked │ Tag-Based │
 ├───────────────────┼───────────────────┼───────────────────┤
 │ Strict tree │ Node-graph │ Multi-label │
 │ Single-parent │ Associative links │ Categorization │
 └───────────────────┴───────────────────┴───────────────────┘
```

### Hierarchical (Folder Trees)
* **Mechanics**: A rigid, top-down tree structure where every file resides in exactly one parent folder.
* **When It Wins**: Operational execution, short-term project filing, and environments requiring strict access boundaries or clear physical folder mapping.
* **Failure Modes**: Scales poorly in large codebases. It forces complex technical relationships into a single parent folder, causing "orphan pages," content duplication, and high cognitive overhead during search.

### Networked / Linked (Graph-Based)
* **Mechanics**: Documents act as nodes in a graph connected by explicit bidirectional links (`[[Note Title]]`).
* **When It Wins**: Long-term conceptual knowledge, system architecture design patterns, and cross-cutting technical domains. It mirrors human associative mental models and allows non-linear discovery.
* **Failure Modes**: Can degrade into a high-entropy, chaotic "note museum" without regular curation or structural entry points.

### Tag-Based (Folksonomy / Metadata)
* **Mechanics**: Attaching flat or nested labels (`#status/draft`, `#domain/auth`) to notes, allowing a single document to exist across multiple filter dimensions.
* **When It Wins**: Cross-cutting queries, state tracking (`#toread`, `#processing`), and multi-dimensional filtering across diverse topics.
* **Failure Modes**: "Tag explosion". Without strict schema governance, synonyms proliferate (`#postgres`, `#postgresql`, `#pg`), destroying search precision in both lexical indexing and vector retrieval.

---

## 2. Structural Frameworks: PARA, Zettelkasten, MOCs, & Johnny Decimal

| Framework | Originator | Core Organizing Principle | Primary Use Case | Learning Curve |
|:--- |:--- |:--- |:--- |:--- |
| **PARA** | Tiago Forte | **Actionability**: Organized by time-horizon and deadline. | Project execution & workspace focus. | Low |
| **Zettelkasten** | Niklas Luhmann | **Atomicity & Connectivity**: Single ideas linked bidirectionally. | Deep research, technical pattern building. | High |
| **Maps of Content (MOCs)** | Nick Milo (LYT) | **Fluid Aggregation**: Non-hierarchical hub pages. | Navigating complex node clusters. | Medium |
| **Johnny Decimal** | Johnny Noble | **Numbered Hierarchy**: Indexing via a fixed $10 \times 10$ tree. | Operations, IT administration, archiving. | Low |

### The PARA Method
PARA categorizes all workspace assets into four strict top-down folders based on actionability:
1. **Projects**: Short-term efforts with a concrete goal and fixed deadline (e.g., `01 Projects/Q3-Auth-Migration`).
2. **Areas**: Long-term ongoing responsibilities without a deadline (e.g., `02 Areas/Infrastructure-Reliability`).
3. **Resources**: Curated library of external reference materials and topics of ongoing interest (e.g., `03 Resources/Kafka-Benchmarking`).
4. **Archives**: Inactive items from the above three categories retained for cold storage.

### Zettelkasten
A bottom-up system built around three distinct note lifecycles:
* **Fleeting Notes**: Frictionless, temporary raw captures (inbox items, scratchpad dumps).
* **Literature Notes**: Summaries and key takeaways from external sources (papers, API specs) written in your own words, stored separately in `Resources`.
* **Permanent Notes**: The core of the system—atomic, self-contained ideas written in clear prose and linked into the existing note graph.

### Maps of Content (MOCs)
MOCs solve the chaos of unorganized networked notes. An MOC is a fluid Markdown hub document that links to atomic notes within a specific domain (e.g., `Observability MOC.md`), providing entry points without enforcing static subfolder trees.

### The Hybrid "Hub-and-Spoke" Integration Architecture
To prevent the conflict where timeless permanent notes get trapped and archived inside temporary project folders, knowledge platforms implement a **Hub-and-Spoke Model**:

```
 ┌────────────────────────────────────────────────────────┐
 │ 00 Inbox (Fleeting) │
 └───────────────────────────┬────────────────────────────┘
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ PARA Folders (Hub of Action) │
 │ 01 Projects │ 02 Areas │ 03 Resources │ 04 Archive│
 └───────────────────────────┬────────────────────────────┘
 │
 (Links, Never Moves Files)
 │
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ 10 Zettelkasten (Spoke of Insight) │
 │ [Permanent Atomic Notes & MOCs] │
 └────────────────────────────────────────────────────────┘
```

* **Physical Separation**: `01 Projects` holds active project management files; `10 Zettelkasten` remains a co-equal, permanent top-level folder for atomic knowledge.
* **Functional Linkage**: Project notes link to Permanent Notes (`"We are adopting [[Idempotency-Keys]] for this API"`). When the project closes and moves to `04 Archive`, the Permanent Note stays intact in `10 Zettelkasten` for future projects.

---

## 3. Page Templates & Recommended Sections

Standardizing page layouts enforces structural completeness and allows static site generators, linter tooling, and AI agents to parse files deterministically.

### Architecture Decision Records (ADRs)

#### Classic Nygard Template vs. MADR Template
* **Nygard (5 Sections)**: *Title, Status, Context, Decision, Consequences*. A controlled comparison reported in an arXiv preprint found this lean template easier to comprehend and adopt than several more elaborate alternatives — promising empirical evidence, not a universal mandate (see Ch. 3).
* **MADR (Markdown Architectural Decision Records)**: Expands Nygard by adding *Decision Drivers*, *Considered Options*, and *Pros/Cons Comparison Matrices*. Recommended for large-scale enterprise decisions where explicit rationale and trade-off evaluation are required.

#### Agent-Optimized ADR Schema
When coding agents process ADRs, prose is replaced with machine-verifiable directives:
* **`applies_to` File Globs**: Restricts execution scope (e.g., `applies_to: "src/api/v2/**/*.ts"`) so agents don't burn context loading irrelevant rules.
* **Normative Imperative Directives**: Uses RFC 2119 keywords (`MUST`, `MUST NOT`, `SHALL`) instead of conversational rationale.
* **Verifiable Checks**: Includes inline grep/lint validation scripts so agents or CI pipelines can automatically verify compliance.
* **Token Budget**: Enforces a strict line limit (<200 lines per record) to maintain LLM context adherence.

### Integration & Tooling Documentation Templates

```
 DOCUMENTATION TEMPLATE SCHEMAS
 ┌──────────────────────────────────┬──────────────────────────────────┐
 │ Integration Source Page │ Tool Page │
 │ (source.md) │ (tools/*.md) │
 ├──────────────────────────────────┼──────────────────────────────────┤
 │ ## About │ ## About │
 │ ## Example │ ## Example │
 │ ## Reference │ ## Parameters (Optional) │
 │ ## Available Tools (Optional) │ ## Output Format (Optional) │
 │ {{< list-tools >}} │ ## Compatible Sources (Optional) │
 └──────────────────────────────────┴──────────────────────────────────┘
```

* **Integration Source Page (`source.md`)**: Required H2 headings must follow a strict sequential order: `## About`, `## Example`, and `## Reference`. Optional allowed sections include `## Requirements`, `## Available Tools` (must contain the `{{< list-tools >}}` shortcode), `## Advanced Usage`, and `## Troubleshooting`.
* **Tool Page (`tools/<tool-name>.md`)**: Required H2 headings: `## About` and `## Example`. Optional sections: `## Compatible Sources` (must contain `{{< compatible-sources >}}`), `## Parameters`, `## Output Format`, `## Reference`, and `## Troubleshooting`.
* **Repository Entry Point (`START_HERE.md`)**: Designed to be read in under 5 minutes. Contains: (1) Project Overview, (2) Team Roster & Timezones, (3) Current Sprint State, (4) Critical Architecture Decisions, and (5) Pointers to Credentials/Environment setup.

### Diátaxis Intent-Based Quadrants

```
 DIÁTAXIS FRAMEWORK QUADRANTS
 
 PRACTICAL THEORETICAL
 ┌───────────────────┬───────────────────┐
 STUDYING │ TUTORIALS │ EXPLANATION │
 │ (Learning-Oriented)│ (Understanding-Oriented)│
 ├───────────────────┼───────────────────┤
 WORKING │ HOW-TO GUIDES │ REFERENCE │
 │ (Goal-Oriented) │ (Information-Oriented)│
 └───────────────────┴───────────────────┘
```

1. **Tutorials (Learning-Oriented)**: Prescriptive, hands-on lessons for beginners. Focuses on guiding action without interrupting the lesson with deep theoretical explanations.
2. **How-To Guides (Goal-Oriented)**: Task-focused "recipes" for competent users solving specific real-world problems.
3. **Reference (Information-Oriented)**: Factual, terse, and structured descriptions of the underlying system (APIs, schemas, CLI parameters) designed for rapid lookup.
4. **Explanation (Understanding-Oriented)**: Discursive, high-level discussions illuminating architectural design choices, context, and trade-offs.

---

## 4. Naming Conventions

Strict naming conventions ensure file system compatibility, prevent broken links, and simplify programmatic indexing.

### Filename Formatting Rules
* **Lowercase Hyphenated Slugs**: Use lowercase alphanumeric characters separated exclusively by hyphens (e.g., `0007-use-postgres-for-tenant-storage.md`). Avoid spaces, underscores, or uppercase letters in physical paths.
* **Imperative Present-Tense Verb Phrases**: Name action or decision files using present-tense imperative verb phrases (e.g., `choose-database.md`, `format-timestamps.md`, `manage-passwords.md`). This mirrors git commit message conventions and improves readability.
* **Chronological Meeting & Incident Logs**: Use ISO 8601 date prefixes for event-based documents: `YYYY-MM-DD_Topic_Summary.md` (e.g., `2026-03-15_Incident_DB_Connection_Pool_Exhaustion.md`).
* **Numbered Sequence Prefixes**: Prepend sequential two-digit prefixes to enforce reading order in static site navigation or onboarding paths (`00_overview.md`, `01_architecture.md`, `02_deployment.md`).

---

## 5. Metadata & Frontmatter Design

YAML frontmatter provides structured, machine-readable key-value pairs at the top of Markdown documents.

### Recommended Frontmatter Schema
```yaml
---
title: "Use PostgreSQL for Multi-Tenant Storage"
id: "ADR-0007"
owner: "team-platform"
applies_to: "services/tenant-db/**"
authority_tier: 1
status: "accepted" # [draft | proposed | accepted | superseded | archived]
last_reviewed: 2026-03-15
tags: [database, postgresql, multi-tenancy]
---
```

### Document Authority Tier Hierarchy
To prevent AI agents from treating informal meeting notes with the same weight as corporate architectural standards, platforms implement an explicit four-tier authority hierarchy:

```
 DOCUMENT AUTHORITY TIERS
 ┌──────────────────────────────────────────────────────────────┐
 │ TIER 1: Source of Truth (Read-Only for AI) │
 │ Executive directives, approved ADRs, security policies │
 ├──────────────────────────────────────────────────────────────┤
 │ TIER 2: Core Technical Knowledge │
 │ Architecture specs, platform design, API contracts │
 ├──────────────────────────────────────────────────────────────┤
 │ TIER 3: Implementation & Operational State │
 │ Sprint plans, active meeting notes, transient reports │
 ├──────────────────────────────────────────────────────────────┤
 │ TIER 4: Archive / Historical (Non-Authoritative) │
 │ Deprecated specs, closed sprint retrospectives │
 └──────────────────────────────────────────────────────────────┘
```

* **Tier 1: Source of Truth**: Approved architecture decision records, security policies, and executive directives. Read-only for automated agents; if an agent answer conflicts with Tier 1, the agent is wrong.
* **Tier 2: Core Technical Knowledge**: System design specifications, platform strategy documents, and core component guides.
* **Tier 3: Implementation & Operational State**: Working sprint files, daily meeting notes, and active status reports.
* **Tier 4: Archive / Historical**: Superseded documents marked explicitly with a `status: archived` frontmatter banner to exclude them from active AI retrieval and search indices.

---

## 6. Taxonomy vs. Folksonomy & Governance

* **Taxonomy (Controlled Vocabulary)**: A centralized, pre-approved list of tags and categories managed in a single schema file (e.g., `.hugo/data/filters.yaml`).
* **Folksonomy (Uncontrolled Tagging)**: Ad-hoc, user-generated labels. While frictionless, folksonomies degrade over time as developers invent overlapping tags (`#js`, `#javascript`, `#es6`), causing search fragmentation.

### Rules of Thumb for Taxonomy Governance
1. **Enforce Central Validation**: Validate all tags in CI/CD pipelines using linter scripts (`lint-docs-filters.sh`) that block pull requests containing unapproved tags.
2. **Casing Conventions**: Require **Title Case** (`Data Sources`, `Frameworks`) or strict lowercase for taxonomy keys, blocking `snake_case` or mixed casing.
3. **Orthogonal Tagging Rule**: Restrict tags to metadata attributes that cut across the entire KB (e.g., `#lang/go`, `#compliance/soc2`), and rely on bidirectional links or MOCs for conceptual categorization.

---

## 7. AI-Ready Consumption Standards (`llms.txt`)

To optimize documentation for external AI coding assistants, internal RAG systems, and agentic workflows, knowledge bases serve two machine-readable files at the domain root:

```
 llms.txt ARCHITECTURE
 ┌──────────────────────────────────┬──────────────────────────────────┐
 │ /llms.txt (Summary Index) │ /llms-full.txt (Full Context) │
 ├──────────────────────────────────┼──────────────────────────────────┤
 │ # Brand/Product Name │ Concatenated, raw Markdown │
 │ > Blockquote Summary │ corpus containing all Tier 1/2 │
 │ ## Section Name │ pages for single-pass fetch │
 │ - [Title](URL): One-line summary │ ingestion by large-context LLMs. │
 └──────────────────────────────────┴──────────────────────────────────┘
```

### A Tested `llms.txt` Shape
`llms.txt` is an emerging convention. If an intended AI consumer supports it, test a consistent shape such as a project H1, short summary, logical H2 categories, and descriptive links in the form `- [Page Title](URL): Description`. Confirm the consumer actually discovers and uses the file; do not assume a format is universally fetched or parsed.

---

## 8. Summary Checklist: High-Quality vs. Poor Knowledge Base

| Quality Dimension | High-Quality Knowledge Platform | Poor Knowledge Base Anti-Pattern |
|:--- |:--- |:--- |
| **Source of Truth** | Single canonical location per policy/spec; SSoT enforced via repo co-location. | **Duplicated Truth**: Same guidance copied across Slack, Confluence, and code comments. |
| **Contextual Rationale** | Captures "why" decisions were made, including trade-offs and rejected options. | **Write-Only Storage**: High-volume prose generated during launch but never read or updated. |
| **Discoverability** | Dual-engine PARA + Zettelkasten linked via MOCs and hybrid search. | **Orphan Pages & Deep Nesting**: Files isolated in deep folder trees unreachable by search. |
| **Freshness & Integrity** | Event-driven updates on ticket resolution/commits; automated CI linting. | **The Dead Wiki**: Unowned, stale documentation that misleads developers and AI agents. |

---

← [Prev: Fundamentals](chapter01-fundamentals.md) | [Index](README.md) | [Next: Documentation Frameworks](chapter03-documentation-frameworks.md) →

## Related chapters
- [chapter01-fundamentals](chapter01-fundamentals.md) — the value case for getting this right
- [chapter03-documentation-frameworks](chapter03-documentation-frameworks.md) — the Diátaxis quadrants referenced here in full
- [chapter04-tooling-landscape](chapter04-tooling-landscape.md) — tools that implement these organizational models
- [chapter07-ai-ready-kb](chapter07-ai-ready-kb.md) — frontmatter and authority-tier schemas in more depth
- [chapter10-anti-patterns](chapter10-anti-patterns.md) — orphan pages, tag explosion, and over-structuring failure modes
