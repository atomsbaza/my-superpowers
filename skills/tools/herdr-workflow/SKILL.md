---
name: herdr-workflow
description: Coordinate Codex CLI, Claude CLI, Kiro CLI, and other supported coding agents through Herdr. Use when creating or managing Herdr panes, starting an agent, assigning parallel work, gathering an agent handoff, or isolating agent code changes in Git worktrees.
---

# Herdr workflow

Follow the built-in Herdr guidance first:

```sh
herdr --skill
```

Use this skill for the team conventions below. Do not use Herdr controls unless `HERDR_ENV=1`.

## Team rules

- Use Herdr agent controls for recognized coding agents. Use pane controls only for raw terminals or ordinary commands.
- Keep background work unfocused with `--no-focus`.
- Discover pane and agent IDs from Herdr JSON responses; do not infer them from layout order.
- Give each live agent a unique role name: `implementer`, `reviewer`, `tester`, or a clear task-specific equivalent. Herdr rejects a duplicate live name, so whenever more than one task pipeline may run at once, scope names to the task, e.g. `implementer-<task-slug>`, `reviewer-<task-slug>`.
- Require a dedicated Git worktree for every coding agent that might modify code. A read-only research or review agent may use the primary checkout only when its task is not tied to a specific in-progress worktree (e.g. general codebase questions). When reviewing or testing a specific implementer's in-progress work, point that agent's pane `--cwd` at the **implementer's own worktree** so it sees the actual uncommitted changes — the primary checkout will not show them.
- When `herdr worktree create` or `herdr worktree open` creates a dedicated worktree, use the returned root pane directly for the agent. Do not split another pane after opening or creating that worktree; split only when reusing an existing workspace that has no worktree-created root pane.
- Never close, interrupt, or repurpose a pane, worktree, tab, or session not created for the current task.

## Coordinate an agent

1. Verify the session and inspect the current layout:

   ```sh
   test "${HERDR_ENV:-}" = 1
   herdr pane current --current
   herdr pane layout --pane "$HERDR_PANE_ID"
   ```

2. Create or select an isolated worktree before starting any agent that can edit code. Use the repository's established worktree convention; inspect `herdr worktree --help` when using Herdr's helper. If `herdr worktree create` or `herdr worktree open` returns a root pane, keep its `.result.root_pane.pane_id` for the agent.

3. If the worktree helper returned a root pane, use it as the available shell pane and keep it unfocused. Only create a background sibling pane when starting from an existing workspace or tab without a dedicated worktree root. Split right when the calling pane is wide; otherwise split down:

   ```sh
   herdr pane split --current --direction down --cwd <worktree-path> --no-focus
   ```

   Take the new pane ID from `.result.pane.pane_id`.

4. Start the requested supported agent in the available shell pane:

   ```sh
   herdr agent start implementer --kind codex --pane <pane-id>
   ```

   Replace `codex` with the requested kind, such as `claude` or `kiro`. Do not assume the kind is installed; use `herdr agent start --help` if needed.

5. Assign a scoped task with completion criteria and require a handoff:

   ```sh
   herdr agent prompt implementer "Work only in your assigned worktree. Implement <task>. Run the relevant validation. When done, report: changed files, validation run/results, remaining risks, and the branch/worktree to integrate." --wait --timeout 120000
   ```

6. Read the result before any follow-up or integration:

   ```sh
   herdr agent read implementer --source recent-unwrapped --lines 120
   ```

## Handle agent state

- On `done` or `idle`, read the handoff and independently inspect changes or validation as appropriate.
- On `blocked`, run `herdr agent get <name>` and `herdr agent read <name> --source recent-unwrapped --lines 120`; route the question or approval to the lead/user. Do not blindly send approval keys.
- On timeout or `unknown`, inspect output first. Do not resend a prompt until it is clear whether the agent is still working.
- On `agent_prompt_stalled`, inspect `herdr agent get <name>` and `herdr agent read <name>` before retrying. The agent may already be idle for a different reason; do not resend the same prompt blindly.

## Parallel work and handoff

Assign non-overlapping responsibilities and worktrees. For example: one `implementer` changes code, one `reviewer` reviews the implementation worktree without editing it, and one `tester` validates it in a separate worktree or isolated environment.

Before integration, collect from every agent:

- worktree path and branch;
- changed files and intent;
- commands run and their results;
- remaining risks, blockers, or follow-ups.

The lead agent integrates only after reviewing the handoff and relevant diff. Keep the agent pane available until that handoff is accepted.

## Verify a document against live system state

Use this for a read-only fact-check — e.g. confirming a research report, guide, or generated doc actually matches a live CLI/API/docs site — as opposed to reviewing code changes. No worktree is required since nothing is being edited.

1. Default to the **current Herdr workspace** — do not create a new `herdr workspace` just to run a verification agent; splitting a pane in the existing workspace/tab is enough. Only create a new workspace when the document under review concerns a different project/cwd than what's currently open (`herdr workspace create --cwd <path> --label <slug> --no-focus`).
2. Split a pane in that workspace with `--no-focus` and start the requested agent kind under a task-scoped name (e.g. `reviewer-<topic>`).
3. Prompt it with the file path to review and concrete verification instructions: what to cross-check against (live `--help` output, docs URLs, actual runtime behavior), and what to report back (what checks out, what's wrong or invented, what's missing, a pass/fail verdict). Use `--wait --timeout <ms>`.
4. Read the result with `herdr agent read <name> --source recent-unwrapped --lines <n>`.
5. Fix any confirmed issues yourself (directly, not via the reviewing agent), then re-prompt the **same** agent/pane for a follow-up pass instead of starting a new one — it already has the review context loaded, and reusing it is cheaper and catches regressions from the fix itself.
6. Repeat until a clean pass, then close the pane per Clean up after integration below.

This differs from Coordinate an agent above in three ways: no worktree, the agent is reused across iterations rather than restarted per round, and completion is a pass/fail verdict rather than a code handoff.

## Clean up after integration

Once a handoff is accepted and integrated, reclaim the resources this workflow created for that task — do not leave panes, agents, or worktrees running indefinitely:

```sh
herdr pane close <pane-id>
herdr worktree remove <worktree-path>
```

Only close or remove panes, agents, and worktrees this workflow created for the completed task. Leave anything else untouched.
