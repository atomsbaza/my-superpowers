# Maintenance and Governance

## 1. Keeping Docs Fresh: Event-Driven Updates vs. Calendar Reviews

### The Physics of Documentation Decay
Documentation decay is a physics problem, not a people problem. A document is a static snapshot of a system, whereas software reality is a continuous movie. While human developers historically compensated for bad information by cross-checking live code or asking senior peers, AI coding agents and RAG systems do not. AI tools operate with total confidence on whatever a document says, turning static, outdated text into confident, scaled operational failures.

### Event-Driven Updates
Relying on voluntary human discipline or periodic "documentation days" consistently fails when competing with deadline pressures and team turnover. High-performing engineering organizations transition from **schedule-driven** maintenance to an **event-driven update loop**:

```
 EVENT-DRIVEN UPDATE LOOP
 ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
 │ Jira / GitHub PR │ ──► │ Automated Change │ ──► │ Surgical Doc │
 │ Event Closes │ │ Detection Engine │ │ Patch / Diff PR │
 └──────────────────┘ └──────────────────┘ └──────────────────┘
```

When a ticket closes (e.g., removing a manual pipeline gate or altering an API payload), automated tooling maps the ticket's resolution context and touched components directly to the knowledge base, generating a surgical diff on affected pages.

Event-driven maintenance should be the primary freshness mechanism, while scheduled audits remain a backstop for changes that lack a clean machine event: policy drift, ownership changes, external dependency changes, and incorrect assumptions that survive ordinary pull-request review.

### The "Continuous Context" Framework
To prevent context pollution in human and agentic workflows, knowledge must be categorized into three distinct types, each governed by its own origin and update mechanism:

| Context Type | Definition & Examples | Update Mechanism & Cadence |
|:--- |:--- |:--- |
| **Declared Context** | Institutional human knowledge, business rules, domain ontologies, strategic intent (e.g., *"We soft-delete customer data"*). | Cannot be computed from code. Managed as a contract needing periodic human re-validation. |
| **Derived Context** | Summaries generated from fast-changing technical state (e.g., schemas, lineage, incident histories, freshness). | Computed automatically via pipeline integrations and live metadata extraction. |
| **Observed Context** | Inferred system behavior based on actual usage (e.g., tables joined in 80% of queries, silent deprecations). | Inferred continuously by observing system telemetries, logs, and query patterns. |

---

## 2. Ownership & Governance Models

### Single Named Ownership (Directly Responsible Individuals)
Shared ownership often diffuses accountability. One vendor-reported survey of 143 engineering leaders identified assigning a **single named owner** to every critical document as a commonly adopted response to documentation drift (reported by 37% of respondents). Treat this as directional practitioner evidence, not a universal causal result.

```
 DOCUMENTATION OWNERSHIP MODEL
 ┌──────────────────────────────────────────────────────────────────┐
 │ Single Named DRI (Directly Responsible Individual) │
 │ • Accountable for page accuracy, verification, and freshness │
 ├──────────────────────────────────────────────────────────────────┤
 │ Documentation Champions / Guilds │
 │ • Runs peer reviews, establishes style standards, audits health │
 ├──────────────────────────────────────────────────────────────────┤
 │ Triage & Reaction Rotations │
 │ • On-call engineers who triage incoming doc bugs and link rot │
 └──────────────────────────────────────────────────────────────────┘
```

* **The Embarrassment Principle**: *"Stale docs don't get caught by a committee. They get caught by the one person who'd be embarrassed if it were wrong"*.
* **Metadata Enforcement**: Frontmatter schemas in Markdown repositories must mandate an explicit `owner` field (e.g., `owner: "team-platform"` or `owner: "alex-garcia"`), blocking CI/CD pipelines if missing.

### Documentation Champions & Guilds
Organizations deploy **Documentation Champions** across squads. Champions establish peer review guidelines, conduct writing workshops, and maintain the repository's style rules.

### Operational Team Rotations
* **Reaction / Triage Rotations**: Engineering teams assign a rotating "reaction engineer" on a weekly basis to triage documentation issues, update broken setup instructions, and review incoming documentation PRs.
* **Support Pods**: Linking support engineers directly to specific documentation domains ensures that recurring customer tickets immediately trigger documentation backlog items.

---

## 3. Review Cadences, SLAs, & Verification Signals

### Freshness SLAs by Context Type
Rather than applying uniform review schedules across a knowledge base, freshness Service Level Agreements (SLAs) must be enforced based on context volatility:

```
 FRESHNESS SLA HIERARCHY
 ┌────────────────────────────────────────────────────────┐
 │ Incident Status & Operational Outages │ Minutes │
 ├────────────────────────────────────────┼───────────────┤
 │ System Schemas & API Contracts │ Hours │
 ├────────────────────────────────────────┼───────────────┤
 │ Technical Data Dictionaries │ Days │
 ├────────────────────────────────────────┼───────────────┤
 │ Declared Business Rules & Policies │ Annually │
 └────────────────────────────────────────┴───────────────┘
```

### Page Verification Badges & Frontmatter
To build trust, documents display visual and machine-readable verification signals:
* **Human-Facing Trust Badges**: Rendering explicit verification metadata at the top of pages (e.g., *"Verified 3 days ago by @sarah"*) allows human readers and AI search agents to weigh document authority.
* **Machine-Readable Metadata**:
 ```yaml
 ---
 title: "Authentication Gateway Architecture"
 owner: "team-identity"
 last_reviewed: 2026-07-15
 review_interval: "90d"
 authority_tier: 1
 ---
 ```

### The 90-Day Page-Age Drift Audit Procedure
To identify latent documentation drift, teams execute a quarterly two-step audit:
1. **Page-Age Extraction**: Query workspace analytics (e.g., Confluence API, Git log) to list operational pages not updated in $>90$ days.
2. **Jira/Git Cross-Referencing**: Cross-reference those old pages against Jira tickets closed or Git commits merged in the same 90-day window covering those components. The overlap represents high-risk documentation drift that must be triaged.

---

## 4. Doc Rot Detection & Automated Quality Gates

### Static Linting Pipelines (Docs-as-Code)
Documentation quality gates run inside CI/CD pipelines to validate Markdown syntax, style guidelines, and readability before merging:

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

* **`markdownlint`**: Checks Markdown structure, heading hierarchies, list indentation, and paragraph spacing.
* **`Vale`**: Prose linter enforcing style guide compliance, active voice, non-inclusive language checks, and terminology consistency.
* **Flesch-Kincaid Readability Testing**: Integrated via Vale (`ReadingLevel.yml`) to calculate readability scores based on average sentence length and syllable count, alerting when prose becomes overly complex:
 $$\text{Grade Level} = 0.39 \left(\frac{\text{total words}}{\text{total sentences}}\right) + 11.8 \left(\frac{\text{total syllables}}{\text{total words}}\right) - 15.59$$
* **Custom Shell & AST Scripts**: Scripts like `lint-doc.sh` enforce long-form `curl` options (`--header`), lower-case filenames, mandatory frontmatter headers, and valid Mermaid diagram syntax.

### Link Integrity Automation
* **`Lychee` / `Baler`**: Fast, async link checkers run in pre-commit hooks or scheduled GitHub Actions workflows to detect dead internal paths, expired external domains, and broken anchors. Broken external links that fail due to rate-limiting are explicitly cataloged in `.lycheeignore` alongside explanatory comments.

### AI-Driven Change & Drift Detection
* **Repository-Native Code Wikis**: Tools adapting Karpathy's LLM Wiki pattern compile raw codebase changes into persistent Markdown docs under `/docs`. Incremental sync workflows (`/doc-resync`) inspect Git commit pointers recorded in `docs/log.md`, map modified source paths via YAML `sources[]` frontmatter, and patch affected doc sections.
* **Self-Maintaining Knowledge Agents**: Background agents (such as Slite Agent or EkLine Docs Reviewer) continuously monitor connected tools (Slack, Jira, GitHub) to detect knowledge drift, automatically opening draft pull requests with proposed corrections when code and docs diverge.

Generated patches are proposals, not proof of correctness. Require code anchors, executable verification where possible, and human review for Tier 1/2 documents; otherwise automation can scale stale assumptions as efficiently as it scales valid updates.

---

## 5. Stale Content Policies: Archiving vs. Deleting

### Why Stale Docs Can Be Worse Than Missing Docs
Practitioner reports consistently argue that **stale documentation can be worse than no documentation**. Missing documentation signals that verification is necessary; stale documentation can carry the **false visual authority** of clean formatting, working links, and a historical author, misleading engineers during incident response.
* **The AI Hallucination Multiplier**: One vendor survey reports that 76% of participating engineering leaders had observed an AI tool read a stale document and confidently return an incorrect answer. This is a useful risk signal, not a general population estimate.
* **Reported Case Examples (not independently verified benchmarks)**:
 * *Fulfill.com*: Lost **$47,000 in a single week** when an AI assistant and warehouse team followed a lamination SOP that referenced a discontinued carrier code (stale for 237 days).
 * *Insurance Panda*: Suffered **~$40,000 in carrier chargebacks** due to a 2-year-old state compliance cheat sheet.
 * *Nexus Homebuyers*: Lost **~$40,000 in net profit** from a 14-month-old comp sheet.
 * *Gartner Estimate*: Poor data quality has been reported as costing organizations an average of **$12.9 million annually**; do not attribute the entire figure specifically to documentation without checking the original methodology.

### Search De-Indexing & Archiving Protocols
Simply moving a file to an "Archive" folder is insufficient if search engines and RAG pipelines still index it.
* **Strict De-Indexing Rule**: Archived pages MUST be explicitly excluded from search indexes, vector databases, and `llms.txt` manifests.
* **Archival Banners**: Deprecated pages retained for historical compliance MUST display a prominent top-line Markdown banner marking them as non-authoritative:
 ```markdown
 > ⚠️ **DEPRECATED / NON-AUTHORITATIVE**: This document was superseded by [ADR-0012](../adr/0012-new-auth.md) on 2026-03-15. It is retained solely for historical audit purposes.
 ```

### The 4-Tier Document Authority Hierarchy
To prevent AI agents and developers from treating informal notes with the same weight as corporate architectural standards, platforms implement an explicit four-tier authority hierarchy:

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

1. **Tier 1: Source of Truth**: Approved architecture decision records, security policies, and executive directives. Read-only for AI agents; if an agent answer conflicts with Tier 1, the agent is wrong.
2. **Tier 2: Core Technical Knowledge**: System design specifications, platform strategy documents, and core component guides.
3. **Tier 3: Implementation & Operational State**: Working sprint files, daily meeting notes, and active status reports.
4. **Tier 4: Archive / Historical**: Superseded documents marked explicitly with a `status: archived` frontmatter banner to exclude them from active AI retrieval.

---

## 6. Contribution Workflows & Developer Experience

### Docs-First & SSoT Methodology
Under GitLab's **Docs-First / Single Source of Truth (SSoT)** methodology, documentation is the heartbeat of work:
* **The Link-First Rule**: If a question is asked in Slack/teams, engineers must share a link to the authoritative documentation rather than rephrasing the answer in chat.
* **Merge Request Requirement**: If information does not exist in the documentation, the engineer MUST open a Merge/Pull Request to add it to the documentation first, then share the MR link.

```
 DOCS-FIRST COMMUNICATION LOOP
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

### The Onboarding "Fix-PR" Pattern
To build an immediate contribution habit and keep setup guides accurate, new engineering hires are assigned an **Onboarding Fix-PR** during their first week:
* **Execution**: The new engineer is instructed to execute the repository setup guide, document every point of friction, outdated command, or missing environment variable, and submit a documentation pull request by Day 3–5.
* **Outcome**: Validates pipeline access, achieves "time-to-first-commit" quickly, and continuously refixes setup documentation for the next cohort.

### PR Review Gates & Impact
The following source-reported, case-specific examples illustrate possible outcomes from integrating automated documentation linters into GitHub Actions or GitLab CI/CD. They are not portable benchmarks; measure outcomes in the local workflow.

| Illustrative Metric | Source-Reported Before | Source-Reported After |
|:--- |:--- |:--- |
| **Avg. Review Cycles per Docs PR** | 2.4 cycles | **1.4 cycles** |
| **Time to First Feedback** | 1–3 days | **Instant (Inline PR Comments)** |
| **Style-Related Review Comments** | ~60% of human review time | **~10%** |
| **Broken Links Shipped to Prod** | Monthly occurrences | **Rare** |

---

## 7. Knowledge Base Health Metrics & Framework Alignment

### Core Knowledge Base Health Metrics

```
 KB HEALTH METRICS DASHBOARD
 ┌───────────────────────┬───────────────────────┬───────────────────────┐
 │ Search Success Rate │ Document Freshness % │ AI Bot vs. Human │
 │ (Zero-result query %) │ (% compliant with SLA)│ Traffic Ratio │
 └───────────────────────┴───────────────────────┴───────────────────────┘
```

1. **Search Success Rate**: Percentage of user queries that result in a document click versus "zero-result queries" or immediate query reformulations.
2. **Freshness Compliance %**: Percentage of active documents whose `last_reviewed` date falls within its tier's freshness SLA.
3. **Usage & Bot Analytics**: Tracking traffic across human readers and AI user agents (ClaudeBot, GPTBot, Cursor) inspecting `/llms.txt` and `/llms-full.txt` to identify high-demand context surfaces.
4. **Documentation Coverage**: Percentage of production microservices or modules with linked, verified Tier 2 specs and C4 Container diagrams.

### DORA Metrics Alignment
High-quality, maintained documentation directly accelerates software delivery performance:
* **Failed Deployment Recovery Time (MTTR)**: Accurate, searchable runbooks dramatically reduce recovery time by allowing on-call responders to debug systems without hunting for tribal knowledge.
* **Change Lead Time**: Clear API specifications, architecture diagrams, and golden path setup guides remove development blockers, accelerating lead time from first commit to production.

### SPACE Framework Alignment & The "Verification Tax"
Documentation quality maps directly across the SPACE framework dimensions:
* **Communication & Collaboration**: Measured via code review turnaround time, handoff clarity, and documentation completeness.
* **Efficiency & Flow**: Evaluated by tracking "blocker time" and setup friction experienced by developers.

```
 THE VERIFICATION TAX BOTTLENECK
 ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
 │ High-Volume AI │ ──► │ Review Queue │ ──► │ System Bottleneck│
 │ Code Generation │ │ Verification Tax │ │ & Reviewer Burnout│
 └──────────────────┘ └──────────────────┘ └──────────────────┘
```

* **The AI Verification Tax**: Research from DORA (2024–2026) and Atlassian's Teamwork Lab highlights the *AI Efficiency Paradox*: while AI tools allow engineers to generate boilerplate code faster, output backs up downstream at review, approval, and verification gates. Reviewing AI-generated code introduces a heavy **verification tax**—cognitive overhead spent auditing code that looks correct but contains subtle errors. High-quality, machine-readable documentation (`llms.txt`, agent-optimized ADRs) reduces this tax by grounding AI tools in explicit architecture constraints before code is generated.

---

## 8. Access Control, Permissions & Confidentiality

### What Must Never Go Into Documentation
Real secrets, credentials, and personal data must never appear in a knowledge base, regardless of how convenient it is to paste a working example:
* **Secrets and Credentials**: Real tokens, personal access tokens, API secrets, application IDs, CI/CD variables, runner tokens, webhook secrets, and system passwords must never be placed in documentation. A personal developer's notes or local knowledge base must not become an unsafe shadow copy of private systems by holding credentials.
* **Real User Information (PII)**: Real usernames and real email addresses must be excluded entirely.
* **Standardized Sanitization Rules**: Use diverse, non-gendered placeholder names with common surnames (e.g., *Sidney Jones*, *Zhang Wei*, *Alex Garcia*); fake email addresses ending in `example.com`; `example.com` (or `gitlab.example.com` for self-managed examples) for generic URLs; and standard placeholder syntax for tokens (e.g., `<your_access_token>`) or explicitly generated fake strings.

### Sensitive Data in Screenshots and Examples
Screenshots of live or internal applications are a common leak vector. In order of preference:
1. **Browser DOM Inspection (Preferred)**: Right-click the element in the browser, select Inspect, and edit the HTML directly in the Elements panel to replace real user data, account IDs, or email addresses with fake example data before capturing the image.
2. **Dedicated Test Environments**: Reproduce the scenario using fake accounts inside an isolated test environment.
3. **Image Blurring (Fallback)**: If the test environment cannot be reproduced and DOM editing is impractical, blur the sensitive data using an image editing tool.

### Open vs. Restricted Content
* **Public-by-Default Paradigm**: High-performing async organizations (such as GitLab) enforce a "public by default" transparency bias for internal documentation — policies, workflows, project plans, and architectural decisions are open to the entire company unless explicitly designated as non-public/confidential.
* **Moving Conversations to SSoT**: When non-confidential discussions start in private messages, emails, or restricted channels, move the conversation to public documentation or a shared issue/PR to eliminate knowledge silos.
* **Formal Confidentiality Levels**: Organizations maintain explicit confidentiality classifications (such as "Not Public" or restricted tiers) for sensitive corporate, financial, legal, or security materials.

### Permission Models in KB Tools
Enterprise wikis (such as Confluence) provide enterprise permissions, and other knowledge base tools support custom user rights, role assignments, and password-protected articles or folders restricted to authorized teams or clients. ISO/IEC/IEEE 26511 defines a **user profile** as a unique attribute set (such as job function or clearance level) used by knowledge systems to restrict or grant access to specific documentation spaces. The corpus covers these permission models at a high level; granular, tool-by-tool role-based permission matrix configuration is thin and better treated as vendor-specific setup work.

### Access Control in AI / RAG Architectures
Connecting large language models and search engines to internal documentation introduces access-control considerations specific to retrieval:
* **Hard Metadata Filtering Before Retrieval**: Security boundaries (tenant IDs, user clearance levels, team permissions) must be applied as hard metadata constraints *before* search execution (e.g., `access_level <= user_clearance`). Running semantic vector retrieval before security filtering is a critical anti-pattern that leads to data leakage and access violations.
* **Permission-Aware Search Agents**: AI search agents should inherit the querying user's existing document permissions so generated answers never surface context from pages that user is not authorized to read.
* **Vector Database Inference Risk**: Because raw document embeddings stored in vector databases can potentially be reverse-engineered to infer underlying text, RAG infrastructure needs data encryption, strict guardrails, and access governance around the vector store itself, not just the source documents.

---

## Summary Maintenance Checklist

| Maintenance Dimension | Operational Best Practice | Key Target Metric / Tool |
|:--- |:--- |:--- |
| **Freshness Engine** | Event-driven updates triggered on Jira/PR close events. | Slite Agent / Code Wiki `/doc-resync`. |
| **Ownership** | Single named owner (DRI) in frontmatter schema. | 100% of Tier 1/2 docs with named owner. |
| **Linting Pipeline** | Automated syntax, style, and link checking in CI. | `markdownlint`, `Vale`, `Lychee`. |
| **Stale Content** | De-index dead files from search/AI; apply 4-tier hierarchy. | Zero archived pages in `/llms.txt` or RAG vector indexes. |
| **Onboarding** | Assign new hires a Week 1 "Fix-PR" task on setup guides. | First production commit in $\sim$3–5 days. |

---

← [Prev: Tooling Landscape](chapter04-tooling-landscape.md) | [Index](README.md) | [Next: Search & Retrieval / RAG](chapter06-search-retrieval-rag.md) →

## Related chapters
- [chapter01-fundamentals](chapter01-fundamentals.md) — why stale docs are worse than missing docs
- [chapter04-tooling-landscape](chapter04-tooling-landscape.md) — the linting/CI tools referenced here
- [chapter07-ai-ready-kb](chapter07-ai-ready-kb.md) — the authority-tier hierarchy in its AI-consumption context
- [chapter08-adoption-culture](chapter08-adoption-culture.md) — the cultural side of the same governance problem
- [chapter10-anti-patterns](chapter10-anti-patterns.md) — what happens when this maintenance discipline is skipped
- [chapter12-implementation-roadmap](chapter12-implementation-roadmap.md) — where this governance rhythm fits in a rollout
