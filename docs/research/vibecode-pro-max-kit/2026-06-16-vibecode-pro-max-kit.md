# Research: vibecode-pro-max-kit

## Summary

`vibecode-pro-max-kit` is a spec-driven AI coding harness for Claude Code, Codex CLI, Cursor, Windsurf, and several other AI editors. Its central premise is that the structural problem with AI-assisted development — agents forgetting context, producing spaghetti code, and collapsing mid-task — is not solved by smarter prompts but by enforcing a disciplined, phase-gated workflow. The kit installs approximately 12 specialized agents, 31-34 skill modules, and 7 lifecycle hooks into a project, wiring them together around a five-phase workflow called RIPER-5. Knowledge is stored to disk in a `process/` directory tree so context survives session resets and context compaction. As of June 2026 the repository has approximately 880 stars and 200 forks under an MIT license.

---

## Key Findings

### 1. What the Project Is

The kit's full title is "spec-driven coding harness for vibecoders, product owners, CEOs, and real builders." The problem statement is explicit: AI agents forget context between sessions, documentation goes stale, large tasks collapse when the context window fills, and there is no shareable artifact that lets teammates review AI work. The solution is structural enforcement — phase locks, mandatory approval gates, disk-persisted state — rather than prompt improvements.

The project targets two audiences equally: **technical developers** who want production-grade AI workflows, and **non-technical builders** (CEOs, PMs) who want to drive AI agents toward shippable output without understanding the underlying code.

Source: [GitHub — vibecode-pro-max-kit](https://github.com/withkynam/vibecode-pro-max-kit)

### 2. What It Contains

**Top-level layout after install:**

```
your-project/
├── .claude/
│   ├── agents/            # 12 agent definition files
│   ├── skills/            # 31-34 skill module folders, each with SKILL.md
│   └── hooks/             # 7 lifecycle hooks (.cjs files)
├── .codex/agents/         # Codex-compatible mirrors of agent definitions
├── CLAUDE.md              # Orchestrator configuration
├── AGENTS.md              # Agent + skill registry (cross-tool discovery)
└── process/
    ├── _seeds/            # Scaffold templates
    ├── context/           # Domain-routed knowledge files
    ├── general-plans/     # active/ and completed/ plan folders
    ├── features/          # Per-feature lifecycle folders
    └── development-protocols/
        ├── all-development-protocols.md
        ├── context-maintenance.md
        ├── implementation-standards.md
        ├── intent-clarification.md
        ├── orchestration.md
        ├── parallel-fan-out.md
        ├── phase-programs.md
        └── plan-lifecycle.md
```

**The 12 agents** split into two tiers:

- **Phase agents** (core workflow): `vc-research-agent`, `vc-innovate-agent`, `vc-plan-agent`, `vc-execute-agent`, `vc-fast-mode-agent`, `vc-update-process-agent`
- **Specialist agents** (quality gates): `vc-debugger`, `vc-tester`, `vc-code-reviewer`, `vc-code-simplifier`, `vc-ui-ux-designer`, `vc-git-manager`

Source: [AGENTS.md registry](https://github.com/withkynam/vibecode-pro-max-kit/blob/main/AGENTS.md)

**Notable skills** (each is a folder with a `SKILL.md`):

| Skill | What it does |
|---|---|
| `vc-predict` | 5-persona pre-implementation debate (Architect, Security, Performance, UX, Devil's Advocate) producing GO/CAUTION/STOP verdict |
| `vc-scenario` | Decomposes features across 12 orthogonal dimensions (concurrency, scale, auth, compliance, etc.) to surface edge cases before coding |
| `vc-autoresearch` | Autonomous iterative optimizer for measurable metrics (test coverage, bundle size, lint errors); commits each micro-change, detects stuck loops |
| `vc-security` | STRIDE + OWASP Top 10 audit with dependency scanner and secret detector |
| `vc-team` | Spawns parallel Claude Code sessions with git worktree isolation for parallel execution |
| `vc-watzup` | Read-only session handoff summary — branch, active plans, next steps |
| `vc-setup` | Interactive project onboarding: stack detection, codebase deep-scan, process/ scaffolding |
| `vc-update` | Pulls latest harness version from remote; `vc-publish` pushes local improvements back |

**The 7 hooks** (.cjs files run by Claude Code's hook system):

- `privacy-block.cjs` — intercepts reads of `.env`, SSH keys, and credentials; requires an `APPROVED:` prefix before allowing access
- `session-init.cjs` — runs at startup/resume; detects stack, writes 30+ `CK_`-prefixed environment variables, surfaces previous session state
- `session-state.cjs` — maintains cross-session state
- `subagent-init.cjs` — initializes context for subagent spawns
- `post-edit-simplify-reminder.cjs` — prompts simplification after edits
- `descriptive-name.cjs` — enforces naming conventions
- `scout-block.cjs` — controls scout skill access boundaries

Source: [Hooks directory](https://github.com/withkynam/vibecode-pro-max-kit/tree/main/.claude/hooks)

**Development protocols** are durable markdown files defining shared rules across agents: how to maintain context files, how plans lifecycle from `active/` to `completed/`, how to run parallel fan-out across worktrees, and what constitutes a verified phase in multi-phase programs. These are not prompt suggestions — they are the operating manual that every agent reads.

Source: [process/development-protocols/phase-programs.md](https://github.com/withkynam/vibecode-pro-max-kit/blob/main/process/development-protocols/phase-programs.md)

### 3. How It Works

**Installation** is a single shell command followed by one setup invocation:

```bash
curl -fsSL https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/install.sh | bash
# then in Claude Code:
Run vc-setup
```

The installer: clones the repo into a temp directory, reads `vc-manifest.json` to categorize files (install/merge/copy-if-missing), backs up any existing `.claude/` to `.vibecode-backup/`, and preserves the user's `process/` directory and `.claude/settings.json`. It writes `.vc-installed-files` and `.vc-version` for update tracking.

Source: [install.sh](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/install.sh)

**The RIPER-5 workflow** gates all substantial work:

1. **RESEARCH** — `vc-research-agent` reads the codebase and external docs. No file writes, no suggestions. Concludes with "Say 'go' to move to INNOVATE mode."
2. **INNOVATE** — `vc-innovate-agent` explores 2-3 approaches with trade-off analysis. Still no code.
3. **PLAN** — `vc-plan-agent` writes a technical specification to `process/general-plans/active/` or `process/features/{name}/active/`. The plan includes: files touched (touchpoints), public contract changes, blast radius, rollback strategy, and acceptance criteria. No source files are written.
4. **EXECUTE** — `vc-execute-agent` implements exactly what the approved plan specifies. It pauses at ~50% completion to report status. If reality diverges from the plan, it stops and routes back to PLAN rather than improvising.
5. **UPDATE PROCESS** — `vc-update-process-agent` reviews the session, proposes improvements to context files, agent prompts, and process documents, presents them for user approval, then implements approved items and archives the plan to `completed/`.

Each transition requires an explicit user command ("go" or a mode command).

Source: [README.md](https://github.com/withkynam/vibecode-pro-max-kit/blob/main/README.md) | [CLAUDE.md](https://github.com/withkynam/vibecode-pro-max-kit/blob/main/CLAUDE.md)

**Context routing** uses `process/context/all-context.md` as a root router. Agents read the root router first, then follow its routing table to domain-specific context groups. When a topic accumulates 5+ artifacts, it is promoted to its own dedicated context group.

**Phase programs** extend RIPER-5 for large multi-phase initiatives. An umbrella orchestration plan runs alongside individual phase plans. Each phase runs its own 10-step read-execute-validate-report loop, and only advances after its own gates pass AND regression checks on previously verified surfaces pass. Status labels (`PLANNED`, `CODE DONE`, `TESTING`, `VERIFIED`, `BLOCKED`) are honest checkpoints, not aspirational markers.

Source: [phase-programs.md](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/process/development-protocols/phase-programs.md)

**Parallel execution** via `vc-team` spawns multiple Claude Code sessions per git worktree, each with isolated context windows, coordinating through a task-list and messaging system. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and Claude Opus 4.6.

### 4. Who It's For and What Problems It Solves

The kit targets three distinct personas:

- **Developers on long-lived codebases** — structured workflows, durable specs, context that compounds over weeks
- **Product owners and PMs** — plan artifacts are readable without understanding raw prompts; they can review and approve AI work before execution
- **Non-technical builders (CEOs, solopreneurs)** — phase gates prevent the agent from charging ahead before intent is understood

Problems explicitly addressed:

- **Context rot** — knowledge is persisted to disk rather than held only in the chat window
- **Mid-task collapse** — phase-locked disk state survives context compaction and session resets
- **Silent deviation** — agents stop rather than improvise when reality diverges from the plan
- **Stale documentation** — `vc-update-process-agent` refreshes context files after every feature
- **High-risk paths** — auth, billing, schema changes, and API contracts require an "evidence pack" before the agent considers them complete

### 5. Strengths and Notable Ideas Worth Borrowing

**Phase locking via tool restriction, not suggestions.** The research agent literally does not have write tools. The plan agent can only write to `process/*/active/`. This is structural capability removal, not a "please don't" rule. Teams can adopt this pattern independently by defining per-agent tool allowlists.

**The UPDATE PROCESS phase as a first-class workflow step.** Making knowledge capture mandatory and requiring user approval of each proposed improvement ensures the self-improvement loop doesn't silently corrupt context. This is the most novel architectural idea in the kit.

**`vc-predict` — 5-persona pre-implementation debate.** Running Architect, Security, Performance, UX, and Devil's Advocate perspectives in parallel before writing any code, synthesizing a structured GO/CAUTION/STOP verdict — portable with no kit dependency.

Source: [vc-predict SKILL.md](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-predict/SKILL.md)

**`vc-scenario` — 12-dimension edge case generation.** Systematically applying 12 orthogonal dimensions (concurrency, scale, auth boundaries, compliance, error cascades, etc.) to any feature before test design. Reusable as a standalone checklist.

Source: [vc-scenario SKILL.md](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-scenario/SKILL.md)

**`vc-autoresearch` — autonomous metric optimization.** One-sentence atomic changes, git commits as cross-iteration memory, stuck detection after 10 consecutive failures, TSV result tracking. A clean framework for mechanical improvement tasks (coverage, bundle size, lint).

Source: [vc-autoresearch SKILL.md](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-autoresearch/SKILL.md)

**Evidence packs for high-risk work.** Requiring a `risk-gate.json` and `context-snippets.json` before auth, billing, and schema changes are considered complete.

**Context routing via a root router file.** `all-context.md` acts as a living index that agents read first and follow. Reorganization is transparent to agents; no stale hardcoded references.

**The `process/` directory as a team artifact.** Plans, contexts, and protocols live in the repository — version-controlled, shareable, inspectable by humans without any special interface.

**Cross-IDE compatibility via open standards.** `AGENTS.md` and `SKILL.md` work in Claude Code, Cursor, Codex, and Windsurf without adapters.

Source: [AGENTS.md](https://github.com/withkynam/vibecode-pro-max-kit/blob/main/AGENTS.md)

### 6. Gaps, Limitations, and Things It Does Not Cover

**Setup overhead is real.** Adding `.claude/`, `process/`, `CLAUDE.md`, `AGENTS.md`, and `.codex/` to the repository root is a visible structural change. Monorepos or CI systems sensitive to root-level files need evaluation.

**Self-improvement quality depends on early context quality.** If the first sessions produce poorly-formatted or inaccurate context files, subsequent agents build on that noise. No validation mechanism to detect context drift other than `vc-audit-context`.

**Model version stability is unvalidated.** Agent behaviors defined in markdown files need ongoing maintenance as model behavior shifts.

**`vc-team` has narrow platform support.** Experimental flag, CLI-only, Opus 4.6 required, 400K-800K tokens for execute templates. Do not depend on for production workflows yet.

**Two contributors is a concentration risk.** Framework-level decisions are not yet community-driven. Core is tightly held.

**Metric inconsistency in public documentation.** Skill counts (31, 32, 34) and star counts (668, 874, 885) conflict across sources — treat as approximate.

**No built-in harness health CI.** `vc-audit-vc` skill exists but no CI pipeline validates agent definitions, skill files, or hook logic on each commit.

**RIPER-5 is not appropriate for all work.** Trivial fixes (single file, under 15 lines, no schema or auth changes) can bypass full phase sequence. Newer teams may over-apply it, creating friction without benefit.

### 7. How a Team Could Adopt or Adapt It

**Full adoption path:**

1. Run the installer in a development branch, review all added files before merging to main
2. Run `vc-setup` in Claude Code — do not skip; empty context files undermine the entire system
3. Agree on a starting agent set (recommended: `vc-research-agent`, `vc-plan-agent`, `vc-execute-agent`, `vc-update-process-agent`)
4. Run `vc-predict` on the first 2-3 significant features to build team familiarity
5. After each feature, run `vc-update-process-agent` to begin compounding context improvements

**Selective adoption (borrow ideas without full install):**

- **The plan file format**: Mandate touchpoints, blast radius, and acceptance criteria in every feature ticket
- **`vc-predict` pattern**: Structured pre-implementation review with explicitly named personas before high-stakes decisions
- **`vc-scenario` checklist**: Add the 12-dimension edge case table to code review or QA checklists
- **Phase-locked tool restriction**: Define explicit tool allowlists per agent type in custom Claude Code agents
- **Context routing via a root router**: Single `all-context.md` index linking to domain-specific context files, updated after each feature
- **Evidence pack requirement**: Formal evidence artifact required before closing issues touching auth, billing, or schema

**Adaptation considerations:**

- Rename `vc-` prefixes to team's internal namespace if mixing with other Claude workflows
- For monorepos, evaluate whether `process/` belongs at the repo root or per-package
- If already using CLAUDE.md or AGENTS.md, review installer merge carefully — backup exists but manual review is safer
- `vc-publish` can be pointed at a private fork for teams with internal tooling

---

## Trade-offs / Caveats

- **Metric inconsistency across sources.** Star count: 885 (GitHub page), 874 (Trendshift), 668 (search snippet). Skill count: 31 (README), 32 (search title), 34 (directory listing). All counts are approximate as of June 2026.
- **The Salvucci external review** is the only third-party analysis found. Broadly positive but notes setup overhead, data quality dependency, and model stability concerns. May reflect a pre-v2.4.2 version.
- **RIPER-5 phase sequencing adds latency.** Mandatory research-innovate-plan gates before any code is written — a safety feature that also means simple changes require multiple explicit approvals.
- **`vc-team` parallel execution is experimental.** Non-default environment variable, CLI-only, Opus 4.6 required. Do not depend on for production workflows.

---

## Sources

- [GitHub — withkynam/vibecode-pro-max-kit](https://github.com/withkynam/vibecode-pro-max-kit)
- [README.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/README.md)
- [CLAUDE.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/CLAUDE.md)
- [AGENTS.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/AGENTS.md)
- [install.sh (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/install.sh)
- [vc-execute-agent.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/agents/vc-execute-agent.md)
- [vc-research-agent.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/agents/vc-research-agent.md)
- [vc-plan-agent.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/agents/vc-plan-agent.md)
- [vc-debugger.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/agents/vc-debugger.md)
- [vc-update-process-agent.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/agents/vc-update-process-agent.md)
- [vc-predict SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-predict/SKILL.md)
- [vc-scenario SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-scenario/SKILL.md)
- [vc-autoresearch SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-autoresearch/SKILL.md)
- [vc-security SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-security/SKILL.md)
- [vc-team SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-team/SKILL.md)
- [vc-setup SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-setup/SKILL.md)
- [vc-watzup SKILL.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/skills/vc-watzup/SKILL.md)
- [privacy-block.cjs (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/hooks/privacy-block.cjs)
- [session-init.cjs (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/.claude/hooks/session-init.cjs)
- [phase-programs.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/process/development-protocols/phase-programs.md)
- [implementation-standards.md (raw)](https://raw.githubusercontent.com/withkynam/vibecode-pro-max-kit/main/process/development-protocols/implementation-standards.md)
- [Trendshift — vibecode-pro-max-kit](https://trendshift.io/repositories/40541)
- [Stefano Salvucci — Vibecode Pro Max Kit vs Context Rot](https://www.stefanosalvucci.com/en/blog/vibecode-pro-max-kit-ai-context-memory-tool)
