---
name: verify-before-stop
description: >
  Always-on regression guard: runs tests on git-changed files before any session ends.
  Blocks the session stop if tests fail, preventing silent regressions from slipping
  through. Not a loop — fires once per session end. Requires its Stop hook wired in
  .claude/settings.json. Activate with /verify-before-stop setup.
allowed-tools: Bash, Read
disable-model-invocation: true
---

# Verify Before Stop

This skill is a background safety net, not an active workflow. Its Stop hook
automatically runs every time a Claude Code session ends and there are git-changed files.

## What it does

On every session stop:
1. Check `git diff --name-only HEAD` — any changed files?
2. If no changes → approve stop (nothing to verify)
3. If changes exist → run the configured verify command
4. Pass → approve stop
5. Fail → block stop, show failure output, Claude fixes before exiting

## Setup

When the user invokes `/verify-before-stop setup`:

1. Detect the project's test command (or ask):
   - `package.json` with test script → `npm test`
   - `pyproject.toml` or `setup.py` → `pytest`
   - `*.xcodeproj` → `xcodebuild test` (ask for scheme)
   - `go.mod` → `go test ./...`
   - `Makefile` with `test` target → `make test`

2. Write `.claude/verify-on-stop.json`:
   ```json
   {"verify_cmd": "npm test", "enabled": true}
   ```

3. Confirm: "Verify-before-stop is active. On every session end with uncommitted
   changes, I'll run `npm test` before stopping."

## Subcommands

- `/verify-before-stop setup` — detect test command and write config
- `/verify-before-stop disable` — set `enabled: false` in config
- `/verify-before-stop enable` — set `enabled: true` in config
- `/verify-before-stop status` — show current config

## When stop is blocked

The hook injects failure output into the session. Claude should:
1. Read the failure output
2. Fix the regression (it was introduced by this session's changes)
3. The hook will re-run on the next stop attempt

## Setup instructions (for humans)

Add to `.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/verify-before-stop/hooks/verify-changed.sh"
          }
        ]
      }
    ]
  }
}
```

**Note:** If you also use the loop skill, both Stop hooks coexist safely. The loop skill
writes `.claude/loop-state.json` to activate its hook; verify-before-stop reads
`.claude/verify-on-stop.json`. They are independent.

Or copy `~/.claude/skills/verify-before-stop/settings-snippet.json` and merge it in.
