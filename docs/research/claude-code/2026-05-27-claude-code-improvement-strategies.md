# Research: Making Claude Code Progressively Better Over Time

## Summary

Claude Code's long-term effectiveness rests on two distinct ideas that are easy to conflate: configuration (what Claude knows at session start) and compounding improvement (how that configuration evolves based on real experience). The official Anthropic guidance provides a clear substrate — CLAUDE.md, `.claude/rules/`, skills, hooks, subagents, and MCP servers — but the community has converged on one overriding practice: after every correction, capture the lesson somewhere permanent. Auto memory (shipped in Claude Code v2.1.59, February 2026) automates part of this loop. The rest requires deliberate habits around pruning, retrospectives, and treating configuration files as living artifacts rather than one-time setup.

---

## Key Findings

### 1. The Improvement Loop Is the Spine

The highest-leverage practice is treating every correction as a configuration update. Boris Cherny's (Claude Code creator) ~100-line CLAUDE.md is structured explicitly around this: it includes a self-improvement loop directive — "After ANY correction: update `tasks/lessons.md`" — and a lessons file is maintained as a session-to-session log [Claude Code Creator Workflow](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/).

The Towards Data Science community piece extends this further with a nightly self-reflection skill: a scheduled cron invokes Claude Code to review the past 24 hours of interactions, identify patterns in failures, and update documentation, skills, and hooks autonomously [How I Continually Improve My Claude Code](https://towardsdatascience.com/how-i-continually-improve-my-claude-code/).

The official memory documentation codifies the trigger conditions for adding to CLAUDE.md: "Claude makes the same mistake a second time; a code review catches something Claude should have known; you type the same correction that you typed last session" [How Claude Remembers Your Project](https://code.claude.com/docs/en/memory).

### 2. CLAUDE.md: Lean and Curated, Not Comprehensive

The official guidance recommends a target under 200 lines per CLAUDE.md file, with adherence degrading on longer files [How Claude Remembers Your Project](https://code.claude.com/docs/en/memory). The official best practices page frames the curation test as: "Would removing this cause Claude to make mistakes? If not, cut it" [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices).

What belongs: bash commands Claude can't guess, code style rules that diverge from defaults, testing instructions, repo etiquette, architectural decisions specific to the project, environment quirks, common gotchas. What to exclude: standard language conventions Claude already knows, information that changes frequently, file-by-file codebase tours.

Adding emphasis markers like "IMPORTANT" or "YOU MUST" to high-priority rules improves adherence. Checking CLAUDE.md into git lets the file compound in value across the whole team.

CLAUDE.md files stack hierarchically: `~/.claude/CLAUDE.md` (all projects), `./CLAUDE.md` or `./.claude/CLAUDE.md` (project, shared), `./CLAUDE.local.md` (personal, gitignored), and parent/child directories for monorepos. All discovered files are concatenated, not overridden.

### 3. `.claude/rules/`: Modular, Path-Scoped Instructions

For larger projects, `.claude/rules/` decomposes instructions into individual topic-scoped markdown files (e.g., `testing.md`, `api-design.md`, `security.md`). Without YAML frontmatter, rules load unconditionally at session start. With YAML frontmatter, rules become conditional:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All API endpoints must include input validation
```

Path-scoped rules trigger only when Claude reads matching files, preventing context bloat when working in unrelated areas. User-level rules at `~/.claude/rules/` apply to every project.

### 4. Skills: On-Demand, Not Always-Loaded

Skills (`.claude/skills/<name>/SKILL.md`) are markdown files Claude loads on demand rather than every session. They are the right home for multi-step repeatable procedures, domain knowledge that only applies sometimes, and long reference content that would otherwise inflate CLAUDE.md.

Skills can define slash commands: `/fix-issue 1234` invokes a skill that runs `gh issue view`, locates relevant files, implements a fix, writes tests, and opens a PR. Setting `disable-model-invocation: true` in the frontmatter makes a skill side-effect-safe and manually invoked only.

### 5. Hooks: Deterministic Enforcement

Hooks run shell commands at fixed lifecycle points (PreToolUse, PostToolUse, PreCompact, Stop, etc.) regardless of what the model decides. The official docs state: "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens."

A community heuristic (not an official Anthropic measurement) estimates CLAUDE.md instructions are followed ~70% of the time while hooks enforce at 100% — treat this as directional. The practical implication: use CLAUDE.md for guidance, hooks for non-negotiables.

Common hook patterns:
- `PreToolUse` on `Bash`: block writes to sensitive files (`.env`, `.key`, `.pem`, migration folders)
- `PostToolUse` on `Edit`: run `eslint` or formatters after each file change
- `Stop`: send desktop notifications when Claude needs input
- `PostToolUse`: validate command output format before it re-enters context

### 6. Subagents: Context Preservation and Specialization

Subagents (`.claude/agents/<name>.md`) run in their own context windows with their own system prompt, tool access, and optionally a different model.

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
You are a senior security engineer. Review code for...
```

Practical patterns:
- **Writer/Reviewer**: one session implements, a fresh subagent reviews the diff with no bias toward the code it just read
- **Parallel research**: multiple subagents investigate separate parts of a codebase simultaneously
- **Cost control**: route lightweight tasks to `haiku` via the `model:` field in subagent frontmatter
- Subagents can maintain their own auto memory independently of the main session

### 7. Auto Memory: Claude Learning Without Manual Effort

Auto memory (v2.1.59+, February 2026) lets Claude save its own notes across sessions. Storage lives at `~/.claude/projects/<repo>/memory/MEMORY.md`, loaded for the first 200 lines or 25KB at session start. Overflow files are read on demand.

Claude decides what is worth remembering — build commands, debugging insights, code style preferences discovered mid-session — without requiring any user action. All files are plain markdown, editable at any time via `/memory`.

Auto memory is per-git-repo and machine-local. It is not shared across machines or cloud environments.

### 8. MCP Servers: External Context and Tools

MCP servers connect Claude to external tools (databases, issue trackers, Figma, Notion, deployment platforms) without relying on the model's general knowledge.

Community best practices:
- Scope by sensitivity: project scope for team-safe tools, user scope for private tokens
- Install one at a time and verify Claude uses it correctly before adding the next
- Prefer small, well-described tools over massive APIs that flood context with irrelevant listings
- Request summaries rather than raw output when tools return large payloads
- Never commit secrets — read tokens from environment variables or native secret storage

### 9. Prompt Engineering Within Sessions

- **Plan mode first**: use plan mode for any multi-file or ambiguous task; correct the plan before implementation begins
- **Give Claude verification criteria**: concrete examples and test cases outperform vague descriptions
- **Let Claude interview you**: for larger features, start with `"I want to build X. Interview me using the AskUserQuestion tool."` then start a fresh session with the resulting spec
- **`/clear` hygiene**: one task per conversation avoids context pollution
- **Escape from correction loops**: if Claude makes the same mistake twice, `/clear` and write a better initial prompt
- **Session retrospectives**: ask "What did you learn this session?" and route the output to `tasks/lessons.md`, CLAUDE.md, or the appropriate skill/rule file

---

## Decision Matrix: Which Extension Mechanism to Use

| Mechanism | Who writes it | When it loads | Enforcement | Best for |
|---|---|---|---|---|
| `CLAUDE.md` | You | Every session | Advisory | Project-wide conventions, always-applicable rules |
| `.claude/rules/*.md` (unconditional) | You | Every session | Advisory | Modular topic organization, team-maintainable |
| `.claude/rules/*.md` (path-scoped) | You | On matching file read | Advisory | Language/directory-specific rules without context bloat |
| `Skills` | You | On demand / slash command | Advisory | Multi-step workflows, long domain knowledge, procedures |
| `Hooks` | You | At lifecycle events | Deterministic | Linting, formatting, security blocks, notifications |
| `Subagents` | You | On delegation | Advisory | Context isolation, specialized focus, parallel research |
| `Auto memory` | Claude | Every session (first 200 lines) | Advisory | Session learnings, build commands, debugging insights |
| `MCP servers` | You/ops | On tool call | Tool availability | External services, databases, APIs, design tools |

---

## Trade-offs / Caveats

- **Adherence is probabilistic.** CLAUDE.md and rules files are context — Claude reads them and tries to follow them, but compliance is not guaranteed. If an action must happen, encode it in a hook. The "70% vs 100%" figure is a community heuristic, not an Anthropic measurement.
- **The 60% context capacity threshold** (don't let context exceed 60% before `/clear`) is a community rule of thumb, not an official Anthropic recommendation.
- **Auto memory is machine-local.** Notes do not sync across machines or cloud environments.
- **Adversarial review gap.** A reviewer prompted to find gaps will usually report some even when code is sound. Scope reviewer subagents explicitly.
- **Most official docs carry no publication date.** Community posts cited here are current as of May 2026.

---

## Sources

- [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — Official Anthropic guide
- [How Claude Remembers Your Project](https://code.claude.com/docs/en/memory) — Official Anthropic memory documentation
- [Create Custom Subagents](https://code.claude.com/docs/en/sub-agents) — Official Anthropic subagent documentation
- [Automate Workflows with Hooks](https://code.claude.com/docs/en/hooks-guide) — Official Anthropic hooks guide
- [Claude Code Setup: MCP, Hooks, Skills 2026](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/) — Community setup guide
- [I Spent 6 Months Tuning Claude Code](https://medium.com/data-science-collective/i-spent-6-months-tuning-claude-code-heres-the-exact-setup-that-finally-worked-b41c67628478) — Community post (Anubhav, Apr 2026)
- [How I Continually Improve My Claude Code](https://towardsdatascience.com/how-i-continually-improve-my-claude-code/) — Community post on nightly self-reflection and autonomous improvement loops
- [Claude Code Tips I Wish I'd Had From Day One](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) — Community post (marmelab, Apr 2026)
- [Claude Code Creator Workflow: CLAUDE.md](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/) — Analysis of Boris Cherny's CLAUDE.md and lessons.md pattern
- [How Claude Code Rules Actually Work](https://joseparreogarcia.substack.com/p/how-claude-code-rules-actually-work) — Technical deep-dive on `.claude/rules/` loading behavior
- [Claude Code Rules for AI](https://kirill-markin.com/articles/claude-code-rules-for-ai/) — Community source for advisory/deterministic distinction
