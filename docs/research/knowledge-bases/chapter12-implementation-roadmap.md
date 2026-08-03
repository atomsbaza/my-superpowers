# Implementation Roadmap

Establishing a software engineering knowledge base (KB) from scratch requires treating documentation as **operational software infrastructure** rather than a static, one-time administrative chore. 

Here is a step-by-step implementation roadmap grounded in industry standards and empirical research, guiding a project from zero to a healthy, AI-ready knowledge platform.

---

## Phase 1: Tool Selection & Architectural Decisions

Before writing documentation, make three sequential architectural decisions based on your team's profile and workflow:

```
 TOOL SELECTION DECISION TREE
 ┌─────────────────────────────────────────────────────────────────┐
 │ 1. Define Primary Audience & Purpose │
 │ (Is it for technical ICs/code, or cross-functional team PMs?)│
 └────────────────────────────────┬────────────────────────────────┘
 │
 ┌──────────────┴──────────────┐
 ▼ ▼
 Technical ICs / Developers Cross-Functional / PMs
 ┌──────────────────────────────┐ ┌──────────────────────────────┐
 │ 2. Architecture Model │ │ 2. Architecture Model │
 │ Docs-as-Code (Git-backed) │ │ Database-Backed Wiki │
 └──────────────┬───────────────┘ └──────────────┬───────────────┘
 │ │
 ▼ ▼
 ┌──────────────────────────────┐ ┌──────────────────────────────┐
 │ 3. Static Site Engine │ │ 3. Collaborative Engine │
 │ MkDocs, Docusaurus, or │ │ GitBook (Git-sync), │
 │ Markdoc AST │ │ Confluence, Notion, Slite │
 └──────────────────────────────┘ └──────────────────────────────┘
```

1. **Identify Purpose and Audience**: Determine whether the KB serves engineering execution (architecture, API specs, runbooks) or cross-functional alignment (sprint planning, HR, product vision).
2. **Select the Storage Architecture (Git-Backed vs. Database-Backed)**:
 * **Docs-as-Code (Git-Backed)**: Recommended for technical teams. Co-locating plain Markdown files directly inside the code repository ensures documentation branches, reviews, and versioning evolve synchronously with code changes, eliminating drift.
 * **Database-Backed (Wiki/Workspace)**: Appropriate when non-technical product managers, designers, or business analysts must co-author material. Tools with two-way Git synchronization (e.g., GitBook) bridge this gap.
3. **Choose the Rendering Framework**: If using Docs-as-Code, adopt standard static site generators like **MkDocs** (Python-based, ultra-fast compile times), **Docusaurus** (React/MDX, native versioning), or **Markdoc** (Stripe’s open-source Markdown-superset parsing to a declarative AST for safe UI tags).

---

## Phase 2: Minimal Initial Structure (Avoid Over-Engineering)

**Rule of Thumb**: Start with a lean, shallow structure. Prematurely creating 15-field templates or deeply nested subfolders causes high administrative friction, discouraging developer contributions.

### Recommended Minimal Directory Layout
Adopt a lightweight top-down folder hierarchy with numerical prefixes to enforce logical file ordering:

```
/
├── START_HERE.md # Canonical 5-minute project entry point
├── AGENTS.md # AI agent instructions & workspace rules
├── 00_Inbox/ # Frictionless capture for raw/fleeting notes
├── 01_Projects/ # Active sprint work & milestone initiatives
├── 02_Architecture/ # C4 diagrams, system design specs, & ADRs
│ └── adr/ # Immutable Architecture Decision Records
├── 03_Operations/ # Incident runbooks & troubleshooting guides
└── 04_Archive/ # Deprecated specs (de-indexed from search)
```

### Information Architecture Frameworks
Combine two structural models:
* **The Diátaxis Framework**: Divide technical prose strictly by **user intent** into four non-overlapping quadrants: *Tutorials* (learning-oriented), *How-To Guides* (goal-oriented recipes), *Reference* (terse, factual specifications), and *Explanation* (conceptual rationale).
* **The PARA System**: Organize operational files by **actionability**: *Projects* (deadline-driven), *Areas* (ongoing responsibilities), *Resources* (reference topics), and *Archives* (inactive storage).

---

## Phase 3: Seeding Content (The First 10 Pages)

Do not attempt to document the entire system upfront—stalling in an infinite rewrite loop is a primary failure mode. Publish as soon as you have ~5 to 10 core operational pages:

1. **`START_HERE.md`**: Placed at the root; readable in under 5 minutes. Covers: (1) high-level system purpose, (2) team roster and roles, (3) current sprint goals, (4) critical architecture pointers, and (5) credential/environment setup links.
2. **Environment Setup & Quickstart (`01_quickstart.md`)**: A step-by-step tutorial guiding a developer from `git clone` to running the application locally.
3. **System Context & Container Diagrams (`02_architecture.md`)**: Level 1 and Level 2 **C4 Model** diagrams showing system boundaries, external dependencies, deployable containers, and protocols.
4. **Primary Architecture Decision Record (`adr/0001-core-stack.md`)**: Uses Michael Nygard’s 5-section template (*Title, Status, Context, Decision, Consequences*) to capture the foundational stack choice.
5. **Top Operational Runbook (`03_runbook_db_pool.md`)**: Prescriptive step-by-step diagnostic and remediation steps for the most common P1/P2 production alert.
6. **Coding Standards & Conventions**: Guidelines for language-specific style, testing requirements, and error-handling patterns.
7. **API/Interface Specifications**: OpenAPI or Protobuf schemas describing core service contracts.
8. **Onboarding Checklist (30-60-90 Day Expectations)**: Explicit milestones and KPIs for new hires.
9. **Support & Escalation Pathways**: PagerDuty schedules, Slack triage channels, and Tier-2 escalation procedures.
10. **Repository Glossary**: Canonical definitions of domain terms and abbreviations.

---

## Phase 4: Launch, Culture, & Adoption Workflows

A knowledge base succeeds through cultural alignment and operational gates, not passive storage:

```
 HANDBOOK-FIRST WORKFLOW
 ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
 │ Question Asked │ ──► │ Does Doc Exist in │ ──► │ Share Canonical │
 │ in Slack/Teams/PR │ │ SSoT Repo? │ Yes │ Doc URL Link │
 └───────────────────┘ └───────────────────┘ └───────────────────┘
 │
 No │
 ▼
 ┌───────────────────┐
 │ Open Docs PR/MR │
 │ First, Share PR │
 └───────────────────┘
```

* **The "Link-First" Communication Rule**: When engineers ask questions in Slack or code reviews, team members reply exclusively with a link to the canonical documentation. If the documentation does not exist, the answer is drafted in a documentation Pull Request first, and the PR link is shared.
* **Definition of Done (DoD) PR Gate**: Feature PRs altering API schemas, configuration parameters, or infrastructure **MUST NOT be merged** without accompanying Markdown updates in the same PR.
* **Single Named Ownership (DRI)**: Require an explicit `owner` handle in every file's YAML frontmatter (e.g., `owner: "team-platform"` or `owner: "alex-garcia"`). Committee ownership leads to zero accountability.
* **The Onboarding "Fix-PR" Pattern**: Assign new hires a Week 1 task to execute setup guides, document every point of friction or outdated command, and submit a documentation PR by Day 3–5. This builds an immediate contribution habit while fixing setup guides for the next cohort.

---

## Phase 5: Maintenance Rhythm & Continuous Governance

Documentation decay is a physics problem: software changes continuously while static prose remains frozen.

### Event-Driven Updates vs. Calendar Reminders
Transition from calendar reminders to **event-driven maintenance**. Tie documentation reviews directly to Jira ticket closures, GitHub PR merges, or release milestones. Closing a infrastructure ticket automatically triggers a review task or diff proposal for affected runbooks.

```
 DOCS-AS-CODE CI/CD QUALITY PIPELINE
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ Git Commit │ ──► │ markdownlint │ ──► │ Vale │ ──► │ Lychee │
 │ (MD/MDX File)│ │(Syntax Check)│ │(Prose Check) │ │(Link Checker)│
 └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
 │
 ▼
 ┌──────────────────────────────┐
 │ Automated PR/MR Review Gate │
 └──────────────────────────────┘
```

### Automated Quality Gates (CI/CD Linters)
Integrate automated linters into GitHub Actions or GitLab CI to block broken content before it hits main branches:
* **`markdownlint`**: Enforces syntax formatting, heading hierarchies, and list spacing.
* **`Vale`**: Enforces prose style guide rules, active voice, non-inclusive language checks, and readability scores (e.g., Flesch-Kincaid).
* **`Lychee` / `Baler`**: Scans files asynchronously for dead internal links, broken anchors, and expired external domains.

### Stale Content Archiving Policy
* **Never Delete—Archive and De-index**: Move superseded documents to `04_Archive/`, prepend a top-line Markdown banner marking them as non-authoritative, and **de-index them from search engines, vector databases, and `llms.txt` manifests**. Stale documentation carrying clean formatting actively misdirects developers during outages.
* **Quarterly Drift Audit**: Run a quarterly script filtering for pages not updated in $>90$ days, cross-referencing them against closed Jira components to identify high-risk documentation drift.

---

## Phase 6: Optional AI / RAG Layer (Scaling & Automation)

Once the Markdown repository and CI linters are stable, layer in AI capabilities for automated maintenance and AI-assistant consumption:

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

1. **Serve `llms.txt` and `llms-full.txt`**: Serve machine-readable indexes at the domain/repo root to allow IDE coding assistants (Cursor, Copilot, Claude Code) to navigate technical documentation cleanly without burning context tokens on HTML sidebars.
2. **Enforce a 4-Tier Document Authority Hierarchy**:
 * **Tier 1 (Source of Truth)**: Read-only for AI. Accepted ADRs, security policies, and executive directives.
 * **Tier 2 (Core Knowledge)**: Architecture design specs and API contracts.
 * **Tier 3 (Implementation)**: Active sprint notes and transient reports.
 * **Tier 4 (Archive)**: Deprecated specs explicitly excluded from AI retrieval.
3. **LLM-Maintained Code Wikis**: Implement workflows (such as `/generate-documentation-from-code` and `/doc-resync`) that compile codebase analysis into Markdown pages under `docs/`, using commit SHAs in `docs/log.md` to patch affected pages incrementally after merges.
4. **Production RAG & Retrieval Design**:
 * **Chunking**: Set prose chunk sizes to **500–800 tokens** (50-token overlap) and code chunks to **200–400 tokens** split along AST boundaries.
 * **Hybrid Search (BM25 + Dense Vectors)**: Fuse lexical keyword matching with vector embeddings via Reciprocal Rank Fusion ($k=60$), delivering a 10–20% recall lift on entity/code queries.
 * **Cross-Encoder Reranking**: Re-score the top 12–20 retrieved candidates down to the best 5–10 chunks for the LLM context window.
 * **Provenance Enforcement**: Force LLMs to cite exact `file:line` anchors in outputs.

---

## What to Explicitly Defer at the Start

To prevent burnout and launch failures, **do NOT do the following during the initial setup**:

* ❌ **Do NOT design elaborate folder trees or complex multi-tag taxonomies**: Structure should emerge organically from atomic links and concept clusters over time.
* ❌ **Do NOT attempt to document legacy technical debt or past meetings**: Focus exclusively on current operational reality and active sprint needs.
* ❌ **Do NOT build custom vector databases or complex RAG infrastructure upfront**: AI tools cannot fix unorganized or inaccurate source material; establish human trust and static Markdown CI quality gates first.
* ❌ **Do NOT enforce strict multi-stage approval bureaucracies**: High authoring friction leads directly to abandoned, "write-only" knowledge bases.

---

← [Prev: Decision Rules](chapter11-decision-rules.md) | [Index](README.md) →

## Related chapters
- [chapter01-fundamentals](chapter01-fundamentals.md) — why this roadmap matters
- [chapter02-information-architecture](chapter02-information-architecture.md) — the Diátaxis/PARA structure used in Phase 2
- [chapter03-documentation-frameworks](chapter03-documentation-frameworks.md) — ADR and C4 templates used in Phase 3
- [chapter04-tooling-landscape](chapter04-tooling-landscape.md) — tool selection detail for Phase 1
- [chapter05-maintenance-governance](chapter05-maintenance-governance.md) — the maintenance rhythm in Phase 5
- [chapter07-ai-ready-kb](chapter07-ai-ready-kb.md) — the optional AI/RAG layer in Phase 6
- [chapter10-anti-patterns](chapter10-anti-patterns.md) — what this roadmap explicitly avoids
