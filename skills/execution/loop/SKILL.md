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
- **Resumable runs execute from compiled state, not raw transcript (2026-09-10).**
  Persist progress as a compacted state file (current goal, done/failed items,
  next action) and resume from it — never by replaying the raw event log. A run
  that fails at hour 6 should stream-log every step server-side so it can
  resume from logs instead of restarting the whole task.
- **Contract-based completion.** Frame each turn's question as "which action
  leads to an outcome the contract accepts," not "what do I do next" — and
  keep tools that *propose* work separate from tools that *execute* it, so
  proposals are gated before execution.
- **Classify failure before rerunning (2026-09-12).** When the agent forgets
  constraints, picks the wrong tool, or loops until budget death, the
  environment was underspecified — it is not "the model being dumb". The
  fix sequence: classify the failure (missing contract? missing capability?
  weak evidence gate?), fix that gap in the harness, then rerun the *exact*
  failing case. Never "same prompt, but louder" — a louder rerun reproduces
  the same failure at higher cost. Harness layers to check in order: task
  contract, context compilation, permissioned tool gateway, durable state,
  evidence gates, trace + recovery.
- **Same agent + same context re-checking itself is a confidence loop, not
  verification (2026-09-10).** Verification must come from a different vantage:
  the checker hook, a fresh context, or an on-disk check — not the same session
  re-reading its own output. Related: cross-model review beats same-model
  review (see AGENTS.md orchestrator conventions).
- **Budget long workflows as r^H — and do NOT compensate by compressing
  context (2026-09-15, arXiv:2609.01660).** Across 9 models and 10,664
  trajectories, long-horizon task success follows a geometric law in the
  number of dependent steps, collapsing from ~100% to near 0% within ~16
  steps — and *shortening the context window makes rot faster* (logit slope
  −0.69 vs −0.44), refuting "lost-in-the-middle" as a justification for
  aggressive compression. The fix is fewer dependent steps: split the task
  with checkpoint/resume, keep the steps you keep well-fed.
- **Fork vs isolated subagent context (2026-09-15, LangChain Deep Agents).**
  `fork` passes the supervisor's whole state to the subagent — use when the
  work continues an existing task (implementing an already-diagnosed fix;
  no re-reading files). `isolated` starts empty — use for verifiers and
  reviewers, because inheriting the supervisor's reasoning makes the review
  non-independent. Decide per role: does it need *history* or *neutrality*?
  (This is the context-level reason cross-model review works.)
- **Context trimming has a floor — keep protocol-critical state first
  (2026-09-17, arXiv:2609.16461).** Comparing five trimming strategies:
  naive recency/summarization saves ~60% of tokens but drops task success
  to 67–77%, while protocol-aware trimming with adaptive budgets holds 96%
  at 56% savings; a retained-context budget ≤25% raises failure odds ~11×
  vs ≥50% (paper numbers, unverified). When compacting or checkpointing,
  persist protocol-critical state (tool state, unresolved dependencies,
  current plan) before trimming anything, and never cut retained context
  below ~50%. Complements the r^H rule above: fewer dependent steps first,
  then trim above the floor.
- **A clean trace is not ground truth (2026-09-17, "Corrupt Plans, Clean
  Traces").** Attackers can plant a corrupted plan while the chain-of-
  thought trace stays clean — and separately, scratchpad persistence is the
  strongest predictor of long-horizon success. Judge loop iterations by
  on-disk state (the persisted scratchpad/checkpoint), never by a
  well-written transcript; the checker hook exists precisely because
  self-reported narration can diverge from reality.

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

### Hook gotchas (2026-09, practitioner reports — verify your wiring)

- **Blocking requires exit code 2.** A JSON `{"decision":"block"}` with exit 0 is
  silently ignored — the #1 reason a checker "doesn't work". Emit exit 2 on failure.
- **Stop-hook messages arrive in tool-result format**, and the model is trained to
  distrust tool results — some blocks get accepted and the agent simply stops instead
  of iterating. For hard enforcement prefer a PreToolUse gate (+ PostToolUse flag)
  over a Stop hook as the only gate.
- **Payloads arrive on stdin** (not env vars); project `.claude/settings.local.json`
  **overrides** — does not merge with — user-level settings; hook settings load once
  at session start. Debug real behavior with `claude --debug hooks`.

### Bounded-loop requirements (2026-09-08, arXiv:2609.00050; full analysis in
`docs/research/agentic-ai/2026-09-08-verification-product-bounded-loops.md`)

Any autonomous loop (this one included) must declare, before starting:

- **Budget** — max iterations, wall-clock, and/or token cost, written into the
  state file, not held in the model's head. Survey of 36,710 repos: loops in
  the wild almost never commit a budget or stop condition — the default is
  the unbounded loop, and it's the failure mode.
- **Persisted state** — progress lives in the state file so a restart resumes
  instead of redoing.
- **Evidence gate** — the loop advances only on machine-checkable output
  (exit code, real command output), never model self-assessment. Removing the
  recovery/verify loop dropped verified completion 95.0% → 12.9% (same model,
  same tasks); self-report gates produce phantom progression.
- **Evidence-gated transitions** (graph engineering) and **bounded retry with
  explicit stop conditions** (loop engineering) are separate concerns from
  per-action authorization (zero-trust harness) — a loop can verify its own
  work and still need external permission to act.

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
