---
name: agent-radar
description: Discover, verify, rank, and recommend technically useful developments in AI agent engineering from X/Twitter, GitHub, and the web. Use when the user asks for an agent engineering radar, current agent tools, Codex or Claude Code Skills, MCP servers, coding-agent workflows, agent harnesses, multi-agent systems, context engineering, orchestration, memory, evaluation, or developer tooling; prioritize source code and primary evidence over popularity or hype.
---

# Agent Radar

Produce an evidence-backed engineering radar, not a generic AI-news summary. Optimize for practical usefulness to an experienced backend/software engineer interested in .NET, AI engineering, Codex CLI, OpenCode, MCP, Agent Skills, architecture, and developer productivity.

## Operating rules

- Treat X/Twitter as a discovery layer, never as the source of truth.
- Prefer recent evidence: search the last 7 days by default; expand to 30 days only when the 7-day set is too small or a project needs historical context.
- Prefer source code, documentation, implementations, architecture diagrams, benchmarks, evaluations, tests, and reproducible workflows over engagement, follower count, or branding.
- Ignore or heavily penalize generic AI news, marketing without technical substance, engagement bait, beginner tutorials, prompt collections, listicles, unverified claims, crypto promotion, pure speculation, and launches without code, docs, benchmarks, or architecture.
- Do not invent repositories, links, metrics, dates, benchmark results, licenses, activity, compatibility, pricing, or adoption.
- Distinguish clearly between observed facts, author claims, and engineering inference.
- Keep the research read-only. Do not install software, run untrusted code, write to repositories, authenticate to social accounts, or grant permissions as part of a radar run.

## Source and tool routing

Use the configured XPOZ MCP server as the primary X/Twitter discovery source. Select its search capability from the available tools; do not invent a tool name if the server exposes a different one. Search several targeted queries rather than one broad query:

- `agent skills`, `AI agent skills`, `Codex skills`, `Claude Code skills`
- `MCP server`, `agent harness`, `coding agents`, `agent framework`
- `context engineering`, `AI coding workflow`, `multi agent coding`
- `agent orchestration`, `agent memory`, `agent evaluation`, `AI developer tools`

Add queries when new terminology, repository names, or authors emerge. Use available GitHub inspection capabilities or official repository pages to inspect linked projects. Use web research for official documentation, specifications, announcements, benchmarks, pricing, compatibility, licensing, and deprecation status. Prefer primary sources and link/cite the exact source supporting each current claim.

If XPOZ or another expected source is unavailable, continue with the remaining sources and explicitly disclose the gap; never imply that the unavailable source was searched.

## Focus modes

Adapt the query set, filtering, and recommendation depth to the user's focus:

- **Skills**: Codex Skills, Claude Code Skills, Agent Skills, and reusable workflows.
- **MCP**: servers, clients, tool integrations, architecture, permissions, and security.
- **Coding Agents**: Codex, OpenCode, Claude Code, Kiro, harnesses, repository automation, and developer workflows.
- **Architecture**: multi-agent design, context management, memory, planning, and tool orchestration.
- **Evaluation**: benchmarks, coding-agent performance, reliability, testing, and evaluation methodology.

If no focus is given, cover the full scope but favor items that can improve real software-engineering workflows.

## Research workflow

Follow these stages in order. Scale the depth to the user's request, but preserve source verification for every strong recommendation.

### 1. Discover

Run multiple targeted XPOZ searches and collect approximately 20–40 candidate posts when possible. For each candidate record:

- author and post date
- post URL and concise text summary
- engagement metrics, only when available and only as secondary evidence
- project/tool/technique name
- GitHub, documentation, article, paper, or demo links
- the concrete technical claim worth checking

Use recency and technical substance for initial ordering, not popularity.

### 2. Deduplicate

Merge candidates about the same repository, tool, framework, technique, announcement, or paper. Keep the earliest primary source or the most technically useful source, and retain supporting posts only when they add distinct evidence.

### 3. Filter

Remove candidates with little engineering substance. Retain an item when it has at least one of:

- source code or a real implementation
- useful documentation or architecture detail
- a benchmark/evaluation with enough methodology to inspect
- a reusable workflow or novel engineering technique
- strong technical discussion from experienced practitioners

Reduce to approximately 10–20 promising items before deep verification.

### 4. Verify

Inspect the linked primary sources. For GitHub repositories, inspect as applicable:

- README, documentation, examples, and repository structure
- recent commits, releases, issues, and pull requests
- license and installation instructions
- tests, CI, error handling, and security-relevant code

Determine whether the implementation matches the claim, whether development is active, whether it is production-ready, experimental, or abandoned, whether setup complexity is justified, whether it duplicates existing tools, and whether it introduces security or operational risks. Do not equate recent commits or stars with quality.

Use official web sources to verify claims that GitHub or X cannot establish, including API availability, compatibility, pricing, quotas, licensing, benchmark definitions, and deprecation status. Record the observed date for time-sensitive evidence.

### 5. Evaluate and rank

Score each shortlisted item from 0–10 on:

- **Technical Quality**: code, architecture, docs, tests, maintainability, API design, error handling, and security awareness.
- **Practical Usefulness**: real problem solved, current usability, manual work reduced, setup effort, and value beyond a demo.
- **Novelty**: meaningful new idea or improvement versus a wrapper, rebrand, or duplicate.
- **Agent Engineering Relevance**: coding agents, Skills, MCP, tool calling, context, memory, evaluation, orchestration, or multi-agent systems.
- **Software Engineering Relevance**: architecture, debugging, testing, observability, reliability, security, CI/CD, code review, or repository workflows.
- **Codex/OpenCode Relevance**: Codex CLI, OpenCode, MCP, Agent Skills, AGENTS.md, CLI development, or repository automation.

Calculate an approximate weighted score:

`0.25 × Technical Quality + 0.25 × Practical Usefulness + 0.20 × Agent Engineering Relevance + 0.10 × Software Engineering Relevance + 0.10 × Codex/OpenCode Relevance + 0.10 × Novelty`

Report one decimal place. Apply engineering judgment when the formula misleads—for example, a highly novel but unusable research prototype may deserve WATCH rather than a high recommendation. Rank by practical engineering value and evidence confidence, not score alone.

### 6. Classify

Give every shortlisted item exactly one classification:

- **INSTALL**: immediately useful, mature enough to try, reasonable setup, and technically strong.
- **LEARN FROM**: useful implementation or architecture, but not worth adopting directly.
- **TURN INTO SKILL**: reusable workflow that can be automated as a custom Codex/OpenCode Skill, especially when the original tool is unnecessary or overly complex.
- **WATCH**: promising but immature, under-documented, early-stage, or awaiting adoption/evidence.
- **IGNORE**: marketing, weak or unverified engineering, abandoned, redundant, unsafe, or not practically useful.

## Security and operational review

Explicitly flag requirements for browser cookies, session tokens, personal API keys, shell or arbitrary command execution, elevated privileges, repository write access, social-media write permissions, untrusted remote MCP servers, or access to sensitive code/data.

Prefer read-only integrations for research. Never recommend placing credentials in prompts or committed configuration. When a project needs secrets or broad permissions, state the minimum permissions, sandboxing, credential-handling, and isolation needed before testing. Treat remote MCP servers and agent tools as untrusted until their code, transport, permissions, and data flow are inspected.

## Required report format

Start with:

```markdown
# Agent Engineering Radar — YYYY-MM-DD

## Executive Summary

Scanned:
- N X posts
- N GitHub repositories
- N documentation sources

Top findings:
- N INSTALL
- N TURN INTO SKILL
- N LEARN FROM
- N WATCH
```

Use the actual counts. If a source was unavailable, say so instead of fabricating a count. Then rank the most interesting findings. For each finding, include:

```markdown
## 1. Project / Idea Name

**Classification:** TURN INTO SKILL
**Overall Score:** 8.7/10

**Source**
- X: <URL>
- GitHub: <URL>
- Docs: <URL>

**What it is**

Concise technical explanation.

**Why it matters**

Explain the engineering value for the user's context.

**How it works**

Explain the architecture or workflow, distinguishing verified facts from inference.

**Evaluation**

- Technical Quality: N/10
- Practical Usefulness: N/10
- Novelty: N/10
- Agent Engineering Relevance: N/10
- Software Engineering Relevance: N/10
- Codex/OpenCode Relevance: N/10

**Strengths**

- ...

**Weaknesses**

- ...

**Security / Operational Concerns**

- ...

**Recommendation**

State exactly what to do next: install in a sandbox, study without adopting, reimplement as a Skill, watch releases, or ignore.

**Potential Skill Idea**

When applicable, provide the skill name, purpose, trigger conditions, required tools, workflow, expected output, and security constraints.
```

Do not include a finding solely because it is popular. Keep the report focused on evidence and action. Cite web-derived claims near the claim using direct Markdown links, and include source URLs even when browsing citations are not required by the host environment.

Always finish with:

```markdown
# Recommended Actions

## Try Now

Projects worth installing or testing immediately.

## Build as Skills

Ideas that should be implemented as custom Agent Skills.

## Learn

Repositories or techniques worth studying.

## Watch

Early-stage projects worth monitoring.

## Ignore

Popular items that are not worth further attention.
```

## Skill extraction

Treat reusable workflow extraction as a first-class outcome. When an item is suitable, propose:

- skill name
- purpose
- trigger conditions
- required tools
- ordered workflow
- expected output
- security constraints

Use this compact workflow notation when helpful:

`X discovery → link extraction → repository inspection → documentation verification → scoring → recommendation`

Prefer a custom Skill when it captures a repeatable research or engineering workflow, reduces context/tool overhead, or provides safer read-only behavior than adopting the original project. Do not propose a Skill merely to repackage a useful library.

## Final quality gate

Before responding, verify that:

- every strong recommendation has a primary source or is marked provisional
- X claims are corroborated externally when technically important
- current facts have dates or clear source context
- scores reflect evidence and not engagement
- classifications match maturity, usefulness, and setup effort
- security implications are explicit
- missing tools or unavailable sources are disclosed
- the final action list is concrete and prioritized
