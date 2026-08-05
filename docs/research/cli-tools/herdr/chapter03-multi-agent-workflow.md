# Chapter 3: Workflow — Coordinating Parallel Coding Agents

The primary workflow involves isolating tasks to prevent "blast radius" issues and race conditions.

## Standard Orchestration Sequence

1. **Isolation:** Create a Git Worktree to host the agent. This provides a clean directory and branch.
2. **Topology:** Split the current pane and capture the new ID.
   - `herdr pane split --current --direction right`
3. **Initialization:** Start an agent kind (e.g., `codex`).
   - `herdr agent start assistant-1 --kind codex --pane <pane_id>`
4. **Tasking:** For a recognized agent, use `herdr agent prompt` to send the task (it handles submission atomically, no separate keystroke race):
   - `herdr agent prompt assistant-1 "Optimize database queries" --wait --timeout 120000`

   For an ordinary shell command in a pane (not a named agent), use `herdr pane run` instead — same atomic-submission guarantee, but targeting the raw pane rather than a recognized agent.
5. **Observation:** Monitor for `blocked` states (UI prompts/permissions).
   - `herdr agent wait assistant-1 --until blocked`

## Data Retrieval and Alternate-Screen History

When collecting results via `herdr agent read`, use `--source recent-unwrapped` to preserve formatting.

Herdr automates alternate-screen history retrieval for full-screen agents: when a `--lines` request exceeds what's on the visible screen, `pane read`/`agent read` scroll the alternate-screen buffer to collect additional transcript (subject to the agent being idle/at the bottom of its transcript), then restore the viewport afterward. See the agent-automation docs (`herdr.dev/docs/agent-automation/`) for the exact preconditions before relying on this in a script.

---

Previous: [Chapter 2 — Core CLI Command Hierarchy](chapter02-cli-command-hierarchy.md) · Next: [Chapter 4 — Agent Integrations & Support Matrix](chapter04-agent-integrations.md)
