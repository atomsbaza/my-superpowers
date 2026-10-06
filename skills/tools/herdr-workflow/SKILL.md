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
- Give each live agent a name that starts with its role — `implementer`, `reviewer`, `tester`, or a clear equivalent — never the bare issue/task title or slug alone; a name without a role prefix doesn't say what the agent is for. Herdr rejects a duplicate live name, so whenever more than one task pipeline may run at once, append the task slug: `implementer-<task-slug>`, `reviewer-<task-slug>` (e.g. `implementer-1834`, not `1834-worktree-remove-error`).
- Require a dedicated Git worktree for every coding agent that might modify code. Create or open it with `--workspace <current-workspace-id>` so it remains in the current Herdr workspace. A read-only research or review agent may use the primary checkout only when its task is not tied to a specific in-progress worktree (e.g. general codebase questions). When reviewing or testing a specific implementer's in-progress work, point that agent's pane `--cwd` at the **implementer's own worktree** so it sees the actual uncommitted changes — the primary checkout will not show them.
- When `herdr worktree create` or `herdr worktree open` creates a dedicated worktree, use the returned root pane directly for the agent. Do not split another pane after opening or creating that worktree; split only when reusing an existing workspace that has no worktree-created root pane.
- Before `herdr worktree create` or `herdr worktree open`, confirm the target directory is a Git repository or worktree (`git -C <path> rev-parse --git-dir`). A non-repo target fails with `not_git_worktree` after a wasted workspace-create cycle — scaffold or clone the workspace first.
- Run every task command with the worktree as its working directory (`--cwd` on the pane, or `cd` in the agent prompt). A command run from the lead's own cwd hits the wrong tree or fails outright (`ENOENT package.json`).
- Never close, interrupt, or repurpose a pane, worktree, tab, or session not created for the current task.
- Never put credentials, tokens, or other secrets in `herdr agent prompt` text — prompt text and pane output are persisted and readable. Have agents source secrets from their environment or existing config instead.
- Before creating a new pane, agent, or worktree, check what already exists (`herdr pane layout`, `herdr worktree list`, or equivalent) and reuse or clean up rather than accumulating parallel resources unboundedly.
- Default to the **current Herdr workspace**; never create a new one just to run an agent or hold a worktree. Run multiple agents in panes, tabs, and dedicated worktrees within that workspace, opening or creating each worktree with `--workspace <current-workspace-id>`. Only create a new workspace (`herdr workspace create --cwd <path> --label <slug> --no-focus`) when the target project/cwd differs and no suitable workspace already exists.
- Every prompt sent to a spawned agent (`herdr agent prompt`, any kind) must tell it to use its own skills, subagents, or custom agents where relevant to the task, not just raw tool calls — the spawned agent has the same capability to reach for specialized tooling that the lead agent does.

## Coordinate an agent

1. Verify the session and inspect the current layout. Reuse the current workspace for every agent in this project/task, and take its ID from `.result.pane.workspace_id`:

   ```sh
   test "${HERDR_ENV:-}" = 1
   herdr pane current --current
   herdr pane layout --pane "$HERDR_PANE_ID"
   ```

2. Create or select an isolated worktree before starting any agent that can edit code, passing `--workspace <current-workspace-id>` from step 1 so the worktree opens inside the current workspace instead of Herdr creating a separate workspace. Reuse the same workspace for every agent on this project/task; use its panes, tabs, and dedicated worktrees rather than creating another workspace because another agent is needed. Use the repository's established worktree convention; inspect `herdr worktree --help` when using Herdr's helper. If `herdr worktree create` or `herdr worktree open` returns a root pane, keep its `.result.root_pane.pane_id` for the agent.

3. If the worktree helper returned a root pane, use it as the available shell pane and keep it unfocused. Only create a background sibling pane in the existing workspace or tab when no dedicated worktree root is available. Split right when the calling pane is wide; otherwise split down:

   ```sh
   herdr pane split --current --direction down --cwd <worktree-path> --no-focus
   ```

   Take the new pane ID from `.result.pane.pane_id`.

4. Start the requested supported agent in the available shell pane. `implementer` below is illustrative — scope it to the task (`implementer-<task-slug>`) whenever parallel pipelines are possible, per Team rules:

   ```sh
   herdr agent start implementer --kind codex --pane <pane-id>
   ```

   Replace `codex` with the requested kind, such as `claude` or `kiro`. Do not assume the kind is installed; use `herdr agent start --help` if needed. If the start fails (e.g. the kind isn't installed), remove the worktree and pane created in steps 2-3 before retrying with a different kind or aborting — do not leave them orphaned.

5. Assign a scoped task with completion criteria, telling the agent to use its own skills/subagents where relevant, and require a handoff:

   ```sh
   herdr agent prompt implementer "Work only in your assigned worktree. Implement <task>. Use any of your own skills, subagents, or custom agents where relevant to the task. Run the relevant validation. When done, report: changed files, validation run/results, remaining risks, and the branch/worktree to integrate." --wait --timeout 120000
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

## Wait without resending

`herdr agent prompt ... --wait --timeout <ms>` can time out (`timed out waiting for agent status`) while the agent is still `working`: the timeout only ends the wait, not the work. Never resend the prompt. Check `herdr agent get <name>`, then wait again with `herdr agent wait <name> --until idle --until done --timeout <ms>` (repeat in slices, or run the wait in the background) and read the result with `herdr agent read <name> --source recent-unwrapped --lines 200`. A long review (several minutes) is normal.

## Code review with a Codex reviewer

Use when the user asks for a Codex review (see the user's rule: Codex is allowed as a second reviewer for code reviews, never an automatic gate).

1. Pick the tree: a reviewer of uncommitted work points `--cwd` at the tree that holds the changes (the primary checkout, or the implementer's worktree). No new worktree is needed because the reviewer must not edit.
2. Split a pane with `--no-focus`, start `reviewer-<task-slug>` with `--kind codex`, and prompt it read-only: list the commit range and `git diff` scope, the intent of the change, the concrete risk areas, and ask for high-confidence findings only (file:line, failure scenario, fix; new vs pre-existing; zero findings is fine).
3. If tests or a simulator run are in progress, forbid builds and test runs in the prompt (shared DerivedData / simulator).
4. Treat the findings as advisory: verify each against the code yourself before changing anything, fix confirmed ones directly, then re-prompt the **same** reviewer for a follow-up pass (cap 3 rounds), and close the pane afterwards.
5. Do not use the `codex:codex-rescue` subagent as a substitute: it only starts a background task and hands back a task id, not findings.

## Codex as implementer (the user's standard code workflow, 2026-10-04)

Claude plans, briefs, reviews and integrates; Codex writes and edits the code. Roles and loop: `~/.claude/rules/model-routing.md`. Mechanics:

1. **Everything stays in the user's current workspace and tab** (user decision 2026-10-05: no extra spaces). When the current workspace is itself a Git worktree, `herdr worktree create --workspace <id> ...` is fine. When it is not (e.g. a `~/Work` workspace), do NOT use `herdr worktree create --cwd` (it opens new workspaces): create the worktree with plain git, `git -C <repo> worktree add ~/.herdr/worktrees/<repo>/<task-slug> -b <task-slug> <base>`, then add a pane to the current workspace: `herdr pane split --pane <an existing pane in this workspace> --direction down --cwd <worktree-path> --no-focus`.
2. **One Codex agent per independent task**, in its own pane and worktree, `herdr agent start implementer-<task-slug> --kind codex --pane <pane-id> -- -a never -s workspace-write` (user decision 2026-10-05: Codex never stops to ask; anything needing escalation just fails and it works around it; commands that must run unsandboxed need an allow rule in `~/.codex/rules/default.rules` pointing at the project's own lint/test scripts when that repo ships them). Never start agents with `--dangerously-bypass-approvals-and-sandbox` or `--full-auto` (the user may, in an isolated worktree). Codex's sandbox cannot reach CoreSimulator, so tell it in the brief NOT to run simulator tests; Claude runs them. Codex here runs `glm-5.3-flash` via the ZAI provider (see `~/.codex/config.toml`), so the same data boundary as Jev applies: never point it at real slips or `.private/` folders. Independent tasks run in parallel; do not pile unrelated tasks into one agent. Keep reusing the same agent only for review rounds of the SAME task.
3. Prompt with a brief (see template) and `--wait --timeout <ms>`; a timeout is not a failure, so use `herdr agent wait` slices and never resend.
4. Review the real diff: `git -C <worktree> diff <base>...HEAD`, read the changed files, run the verification yourself. The handoff is a claim, not evidence.
5. Findings go back to the same agent (max 3 rounds unless the user sets a different goal). Then integrate (merge) and clean up: `herdr pane close <pane>`, `git -C <worktree> status --porcelain` clean, then `git -C <repo> worktree remove <worktree>` (or `herdr worktree remove --workspace <id>` if herdr created it).

Brief template (keep it short, no secrets, no personal data):
```
Task: <one sentence goal>.   Work only in this worktree; do not push, merge or touch other branches.
Context/principles: <project rules that matter, e.g. amounts come from parsers not AI; Swift 6 strict concurrency>.
Files in scope: <paths>.   Out of scope: <what not to touch>.
Acceptance criteria: <observable, testable>.
Tests: write the regression/unit test first (<where>), then the fix. Run: <lint cmd>, <unit test cmd>.
Use your own skills/subagents where relevant. When done reply with: changed files, tests run + results, remaining risks.
```
If a build/test would collide with another run (shared simulator), run only lint and unit tests; Claude runs the UI suite on the integrated tree.

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

1. Use the current Herdr workspace per Team rules — do not create a new one just to run a verification agent.
2. Split a pane in that workspace with `--no-focus` and start the requested agent kind under a task-scoped name (e.g. `reviewer-<topic>`).
3. Prompt it with the file path to review and concrete verification instructions: what to cross-check against (live `--help` output, docs URLs, actual runtime behavior), and what to report back (what checks out, what's wrong or invented, what's missing, a pass/fail verdict). Use `--wait --timeout <ms>`.
4. Read the result with `herdr agent read <name> --source recent-unwrapped --lines <n>`.
5. Fix any confirmed issues yourself (directly, not via the reviewing agent), then re-prompt the **same** agent/pane for a follow-up pass instead of starting a new one — it already has the review context loaded, and reusing it is cheaper and catches regressions from the fix itself.
6. Repeat until a clean pass, capped at 3 rounds. If round 3 still fails, stop, report the remaining failures to the user, and let them decide how to proceed. On a clean pass, close the pane per Clean up after integration below.

This differs from Coordinate an agent above in three ways: no worktree, the agent is reused across iterations rather than restarted per round, and completion is a pass/fail verdict rather than a code handoff.

## Clean up after integration

Once a handoff is accepted and integrated, reclaim the panes, agents, and worktrees this workflow created for that task — do not leave them running indefinitely. Keep the shared Herdr workspace for the project/task so other agents can continue using its remaining panes, tabs, and worktrees:

```sh
herdr pane close <pane-id>
git -C <worktree-path> status --porcelain
```

If that status is clean, remove the worktree:

```sh
herdr worktree remove <worktree-path>
```

If it's dirty, do not remove it — list the leftover changes and surface them to the lead/user instead of discarding uncommitted work.

Only close or remove panes, agents, and worktrees this workflow created for the completed task. Leave anything else untouched.
