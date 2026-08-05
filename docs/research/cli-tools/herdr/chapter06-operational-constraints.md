# Chapter 6: Operational Constraints & Known Issues

## Operational Notes

- **`agent start` requires a live shell pane in the foreground.** It cannot start over an editor, a running command, or an already-running agent. An agent launched manually (not via `herdr agent start`) is unnamed and must be addressed by pane ID instead of an agent name.
- **Worktree removal is destructive.** `herdr worktree remove --workspace <id> [--force]` actually runs `git worktree remove` on disk. Closing a workspace in Herdr only closes Herdr's own state and does *not* remove the worktree — don't confuse the two.
- **Config changes have mixed apply semantics.** Some settings pick up on `herdr server reload-config`; others (e.g. `HERDR_PROCESS_DETECTION`) require a full server restart.
- **Known bugs get filed as GitHub issues/discussions** (e.g. restore/addressing edge cases after a server restart, `pane.read` truncation flag accuracy). Check `github.com/herdrdev/herdr/issues` for the current, version-scoped state before assuming a specific bug is present.

## Diagnostic Tools

Use `herdr agent explain <target>` to debug manifest matching. It provides:

- Manifest source/version and local override shadowing.
- Matched rules and region evidence.
- Specific "idle fallback" reasons if no manifest rules triggered.

---

Previous: [Chapter 5 — Configuration & UI](chapter05-configuration.md) · Next: [Chapter 7 — Keyboard Shortcuts](chapter07-keyboard-shortcuts.md)
