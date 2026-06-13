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

## Collection health check (free, no LLM)

Before paying for any eval, run the static doctor over every agent + skill. It's
instant, deterministic, and CI-ready (exits nonzero on errors):

```bash
python3 tools/agent-evals/scripts/doctor.py --repo .
```

It checks frontmatter validity, `name` ↔ location, **broken bundle references**
(a ref is only an error if the file exists *nowhere* in the repo, so valid
cross-skill pointers don't false-flag), **references to non-existent subagents**
(e.g. ones deleted in a reorg), weak descriptions, oversized bodies,
rigid-directive overuse, **duplicate names**, and **cross-description overlap**
(routing/trigger-conflict risk caught statically). Use `--warnings-as-errors`
to fail CI on warnings too.

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

## Autonomous loops

Two loops can run unattended via the `claude` CLI (`claude -p`). Both nest
safely inside a Claude Code session. Pass `--model <id>` matching the model you
ship to, so the test matches what users experience.

### A) Description / routing loop — `optimize_description.py` ✅ verified

A description's real job is **discrimination**: among the sibling agents, win the
queries you own and don't steal a sibling's. That's what we measure — not "did a
single agent trigger?".

> **Why not "did it trigger?"** We tried that first and it was the wrong signal.
> In headless `claude -p` a capable main model just *does* a substantive task
> itself rather than spontaneously delegating to one injected agent (~0 trigger
> rate, unmovable by wording). The fix: inject **all** sibling agents as
> competitors, condition on delegation-sought ("Delegate this to the most
> appropriate specialist: …"), and score **which** agent is picked. Measured
> that way, the current descriptions route correctly **~19/21** with perfect
> precision; the only misses are queries the model handled directly, which a
> description can't fix. Translation: these descriptions are already well-tuned.

**1. Write a routing eval set** — each query labeled with the agent that should
own it (`"none"` = no sibling should). See `evals/routing-evals.json`:

```json
[
  {"query": "Implement an idempotent POST /orders endpoint in C# with EF Core.", "expected_agent": "principal-dotnet-engineer"},
  {"query": "Write ISTQB manual test cases for the password-reset flow.", "expected_agent": "qa-dotnet-engineer"},
  {"query": "Our React cart re-renders on every keystroke — profile and fix it.", "expected_agent": "none"}
]
```

> Queries must be **substantive, specialist-warranting tasks** — trivial ones
> won't delegate regardless of wording. (Confirmed empirically.)

**2. Run the loop** — it injects the competitor field from `--agents-dir`,
splits train/held-out, proposes a sharper description, and keeps the best by
**test** score (not train) to avoid overfitting:

```bash
python3 tools/agent-evals/scripts/optimize_description.py \
  --agent-path .claude/agents/principal-dotnet-engineer.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --max-iterations 5 --runs-per-query 3 --model <model-id> --verbose \
  --output report.json
```

Add `--apply` to write the winner back to the frontmatter. For a single pass
(no optimization) use `trigger_eval.py` with the same args.

### B) Body loop (objective agents only) — `improve_body.py` ✅ validated end-to-end

Improves the agent **body** against objective task evals, gated on a held-out set
so it can't overfit. Only for agents with objectively checkable outputs — the
.NET engineering agents, **not** `po-agent`. Each eval run is seeded from
`--project-template` (a fresh copy of a real repo), the agent runs as the session
(`claude --agent <name>`) inside it, and grading is the deterministic
`--verify-cmd` (exit 0 = pass). It proposes a body edit only on failure and
**accepts it only if train improves and held-out test does not regress**.

```bash
python3 tools/agent-evals/scripts/improve_body.py \
  --agent-path .claude/agents/principal-dotnet-engineer.md \
  --eval-set tools/agent-evals/evals/dotnet-body-evals.json \
  --project-template /path/to/cloned/CleanArchitecture \
  --verify-cmd "dotnet test tests/Domain.UnitTests -c Debug" \
  --workspace /tmp/principal-body-loop \
  --max-iterations 1 --model <model-id> --verbose
```

> **Status:** validated against [jasontaylordev/CleanArchitecture](https://github.com/jasontaylordev/CleanArchitecture)
> (net8.0). The agent added two new colours to the `Colour` value object + NUnit
> tests, and `dotnet test` confirmed it (5→6 passing) — a *genuine* pass, not a
> green no-op. **Caveat:** the accept/reject **gate** path runs only on a failing
> baseline; here the baseline passed, so propose→gate wasn't exercised by a real
> failure. **Requires** the relevant SDK installed and a `--verify-cmd` that
> truly builds/tests (an LLM grader is the fallback and the weak link). Runs
> autonomous agents with `--permission-mode bypassPermissions` inside the
> seeded copy — **use a throwaway dir.** See `docs/improving-agents.md`.

---

## Files

- `scripts/aggregate_benchmark.py` — runs → `benchmark.json` + `benchmark.md`
- `scripts/validate_agent.py` — fast advisory lint of a single agent definition
- `scripts/doctor.py` — static health check across ALL agents + skills (frontmatter, broken refs, stale subagent refs, name↔location, duplicate names, description overlap); CI-ready
- `scripts/trigger_eval.py` — routing/discrimination eval: which sibling agent wins a query (one pass)
- `scripts/optimize_description.py` — autonomous description/routing loop ✅
- `scripts/improve_body.py` — autonomous body loop for objective agents ✅
- `agents/grader.md` — how the grader judges expectations and critiques the eval set
- `references/schemas.md` — exact JSON contracts
- `evals/routing-evals.json` — labeled routing eval set ({query, expected_agent})
- `evals/dotnet-body-evals.json` — objective .NET body evals (verify_cmd-graded)
- `../../docs/improving-agents.md` — the improvement philosophy
