---
name: kirocrew-claude-backend
description: >
  Run KiroCrew with Claude Code as the ACP backend (claude-agent-acp harness)
  instead of kiro-cli — setup from source, isolated test home, model registry
  gotchas, and z.ai/GLM routing. Use when setting up, debugging, or upgrading a
  KiroCrew install that selects agent.acp_backend = claude, or when a Claude
  backend session fails at startup with a model config error.
---

# KiroCrew Claude Backend

KiroCrew (v0.6.0-dev, main ≥ 2026-09-04) ships Claude Code as a selectable ACP
harness: the gateway spawns `claude-agent-acp` instead of `kiro-cli`, and every
request flows through your local `claude` CLI — including whatever
`ANTHROPIC_BASE_URL` it is configured to use (e.g. z.ai → GLM models).

Verified working 2026-09-05 on KiroCrew `d3e67b7e9` (chat + tool use + z.ai
routing confirmed via `ANTHROPIC_LOG=debug claude -p hi`).

## Version gate (check before anything else)

The selectable set lives in `src/kiro_crew/acp_backends.py`:

```python
BASELINE_SELECTABLE_BACKENDS = frozenset({ACP_BACKEND_KIRO, ACP_BACKEND_CLAUDE, ACP_BACKEND_KAS, ACP_BACKEND_CODEX})
```

- **Includes `ACP_BACKEND_CLAUDE`** → good, config will accept `claude`.
- **Not included** (e.g. app bundle `v0.5.0-insider.9`: only kiro + KAS) →
  `kirocrew config set agent.acp_backend claude` will *appear to succeed* but the
  loader silently normalizes the stored value back to `""`. Verify with
  `kirocrew config get` + read the JSON; do not trust the CLI's ✅.
- App bundles install into
  `/Applications/KiroCrew.app/Contents/Resources/backend-dist/kirocrew-backend-arm64/lib/python3.12/site-packages/kiro_crew/`
  — read the installed file, not the GitHub main branch, when diagnosing a
  locally installed version.

## Setup from source (isolated, does not touch the installed app)

```bash
# 1. Worktree + branch from the KiroCrew clone (keep main clean)
cd ~/Work/KiroCrew && git fetch origin main
git worktree add ~/Work/kirocrew-claude-test -b test/claude-backend FETCH_HEAD

# 2. Fresh venv — NEVER borrow another worktree's venv (editable installs
#    point at that worktree's src; python -c spot-checks import stale code
#    silently while pytest passes because conftest.py re-inserts cwd/src)
cd ~/Work/kirocrew-claude-test
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -e ".[voice]" --group dev   # install line from .github/workflows/ci.yml

# 3. ACP adapter (public npm package, install once globally)
npm i -g @agentclientprotocol/claude-agent-acp

# 4. Isolated data home — required when testing; keeps real config safe
export KIROCREW_HOME=$PWD/.test-home

# 5. Config: backend AND matching model (see model registry section)
.venv/bin/kirocrew config set agent.acp_backend claude
.venv/bin/kirocrew config set agent.model opus        # canonical claude key

# 6. Frontend build + stage (gateway serves "Dashboard HTML not found" without it)
cd website && npm install && npm run build && cp -r dist ../src/kiro_crew/static/dist && cd ..

# 7. Run gateway on a side port; `kirocrew token` prints the authed URL
KIROCREW_HOME=$PWD/.test-home .venv/bin/kirocrew gateway --port 5580
```

Verify: `curl http://127.0.0.1:5580/api/health` → `{"ok": true, ...}`, then
`.venv/bin/kirocrew chat -m "Reply with exactly: CLAUDE-BACKEND-OK"`.

## Model registry gotcha (the #1 startup failure)

Claude backend model ids are **canonical keys from
`src/kiro_crew/model_registry.json`** (`opus`, `sonnet`, `fable`, …) — NOT
kiro-cli ids. If `agent.model` holds a kiro id (e.g. `gpt-5.6-luna`), every
session dies at init:

```
AcpError: JSON-RPC error: {'code': -32603, ...
  'details': 'Invalid value for config option model: gpt-5.6-luna'}
```

Fix: `kirocrew config set agent.model opus` (or `sonnet` / `fable`).
When switching `acp_backend`, always switch `agent.model` in the same step.
Canonical → claude adapter ids are mapped via the `providers.claude_code` entry
(e.g. `opus-4.8-1m` → `global.anthropic.claude-opus-4-8[1m]`).

## GLM / z.ai routing

The claude CLI reads `~/.claude/settings.json` → `env.ANTHROPIC_BASE_URL`. If it
points at `https://api.z.ai/api/anthropic`, every KiroCrew Claude-backend session
runs GLM on the z.ai account — no KiroCrew config needed.

Verify routing (never trust the ACP stderr line `baseUrl=native` — that is the
ACP apiType, not the HTTP endpoint):

```bash
ANTHROPIC_LOG=debug claude -p "hi" 2>&1 | grep -m2 "url:"
```

## Known limitations (from upstream docs/system-specs/features/claude-code-provider.md)

- Claude sessions start with **no Crew MCP tools** (`_claude_session_mcp_servers` defaults to `[]`).
- Tools pre-approved in Claude's own settings (including a `.claude/settings.json`
  inside a project) **never reach Crew's approval path** — deny rules, sensitive-path
  checks, and the SEL audit log do not see those calls.
- Reasoning effort for the session goes through the claude CLI's own mechanism,
  not kiro's `/effort` (which kiro-cli rejects on glm models anyway).
- Governance `agent_backend` scope can narrow the selectable set (floor: kiro-cli).

## Operational notes

- `KIROCREW_HOME` + `KIROCREW_PORT` fully isolate a test gateway from the
  installed app — they can run side by side.
- Stop: `KIROCREW_HOME=... .venv/bin/kirocrew stop`, or kill the process.
- `kirocrew token` output may be redacted by output filters — write it to a file
  (e.g. `.test-home/dashboard-url.txt`) and `open` it instead of pasting into chat.
- macOS has no `timeout` command; rely on tool timeouts.
- Upstream release cadence is fast (insider.5 → .9 in 3 days as of 2026-09);
  when a release after insider.9 ships, the installed app can select claude
  without the source setup — this worktree path is then only for dev testing.
