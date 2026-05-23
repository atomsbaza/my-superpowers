# my-superpowers

Personal collection of AI coding agent skills and agents for Claude Code, Codex CLI, Kiro, and other tools.

## Install

```bash
git clone git@github.com:atomsbaza/my-superpowers.git ~/my-superpowers
cd ~/my-superpowers && chmod +x install.sh && ./install.sh
```

Skills are organized into categories in this repo but installed **flat** into each tool's skills directory — so `/research`, `/brainstorming`, etc. all work as expected.

| Tool | Skills path | Agents path |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/` |
| Codex CLI | `~/.agents/skills/` | — |
| Kiro | `~/.kiro/skills/` | — |

---

## Skills

### Planning
> Use before writing any code — design, investigate, document decisions.

| Skill | What it does |
|---|---|
| `brainstorming` | Explore intent and design before implementation |
| `writing-plans` | Turn a spec into a step-by-step implementation plan |
| `spike` | Time-boxed investigation to answer "can we do X?" |
| `prototype` | Build throwaway prototypes to explore designs |
| `adr` | Capture architecture decisions as ADR documents |

### Execution
> Run the plan.

| Skill | What it does |
|---|---|
| `subagent-driven-development` | Execute plans task-by-task with fresh subagents + 2-stage review |
| `executing-plans` | Inline plan execution with checkpoints |
| `dispatching-parallel-agents` | Run independent tasks in parallel |

### Quality & Review
> Ensure the work is correct before shipping.

| Skill | What it does |
|---|---|
| `scrutinize` | Outsider sanity check — "should this exist?" |
| `requesting-code-review` | Structured workflow for requesting a review |
| `receiving-code-review` | Handle review feedback rigorously, not blindly |
| `improve-codebase-architecture` | Find refactoring and architecture opportunities |
| `verification-before-completion` | Run checks before claiming work is done |

### Debugging
> When things go wrong.

| Skill | What it does |
|---|---|
| `diagnose` | Disciplined bug investigation loop |
| `post-mortem` | Write the canonical record of a fixed bug |

### Git & Branches
> Branch management and release workflow.

| Skill | What it does |
|---|---|
| `using-git-worktrees` | Isolated workspace setup before plan execution |
| `finishing-a-development-branch` | Guided merge/PR/cleanup when implementation is done |

### Communication
> Working with humans and other agents.

| Skill | What it does |
|---|---|
| `session-summary` | Summary of current work session from git + context |
| `handoff` | Compact conversation for another agent to pick up |
| `management-talk` | Rewrite technical content for leadership audiences |

### Tools
> Utility and meta skills.

| Skill | What it does |
|---|---|
| `research` | Web research — searches, fetches, synthesizes a cited report |
| `find-skills` | Discover and install new skills |
| `writing-skills` | TDD-based guide for creating new skills |

---

## Agents

> Agents are Claude Code–specific. They run as subagents via the `Agent` tool.

### Review
| Agent | What it does |
|---|---|
| `code-reviewer` | Line-by-line bug and security review |
| `accessibility-reviewer` | Review UI accessibility across platforms |
| `silent-failure-hunter` | Find swallowed errors and unsafe fallbacks |
| `dependency-auditor` | Audit new dependencies before adding them |

### Documentation
| Agent | What it does |
|---|---|
| `docs-writer` | Write READMEs, API docs, inline comments |
| `doc-updater` | Keep docs in sync with code changes |
| `wiki-updater` | Update Logseq project wiki after meaningful work |

### Development
| Agent | What it does |
|---|---|
| `debugger` | Root cause analysis for bugs and crashes |
| `refactor` | Refactor code for clarity and maintainability |
| `test-writer` | Write unit and integration tests for existing code |

### Workflow
| Agent | What it does |
|---|---|
| `pr-description` | Write PR titles and descriptions from git diff |
| `release-checklist` | Pre-release checklist (iOS, web, smart contracts) |

### Research
| Agent | What it does |
|---|---|
| `research` | Web research subagent (WebSearch + WebFetch) |

---

## Credits

Several skills adapted from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.
