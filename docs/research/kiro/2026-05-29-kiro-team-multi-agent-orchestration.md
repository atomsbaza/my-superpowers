# Research: requix/kiro-team — Multi-Agent Orchestration for Kiro CLI

## Summary

`kiro-team` is a ready-to-copy configuration package that layers a structured multi-agent team pattern on top of Kiro CLI's built-in subagent system. It defines four specialized agents (team-lead, builder, validator, documenter) with explicit tool restrictions, a planning skill (`@plan-with-team`), and two bash scripts that wrap `git worktree` to give each execution run an isolated branch. The system enforces a strict planning → build → validate → document loop with a bounded retry protocol and automatic merge-on-success behavior. It requires **Kiro CLI 2.0 or later**, is MIT-licensed, and was last updated May 2026.

---

## What It Is and What Problem It Solves

`kiro-team` is not a standalone npm/pip package — it is a **copy-into-your-project configuration set**: a `.kiro/` directory and a `scripts/` directory.

The core problem it solves: Kiro CLI's built-in subagent system gives you the primitive (spawn an agent, restrict its tools), but does not prescribe *who does what, when, or in what isolation boundary*. `kiro-team` is an opinionated workflow pattern built on top of that primitive.

Each spec execution runs in a dedicated `git worktree` (`.worktrees/<spec-name>/`), so multiple plans can execute in parallel in separate terminals without filesystem conflicts.

Source: [GitHub — requix/kiro-team](https://github.com/requix/kiro-team)

---

## Repository Structure

```
kiro-team/
├── .kiro/
│   ├── agents/               ← 4 agent configs (JSON + prompt Markdown)
│   ├── prompts/              ← plan-with-team.md (legacy prompt path)
│   └── skills/
│       └── plan-with-team/
│           └── SKILL.md      ← skill definition for @plan-with-team
├── scripts/
│   ├── worktree-create.sh
│   └── worktree-merge.sh
├── .gitignore
├── LICENSE                   ← MIT
└── README.md
```

---

## Installation

No package manager install. The setup is a direct file copy:

```bash
# Copy .kiro and scripts into the root of your project
cp -r .kiro /path/to/your/project/
cp -r scripts /path/to/your/project/scripts

# Optionally enable the TODO list feature in Kiro CLI
kiro-cli settings chat.enableTodoList true
```

The `.kiro/agents/` files must remain at the root level of that directory — no subdirectories — for Kiro to resolve them as named subagents.

---

## Agent Roles and Tool Restrictions

All four agents use `claude-sonnet-4` as the model. Tool access is enforced via both `tools` and `allowedTools` arrays in each JSON config (both must match):

| Agent | Tools | What It Cannot Do |
|---|---|---|
| **team-lead** | `read`, `subagent`, `todo` | Write code or files directly |
| **builder** | `read`, `write`, `shell` | Spawn agents or access todo list |
| **validator** | `read`, `shell` (read-only mode) | Modify any files |
| **documenter** | `read`, `write` | Run shell commands or spawn agents |

The `team-lead.json` `toolsSettings` block uses `trustedAgents` to restrict delegation to only the three named agents:

```json
"toolsSettings": {
  "subagent": {
    "trustedAgents": ["builder", "validator", "documenter"]
  }
}
```

This means the team-lead cannot accidentally delegate to any other custom agent in the workspace.

---

## The `@plan-with-team` Skill

- Invoked in Kiro chat via `@plan-with-team <description>` — no clarification prompts, generates a spec immediately.
- Writes a Markdown spec file to `specs/<kebab-case-name>.md` with: task description, problem/solution, file inventory, team member assignments, numbered tasks with declared dependencies, acceptance criteria, and validation commands.
- Does **not** write code or spawn agents — planning only.
- After planning, the user switches agent with `/agent swap` → `team-lead` and instructs it to execute the plan.

---

## Execution Workflow (End-to-End)

1. **Plan**: `@plan-with-team <description>` → creates `specs/<name>.md`
2. **Swap**: `/agent swap` → `team-lead`
3. **Team Lead initializes**: Runs `bash scripts/worktree-create.sh <spec-name>` as its **first action** to create `.worktrees/<spec-name>/` on branch `spec/<spec-name>`
4. **Build loop** (per task in the spec):
   - Spawns builder with absolute worktree path and task instructions
   - Builder writes files, commits changes, reports results
   - Team lead immediately spawns validator; validator reads files, runs tests (read-only), reports pass/fail
   - On pass: TODO item marked complete; move to next task
   - On fail: retry up to 3 attempts (attempt 3 puts validator in diagnostic mode, builder receives root-cause analysis); 4th failure writes an incident report and marks task `[BLOCKED]`
5. **Pre-merge checkpoint**: Team lead verifies clean working directory, branch exists, commit history present, all expected files exist
6. **Merge**: Runs `bash scripts/worktree-merge.sh <spec-name>` which does `git merge --no-ff`, removes the worktree directory, deletes the branch, and prunes stale refs
7. **Documentation** (non-blocking): Spawns documenter to write `app_docs/feature-<name>.md`

---

## The Worktree Scripts

**`worktree-create.sh <spec-name>`**: Idempotent — if `.worktrees/<spec-name>/` already exists, prints its path and exits cleanly. If a stale branch without a worktree exists, deletes the orphaned branch first. Creates the worktree via `git worktree add`.

**`worktree-merge.sh <spec-name>`**: Merges `spec/<spec-name>` into the current branch with `--no-ff`. On success: removes worktree directory, deletes branch, prunes refs. On conflict: identifies conflicting files, aborts the merge, preserves the worktree for manual resolution. Exits with code 1 on failure.

---

## How It Relates to Kiro's Built-in Subagent System

`kiro-team` is an **opinionated pattern layered on top** of the native primitive — it does not modify or extend Kiro's code:

| Layer | Kiro Built-in | kiro-team |
|---|---|---|
| Agent spawn mechanism | `subagent` tool | Uses same `subagent` tool |
| Parallel execution | Up to 4 concurrent | Sequential per task (builder then validator) |
| Tool restrictions | `tools`/`allowedTools` JSON fields | Preconfigured per-role restrictions |
| Workflow structure | You define it | Prescribes plan→build→validate→document |
| Isolation | None built in | Git worktree per spec |
| Retry/recovery | None built in | Bounded 3-attempt retry with incident reports |
| Progress tracking | Ctrl+G monitor | TODO list (team-lead only) |

---

## Documentation Output

The documenter agent writes to `app_docs/` using the naming convention `feature-<descriptive-name>.md`. Each doc includes: overview, what was built, technical implementation (file paths, functions, APIs, new dependencies), usage (with commands and code examples), and configuration. It creates `app_docs/` if it does not exist. Documentation generation is non-blocking.

---

## Maintenance Status

- 7 total commits; 3 in May 2026, 1 in March 2026, 3 in February 2026
- Most recent commit: "feat: Kiro CLI 2.0 compatibility (#7)" — May 6, 2026
- 0 open issues, 0 closed issues
- Single maintainer (requix)
- MIT license

---

## Trade-offs / Caveats

- **Kiro CLI 2.0 minimum requirement is a hard constraint.** Verify your Kiro CLI version before adopting.
- **`todo` tool is not available in the subagent runtime** (Kiro CLI platform limitation). Only the team-lead can see the TODO list — subagents operate blind to overall progress.
- **Builder tasks are sequential, not parallel within a spec.** Two separate specs can run in parallel in separate terminals, but within a single spec tasks are sequential.
- **No MCP server integrations.** Unlike the AWS official sample, kiro-team ships with no MCP dependencies. Simpler setup but no live documentation lookup or external API access unless you add those yourself.
- **No hooks.** Agents have no Pre/Post Tool Use enforcement.
- **Single maintainer, small repo.** Treat as a starter template to fork and customize rather than a stable upstream dependency.
- **Spec quality drives execution quality.** The team-lead reads spec files verbatim — vague acceptance criteria or validation commands will produce inconsistent results.
- **Conflict resolution is manual.** If `worktree-merge.sh` encounters a merge conflict, it aborts and exits with code 1, leaving the worktree intact for manual resolution.
- **IDE vs CLI format.** This repo targets **CLI only**. Configs are not directly portable to IDE markdown frontmatter format.

---

## Sources

- [GitHub — requix/kiro-team](https://github.com/requix/kiro-team) — primary source: README, file structure, commit history
- [Kiro CLI Subagents Documentation](https://kiro.dev/docs/cli/chat/subagents/) — the underlying primitive
- [DEV Community — Parallel Execution with Kiro Custom Subagents](https://dev.to/aws-builders/aws-parallel-execution-of-tasks-using-kiros-custom-subagents-kiro-n77) — parallel execution benchmarks (~61% faster than sequential)
- [GitHub — aws-samples/sample-kiro-cli-multiagent-development](https://github.com/aws-samples/sample-kiro-cli-multiagent-development) — AWS official multi-agent reference for comparison
- [Kiro IDE Changelog](https://kiro.dev/changelog/ide/) — timeline context for when the ecosystem kiro-team targets became available
