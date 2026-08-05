# Chapter 4: Agent Integrations & Support Matrix

## Integration Mechanics

Herdr classifies agent states via two authoritative signals:

- **Lifecycle Authority Hooks:** Agents with an installed Herdr integration (`herdr integration install <agent>`) report status directly via local socket API, taking priority over screen parsing. Without the integration installed, even a "hook-capable" agent falls back to screen detection.
- **Screen Manifest Parsing:** For agents without lifecycle hooks active, Herdr parses the foreground process name and the bottom-buffer snapshot, and also evaluates terminal title (OSC 0/2) and progress sequences as detection evidence.

## Agent Support Matrix

19 agent CLIs are detected out of the box; support quality varies — some get lifecycle hooks (when their integration is installed), most rely on screen-based status detection only. Codex and Claude Code currently use screen-based detection. Gemini CLI and Cline are detected but less thoroughly tested. Check `herdr.dev/docs/agents/` for the current authoritative matrix and exact `agent start --kind` values (e.g. `codex`, `claude`, `agy`, and others) before scripting against it — this matrix goes stale quickly, don't hardcode it.

Run `herdr agent explain <target>` on a live agent to see which signal (hook vs. manifest) Herdr is actually using for it.

## Agent Identity

Agent names must be unique and follow the regex constraint: `[a-z][a-z0-9_-]{0,31}`. Attach to any agent with `herdr agent attach <target>` and detach using `ctrl+b q`.

## Integration Management

- `herdr integration install <agent>` — installs the lifecycle-hook integration for a supported agent (note: for Claude, this rewrites `~/.claude/settings.json` to add a hook — review the diff, don't blindly run it on a config you care about).
- `herdr integration status` — shows which agents have integrations installed and whether hooks or screen detection are currently authoritative for each.

---

Previous: [Chapter 3 — Multi-Agent Workflow](chapter03-multi-agent-workflow.md) · Next: [Chapter 5 — Configuration & UI](chapter05-configuration.md)
