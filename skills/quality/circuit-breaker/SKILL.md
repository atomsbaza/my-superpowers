---
name: circuit-breaker
description: >
  Enhanced loop Stop hook that detects when the agent is stuck (same error repeating)
  and escalates to a human checkpoint instead of burning more iterations. Drop-in
  replacement for the loop skill's verify.sh in .claude/settings.json. Use when you
  want the loop skill's verification plus automatic stuck-detection. Invoke
  /circuit-breaker setup to configure.
allowed-tools: Bash, Read
disable-model-invocation: true
---

# Circuit Breaker

The circuit breaker is a Stop hook that wraps the loop skill's verification with
stuck-detection. It fires on every session stop and does two things:

1. **Verification** — runs the configured verify command (same as loop skill)
2. **Stuck detection** — if the same error recurs N times consecutively, it escalates
   to a human checkpoint instead of burning another iteration on a problem that isn't
   converging

## When to use instead of loop's verify.sh

Use the circuit breaker when:
- Tasks are complex and may get stuck in error loops
- You want automatic escalation instead of hitting the max-iterations cap
- You're running long loops where cost matters

Use loop's plain verify.sh when:
- Tasks are simple and well-scoped
- You prefer a hard cap with a summary over a human checkpoint

## Setup

When the user invokes `/circuit-breaker setup`:

1. Check if `.claude/loop-state.json` exists (loop skill must be set up first).
2. Ask for `max_consecutive_failures` (default: 3).
3. Update `.claude/loop-state.json` to add the field:
   ```json
   {"iteration": 0, "max": 10, "verify_cmd": "npm test",
    "max_consecutive_failures": 3, "consecutive_failures": 0, "last_error_hash": ""}
   ```
4. Tell the user to replace `loop/hooks/verify.sh` with `circuit-breaker/hooks/circuit-breaker.sh`
   in their `.claude/settings.json` (or merge `settings-snippet.json`).

## How it works

Each Stop event:
```
run verify_cmd
  → PASS: reset consecutive_failures=0, approve stop
  → FAIL:
      hash the error output
      if hash == last_error_hash: consecutive_failures++
      else: consecutive_failures=1, last_error_hash=new_hash
      if consecutive_failures >= max_consecutive_failures:
        approve stop with CIRCUIT_BREAK escalation message
      else:
        block with LOOP_VERIFY_FAIL (normal loop continuation)
```

## Subcommands

- `/circuit-breaker setup` — configure and wire
- `/circuit-breaker status` — show current state (iterations, consecutive failures, last error)
- `/circuit-breaker reset` — clear consecutive_failures and last_error_hash

## Setup instructions (for humans)

Replace the loop hook in `.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/circuit-breaker/hooks/circuit-breaker.sh"
          }
        ]
      }
    ]
  }
}
```
