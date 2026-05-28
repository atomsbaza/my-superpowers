# Research: Kiro CLI Headless Mode — Developer Workflow Integration

## Summary

Kiro CLI headless mode, introduced in [CLI 2.0](https://kiro.dev/blog/cli-2-0/) (released April 2026), allows the CLI to run fully non-interactively via API key authentication and the `--no-interactive` flag. It is designed for CI/CD pipelines, cron jobs, containers, and any scripted context where a human is not present at the terminal. The feature is real, officially documented, and stable enough for production use with caveats. Three constraints materially affect the adopt/skip decision: it is subscription-gated to Pro and above, a live bug in CLI 2.0 default mode may prevent MCP servers from loading at all, and native `preCommit` git hook events do not yet exist (though `kiro-cli` can be called from a standard shell `pre-commit` script).

---

## Key Findings

### 1. What Headless Mode Is and How It Differs from Interactive Mode

Headless mode activates automatically when the `KIRO_API_KEY` environment variable is set. The primary behavioral difference from interactive mode is that the CLI accepts a prompt as a command-line argument, executes it end-to-end, writes the response to stdout, and exits — there is no session loop, no interactive slash commands (`/model`, `/agent`), no mid-run user prompts, and no terminal UI. [Headless Mode — Official Docs](https://kiro.dev/docs/cli/headless/)

| Dimension | Interactive | Headless |
|-----------|-------------|----------|
| Authentication | `kiro-cli login` (browser) | `KIRO_API_KEY` env var |
| Terminal UI | Full TUI with spinners, panels | Disabled |
| User input during run | Yes | No |
| Output destination | Interactive pane | stdout |
| Slash commands | Available | Not available |

### 2. Commands and Flags

The core invocation pattern is: [CLI Commands Reference](https://kiro.dev/docs/cli/reference/cli-commands/)

```sh
KIRO_API_KEY=ksk_xxxxxxxx kiro-cli chat --no-interactive "your prompt here"
```

**Flag reference for headless use:**

| Flag | Purpose |
|------|---------|
| `--no-interactive` | Print first response to stdout and exit; this is the headless switch |
| `--trust-all-tools` | Auto-approve all tool operations; required in unattended runs if no per-tool trust configured |
| `--trust-tools=<list>` | Approve specific tool categories only (comma-separated); prefer over `--trust-all-tools` |
| `--require-mcp-startup` | Exit with code 3 if any MCP server fails to start; critical for pipelines that depend on MCP tools |
| `--agent <name>` | Invoke a named agent defined in `.kiro/agents/` |
| `--format json` | Machine-readable output for select commands (not for `chat`) |
| `--verbose` / `-v` | Increase logging verbosity; can be stacked (`-vv`, `-vvv`) |
| `NO_COLOR=1` (env var) | Suppress ANSI color codes in stdout |

Pipe context into the prompt with standard Unix pipes: [Headless Mode Intro Blog](https://kiro.dev/blog/introducing-headless-mode/)

```sh
git diff | kiro-cli chat --no-interactive "Review these changes for bugs and security issues"
```

### 3. Authentication Setup

1. Ensure your account is on Kiro Pro, Pro+, or Power (see Limitation #1 below).
2. Go to `app.kiro.dev` → API Keys → create a new key. Copy it immediately — the full value is only shown once.
3. Set `KIRO_API_KEY` as a secret in your CI/CD platform (GitHub Actions Secrets, GitLab CI Variables, etc.).
4. Never hardcode the key in pipeline YAML or commit it to source control. [Authentication — Official Docs](https://kiro.dev/docs/cli/authentication/)

Verify active credentials at any time with `kiro-cli whoami`.

**Authentication precedence:** active browser session → `KIRO_API_KEY` env var → interactive sign-in prompt.

### 4. Exit Codes for CI/CD Scripting

[Exit Codes — Official Docs](https://kiro.dev/docs/cli/reference/exit-codes/)

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General failure (auth error, invalid args, operation failed) |
| 3 | MCP server failed to start (only triggered when `--require-mcp-startup` is set) |

Without `--require-mcp-startup`, MCP failures produce warnings but exit 0 — a silent success that masks a broken tool environment.

### 5. CI/CD Pipeline Integration

The canonical GitHub Actions pattern from official documentation: [Headless Mode Intro Blog](https://kiro.dev/blog/introducing-headless-mode/)

```yaml
name: Kiro Code Review
on: [push]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Kiro CLI
        run: curl -fsSL https://kiro.dev/install.sh | sh
      - name: Run review
        env:
          KIRO_API_KEY: ${{ secrets.KIRO_API_KEY }}
        run: |
          git diff HEAD~1 | kiro-cli chat --no-interactive \
            --trust-tools=read,grep \
            --require-mcp-startup \
            "Review these changes for security issues and bugs"
```

Other documented CI/CD use cases: [Kiro CLI 2.0 Announcement](https://kiro.dev/blog/cli-2-0/)
- Documentation generation on merge to `main`
- Dependency vulnerability audits on schedule
- PR summary generation from `git diff`
- Framework migration pattern identification across a codebase

### 6. Agent Files for Reusable Headless Automation

Rather than embedding the full prompt in CI YAML, define an agent in `.kiro/agents/<name>.json`. The agent configuration supports `prompt`, `tools`, `allowedTools`, `hooks`, and `mcpServers` fields. Store these files in source control — they version with the code they operate on and can be reviewed in PRs. Invoke with: [Agent Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference/)

```sh
kiro-cli chat --no-interactive --agent code-reviewer "Review staged changes"
```

### 7. Hooks Available in CLI Mode

The CLI supports five hook event types, configured in the agent JSON. These fire during agent execution and are useful for audit logging, blocking specific tool calls, or injecting context: [CLI Hooks — Official Docs](https://kiro.dev/docs/cli/hooks/)

| Hook | When It Fires |
|------|--------------|
| `AgentSpawn` | On agent activation |
| `UserPromptSubmit` | When the initial prompt is received |
| `PreToolUse` | Before each tool call; exit code 2 blocks the tool and returns error to LLM |
| `PostToolUse` | After each tool call completes |
| `Stop` | When the agent finishes its response turn |

Hooks receive JSON context via stdin. The `PreToolUse` hook's exit-code-2 blocking mechanism is a practical control for preventing write or shell operations in read-only audit pipelines.

### 8. Pre-Commit Hook Integration

There is **no native `preCommit` event type** in Kiro's hook system as of May 2026. This has been requested (Issue #6436) with no team response or milestone. [Feature Request — GitHub](https://github.com/kirodotdev/Kiro/issues/6436)

However, `kiro-cli` is a standard executable and can be called directly from a git `pre-commit` shell hook:

```sh
# .git/hooks/pre-commit (must be chmod +x)
#!/bin/sh
git diff --cached | KIRO_API_KEY="$KIRO_API_KEY" kiro-cli chat --no-interactive \
  --trust-tools=read,grep \
  "Review these staged changes. If critical issues exist, print BLOCK: <reason> on the first line."
```

This approach works but requires the team to implement blocking logic themselves (parse the output for a sentinel string; exit 1 to block the commit). It is not a first-class integration.

---

## Trade-offs / Caveats

### High-Impact — Evaluate Before Adopting

**1. Subscription gate on API key auth.**
Headless mode requires an API key, and API key generation requires Kiro Pro, Pro+, or Power. Free-tier users cannot use headless mode. For teams, administrators must also enable the API key feature in governance settings before individual users can generate keys. This is a hard prerequisite, not a soft one. [Authentication Docs](https://kiro.dev/docs/cli/authentication/)

**2. Active CLI 2.0 bug: MCP servers may not load in default mode.**
Issue #7425 (filed against CLI 2.0.0) reports that MCP servers configured in the tool show "0 servers" in the new default TUI mode, while all servers load correctly with `--classic`. The workaround is `kiro-cli --classic`, but this is an unresolved regression. If your headless workflow depends on MCP tool integrations, this is a live reliability risk. Monitor the issue before adopting MCP-dependent headless jobs. [GitHub Issue #7425](https://github.com/kirodotdev/Kiro/issues/7425)

**3. `--require-mcp-startup` is off by default — silent failure risk.**
Without this flag, MCP server failures produce log warnings but the CLI exits 0. A CI job that depends on an MCP server (database query, external API) will silently succeed while producing incomplete or incorrect output. Always pass `--require-mcp-startup` in pipelines that use MCP tools.

**4. Output contains ANSI codes and progress noise by default.**
The CLI emits terminal formatting characters (color codes, spinner sequences, tool invocation logs). Setting `NO_COLOR=1` reduces this, but does not fully sanitize the output. If the output is being parsed, posted as a PR comment, or passed to another tool, the team needs to strip terminal escape sequences from stdout. There is no documented `--plain` or `--format plain` flag for the `chat` command specifically. [CLI 2.0 Blog](https://kiro.dev/blog/cli-2-0/)

**5. `--trust-tools` accepted values are under-documented.**
The flag accepts comma-separated tool category names (the search summary references `read`, `grep`, `write`, `shell`, `aws`), but the official permissions documentation covers only the interactive `/tools` slash commands — it does not explicitly enumerate the accepted string values for the `--trust-tools` flag in headless context. Teams should test locally before relying on this in automated pipelines. [Tool Permissions Docs](https://kiro.dev/docs/cli/chat/permissions/)

**6. No mid-session context injection.**
The initial prompt is the only opportunity to supply context. If an automated task requires branching logic or follow-up based on intermediate results, it must be encoded entirely in the initial prompt or broken into sequential CLI invocations. Complex multi-step agent tasks may not map cleanly to single-shot headless calls.

**7. No native `preCommit` hook event type.**
Kiro agent hooks do not include a git lifecycle `preCommit` trigger. A shell-based workaround (calling `kiro-cli` from `.git/hooks/pre-commit`) is functional but requires the team to build and maintain blocking logic around CLI output parsing. [GitHub Issue #6436](https://github.com/kirodotdev/Kiro/issues/6436)

### Lower-Impact — Plan For

- API keys are long-lived by default. Establish a rotation policy and revoke immediately if compromised.
- Keys are user-account scoped, not organization-scoped. Each CI service account or team member needs their own key; there is no documented shared service-account key model.
- Administrator governance rules (MCP restrictions, model access, web permissions) apply to API key usage, so team admins need to configure governance settings before unblocking headless use.

---

## Adopt/Skip Signals

**Signals to adopt:**
- Team is on Pro or above and admin has enabled API key governance.
- Use cases are clearly bounded: code review, doc generation, PR summaries, dependency audits — well-matched to single-shot prompts.
- CI platform supports secret management for `KIRO_API_KEY`.
- No dependency on MCP servers (avoids the CLI 2.0 loading bug) or team is willing to track Issue #7425 and use `--classic` workaround.

**Signals to skip or defer:**
- Team is on the free tier — headless is not available.
- Pipelines depend on MCP server tools — the CLI 2.0 loading bug is unresolved and is a reliability risk.
- Workflows require mid-run decision-making or multi-turn context — headless is single-shot only.
- The team needs native git pre-commit integration — the native hook event doesn't exist yet.

---

## Sources

- [Headless Mode — Official Docs (kiro.dev)](https://kiro.dev/docs/cli/headless/)
- [Run Kiro CLI Programmatically: Introducing Headless Mode — Kiro Blog](https://kiro.dev/blog/introducing-headless-mode/)
- [Kiro CLI 2.0: Headless CI/CD Pipelines, Windows Support — Kiro Blog](https://kiro.dev/blog/cli-2-0/)
- [CLI Commands Reference (kiro.dev)](https://kiro.dev/docs/cli/reference/cli-commands/)
- [Authentication Methods — Official Docs (kiro.dev)](https://kiro.dev/docs/cli/authentication/)
- [Exit Codes — Official Docs (kiro.dev)](https://kiro.dev/docs/cli/reference/exit-codes/)
- [Tool Permissions — Official Docs (kiro.dev)](https://kiro.dev/docs/cli/chat/permissions/)
- [CLI Hooks — Official Docs (kiro.dev)](https://kiro.dev/docs/cli/hooks/)
- [Agent Configuration Reference — Official Docs (kiro.dev)](https://kiro.dev/docs/cli/custom-agents/configuration-reference/)
- [Windows Support, Headless Mode, and Terminal UI — Kiro Changelog](https://kiro.dev/changelog/cli/2-0/)
- [GitHub Issue #7425 — MCP Servers Not Loading in CLI 2.0 Default Mode](https://github.com/kirodotdev/Kiro/issues/7425)
- [GitHub Issue #6436 — Feature Request: preCommit Git-Lifecycle Hook Event](https://github.com/kirodotdev/Kiro/issues/6436)
- [Introducing Headless Mode — Brian Beach's Publication](https://blog.brianbeach.com/publications/2026-04-13-introducing-headless-mode/)
