# Spike: Can a Stop hook drive an engineering iteration loop in Claude Code?

**Date:** 2026-06-21
**Timebox:** 2 hours (actual: ~30 min)
**Status:** 🟢 Complete
**Project:** my-superpowers (building a custom "loop" skill)

## Question

> Can a `Stop` hook drive an engineering iteration loop in Claude Code — does returning a `block` decision force another turn, how does the injected context re-enter Claude's reasoning, and can I track iteration count in a state file across turns?

## Why this matters

This is the single unknown standing between the loop research report
([`docs/research/claude-code/2026-06-21-agentic-engineering-loop.md`](../research/claude-code/2026-06-21-agentic-engineering-loop.md))
and a working prototype. The research said the Stop hook is "the loop engine" but stayed
conceptual. If a `block` decision does **not** reliably force another turn, or if there's no
safe way to count iterations, the whole skill design has to change. Answering it empirically
de-risks the build.

## Investigation

### What was tried

1. **Built an isolated headless harness** in a temp dir (`/tmp/loop-spike.*`) so the test
   could not corrupt the live session: a `Stop` hook shell script + a `settings.json` wiring it,
   run under `claude -p ... --settings <file> --output-format json`.

2. **Hook logic:** read iteration count from `.claude/loop-state.json` (default 0), increment,
   write back. While `count < MAX(3)`, return `{"decision":"block","reason":"...instructions..."}`
   to force another turn. At `count == MAX`, return `{"decision":"approve"}` to allow stop.
   Every raw stdin payload was appended to `hook-input.log` to capture the real input schema.

3. **Ran it** with a trivial pure-text prompt ("Say 'hello' and nothing else.") — no tools, so
   no permission bypass needed. Observed `num_turns`, the final result text, the state file, and
   the logged hook inputs.

### Findings

**1. A `block` decision reliably forces another turn.** `num_turns: 3` and the hook fired
exactly 3 times. The loop ran until the hook stopped blocking.

**2. The `reason` field re-injects as instructions Claude follows.** The hook's `reason` told
Claude to output "iteration N complete". The final result was `"iteration 2 complete"` — Claude
acted on text that came *only* from the hook, never from the user. Re-injection works via the
`reason` field of a Stop-block decision (no separate `additionalContext` field was needed for
the basic case).

**3. State-file iteration tracking works and is owned by the hook, not the agent.**
`loop-state.json` advanced 0 → 3 across turns. The agent never saw or touched it; the hook
process is the sole writer. This is exactly the "keep loop control outside agent-editable files"
pattern the research recommended.

**4. `stop_hook_active` is the built-in infinite-loop guard.** It was `false` on the first
Stop event and `true` on every subsequent one (i.e., once a hook has already blocked a stop).
A well-behaved hook should check this to avoid runaway loops — it's a platform-provided safety
rail that complements (or replaces) a custom counter.

**5. The Stop hook input schema (claude 2.1.178):**
```
keys: background_tasks, cwd, effort, hook_event_name, last_assistant_message,
      permission_mode, session_crons, session_id, stop_hook_active, transcript_path
```
Notably useful for a verification loop: `last_assistant_message` (inspect what Claude just
said), `transcript_path` (full history on disk), `cwd`, and `session_id`.

### Evidence

Final run result (trimmed):
```json
{"type":"result","subtype":"success","num_turns":3,
 "result":"iteration 2 complete","stop_reason":"end_turn", ...}
```

Turn-by-turn trace (reconstructed):
| Turn | Claude says | Hook count | Decision |
|---|---|---|---|
| 1 | "hello" | 1 < 3 | block → "say iteration 1 complete" |
| 2 | "iteration 1 complete" | 2 < 3 | block → "say iteration 2 complete" |
| 3 | "iteration 2 complete" | 3 == MAX | approve → loop ends |

Final `loop-state.json`: `{"iteration": 3}`. Hook fired 3 times (`hook-input.log` = 3 lines).
`stop_hook_active`: `false, true, true`.

Working hook core:
```bash
STATE="$CLAUDE_PROJECT_DIR/.claude/loop-state.json"
input=$(cat)
count=$(grep -o '"iteration"[: ]*[0-9]*' "$STATE" 2>/dev/null | grep -o '[0-9]*'); count=$((count+1))
echo "{\"iteration\": $count}" > "$STATE"
if [ "$count" -lt "$MAX" ]; then
  echo "{\"decision\":\"block\",\"reason\":\"...instructions for next turn...\"}"
else
  echo "{\"decision\":\"approve\"}"
fi
exit 0
```
Settings wiring:
```json
{ "hooks": { "Stop": [ { "hooks": [
  { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR/.claude/stop-loop.sh\"" }
] } ] } }
```

## Recommendation

**Decision: GO**

**Rationale:** All three sub-questions resolved affirmatively with direct evidence. The Stop
hook is a viable, reliable loop engine: `block` forces iteration, `reason` carries instructions
back into Claude's context, and a hook-owned state file gives safe cross-turn iteration tracking.
The platform even provides `stop_hook_active` as a free infinite-loop guard.

**If GO — implementation notes:**
- **Use `stop_hook_active` as the primary safety rail**, not just a custom counter. If
  `stop_hook_active == true` AND your verification has passed (or your cap is hit), approve the
  stop. This prevents runaway loops even if the state file is missing/corrupt.
- **The hook owns loop control.** Keep the state file off-limits to the agent (don't expose it as
  an editable target). Iteration count, last error, last verdict all live here.
- **Drive continuation through `reason`.** It re-injects as the next turn's instructions — use it
  to feed verification failures back ("tests still failing: <output>, fix and continue").
- **For real verification**, the hook should run the test/lint command itself (ground truth) and
  only block when it fails — never trust `last_assistant_message` self-report alone (the
  maker-checker principle from the research).
- **Settings live in `.claude/settings.json`**; `$CLAUDE_PROJECT_DIR` resolves correctly inside
  the `command` string. Quote it for paths with spaces.
- A pure skill (SKILL.md only) **cannot** set this up by itself — the loop needs the Stop hook in
  settings. The skill should either ship a hook + settings snippet or instruct the user to install
  one. (Matches the research caveat that `maxTurns` is an SDK/CLI concern, not a SKILL.md field.)

## Open questions (out of scope, worth tracking)

- Does `hookSpecificOutput.additionalContext` differ from `reason` in how/where it injects?
  `reason` was sufficient here; the newer field may format differently.
- Interaction with the documented "puttering" bug (#52362) — does a verification-gated Stop hook
  actually catch a false-termination, or does puttering happen *before* the Stop event fires?
- Behavior under context compaction during a long loop: does the `reason` re-injection survive a
  `PreCompact` event mid-loop?
- How does this compose with subagents (maker-checker) — can the Stop hook be `type: "agent"` to
  run an independent checker without consuming main context?

## Time spent

~30 min of a 2-hour timebox. Answer was clear well within budget.
