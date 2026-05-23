# my-superpowers

Personal collection of AI coding agent skills and agents for Claude Code, Codex CLI, Kiro, and other tools.

## What's inside

- `skills/` — reusable skill prompts (cross-platform)
- `agents/` — agent definitions (Claude Code)

## Install

```bash
git clone <this-repo> ~/my-superpowers
cd ~/my-superpowers
chmod +x install.sh
./install.sh
```

The install script symlinks skills into the right directories for each tool detected on your machine:

| Tool | Skills path | Agents path |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/` |
| Codex CLI | `~/.agents/skills/` | — |
| Kiro | `~/.kiro/skills/` | — |

## Skills

| Skill | What it does |
|---|---|
| `research` | Web research agent — searches, fetches, synthesizes a cited report |
| `brainstorming` | Explore intent and design before implementation |
| `writing-plans` | Turn a spec into a step-by-step implementation plan |
| `subagent-driven-development` | Execute plans task-by-task with fresh subagents + 2-stage review |
| `executing-plans` | Inline plan execution with checkpoints |
| `dispatching-parallel-agents` | Run independent tasks in parallel |
| `finishing-a-development-branch` | Guided merge/PR/cleanup when implementation is done |
| `verification-before-completion` | Run checks before claiming work is done |
| `using-git-worktrees` | Isolated workspace setup before plan execution |
| `requesting-code-review` | Structured workflow for requesting review |
| `receiving-code-review` | Handle review feedback rigorously |
| `scrutinize` | Outsider sanity check — "should this exist?" |
| `adr` | Capture architecture decisions as ADR documents |
| `diagnose` | Disciplined bug investigation loop |
| `post-mortem` | Write the canonical record of a fixed bug |
| `spike` | Time-boxed technical investigation |
| `prototype` | Build throwaway prototypes to explore designs |
| `session-summary` | Summary of current work session |
| `handoff` | Compact conversation for another agent |
| `management-talk` | Rewrite technical content for leadership |
| `improve-codebase-architecture` | Find refactoring opportunities in a codebase |
| `find-skills` | Discover and install new skills |
| `writing-skills` | TDD-based guide for creating new skills |

## Agents (Claude Code)

| Agent | What it does |
|---|---|
| `research` | Web research subagent (WebSearch + WebFetch) |
| `code-reviewer` | Line-by-line bug and security review |
| `debugger` | Root cause analysis for bugs |
| `docs-writer` | Write documentation |
| `doc-updater` | Keep docs in sync with code |
| `refactor` | Refactor for clarity and maintainability |
| `test-writer` | Write tests for existing code |
| `pr-description` | Write PR titles and descriptions |
| `dependency-auditor` | Audit new dependencies before adding |
| `silent-failure-hunter` | Find swallowed errors and unsafe fallbacks |
| `release-checklist` | Pre-release checklist |
| `accessibility-reviewer` | Review UI accessibility |
| `wiki-updater` | Update Logseq project wiki |

## Credits

Several skills adapted from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.
