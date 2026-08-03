# Anti-Patterns

## 1. The Dead / Abandoned Wiki

* **Symptoms**: High volume of obsolete, unowned pages with edit timestamps dating back months or years. New developers follow setup instructions or architecture guides into immediate technical failure, while experienced engineers abandon the wiki entirely in favor of asking peers in Slack.
* **Root Cause**: Storing documentation in a disconnected, third-party platform without clear individual ownership (Directly Responsible Individuals) or automated change-detection mechanisms tied to code commits and ticket closures.
* **Remedy**: 
 1. Assign a **single named DRI (`owner`)** in every document’s YAML frontmatter schema (e.g., `owner: "alex-garcia"`), eliminating committee ownership.
 2. Implement an **event-driven update loop**: closing a Jira ticket or merging a pull request triggers change detection against linked documentation pages to propose surgical updates.
 3. Enforce **automated CI/CD quality gates** (`markdownlint`, `Vale`, `Lychee`) to fail PR builds on broken links, style violations, or missing frontmatter.

---

## 2. Duplicated Truth Across Tools

* **Symptoms**: Identical or conflicting technical guidance resides across Slack threads, Confluence pages, Notion databases, README files, and inline code comments. Developers argue over which document represents current reality.
* **Root Cause**: Lack of an explicit **Single Source of Truth (SSoT)** strategy and failure to enforce a "Link-First" communication culture across the engineering organization.
* **Remedy**:
 1. Establish an explicit SSoT policy where every policy, API contract, or workflow exists in exactly **one authoritative location** (e.g., Docs-as-Code co-located in Git repositories or a central company handbook).
 2. Enforce the **"Link-First" rule**: when answering questions in Slack or code reviews, engineers must share the canonical SSoT URL rather than rephrasing the answer. If the documentation does not exist, a pull request must be opened first, and the PR link shared.
 3. Deploy **AI de-duplication pipelines** (e.g., Architecture Agents or Code Wikis) to scan, de-duplicate, and consolidate scattered decisions into single authoritative records.

---

## 3. Orphan Pages and Deep Nesting

* **Symptoms**: High-value documents exist within the knowledge base but are unreachable via navigation menus or standard search queries. Content sits in "isolated nodes" that are rarely discovered by humans or retrieved by AI search agents.
* **Root Cause**: Forcing complex, multi-dimensional technical relationships into rigid, single-parent hierarchical folder trees.
* **Remedy**:
 1. Transition from pure folder trees to a **networked (linked) architecture** using bidirectional links (`[[Note Title]]`).
 2. Build **Maps of Content (MOCs)** and top-level routing indexes (`docs/index.md` or `KNOWLEDGE_BASE.md`) that cluster related documents by concept rather than physical folder depth.
 3. Run **automated linter scripts** in CI to detect orphaned Markdown files lacking incoming links or index entries.

---

## 4. Over-Structuring Too Early

* **Symptoms**: Elaborate folder hierarchies, complex multi-tag taxonomies, and 15-field page templates sit empty. Developers feel intimidated by administrative overhead and stop capturing notes altogether.
* **Root Cause**: Premature optimization—attempting to design a complete, rigid taxonomy before understanding real developer usage patterns and information flows.
* **Remedy**:
 1. Start with a minimal structure: a single `00 Inbox` folder for raw captures, `01 Projects`, `02 Areas`, `03 Resources`, `04 Archive`, and a `10 Zettelkasten` for permanent notes.
 2. Enforce minimal page templates (e.g., Title, Body, 2–3 links).
 3. Allow structure and taxonomy tags to **emerge organically** from note clusters over time rather than imposing them upfront.

---

## 5. Tool Churn & Fragmentation

* **Symptoms**: Knowledge is fragmented across 5–10 tools (Notion, Confluence, Obsidian, Google Docs, Slack, shared drives). The team undergoes frequent tool migrations, causing notes to lose version history and never build compounding value.
* **Root Cause**: Tool-hopping in search of software features rather than committing to core capture, connection, and maintenance habits.
* **Remedy**:
 1. Establish clear functional boundaries: technical, code-enforcing documentation lives directly in Git repositories (Docs-as-Code), while general team/organizational guidelines reside in a single primary team wiki.
 2. Commit to a tool choice for a minimum of 6 months before evaluating alternatives.
 3. Require all tools to support open standards (plain Markdown / CommonMark) to eliminate vendor lock-in and simplify future migrations.

---

## 6. The Write-Only Knowledge Base (Nobody Reads)

* **Symptoms**: Voluminous documentation is written during launch "sprints" or hackathons, but analytics show zero page views, zero citations, and high knowledge entropy.
* **Root Cause**: Treating documentation as a one-time deliverable or static warehouse rather than an active operational infrastructure integrated into daily developer workflows.
* **Remedy**:
 1. Integrate documentation directly into the **Definition of Done (DoD)** for pull requests—code cannot be merged without corresponding doc updates.
 2. Embed documentation directly inside developer environments (VS Code IDE extensions, Internal Developer Portals like Backstage).
 3. Where identified target consumers support it, publish an emerging-convention manifest (`llms.txt`, and optionally `llms-full.txt`) and test that those consumers actually discover, use, and respect the canonical content.

---

## 7. Stale Documentation Eroding Trust

* **Symptoms**: On-call engineers burn hours debugging fictional versions of systems during outages. AI assistants repeat outdated instructions with total confidence, scaling errors across the team.
* **Root Cause**: Software reality evolves continuously while static documentation remains a frozen snapshot; calendar-based review reminders fail under deadline pressure.
* **Remedy**:
 1. Transition from calendar reviews to **event-driven update loops**: closing a ticket or merging an architectural PR automatically triggers a doc review task or AI diff proposal.
 2. Display **visual trust badges** (e.g., *"Verified 3 days ago by @sarah"*) and frontmatter metadata (`last_reviewed`, `review_interval`) on all operational pages.
 3. Implement a **4-Tier Document Authority Hierarchy** and de-index Tier 4 (Archived/Deprecated) pages from search engines, vector databases, and `llms.txt` manifests so stale docs never feed AI generation.

---

## 8. Knowledge Silos and Hero Culture

* **Symptoms**: Senior engineers are trapped in "hero mode," suffering from continuous Slack interruptions and burnout. Onboarding new engineers takes weeks or months, creating catastrophic organizational risk ("bus factor").
* **Root Cause**: Relying on uncodified, tacit knowledge locked in individual minds and culturally rewarding real-time "heroic" interventions over asynchronous documentation.
* **Remedy**:
 1. Assign new engineering hires an **"Onboarding Fix-PR"** during their first week: they must execute setup guides, document every point of friction, and submit a documentation PR by Day 3–5.
 2. Link high-quality documentation contributions directly to **engineering career ladders and promotion criteria**.
 3. Use **LLM-maintained Code Wiki** workflows (`/generate-documentation-from-code`) to propose anchored Markdown patches; keep `TODO-VERIFY` and `CONTRADICTION` markers, executable checks, and human review rather than publishing generated text automatically.

---

## 9. The Collector’s Fallacy (Saving vs. Thinking)

* **Symptoms**: A bloated workspace containing 500+ saved PDFs, book highlights, and bookmarked URLs, but fewer than 20 processed, original notes.
* **Root Cause**: Confusing the passive act of capturing or saving information with actual comprehension and synthesis.
* **Remedy**:
 1. Enforce a strict **capture filter**: save only information directly relevant to active projects or core research questions.
 2. Apply the **Zettelkasten rule**: force yourself to restate external source summaries into atomic, permanent notes written in your own words before filing.
 3. Schedule a **weekly review** to process the inbox and purge low-value captures without guilt.

---

## 10. Diátaxis Quadrant Blurring (Content Drift)

* **Symptoms**: Technical reference pages are cluttered with chatty setup instructions; goal-oriented how-to guides are bloated with deep theoretical rationale; beginner tutorials pause to explain complex edge cases.
* **Root Cause**: Multiple contributors authoring documentation without intent-based structural rules or automated linter enforcement.
* **Remedy**:
 1. Adopt the 4-quadrant **Diátaxis framework**—strictly separating content by user intent into *Tutorials* (learning-oriented), *How-To Guides* (goal-oriented), *Reference* (information-oriented), and *Explanation* (understanding-oriented).
 2. Enforce strict H2 heading hierarchies and shortcodes in CI pipelines (e.g., requiring `## About`, `## Example`, `## Reference` in specific sequential order).

---

## 11. AI & RAG Retrieval Anti-Patterns (Machine-Consumption Failure Modes)

* **Symptoms**: Internal RAG engines and AI coding assistants retrieve noisy, irrelevant context, miss exact code symbols, hallucinate parameter names, or quote superseded policies.
* **Root Cause**: Untested chunking and candidate settings; retrieving too few candidates; relying on one search mode without comparison; lack of citable `file:line` prompt anchors; and indexing archived documents.
* **Remedy**:
 1. **Calibrate chunks**: Start by testing 500–800 tokens (50-token overlap) for prose and 200–400 tokens (AST boundaries) for code against representative labeled queries.
 2. **Compare retrieval modes**: Test lexical BM25, dense vector search, and hybrid RRF (with $k=60$ as a starting value); reported recall lifts are corpus-specific.
 3. **Tune retrieval and reranking**: Start with 12–20 candidates and 5–10 final chunks, then choose settings from retrieval/answer metrics, latency, and cost.
 4. **Require provenance and review**: Use explicit `file:line` anchors, verification checks, and human review; validate that any citation resolves to retrieved evidence.

---

## Summary Checklist: Anti-Pattern vs. Corrective Architecture

| Anti-Pattern | Primary Failure Mode | Corrective Architecture / Pattern |
|:--- |:--- |:--- |
| **Dead Wiki** | Unowned, stale platform misleading users. | Single named DRI (`owner`) + Event-driven review triggers + CI linters. |
| **Duplicated Truth** | Conflicting guidance across tools. | Single Source of Truth (SSoT) + "Link-First" communication policy. |
| **Orphan Pages** | Deeply nested, unlinked documents. | Networked Zettelkasten links + Maps of Content (MOCs) + `index.md` catalogs. |
| **Over-Structuring** | Rigid, empty folder taxonomies. | Lean 5-folder PARA setup + Emergent structure from atomic links. |
| **Tool Churn** | Fragmented notes across 5+ apps. | In-repo Docs-as-Code for technical specs + Commit to single team wiki. |
| **Write-Only KB** | High-volume prose nobody reads. | Definition of Done (DoD) PR gates + IDE integrations + tested optional AI manifests. |
| **Stale Docs** | Outdated runbooks causing outage delays. | Jira/PR event-driven update loop + Trust badges + 4-Tier Authority Hierarchy. |
| **Knowledge Silos** | Tacit knowledge locked in heads. | "Onboarding Fix-PRs" + Promotion incentives + reviewed, anchored Code Wiki proposals. |
| **Diátaxis Blurring** | Mixed content types degrading lookup. | 4 Diátaxis Quadrants + Strict H2 heading linter rules in CI. |
| **RAG Noise** | Weak retrieval & AI hallucinations. | Locally calibrated chunks + compared retrieval modes + tuned reranking + provenance. |

---

← [Prev: Case Studies](chapter09-case-studies.md) | [Index](README.md) | [Next: Decision Rules](chapter11-decision-rules.md) →

## Related chapters
- [chapter01-fundamentals](chapter01-fundamentals.md) — the quality criteria these anti-patterns violate
- [chapter02-information-architecture](chapter02-information-architecture.md) — orphan pages, tag explosion, over-structuring
- [chapter05-maintenance-governance](chapter05-maintenance-governance.md) — the fixes for dead wikis and stale docs
- [chapter06-search-retrieval-rag](chapter06-search-retrieval-rag.md) — the RAG retrieval anti-patterns in full detail
- [chapter08-adoption-culture](chapter08-adoption-culture.md) — knowledge silos and hero culture root causes
