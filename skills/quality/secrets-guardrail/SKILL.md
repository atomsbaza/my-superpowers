---
name: secrets-guardrail
description: >
  PostToolUse hook that redacts credential patterns from all tool output before Claude
  sees it — API keys, tokens, passwords, connection strings. Zero-config security layer,
  drops in alongside existing hooks. Invoke /secrets-guardrail setup to wire it into
  a project's settings. No skill invocation needed after setup — it runs automatically.
allowed-tools: Bash, Read
disable-model-invocation: true
---

# Secrets Guardrail

A PostToolUse hook that intercepts every tool output and redacts recognized credential
patterns before they enter Claude's context window. Prevents secrets from being logged,
summarised, or inadvertently included in generated code.

## What it redacts

| Pattern | Example | Replacement |
|---|---|---|
| Anthropic API keys | `sk-ant-api03-...` | `[REDACTED:anthropic-key]` |
| OpenAI API keys | `sk-proj-...` / `sk-...T3Bl` | `[REDACTED:openai-key]` |
| GitHub tokens | `ghp_...` / `ghs_...` / `github_pat_...` | `[REDACTED:github-token]` |
| AWS access keys | `AKIA...` | `[REDACTED:aws-key]` |
| Bearer tokens | `Bearer eyJ...` | `Bearer [REDACTED:token]` |
| JWT tokens | `eyJ[a-zA-Z0-9]...` | `[REDACTED:jwt]` |
| Connection strings | `mongodb+srv://:...@` | `[REDACTED:connection-string]` |
| `.env` assignments | `SECRET_KEY=abc123` | `SECRET_KEY=[REDACTED]` |
| Generic long secrets | 40+ char hex/base64 in key=value context | `[REDACTED:secret]` |

## What it does NOT redact

- File contents of `.env` files (you chose to read them — the hook truncates the log)
- Secrets already in the codebase (use a secrets scanner for that)
- Short values that might be secrets (too many false positives)

## Setup

When the user invokes `/secrets-guardrail setup`:

1. Show the hook config to add to `.claude/settings.json`
2. Note that PostToolUse hooks cannot block (tool already ran) — the hook replaces
   the output Claude sees via `updatedToolOutput`

Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/secrets-guardrail/hooks/redact.sh"
          }
        ]
      }
    ]
  }
}
```

Or copy `~/.claude/skills/secrets-guardrail/settings-snippet.json` and merge it in.

## Subcommands

- `/secrets-guardrail setup` — show setup instructions
- `/secrets-guardrail test` — run the redact script on sample input to verify it works
