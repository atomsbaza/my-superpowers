# Improving Agents — the philosophy

How to turn evaluation results (`tools/agent-evals/`) into a better agent
definition. The mechanics measure *whether* a change helped; this is *how* to
decide what to change. Adapted from the "heart of the loop" in Anthropic's
skill-creator, applied to the agent definitions in `.claude/agents/`.

The premise: an agent definition will run thousands of times across prompts you
will never see. You iterate on a handful of test cases because they're fast to
judge — but a definition that only wins on those cases is worthless. Everything
below is in service of **generalizing**, not fitting the test set.

---

## 1. Generalize from the feedback — don't patch the example

When an eval fails, the tempting fix is a narrow rule aimed at that exact case
("when the endpoint is an upsert, use ON DUPLICATE KEY"). Resist it. Narrow
rules pile up, fight each other, and don't transfer. If an issue is stubborn,
try a *different framing* — a new metaphor, a different working pattern, a
worked example that shows the principle — rather than clamping down with one
more special case. It's cheap to try; you might land on something that fixes a
whole class of failures at once.

## 2. Keep the definition lean

Read the **transcripts**, not just the final outputs. If the agent wastes turns
on something unproductive, find the instruction that's causing it and cut it.
Every line in the body is always-loaded context and a claim on the model's
attention; a line that isn't pulling its weight is costing you. `validate_agent.py`
flags an over-long body — but the real test is whether removing a paragraph
*changes the benchmark*. If it doesn't, it was decoration.

## 3. Explain the *why*, don't bark `NEVER`

Today's models have good theory of mind. Tell them *why* something matters and
they generalize to cases you didn't enumerate; give them a rigid `ALWAYS/NEVER`
and they follow it literally and brittlely. If you catch yourself writing an
all-caps absolute, that's a yellow flag — reframe it as the reasoning behind the
rule.

This is **reframe, not delete.** Some constraints encode genuine domain rules
(`po-agent`: "acceptance criteria must be verifiable"). Keep the rule — but state
the consequence that makes it matter, so the model applies it with judgment:

> Before: *Never write acceptance criteria that cannot be verified.*
> After: *Acceptance criteria exist so QA and dev can agree, before coding,
> on exactly what "done" means. "The system should be fast" can't be checked,
> so it can't settle a dispute — give a measurable threshold instead.*

Same rule. The second version survives contact with a case the first didn't
anticipate.

## 4. Bundle repeated work

Read the transcripts across test cases. If every `with_agent` run independently
writes a similar helper (the same Testcontainers fixture, the same scaffold
script), that's a strong signal: write it once, put it in a `scripts/` or
`reference/` file beside the agent, and have the definition point to it. You pay
the cost once instead of on every future invocation.

---

## Which agents get measured how

The quantitative A/B engine is only as rigorous as its assertions are
*objective*. That makes it a good fit for some agents and a bad fit for others —
and pretending otherwise reproduces exactly the overfitting trap above.

| Agent | Output | How to evaluate |
|---|---|---|
| `principal-dotnet-engineer` | C# that compiles, tests that pass | **Quantitative A/B** — assertions like "builds", "test passes", "token threaded". Strong fit. |
| `qa-dotnet-engineer` | test code, plans | **Mostly quantitative** — does the generated test compile and actually exercise the path? Plus qualitative for coverage judgment. |
| `po-agent` | BRDs, PRDs, stories, roadmaps | **Qualitative review** — "is this a good PRD" is human judgment; forcing pass/fail assertions yields non-discriminating checks and false confidence. |

**All three** still benefit from **description / routing** evals — but measure
the right thing (see below).

> **Finding (2026-06): descriptions control routing, not spontaneous triggering.**
> We first measured "does this single agent trigger?" and got ~0 — in headless
> `claude -p` a capable main model just does substantive tasks itself instead of
> delegating to one injected agent, and no wording changes that. The signal a
> description *does* control is **which sibling wins** once delegation happens.
> Measured that way (inject all siblings as competitors, condition on
> delegation-sought, score the pick), the current descriptions route **~19/21**
> correctly with perfect precision — they're already well-tuned. So
> `optimize_description.py` is most valuable as a **regression guard when you add
> or change an agent**, not as a routine tuner.

For the qualitative agents: still run the test prompts and still show outputs to
a human for review — just skip the benchmark numbers and the baseline
comparison, and drive improvement from the human feedback directly. Don't
manufacture assertions to look rigorous.

---

## v1 limitation: single run per configuration

skill-creator runs each eval **3× per configuration** and reports within-eval
variance — its main defense against LLM nondeterminism. This harness currently
does **one run per config**, so the stddev in `benchmark.md` is *spread across
different evals* (the agent is uneven from task to task), **not** flakiness of a
single task. "Run it more times" would not change that number. Treat a single
run as a directional signal, not a verdict; for a result you'll act on, spawn
the same eval a few times by hand and eyeball the spread. Adding a
`runs_per_configuration` loop is the natural next upgrade.

## Body loop: validated

`improve_body.py` was validated end-to-end against
[jasontaylordev/CleanArchitecture](https://github.com/jasontaylordev/CleanArchitecture)
(net8.0): `principal-dotnet-engineer` added two new colours to the `Colour`
value object plus NUnit tests, graded by a real `dotnet test` (5→6 passing) — a
genuine pass, not a green no-op. Two things that made it trustworthy: each run
is seeded from a fresh copy of the project (`--project-template`), and grading is
a deterministic `--verify-cmd` that actually builds and tests (not an LLM
grader). Open item: the accept/reject **gate** only fires on a failing baseline,
which didn't occur here, so that branch hasn't run against a real failure.

## The discipline in one line

Measure against a baseline, read the transcripts, generalize the fix, explain
the why, and keep cutting until every line earns its place.
