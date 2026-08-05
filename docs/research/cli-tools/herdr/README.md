# Herdr: a terminal multiplexer for AI coding agents — Research

**Site:** https://herdr.dev/
**Repo:** https://github.com/herdrdev/herdr

**Provenance:** NotebookLM deep research (68 sources: official herdr.dev docs, GitHub issues/discussions, third-party blog posts), collected 2026-08-06, then verified against the installed `herdr 0.8.0` CLI and live docs by Codex across two review rounds (via a Herdr pane, per the `herdr-workflow` skill). The first NotebookLM draft contained several errors — stale install commands, an invented config key, a fabricated keyboard-mode model, a wrong agent support matrix, unverifiable "known issues" — all caught and corrected before this version. See [Appendix: Verification Notes](appendix-verification-notes.md) for the full list of what was cut/fixed and why.

---

## Executive Summary

Coordinating multiple AI coding agents (Claude Code, Codex, Cursor, etc.) across terminal panes and git worktrees today means manual tab-juggling with no persistence across disconnects/restarts and no programmatic way for agents to drive each other. Herdr is a Rust client/server terminal runtime purpose-built for this: it keeps agent sessions alive, tracks per-agent status (working/blocked/idle), and exposes a CLI plus a local socket API so agents can split panes, spin up other agents, and coordinate without blind keystroke automation.

The server survives client disconnects and SSH drops — long-running tasks keep going while you're detached — but a full server/machine restart is a different case: layout and cwd are restored, and supported agents' native conversations can resume if their integration is installed, but ordinary running processes are not preserved across a restart. Agent status comes from two signals: lifecycle hooks (installed per-agent, authoritative) or screen-manifest parsing (fallback, used by Codex and Claude Code today). Everything below reflects `herdr 0.8.0`; treat any specific version number, exact matrix entry, or bug claim as something to re-check against `herdr.dev/docs/` before depending on it in a script.

---

## Table of Contents

### Chapters

1. [Architecture & Installation](chapter01-architecture-and-install.md) — client/server model, persistence semantics, install commands per platform, shell completions.
2. [Core CLI Command Hierarchy](chapter02-cli-command-hierarchy.md) — the three primitives (layout/pane/agent), subcommand reference, JSON/ID handling for automation.
3. [Multi-Agent Workflow](chapter03-multi-agent-workflow.md) — the standard orchestration sequence: worktree isolation, pane split, agent start/prompt/wait, alternate-screen history retrieval.
4. [Agent Integrations & Support Matrix](chapter04-agent-integrations.md) — lifecycle hooks vs. screen manifests, agent identity rules, `herdr integration install/status`.
5. [Configuration & UI](chapter05-configuration.md) — `config.toml` location, validation, environment variables, apply semantics, discovering UI keys via `--default-config`.
6. [Operational Constraints & Known Issues](chapter06-operational-constraints.md) — foreground-pane requirement, destructive worktree removal, config apply timing, where to check live bug status.
7. [Keyboard Shortcuts](chapter07-keyboard-shortcuts.md) — prefix mode vs. copy mode defaults, and the mouse-driven alternative.

### Appendix

- [Verification Notes](appendix-verification-notes.md) — what the first NotebookLM draft got wrong, how Codex caught it, and the one over-correction that got caught on a second pass.

---

## How to use this

Read chapter 3 first if you just want the day-to-day orchestration recipe. Read chapters 1–2 first if you're installing and scripting against the CLI for the first time. Chapter 4 and the appendix matter most if you're deciding whether to trust a specific agent-support or bug claim — the short version is: don't hardcode the agent matrix or any "known issue" from a static doc, always re-check `herdr.dev/docs/` or `herdr --default-config`/`herdr --help` directly, since both evolve quickly and a stale copy is exactly what caused the first-draft errors here.
