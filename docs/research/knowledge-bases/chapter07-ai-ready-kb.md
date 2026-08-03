# AI-Ready Knowledge Bases

## 1. Structuring Markdown for LLM & Agent Consumption

Traditional human-facing documentation sites rely on complex HTML, client-side JavaScript, ads, and navigation sidebars that waste LLM context window tokens and increase processing latency. Structuring Markdown specifically for AI agents optimizes token efficiency and minimizes model hallucination.

```
 STRUCTURING MARKDOWN FOR AGENTS
 ┌────────────────────────────────────────────────────────┐
 │ Token Efficiency & AST Parsing │
 │ Plain CommonMark, Markdoc ASTs, or Markform Schemas │
 ├────────────────────────────────────────────────────────┤
 │ Context Scoping │
 │ File-glob activation (applies_to) & <200-line budget │
 ├────────────────────────────────────────────────────────┤
 │ Machine-Verifiable Directives │
 │ RFC 2119 keywords (MUST/SHOULD) + explicit verify cmd │
 └────────────────────────────────────────────────────────┘
```

### Token Efficiency & Abstract Syntax Tree (AST) Parsing
* **Clean Text vs. HTML**: Serving raw, structured Markdown instead of flattened HTML achieves up to a **10x reduction in token consumption**, resulting in faster, cheaper, and more accurate agent execution.
* **Markdoc Framework**: Stripe open-sourced **Markdoc** to parse Markdown into a declarative Abstract Syntax Tree (AST) before rendering. Unlike MDX (which compiles content directly into executable client-side JavaScript and introduces security and parsing risks), Markdoc’s declarative AST allows build-time validation, safe variable interpolation, and static analysis by compilers and LLMs without executing untrusted code.
* **Markform Schemas**: For structured agent workflows, frameworks like **Markform** extend Markdown using invisible HTML comments (`<!-- field -->`) to define fields, instructions, and validation rules inside `.form.md` files. Agents fill these forms via explicit patch operations (`set_string`), self-correcting validation errors early.

### Context Window Scoping & Token Budgets
* **File-Glob Scoping (`applies_to`)**: Coding agents burn context tokens when forced to load irrelevant rules. Attaching an `applies_to` frontmatter glob (e.g., `applies_to: "src/api/v2/**/*.ts"`) activates rules only when an agent modifies matching files.
* **Strict Line Budgets**: Following context engineering guidelines, individual rule files and Architecture Decision Records (ADRs) should be kept under **~200 lines**. Longer files consume excessive context and measurably reduce LLM instruction adherence.
* **Imperative Directives over Prose**: Replace conversational rationale with normative RFC 2119 keywords (`MUST`, `MUST NOT`, `SHOULD`). Directives like *"MUST use PgBouncer connection pooling. MUST NOT execute raw SQL queries"* are significantly easier for agents to parse and obey than long-form prose.
* **Stable Addressable IDs**: Assign addressable IDs (e.g., `R-IMG-001` or `ADR-0007`) to specific rules or decisions so code review bots, commit logs, or agents can cite exact constraints.

---

## 2. The `llms.txt` and `llms-full.txt` Convention

**`llms.txt`** is an emerging machine-readable convention, introduced by Jeremy Howard, for publishing a documentation index at a domain root. It may help some AI coding assistants and Model Context Protocol (MCP) servers navigate documentation, but consumer support and fetching behavior vary. Publish it only for identified target consumers and test that each one actually discovers and uses it.

```
 llms.txt FILE SYSTEM ARCHITECTURE
 ┌──────────────────────────────────────────────────────────────────┐
 │ /llms.txt (Summary Index) │
 │ • Single H1 (Project Name) │
 │ • Summary Blockquote (Scope & Audience) │
 │ • H2 Category Sections │
 │ • Link Items: - [Page Title](URL): One-line agent routing summary│
 ├──────────────────────────────────────────────────────────────────┤
 │ /llms-full.txt (Consolidated Context) │
 │ • Single concatenated, raw Markdown file containing full text │
 │ of key pages, OpenAPI schemas, and code examples. │
 └──────────────────────────────────────────────────────────────────┘
```

### A Practical `llms.txt` Shape
Use the commonly proposed shape as a compatibility experiment, then verify it against the consumers you support:
1. **H1 Header**: A project title.
2. **Summary Blockquote**: A short description of the product and audience.
3. **H2 Category Sections**: Logical groups such as `## Platform`, `## Guides`, and `## API Reference`.
4. **Descriptive Links**: A consistent form such as `- [Page Title](URL): Description`, explaining what is on the page and when an agent should fetch it.

### `llms.txt` vs. `llms-full.txt`
* **`llms.txt` (Summary Index)**: A curated, token-efficient index of high-value links with descriptions. Test whether target agents discover pages and fetch them individually.
* **`llms-full.txt` (Consolidated Context)**: An optional concatenated Markdown export of selected canonical pages, schemas, and examples. It can help consumers with large context windows, but its size, freshness, access controls, and actual consumption must be tested.

### Granular Content Control: `<llms-only>` and `<llms-ignore>`
Platforms like Fern allow fine-grained content tagging:
* **`<llms-only>`**: Injects verbose technical context, internal architecture notes, and cross-references that assist AI models but would clutter human-facing documentation.
* **`<llms-ignore>`**: Strips out marketing banners, navigation hints, and UI elements from LLM endpoints to conserve context tokens.

### The Business-to-Agent (B2A) Protocol Role
Traffic studies and vendor reports are context-specific: public AI crawlers, IDE agents, and MCP servers do not share a single fetching pattern. Treat `llms.txt` as an optional Business-to-Agent (B2A) routing surface and instrument or test the consumers you intend to support before making it canonical.

---

## 3. Frontmatter, Metadata & Schema Design

Structured YAML frontmatter at the top of Markdown files provides the queryable attributes necessary for RAG engines, static site generators, and LLMs to filter context before execution.

### Recommended Frontmatter Schema
```yaml
---
title: "Use PostgreSQL for Multi-Tenant Storage"
id: "ADR-0007"
owner: "team-platform"
applies_to: "services/tenant-db/**"
authority_tier: 1 # [1: SSoT | 2: Core | 3: Implementation | 4: Archive]
last_reviewed: 2026-07-15
review_interval: "90d"
status: "accepted" # [draft | proposed | accepted | superseded | archived]
sources:
 - "src/db/schema.sql"
 - "src/db/connection_pool.go"
tags: [database, postgresql, multi-tenancy]
verify: "scripts/ci/check-db-schema-compliance.sh"
---
```

### Taxonomy & Spec Governance Rules
* **Central Filter Validation**: Validate metadata values against a centralized schema (e.g., `.hugo/data/filters.yaml`) in CI pipelines using linter scripts (e.g., `lint-docs-sample-filters.sh`) to block unapproved or malformed tags.
* **Title Case Casing**: Require **Title Case** for taxonomy keys, blocking `snake_case` or mixed casing.
* **OpenAPI & Spec Discipline**: Ensure consistent `operationId` descriptors, clear `summary`/`description` fields, and strict `snake_case` parameter naming across API specs and docs. AI agents use `operationId`s and field names literally when deciding which API endpoints to invoke.

---

## 4. Document Authority Tiers & Source-of-Truth Marking

To prevent AI agents from treating informal meeting notes or outdated retrospectives with the same weight as executive security policies, knowledge bases enforce a **4-Tier Document Authority Hierarchy**.

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

### The 4-Tier Hierarchy

| Tier Level | Category | Content Types & Examples | AI Agent Operational Rules |
|:--- |:--- |:--- |:--- |
| **Tier 1** | **Source of Truth (SSoT)** | Leadership-approved directives, scorecards, security policies, accepted ADRs. | **Read-Only for AI**. Serves as the ultimate authority. If an AI agent contradicts a Tier 1 document, **the agent is wrong**. Agents must read Tier 1 files first upon session start. |
| **Tier 2** | **Core Knowledge** | System design specs, platform architecture, identity layer designs, API contracts. | The "textbook" for the codebase. Used as primary background context for feature generation and refactoring. |
| **Tier 3** | **Implementation & Analysis** | Sprint planning files, meeting notes, active status reports. | Working documents that change frequently. Used for short-term operational execution. |
| **Tier 4** | **Historical / Archive** | Superseded specs, old retrospectives, deprecated code guides. | **Non-Authoritative**. Excluded from active AI retrieval, vector search indexes, and `llms.txt`. |

### Eliminating Silent Hallucinations
When an outdated document is moved to `archive/`, it must carry a top-line Markdown banner marking it as non-authoritative:
```markdown
> ⚠️ **DEPRECATED / NON-AUTHORITATIVE**: This document was superseded by [ADR-0012](../adr/0012-new-auth.md) on 2026-03-15.
```
By removing archived files from `docs/index.md` and forcing agents to cite Tier 1 files with explicit `file:line` evidence, the system converts **silent hallucinations** into **visible, citable mismatches** that reviewers can immediately catch.

---

## 5. Repository-Grounded Agent Work Requires Evaluation

Repository-level coding-agent benchmarks such as SWD-Bench are useful evidence that codebase context matters, but they are benchmark-specific: they do not prove that a documentation format will improve every repository or task. Use feature- or snippet-level documentation tied to code and source anchors, evaluate it on representative local tasks, and retain human review for consequential changes.

## 6. Automated Documentation Generation & LLM-Maintained Code Wikis

Rather than treating documentation as a manual, one-time deliverable that decays over time, a **Code Wiki** workflow can propose updates from codebase analysis. Generated pages and resync outputs are draft patches, not automatically authoritative documentation: retain source/code anchors, executable checks, and review before accepting them.

```
 CODE WIKI: LLM-MAINTAINED WIKI ARCHITECTURE
 ┌────────────────────────────────────────────────────────┐
 │ LAYER 1: Raw Sources │
 │ Source Code, Migrations, Handlers, Configs (src/) │
 └───────────────────────────┬────────────────────────────┘
 │
 (/generate-documentation-from-code)
 │
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ LAYER 2: Persistent Compiled Wiki │
 │ docs/README.md, docs/index.md, docs/features/*.md │
 └───────────────────────────┬────────────────────────────┘
 │
 (Governed by AGENTS.md)
 │
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ LAYER 3: Schema & Agent Commands │
 │ /doc-resync (Incremental Git-SHA Delta Sync) │
 └────────────────────────────────────────────────────────┘
```

### Core Code Wiki Operations

| Command / Operation | Execution Trigger & Mechanics | Output Artifacts & Behavior |
|:--- |:--- |:--- |
| **/generate-documentation-from-code** | **Initial draft build**: Run for a new codebase or major refactor. Analyze relevant business logic and compile an anchored proposal. | Proposes structured Markdown under `docs/features/<name>.md`, `docs/data-model.md`, `docs/messaging.md`, `docs/cross-cuttings.md`, and `docs/log.md`; review before publication. |
| **/doc-resync** | **Incremental draft sync**: Inspect `git diff` from the recorded base commit and map changed files to pages through `sources[]`. | Proposes affected-page patches and a commit-pointer entry. Tier 1 and 2 changes require human approval; Tier 3 review is risk-based. Retain unresolved `TODO-VERIFY` and `CONTRADICTION` markers. |
| **Ingest** | **Catalog refresh proposal**: Run after an accepted generation or resync. | Updates routing indexes only after link, authority, access-control, and freshness checks. |

### The `START_HERE.md` Pattern
Every repository maintains a canonical `START_HERE.md` at its root designed to be read in under 5 minutes by both humans and entering AI agents:
1. **Project Overview**: System purpose and domain boundaries.
2. **Team Roster & Roles**: Service owners and contact handles.
3. **Current Sprint & State**: Active sprint goals and key board links.
4. **Critical Architecture Context**: Pointers to Tier 1 ADRs and C4 diagrams.
5. **Environment & Credentials**: Pointers to sandbox environments and setup scripts.

---

## 7. Grounding, Citation Practices & Content Trustworthiness

AI-generated documentation carries structural failure modes that must be controlled through explicit prompting, linting, and verification gates.

### Common AI Generation Anti-Patterns (GitLab Style Guide)
* **Repetition**: Restating information already covered on the page or in linked topics. Each section must add new facts without summarizing preceding text or restating titles.
* **Vague or Unverifiable Claims**: Describing system behavior without codebase grounding. Models must not speculate, infer unstated features, or invent command syntax or API parameters.

### Grounding & Evidence Enforcement Rules
1. **File and Line Anchors**: Generated technical claims should link to enforcing source files and line anchors (e.g., `src/core/UserService.go#L42-L60`) in a `Source file links` section.
2. **`TODO-VERIFY` Markers**: If an assumption lacks codebase evidence or a Tier 1 source, retain a `TODO-VERIFY` marker rather than guessing; reviewers resolve or explicitly accept it.
3. **`CONTRADICTION` Markers**: When sources conflict, retain a `CONTRADICTION` tag and alert reviewers rather than choosing an interpretation silently.
4. **Verifiable Checks**: Include inline verification scripts or commands in ADRs and frontmatter (`verify: "scripts/ci/check-db-schema-compliance.sh"`) so CI pipelines and agents can confirm ongoing compliance.

---

## 8. Agent Protocol: How AI Agents Query and Update the Knowledge Base

```
 AGENT WORKSPACE INTERACTION PROTOCOL
 ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
 │ 1. Session Start │ ──► │ 2. Routing Pass │ ──► │ 3. Targeted Fetch │
 │ Read SSoT/Rules │ │ Read index.md │ │ Follow sources[] │
 └───────────────────┘ └───────────────────┘ └───────────────────┘
 │
 ▼
 ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
 │ 6. Log Commit │ ◄── │ 5. Patch Wiki │ ◄── │ 4. Execute Work │
 │ Append log.md │ │ Update sources[] │ │ Write code/diff │
 └───────────────────┘ └───────────────────┘ └───────────────────┘
```

When an AI agent (e.g., Claude Code, Cursor, or an internal agent) enters a repository, configure an interaction protocol appropriate to its capabilities and access controls:

1. **Session Start Ritual**: The agent MUST read `START_HERE.md`, `CLAUDE.md` / `AGENTS.md` rules, and Tier 1 SSoT files before executing any task.
2. **Routing over Blind Search**: Instead of running expensive full-repo searches, the agent queries `docs/index.md` (or `KNOWLEDGE_BASE.md`) to locate the relevant concept cluster and opens only the designated Markdown pages.
3. **Targeted Evidence Fetching**: The agent reads the pre-compiled feature pages. It follows paths listed in `sources[]` *only* if line-level code verification is required.
4. **Execution & Compliance Check**: The agent executes code modifications, validating diffs against active ADR rules via embedded `verify` commands.
5. **Event-Driven Wiki Patching**: Upon task completion, the agent may run `/doc-resync` (or trigger a post-meeting/post-PR workflow) to propose affected wiki patches and update frontmatter `sources[]`. Review Tier 1/2 changes, apply risk-based review to Tier 3, and retain unresolved `TODO-VERIFY` blocks.
6. **Log SHA Commit Pointer**: The agent appends an entry to `docs/log.md` recording the `Commit: <SHA>`, `Base: <SHA>`, and updated pages, preserving the synchronization contract for subsequent agent sessions.

---

## Summary Architectural Checklist

| Architectural Layer | Implementation Standard | Enforcement Mechanism |
|:--- |:--- |:--- |
| **Markdown Formatting** | Plain CommonMark or Markdoc AST; RFC 2119 directives (`MUST`/`SHOULD`); <200 lines/file. | `markdownlint`, `Vale`, `applies_to` file globs. |
| **AI Indexing** | Optional `/llms.txt` and `/llms-full.txt` exports following a tested, consistent shape. | Validate discovery, parsing, access control, freshness, and consumer use. |
| **Authority & Governance**| 4-Tier Authority Hierarchy; Tier 1 SSoT read-only for AI. | Frontmatter `authority_tier: 1` schema; archiving banners. |
| **Code Wiki & Maintenance**| Anchored draft proposals with `sources[]` lists and SHA sync pointers in `docs/log.md`. | Review gates: human approval for Tier 1/2, risk-based review for Tier 3. |
| **Grounding & Trust** | Source/code anchors, `TODO-VERIFY` for unresolved assumptions, `CONTRADICTION` markers, and embedded `verify` scripts. | CI checks plus human review. |

---

← [Prev: Search & Retrieval / RAG](chapter06-search-retrieval-rag.md) | [Index](README.md) | [Next: Adoption & Culture](chapter08-adoption-culture.md) →

## Related chapters
- [chapter02-information-architecture](chapter02-information-architecture.md) — frontmatter schema and authority tiers introduced here
- [chapter05-maintenance-governance](chapter05-maintenance-governance.md) — governance mechanisms that keep AI-consumed docs trustworthy
- [chapter06-search-retrieval-rag](chapter06-search-retrieval-rag.md) — the retrieval pipeline this content feeds
- [chapter11-decision-rules](chapter11-decision-rules.md) — IF/THEN rules for AI-readiness decisions
