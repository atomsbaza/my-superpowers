# Chapter 2: Core CLI Command Hierarchy & Primitives

The system relies on three core primitives. A **pane exists independently** of whether an agent is active; `agent start` simply recognizes and labels a process within an existing shell pane.

## The Three Primitives

| Primitive | Responsibility |
| :--- | :--- |
| **Layout** | Managing the topology of Workspaces, Tabs, and Panes. |
| **Pane** | Controlling raw terminal processes: input, output, and command execution. |
| **Agent** | Managing recognized coding assistants by name, lifecycle state, and metadata. |

## Subcommand Reference

- **Session:** Persistent headless environments. Use `herdr session list` and `herdr session attach`.
- **Workspace:** The top-level project context. `herdr workspace create --label api --no-focus`.
- **Tab:** Sub-layouts. `herdr tab create --workspace <workspace_id> --label debugging`.
- **Pane:** The execution unit. Use `pane split`, `pane run`, and `pane read`.
- **Agent:** The assistant controller. `agent start`, `agent prompt`, and `agent wait`.
- **Worktree:** Git-integrated checkouts. `worktree create` prevents index contention during parallel agent runs.

## JSON and ID Handling

Herdr creation commands return a tripartite JSON structure. For automation, avoid predicting IDs and instead capture the full result:

```bash
# Capture the tripartite response: .result.workspace, .result.tab, and .result.root_pane
created=$(herdr workspace create --cwd ~/project)
pane_id=$(printf '%s\n' "$created" | jq -r '.result.root_pane.pane_id')
```

---

Previous: [Chapter 1 — Architecture & Installation](chapter01-architecture-and-install.md) · Next: [Chapter 3 — Multi-Agent Workflow](chapter03-multi-agent-workflow.md)
