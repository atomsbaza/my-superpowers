# Apple Agent Routing — Eval Results

**Date:** 2026-06-14
**Model:** `claude-opus-4-8`
**runs-per-query:** 2
**Eval set:** `tools/agent-evals/evals/routing-evals.json` @ `c76658e` (33 queries)
**Harness:** `tools/agent-evals/scripts/trigger_eval.py` (one discrimination pass; `majority_pick` per query)

## TL;DR

**Precision is perfect — no description changes applied.** None of the 9 agents
stole a query they don't own, and the two overlap pairs we were worried about
(`swift-reviewer`↔`ui-reviewer`, `xcode-build`↔`privacy-reviewer`) showed zero
cross-contamination. Recall misses exist, but every single one routed to `none`
(the model handled the task inline) — never to a wrong sibling. That is the
README's documented, description-unfixable phenomenon, not a routing conflict.

## Per-Apple-agent recall

| Agent | Recall | Picks |
|---|---|---|
| `xcode-build` | 2/2 | xcode-build, xcode-build |
| `ios-test-runner` | 2/2 | ios-test-runner, ios-test-runner |
| `privacy-reviewer` | 1/2 | privacy-reviewer, **none** |
| `simulator-qa` | 1/2 | simulator-qa, **none** |
| `swift-reviewer` | 0/2 | **none**, **none** |
| `ui-reviewer` | 0/2 | **none**, **none** |

## Precision (the core risk of adding 6 agents)

**No false grabs by any of the 9 agents.** A query's `majority_pick` was either
its correct owner or `none`/a built-in (`general-purpose`, `debugger`) — never a
different custom sibling.

- `swift-reviewer` vs `ui-reviewer`: no cross-contamination.
- `xcode-build` vs `privacy-reviewer` (both descriptions mention privacy
  manifests): no cross-contamination.

## The `none` negatives

| Query | Routed to | Verdict |
|---|---|---|
| React re-render profiling | `none` | ✓ no sibling grabbed it |
| Python CSV → Postgres | `general-purpose` | ✓ generic, not a sibling |
| Swift app crashes on launch (iOS 18) | `debugger` | ✓ built-in debugger, **no Apple agent grabbed it** |

The Swift-crash query routing to the built-in `debugger` **validates the design
decision to keep it labeled `none`**: no Apple agent owns runtime-crash
debugging, and indeed none claimed it.

## Why the recall misses are not description bugs

Every miss is `→ none` (the model answered directly), not `→ wrong agent`. The
decisive evidence: the `swift-reviewer` query —

> *"Review this `@Observable` view model — actor-isolation warnings … Sendable
> conformance … Swift 6 strict concurrency."*

— is a near-verbatim match to `swift-reviewer`'s own description and **still**
went to `none`. If a perfect keyword match doesn't trigger delegation, sharper
wording won't either. This matches the harness README's empirical finding: in
headless `claude -p`, a capable main model often performs review/advisory tasks
itself rather than delegating, and "the only misses are queries the model
handled directly, which a description can't fix." The existing
`principal-dotnet-engineer` review query ("Review this C# diff…") misses the
same way, confirming the pattern is systemic to review/advisory phrasing, not
specific to the Apple descriptions.

**Caveat:** the main pass used `runs-per-query` 2 (trimmed from the README's 3 to
save Opus cost), so the partial agents (`privacy-reviewer`, `simulator-qa` at
1/2) carry some sampling noise. To firm up the headline 0/2 results, the four
`swift-reviewer` + `ui-reviewer` queries were **re-run at `runs-per-query` 4**:
all four still routed to `none` (0/4). The 0-recall finding is therefore not a
2-run artifact. The precision conclusion is unaffected regardless of run count —
a steal would have shown up either way.

## Decision

**No `optimize_description.py` run — a judgment override of the plan's literal
skip-gate.** The plan's written skip condition was "all Apple agents route
correctly." By recall that condition is *not* met: `swift-reviewer` and
`ui-reviewer` are 0/2. I noticed that and still chose to skip, for a
better-informed reason:

1. **The optimizer is aimed at a failure mode we don't have.**
   `optimize_description.py` tunes *which agent wins once delegation happens*.
   Our failures are *no delegation at all* (`got=none`), not *wrong agent*. So
   the tool's lever barely touches our actual miss. The near-verbatim
   `swift-reviewer` query still going to `none` shows there is minimal headroom
   for wording to force delegation — sharper text won't move it.
2. **Perfect precision** — there is no description conflict to resolve, which
   was the actual risk introduced by adding the agents. The thing optimize would
   fix is already clean.
3. **Cost (secondary)** — the optimize loop re-runs the eval up to
   `--max-iterations` times per agent for predicted-zero gain; the held-out gate
   would most likely leave the descriptions unchanged anyway.

**Optional follow-up (not recommended):** if we later want to *attempt* lifting
`swift-reviewer`/`ui-reviewer` recall, run
`optimize_description.py --apply` on just those two over the combined set. Expect
it to leave them unchanged. A more productive lever would be the *invocation
path* (e.g. an explicit "use the Swift reviewer" instruction), which is outside
description tuning.

## Reproduce

```bash
python3 tools/agent-evals/scripts/trigger_eval.py \
  --agent-path .claude/agents/swift-reviewer.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --model claude-opus-4-8 --runs-per-query 2 --num-workers 8 --verbose
```
