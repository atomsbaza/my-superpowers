# Agent Engineering Radar — 2026-08-14

## Executive Summary

Scanned:

- 50+ X posts across 7 targeted XPOZ searches covering Agent Skills, Codex Skills, Claude Code Skills, MCP, agent harnesses, coding agents, and multi-agent development.
- 8 GitHub repositories deeply audited.
- 20+ README, documentation, activity, specification, and official project sources cross-checked.

Top findings:

- 3 INSTALL
- 2 TURN INTO SKILL
- 2 LEARN FROM
- 1 WATCH

The strongest immediate candidates are **Repowise**, **T3 Code**, and **Agent Orchestrator**. The most valuable patterns to reuse in `my-superpowers` are **ECC’s selective workflow packaging**, **Agent Plugins’ portable layout**, and **FiftyOne/Open Circle’s domain-specific skill design**.

This report treats X as a discovery layer. Repository behavior, documentation, licenses, and activity were checked against primary sources. Scores are engineering judgments, not popularity scores.

## 1. Agent Orchestrator

**Classification:** INSTALL  
**Overall Score:** 8.7/10

**Source**

- X: [itsharmanjot/status/2086725673490727270](https://x.com/itsharmanjot/status/2086725673490727270)
- GitHub: [Untrivial-ai/agent-orchestrator](https://github.com/Untrivial-ai/agent-orchestrator)
- Docs: [repository documentation](https://github.com/Untrivial-ai/agent-orchestrator/tree/main/docs)

**What it is**

A meta-harness for running multiple coding agents in parallel. It creates isolated Git workspaces, tracks live terminal/session state, understands pull requests, and can loop on CI failures, review comments, and merge conflicts. The current README lists adapters for 23 worker harnesses, including Claude Code, Codex, OpenCode, Aider, Cursor, Copilot, Goose, Kimi, and others.

**Why it matters**

It addresses the operational gap between “spawn several agents” and “safely integrate their work.” Worktree isolation, review feedback, and CI-aware loops are more useful than simply opening multiple terminals.

**How it works**

The repository separates worker harness adapters, workspace management, session state, reviewer agents, and orchestration logic. The X post’s claim of 25 harnesses is slightly stale or overstated; the current README lists 23 worker adapters.

**Recent activity**

The repository is active and substantial, with current documentation, a large issue/PR surface, and ongoing adapter and workflow work. Exact commit dates in the last seven-day window were not exposed by the fetched GitHub activity page, so activity confidence is lower than for Repowise or T3 Code.

**Evaluation**

- Technical Quality: 8/10
- Practical Usefulness: 9/10
- Novelty: 8/10
- Agent Engineering Relevance: 9/10
- Software Engineering Relevance: 9/10
- Codex/OpenCode Relevance: 9/10

**Post check:** Mostly accurate. The architecture and supported-agent claims are verified; the adapter count is not current.

**Strengths**

- Directly supports Codex and OpenCode.
- Worktree isolation is the right safety boundary for parallel coding agents.
- CI, review, and merge-conflict loops model real engineering workflows.

**Weaknesses**

- Broad adapter coverage increases maintenance and compatibility risk.
- The large issue/PR surface suggests operational rough edges.
- Requires careful workspace and credential isolation before unattended use.

**Security / Operational Concerns**

Use disposable worktrees, least-privilege GitHub credentials, explicit command permissions, and restricted environment variables. Do not let multiple agents share writable secrets or production credentials.

**Recommendation**

Install in a test repository and start with two agents, one reviewer, and explicit human approval before merge.

## 2. T3 Code

**Classification:** INSTALL  
**Overall Score:** 8.5/10

**Source**

- X: [probiex007/status/2086487614669115875](https://x.com/probiex007/status/2086487614669115875)
- GitHub: [pingdotgg/t3code](https://github.com/pingdotgg/t3code)
- Activity: [recent commits](https://github.com/pingdotgg/t3code/commits/main/)

**What it is**

A lightweight GUI and control plane for coding-agent CLIs. It provides agent threads, diffs, commits, pull requests, and isolated worktree workflows across Codex, Claude Code, Cursor, Grok, and OpenCode.

**Why it matters**

It turns several terminal agents into a reviewable workspace. The useful abstraction is not “chat with an agent”; it is “track a change from prompt to diff to commit to PR.”

**How it works**

The application wraps provider CLIs and presents their sessions through web, desktop, and mobile surfaces. Each agent thread can operate on its own branch/worktree, allowing changes to be compared before integration.

**Recent activity**

The [commit history](https://github.com/pingdotgg/t3code/commits/main/) shows active work on Codex collaboration prompts, diff rendering, source-control behavior, and UI fixes from Aug 11–13.

**Evaluation**

- Technical Quality: 8/10
- Practical Usefulness: 9/10
- Novelty: 7/10
- Agent Engineering Relevance: 9/10
- Software Engineering Relevance: 8/10
- Codex/OpenCode Relevance: 9/10

**Post check:** Accurate. The post’s claims about multiple agents, worktrees, diffs, commits, PRs, open source, and MIT licensing match the repository.

**Security / Operational Concerns**

The UI controls local agent processes and repository changes. Run it on trusted machines, review exposed ports/tunnels, and avoid giving remote viewers unrestricted shell or file-system access.

**Recommendation**

Install for hands-on evaluation if you want a visual Codex/OpenCode control plane.

## 3. Repowise

**Classification:** INSTALL  
**Overall Score:** 8.4/10

**Source**

- X: [TheTechDiggest/status/2086163403404652737](https://x.com/TheTechDiggest/status/2086163403404652737)
- GitHub: [repowise-dev/repowise](https://github.com/repowise-dev/repowise)
- Docs: [how it works](https://docs.repowise.dev/getting-started/how-it-works)
- Activity: [recent commits](https://github.com/repowise-dev/repowise/commits/main/)

**What it is**

Repository intelligence for coding agents. It builds code graphs, indexes Git history and documentation, identifies hotspots and ownership patterns, and exposes task-shaped MCP tools for Claude Code, Codex, Cursor, and OpenCode.

**Why it matters**

The strongest idea is converting repository understanding into structured context instead of repeatedly asking an agent to rediscover architecture from raw files. The project also reports token and context-retrieval benchmarks in its README.

**How it works**

The documented design combines tree-sitter parsing, symbol/file graphs, call resolution, Git co-change and hotspot analysis, documentation indexing, architectural decisions, and deterministic code-health detectors. The code-health layer is not presented as an LLM-generated score.

**Recent activity**

The [commit history](https://github.com/repowise-dev/repowise/commits/main/) shows active changes Aug 11–13, including MCP context fixes, agent integration work, OpenCode support, binding classification, and co-change edge fixes.

**Evaluation**

- Technical Quality: 8/10
- Practical Usefulness: 8/10
- Novelty: 8/10
- Agent Engineering Relevance: 9/10
- Software Engineering Relevance: 9/10
- Codex/OpenCode Relevance: 9/10

**Post check:** Mostly accurate. The repository confirms the core capabilities; the post’s “5K GitHub stars” claim was not independently confirmed.

**Security / Operational Concerns**

Review MCP permissions and local data retention. The repository is AGPL-3.0, so check license obligations before embedding it into a proprietary hosted service.

**Recommendation**

Install locally against a representative repository and compare agent performance with and without its context tools.

## 4. Everything Claude Code (ECC)

**Classification:** LEARN FROM  
**Overall Score:** 8.2/10

**Source**

- X: [bibryam/status/2086406954335768695](https://x.com/bibryam/status/2086406954335768695)
- GitHub: [affaan-m/ECC](https://github.com/affaan-m/ECC)
- Docs: [long-form documentation](https://github.com/affaan-m/ECC/tree/main/longform)
- Activity: [recent commits](https://github.com/affaan-m/ECC/commits/main/)

**What it is**

A large Claude Code-centered collection of skills, agents, commands, hooks, memory workflows, model-selection guidance, and security tooling. The repository includes Codex synchronization and adapters for other agent environments.

**Why it matters**

Its value is as a catalog of reusable engineering workflows: persistent context, stop-hook memory capture, selective tool usage, review automation, security checks, and skill contracts.

**How it works**

The canonical workflows are packaged as skills and commands, with hooks handling lifecycle events and memory. The current README reports 68 agents, 284 skills, and 94 commands; the X post’s 67-agent count is slightly stale.

**Recent activity**

The [commit history](https://github.com/affaan-m/ECC/commits/main/) shows active work Aug 8–12, including memory-vault fixes, model-selection documentation, a Pi adapter, continuous-learning changes, and governance skills.

**Evaluation**

- Technical Quality: 8/10
- Practical Usefulness: 8/10
- Novelty: 7/10
- Agent Engineering Relevance: 9/10
- Software Engineering Relevance: 9/10
- Codex/OpenCode Relevance: 8/10

**Post check:** Mostly accurate.

**Strengths**

- Extensive examples of operational skill design.
- Strong attention to hooks, memory, and security.
- Useful Codex synchronization path.

**Weaknesses**

- Installing the entire collection creates routing noise and maintenance overhead.
- Much of the system is optimized for Claude Code conventions.

**Recommendation**

Study it and selectively port individual workflows into this repository rather than installing the full bundle.

**Potential Skill Idea**

Create a `continuous-engineering-memory` skill that triggers after meaningful implementation work, records durable discoveries, and requires explicit redaction before persistence.

## 5. Agent Plugins Specification

**Classification:** LEARN FROM  
**Overall Score:** 8.5/10

**Source**

- X: [_vmlops/status/2086484035669504105](https://x.com/_vmlops/status/2086484035669504105)
- GitHub: [agentplugins/agent-plugins-spec](https://github.com/agentplugins/agent-plugins-spec)
- Standard site: [agent-plugins.org](https://agent-plugins.org/)
- Activity: [recent commits](https://github.com/agentplugins/agent-plugins-spec/commits/main/)

**What it is**

An open plugin packaging specification. The minimal layout uses `plugin.json`, `skills/`, optional `mcp.json`, and client-specific extension areas.

**Why it matters**

This is directly relevant to `my-superpowers`: skills should be portable, discoverable, independently installable, and able to declare integrations without forcing one client’s directory conventions.

**Recent activity**

The repository shows specification, terminology, governance, and MCP-transport work through early August, including the 1.0.0 standardization work.

**Evaluation**

- Technical Quality: 9/10
- Practical Usefulness: 7/10
- Novelty: 9/10
- Agent Engineering Relevance: 9/10
- Software Engineering Relevance: 9/10
- Codex/OpenCode Relevance: 9/10

**Post check:** Partly inaccurate. The packaging claims are supported, but the post’s statement that Google became a core maintainer is not supported by the official TSC list, which names Amazon, Cursor, Microsoft, OpenAI, and Vercel.

**Recommendation**

Learn from the layout and metadata model. Do not migrate this repository wholesale until the specification and client support stabilize.

**Potential Skill Idea**

Add a `skill-package-auditor` skill that validates frontmatter, directory layout, declared tools, license, install targets, and client compatibility before a skill is published.

## 6. DeepSeek Harness

**Classification:** WATCH  
**Overall Score:** 8.1/10

**Source**

- X: [deepseek_ai/status/2087887408440164663](https://x.com/deepseek_ai/status/2087887408440164663)
- GitHub: [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
- Architecture: [architecture.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- Activity: [recent commits](https://github.com/deepseek-ai/deepseek-harness/commits/master/)

**What it is**

An open-source agent harness in developer preview. Models, tools, session logs, agent loops, sandboxes, and orchestration are implemented as plugins around the Cordis foundation.

**Why it matters**

The architecture is a useful counterexample to a monolithic agent runtime. It emphasizes replaceable components, reversible effects, profiles, and plugin bundles.

**Recent activity**

The commit history shows substantial work on Aug 13, including public packaging, release candidate `0.1.0-rc.5`, onboarding, CI, and documentation.

**Evaluation**

- Technical Quality: 9/10
- Practical Usefulness: 7/10
- Novelty: 9/10
- Agent Engineering Relevance: 8/10
- Software Engineering Relevance: 8/10
- Codex/OpenCode Relevance: 8/10

**Post check:** Accurate. The MIT license, plugin architecture, open-source status, and Cordis foundation are confirmed.

**Security / Operational Concerns**

It is explicitly a developer preview with breaking changes. Treat model/tool plugins and sandbox integrations as privileged code; do not deploy against sensitive repositories yet.

**Recommendation**

Watch releases and study the architecture. Revisit installation after the API and plugin contracts settle.

## 7. FiftyOne Skills

**Classification:** TURN INTO SKILL  
**Overall Score:** 7.9/10

**Source**

- X: [jimmy_voxel51/status/2087162226855592357](https://x.com/jimmy_voxel51/status/2087162226855592357)
- GitHub: [voxel51/fiftyone-skills](https://github.com/voxel51/fiftyone-skills)
- Example: [embeddings visualization skill](https://github.com/voxel51/fiftyone-skills/blob/main/skills/fiftyone-embeddings-visualization/SKILL.md)
- Documentation: [official project article](https://voxel51.com/blog/antigravity-cli-fiftyone-skills)

**What it is**

Domain-specific Agent Skills for visual datasets. Skills guide agents through dataset import, deduplication, embeddings, visualization, inference, curation, and interaction with FiftyOne’s operators and MCP server.

**Why it matters**

The implementation demonstrates how a skill can encode a multi-step expert workflow rather than merely provide prose. The example skill contains operational sequencing, tool discovery, context setup, visualization, and cleanup instructions.

**Recent activity**

The repository shows 161 commits and a multi-client structure including Codex and OpenCode integrations. The fetched activity page did not expose a reliable exact commit date inside the seven-day window.

**Evaluation**

- Technical Quality: 8/10
- Practical Usefulness: 8/10 for computer-vision teams
- Novelty: 8/10
- Agent Engineering Relevance: 8/10
- Software Engineering Relevance: 7/10
- Codex/OpenCode Relevance: 8/10

**Post check:** Mostly accurate. The repository confirms the skill collection and documented operator coverage; the specific autonomous demo remains an author claim.

**Recommendation**

Do not install unless working with visual data. Reuse its structure when creating skills for domain APIs, SDKs, or internal tools.

**Potential Skill Idea**

Create skills for high-friction project APIs with: discovery, context initialization, canonical examples, validation checks, and cleanup/rollback steps.

## 8. Open Circle Agent Skills

**Classification:** TURN INTO SKILL  
**Overall Score:** 7.5/10

**Source**

- X: [Abutterflyee/status/2087182095181368989](https://x.com/Abutterflyee/status/2087182095181368989)
- GitHub: [open-circle/agent-skills](https://github.com/open-circle/agent-skills)
- Skill source: [Valibot SKILL.md](https://raw.githubusercontent.com/open-circle/agent-skills/main/skills/valibot/SKILL.md)
- Official docs: [Valibot installation and agent support](https://valibot.dev/guides/installation/)

**What it is**

A small, focused skill repository for Valibot and Formisch. The Valibot skill teaches schema creation, parsing, transformations, type inference, error handling, migration from Zod, and common mistakes.

**Why it matters**

It is a good model for library-specific skills: the skill encodes API facts that agents commonly get wrong, supplies canonical examples, and explicitly warns against confusing similar libraries.

**Recent activity**

The repository page reports 30 commits, MIT licensing, and a small focused scope. The fetched activity endpoint did not expose a reliable latest commit date, so development-velocity confidence is limited.

**Evaluation**

- Technical Quality: 7/10
- Practical Usefulness: 8/10 for TypeScript teams using Valibot
- Novelty: 6/10
- Agent Engineering Relevance: 8/10
- Software Engineering Relevance: 7/10
- Codex/OpenCode Relevance: 8/10

**Post check:** Mostly accurate. The agent skill and Markdown documentation are verified. The MCP server is part of Valibot’s documentation system, not an implementation inside this skill repository.

**Recommendation**

Use the repository as a template for focused SDK and library skills. Install it only in projects that use Valibot or Formisch.

**Potential Skill Idea**

Create a `library-integration-skill` template with API mental model, version-sensitive warnings, canonical examples, migration traps, and validation recipes.

## Rejected or Unscored Candidates

- **Campfire:** technically interesting multi-backend UI and session-replay claims, but the X short link did not resolve to an unambiguous GitHub repository during the audit.
- **Maestro:** several unrelated repositories share the name; the exact repository behind the X post could not be established confidently.
- **Long Horizon Agent Harness:** promising memory, sandbox, sub-agent, and guardrail claims, but the repository link was not resolvable from the captured X result.
- **Genie Code and NeMo Switchyard:** benchmark/engineering claims without an inspectable GitHub implementation tied to the post.
- **Nac and Nuphos:** low-evidence product claims with insufficient repository or implementation detail.

## Security and Operational Summary

Before installing any of the recommended tools:

- Run agents in disposable worktrees or containers.
- Keep GitHub, cloud, and package credentials out of agent-visible environment variables unless required.
- Review every MCP server’s transport, tool list, filesystem scope, and network behavior.
- Require human approval for pushes, merges, destructive shell commands, and production access.
- Review licenses: Repowise is AGPL-3.0; the other highlighted repositories advertise permissive licenses or open specifications.

# Recommended Actions

## Try Now

- Test [Repowise](https://github.com/repowise-dev/repowise) against one representative repository.
- Test [T3 Code](https://github.com/pingdotgg/t3code) as a Codex/OpenCode visual control plane.
- Test [Agent Orchestrator](https://github.com/Untrivial-ai/agent-orchestrator) with two isolated agents and one reviewer.

## Build as Skills

- `skill-package-auditor`: validate Agent Skill structure, metadata, tools, licenses, and client compatibility.
- `library-integration-skill`: generate focused, version-aware skills for SDKs and libraries.
- `continuous-engineering-memory`: capture durable implementation knowledge with redaction and review gates.
- Domain-specific workflow skills modeled after FiftyOne’s operational sequencing.

## Learn

- Study [ECC](https://github.com/affaan-m/ECC) for hooks, memory, security, and workflow packaging.
- Study the [Agent Plugins specification](https://github.com/agentplugins/agent-plugins-spec) for portable distribution.
- Study [DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md) for plugin-oriented runtime design.

## Watch

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) as its developer-preview APIs mature.
- Campfire and Maestro after their exact source repositories can be verified.

## Ignore

- Engagement-bait posts that provide no repository, documentation, benchmark methodology, or reproducible implementation.
- Generic “AI coding agent” announcements whose technical claims cannot be tied to inspectable source.
