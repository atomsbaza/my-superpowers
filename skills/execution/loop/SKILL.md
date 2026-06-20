---
name: loop
description: >
  Engineering loop: autonomously implement → verify (via Stop hook checker) → repeat until
  tests pass or iteration cap is hit. Use when the user says "loop until tests pass",
  "keep going until it works", "fix failing tests autonomously", or asks for iteration on a
  task with a verifiable exit condition. Requires the Stop hook from settings-snippet.json
  wired in the project's .claude/settings.json.
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent
disable-model-invocation: false
---

# Engineering Loop

You are running in an **engineering loop**. A Stop hook (the "checker") verifies your work
after each turn and forces another iteration if verification fails. Your job is to implement;
the hook's job is to verify. Do not self-report success — the hook decides when the loop ends.

## Setup (first invocation)

Ask the user for:
1. **Task** — what to implement or fix
2. **Verify command** — the command that determines success (e.g. `npm test`, `pytest`,
   `swift test`, `make test`). If unsure, detect from the project (package.json → `npm test`,
   pyproject.toml → `pytest`, etc.).
3. **Max iterations** — default 10. Raise for complex tasks; lower for quick fixes.

Then write `.claude/loop-state.json` before making any code changes:
```json
{"iteration": 0, "max": 10, "verify_cmd": "npm test", "task": "fix auth module tests"}
```

**Do not start implementing until this file is written.**

## Each turn: implement

- Make one focused, concrete change toward the goal.
- Use `Bash` to explore before editing: read error output, check types, trace the failure.
- Do NOT run the verify command yourself and report whether it passed.
  The hook runs it independently — your self-report is not used.
- Do NOT say "all tests pass" or "done" — the hook will approve the stop when it's satisfied.

## Reading hook feedback

After each turn, the hook injects one of these into your next context:

**`LOOP_VERIFY_FAIL` (iteration N/MAX)**
> Test output: `<actual output>`
> Fix the above and continue.

→ The checker ran the real command and it failed. Read the output carefully.
  Make the targeted fix. If the same error recurs twice, try a different approach.

**`LOOP_CAP_REACHED`**

→ You hit the max iteration cap. Write a brief summary: what was fixed, what still fails,
  and what the next human step should be.

**`LOOP_APPROVED`**

→ Verification passed. The loop is ending naturally. Write a one-paragraph completion summary.

## Rules

- **Never edit `.claude/loop-state.json`** — the hook owns it.
- **Never skip verification** by claiming success — the hook is the source of truth.
- **One change per turn** — focused edits are easier for the checker to verify.
- **If stuck (same error 2+ turns)** — try a fundamentally different approach, not just
  a tweak.

## How the maker-checker works

```
You (maker)          Stop Hook (checker)
─────────────        ──────────────────────────────────────
implement change  →  hook fires when you finish
                     checker runs: $verify_cmd
                     if FAIL → block + inject failure output into your next turn
                     if PASS → approve → loop ends naturally
```

The checker is independent: it runs the real command and reports exit code + output.
It cannot be fooled by your self-assessment.

## Setup instructions (for humans)

The loop skill requires a Stop hook. Add this to your project's
`.claude/settings.json` (or `.claude/settings.local.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/loop/hooks/verify.sh"
          }
        ]
      }
    ]
  }
}
```

Or copy `~/.claude/skills/loop/settings-snippet.json` and merge it into your project settings.
