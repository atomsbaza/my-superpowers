# Knowledge Bases for Software Projects — Research

**Provenance:** NotebookLM research — 110 web/research sources, 12 full-text Medium articles, and 1 synthesized research brief, collected 2026-08-03 and expanded 2026-08-04. This is a mixed-evidence survey, not a single authoritative source. It combines standards previews, arXiv preprints, official documentation, first-party engineering case studies, vendor research, and practitioner articles. Treat specific numbers (percentages, dollar figures, token counts, and retrieval gains) as source-reported unless the originating study has been independently verified.

**Evidence interpretation:** An arXiv publication is a preprint unless peer review is independently established; an ISO preview is not the complete normative standard; Medium posts and vendor surveys are practitioner evidence; and emerging conventions such as `llms.txt` are not formal standards. Fixed RAG parameters in this handbook are starting hypotheses that must be validated against a representative query set for the local corpus.

---

## Executive Summary

A software engineering knowledge base is not a filing cabinet — it is operational infrastructure that converts tacit, single-person knowledge into explicit, searchable, and increasingly AI-consumable organizational memory. The research converges on four traits that separate a high-performing knowledge platform from a "dead wiki": a canonical single source of truth for every fact, contextual integrity (capturing *why*, not just *what*, through mechanisms like ADRs), structured discoverability (Diátaxis for intent, PARA/Zettelkasten for organization, hybrid BM25+vector search for retrieval), and freshness enforced by event-driven triggers and named ownership, with scheduled audits as a backstop. Real-world case studies — GitLab's handbook, Stripe's Markdoc-based API docs, Google's g3doc, and Spotify's Backstage/TechDocs — show these principles converging independently across different organizations. Practitioner case reports also illustrate the risk of stale documentation, but their dollar figures and causal claims require independent verification before being used as benchmarks.

The research also treats AI-readiness as a first-class design constraint rather than an afterthought. Coding agents and MCP servers are becoming important documentation consumers alongside humans, which motivates practices such as `llms.txt`/`llms-full.txt` manifests, document authority hierarchies, frontmatter schemas with named owners and file-glob scopes, and human-reviewed Code Wiki workflows that patch documentation incrementally from Git diffs. Repository-level evaluation research suggests that fine-grained, feature-oriented documentation can improve coding-agent task performance. On the retrieval side, the material lays out an experimentally testable RAG baseline — content-aware chunking, contextual enrichment, hybrid lexical/semantic fusion, cross-encoder reranking, and retrieval/generation evaluation — rather than a universal parameter recipe.

Culturally, the research is clear that tooling and frameworks fail without adoption incentives: Definition-of-Done gates, "Link-First" norms, onboarding fix-PRs, and DORA/SPACE-metric alignment are what turn a well-designed structure into a living habit rather than a one-time migration project. The closing chapters translate this into a concrete IF/THEN decision-rule catalog and a phased implementation roadmap, so the corpus can be used both as a reference (read any chapter standalone) and as a rollout playbook (read chapters 11–12 first, then pull supporting detail from the chapters they cite).

---

## Table of Contents

### Chapters

1. [Fundamentals](chapter01-fundamentals.md) — knowledge base types, tacit vs. explicit knowledge, and the four traits of a high-quality platform.
2. [Information Architecture](chapter02-information-architecture.md) — hierarchical vs. networked vs. tag-based organization; PARA, Zettelkasten, Johnny Decimal, Maps of Content.
3. [Documentation Frameworks](chapter03-documentation-frameworks.md) — Diátaxis, ADRs (Nygard/MADR), the C4 model, and runbook design.
4. [Tooling Landscape](chapter04-tooling-landscape.md) — Docs-as-Code vs. database-backed wikis, static site generators, linters, and Internal Developer Portals.
5. [Maintenance & Governance](chapter05-maintenance-governance.md) — the Continuous Context model, ownership (DRI), CI quality gates, freshness metrics, and access control/confidentiality.
6. [Search & Retrieval / RAG](chapter06-search-retrieval-rag.md) — BM25, dense vector search, hybrid retrieval, chunking, reranking, and RAG evaluation metrics.
7. [AI-Ready Knowledge Bases](chapter07-ai-ready-kb.md) — structuring Markdown for LLM/agent consumption, `llms.txt`, authority tiers, agent-optimized ADRs.
8. [Adoption & Culture](chapter08-adoption-culture.md) — building a documentation culture, DORA/SPACE metric alignment, and the AI verification tax.
9. [Case Studies](chapter09-case-studies.md) — GitLab, Stripe, Google, Spotify, Twitter/Docbird, enterprise ADR adopters, and cautionary tales of stale documentation.
10. [Anti-Patterns](chapter10-anti-patterns.md) — dead wikis, orphan pages, tag explosion, knowledge silos, hero culture, and RAG-specific failure modes.
11. [Decision Rules](chapter11-decision-rules.md) — a condensed IF/THEN catalog spanning tooling, information architecture, governance, search, and AI-readiness decisions.
12. [Implementation Roadmap](chapter12-implementation-roadmap.md) — the capstone: a phased plan for standing up a knowledge base from scratch.

### Appendices

- [Appendix: Glossary](appendix-glossary.md) — alphabetized definitions of every key term used across the chapters.
- [Appendix: Cheatsheet](appendix-cheatsheet.md) — condensed quick-reference tables (tool selection, Diátaxis quadrants, chunking guidance, KB health metrics, IF/THEN rules).
