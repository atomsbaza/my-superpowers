---
name: tdd-loop
description: >
  Test-Driven Development with automated loop verification: write a failing test first,
  verify it actually fails, then use the loop skill's Stop hook to iterate implementation
  until the test passes. Use when the user says "TDD with loop", "test-first with auto-verify",
  or "red-green using loop". Requires the loop skill's Stop hook wired in .claude/settings.json.
allowed-tools: Read, Edit, Write, Bash, Glob, Grep
disable-model-invocation: false
---

# Test-Driven Development

TDD runs in three phases. The loop skill's Stop hook is the verification engine —
you write the test, then the hook iterates your implementation until the test passes.

## Phase 1 — RED: write the failing test

1. Understand the requirement. Ask the user if anything is ambiguous.
2. Write the test file (or add to an existing one):
   - Name the test after the behaviour: `test_returns_empty_list_when_no_items`
   - Test one behaviour per test case
   - Do not write any implementation yet
3. Run the test to confirm it **fails**:
   ```bash
   <test_command> <test_file_or_filter>
   ```
   **If the test passes without implementation, stop.** The test is wrong — it doesn't
   test real behaviour. Fix it until it fails for the right reason (missing implementation,
   not import errors or syntax).
4. Show the user the failure output and confirm it fails for the right reason.

## Phase 2 — Set up the loop

Once the test fails correctly, initialise the loop state file:
```json
{
  "iteration": 0,
  "max": 10,
  "verify_cmd": "<test_command> <test_file_or_filter>",
  "task": "implement <feature> until test passes"
}
```
Write this to `.claude/loop-state.json`.

**Why a scoped verify_cmd matters:** target just the new test(s), not the full suite.
The loop runs faster and failure output is easier to read.

Example verify commands:
- `pytest tests/test_auth.py::test_login_returns_token -x`
- `npm test -- --testPathPattern=auth --testNamePattern="returns token"`
- `swift test --filter AuthTests/testLoginReturnsToken`
- `go test ./auth/... -run TestLoginReturnsToken`

## Phase 3 — GREEN: implement until passing

Begin the minimal implementation that could make the test pass.

- Minimal means minimal: no premature abstraction, no extra features.
- The loop hook will run `verify_cmd` after each turn and inject failures back.
- When the test passes, the hook approves the stop automatically.

## Phase 4 — REFACTOR (after GREEN)

Once the loop ends with `LOOP_APPROVED`:
1. Review the implementation for clarity, duplication, naming.
2. Refactor freely — the test is your safety net.
3. If you break the test, re-enter the loop with `/loop`.

## Rules

- Never write implementation before the test exists and fails.
- Never modify the test to make it pass (unless the test was genuinely wrong).
- Never edit `.claude/loop-state.json` — the loop hook owns it.
- Minimal implementation only in GREEN phase; refactor is its own step.

## Interaction with the loop skill

TDD uses the loop skill's Stop hook for verification. The hook must be wired:
```json
{ "hooks": { "Stop": [ { "hooks": [
  { "type": "command", "command": "~/.claude/skills/loop/hooks/verify.sh" }
] } ] } }
```
See `~/.claude/skills/loop/settings-snippet.json`.
