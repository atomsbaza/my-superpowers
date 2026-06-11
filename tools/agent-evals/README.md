# agent-evals

A rigorous loop for measuring and improving the agent definitions in
`.claude/agents/`. It is the agent analogue of Anthropic's
[`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator):
instead of asking "does this prompt *feel* better?", it runs the agent **with
vs. without** its definition on realistic tasks and measures the difference.

Two halves, used together:

- **The evaluation engine** (this README + the scripts) — the quantitative,
  A/B-against-baseline measurement.
- **The improvement philosophy** (`../../docs/improving-agents.md`) — how to turn
  results into a better definition without overfitting.

> **Not every agent gets the quantitative engine.** It depends on objectively
> verifiable outputs. `principal-dotnet-engineer` (code compiles / tests pass)
> and `qa-dotnet-engineer` (test code) fit. `po-agent` produces subjective prose
> (PRDs, roadmaps) — forcing pass/fail assertions there manufactures false
> confidence, so it uses the **qualitative review** half plus **description /
> triggering** evals only. This split is deliberate; see `improving-agents.md`.

---

## The loop

```
capture intent → draft/edit the agent → A/B run on test prompts
   → grade → aggregate into benchmark → review with a human
   → improve (generalize, lean, explain why) → repeat → optimize description
```

Figure out where you are in this loop and jump in there. New agent? Start at
intent. Already have a definition and a complaint? Jump straight to the A/B run.

---

## 1. Write a test set

Lint the definition first (cheap, deterministic — catches smells before you
spend tokens):

```bash
python3 tools/agent-evals/scripts/validate_agent.py .claude/agents/<agent>.md
```

Then write 2–3 realistic prompts — the kind of task a real user would actually
hand this agent — into `tools/agent-evals/<agent>/evals.json`. Write the
**prompts first**; draft the `expectations` later while runs are in flight.
Schema: `references/schemas.md`.

---

## 2. Run with-agent AND baseline, in the same turn

The load-bearing step. For each eval, spawn **two** subagents at once via the
Agent tool, telling each to save its output under `<run>/outputs/`:

| Configuration | How | Saves to |
|---|---|---|
| `with_agent` | `subagent_type: <agent>` (e.g. `principal-dotnet-engineer`) — the real registered agent, running under its own frontmatter `tools:`/`model:`/`effort:`. | `<agent>-workspace/iteration-N/<eval-name>/with_agent/` |
| `without_agent` (baseline) | `subagent_type: general-purpose` — same prompt, no agent identity or tool constraints. | `…/without_agent/` |

Using `subagent_type` (not "paste the .md into a prompt") is what makes the
comparison faithful: it runs the agent under the exact tool/model limits the
user actually experiences. Spawn both in the same turn so they finish together
and the comparison is apples-to-apples. The baseline isolates what the
*definition* buys you: if `with_agent` doesn't beat `general-purpose`, the
definition is dead weight.

> **No subagents (Claude.ai)?** Fall back to reading `.claude/agents/<agent>.md`
> and adopting it yourself for the with_agent run, and skip the baseline — same
> environment branch skill-creator uses. Lower fidelity (no real tool/model
> enforcement), but a useful sanity check.
>
> **Editing an existing agent** rather than creating one? You're measuring
> new-vs-old, so make the baseline the previous version: snapshot it first
> (`cp .claude/agents/<agent>.md /tmp/<agent>.snapshot.md`) and run that as the
> baseline instead of `general-purpose`.

The Agent tool returns a `<usage>` block with `subagent_tokens`, `tool_uses`,
and `duration_ms`. Capture it immediately into `<run>/timing.json` — it isn't
persisted anywhere else. Timing is optional; the benchmark works without it.

```json
{ "subagent_tokens": 8617, "tool_uses": 1, "duration_ms": 58375, "total_duration_seconds": 58.4 }
```

Workspace layout:

```
principal-dotnet-engineer-workspace/
└── iteration-1/
    ├── idempotent-upsert-endpoint/
    │   ├── with_agent/    { outputs/, grading.json, timing.json }
    │   └── without_agent/ { outputs/, grading.json, timing.json }
    └── cancellation-token-propagation/
        ├── with_agent/    …
        └── without_agent/ …
```

(The workspace is a sibling of the repo / a scratch dir — it is gitignored, not
committed.)

---

## 3. Grade (while runs finish, draft the assertions)

Draft objective `expectations` per eval — statements that pass only when the
work was genuinely done right (see the *discriminating* test in `agents/grader.md`).
Then grade each run with a grader subagent following `agents/grader.md`; it
writes `grading.json` into each run directory.

---

## 4. Aggregate into a benchmark

```bash
python3 tools/agent-evals/scripts/aggregate_benchmark.py \
  <agent>-workspace/iteration-1 --agent-name <agent>
```

This writes `benchmark.json` and a human-readable `benchmark.md`: pass-rate,
time, and tokens per configuration (mean ± stddev) with the delta, a per-eval
breakdown, and auto-generated analyst notes — notably **non-discriminating
assertions** (pass with *and* without the agent → they don't measure the
agent's value) and **high-variance evals** (possibly flaky).

### Reviewing

This repo is a definitions collection, not an app, so the harness emits
`benchmark.md` rather than a browser viewer — read it directly, or render it
anywhere Markdown renders. If you want skill-creator's interactive
`generate_review.py` viewer, it can be vendored in under
`tools/agent-evals/eval-viewer/` (add an `ATTRIBUTION.md` entry — it's
Anthropic-licensed). Ask before adding it.

Show a human the per-eval outputs and the benchmark, and collect feedback —
especially on the evals where `with_agent` did *not* clearly beat baseline.

---

## 5. Improve, then repeat

Apply improvements per `../../docs/improving-agents.md`, then rerun into
`iteration-2/` (baseline included) and compare. Keep going until the human is
happy, feedback is empty, or you stop making meaningful progress.

---

## Description / triggering optimization (all three agents)

The `description` frontmatter is what decides whether the agent gets invoked at
all — independent of how good the body is, and it applies to subjective agents
too. After the body is solid, build ~20 realistic trigger queries (a mix of
should-trigger and tricky should-*not*-trigger near-misses), and check the
description triggers correctly on them. Make descriptions slightly *pushy* —
Claude tends to under-trigger. See `improving-agents.md` for the method.

---

## Files

- `scripts/aggregate_benchmark.py` — runs → `benchmark.json` + `benchmark.md`
- `scripts/validate_agent.py` — fast advisory lint of an agent definition
- `agents/grader.md` — how the grader judges expectations and critiques the eval set
- `references/schemas.md` — exact JSON contracts
- `../../docs/improving-agents.md` — the improvement philosophy
