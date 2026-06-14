# Apple Agent Routing Validation — Design

**Date:** 2026-06-14
**Status:** Approved (design)
**Author:** brainstorming session

## Problem

PR #7 added 6 Apple platform agents (`swift-reviewer`, `ui-reviewer`,
`xcode-build`, `privacy-reviewer`, `simulator-qa`, `ios-test-runner`) and 7
SwiftUI/Swift skills to the collection. The collection's identity is
**eval-driven** — it ships a static `doctor`, a routing/discrimination eval
loop, and a body eval loop precisely so quality is *measured*, not asserted.

The static `doctor` passes (0 errors), but the **routing eval set
(`evals/routing-evals.json`) only covers the .NET/QA/PO agents**. The 6 new
Apple agents have never been measured for routing. Adding agents changes the
competitive field for *every* agent, so a previously-correct routing decision
can silently degrade. We need to confirm the new agents win their own queries
and don't steal from each other or the existing siblings.

## Goal

Validate routing/discrimination for the Apple agents within the full
collection, fixing only what demonstrably misroutes — without churning the
already-well-tuned .NET/QA/PO descriptions.

Non-goals:
- Body/output-quality evals. The Apple agents are reviewers/QA agents producing
  subjective output; the objective `improve_body.py` loop does not fit them
  (same rationale the README gives for excluding `po-agent`).
- Broadening the collection or refactoring existing agents.

## Approach

Measure first; optimize only if the numbers justify it. Run against
`claude-opus-4-8` (matches what the user ships in Claude Code) so the verdict
reflects real experience.

### 1. Extend the routing eval set

Edit `tools/agent-evals/evals/routing-evals.json`:

- **Add 2 substantive, specialist-warranting queries per Apple agent** (~12
  new), each labeled with its owning agent. Queries must be real, non-trivial
  tasks — the README confirms trivial queries won't delegate regardless of
  wording. Sketch (final wording in implementation):
  - `swift-reviewer` — review `@Observable`/actor-isolation/Sendable under Swift 6;
    review ARC/retain-cycle correctness in a closure-heavy file.
  - `ui-reviewer` — HIG/Liquid-Glass review of a settings screen; SF Symbols 6 +
    Dynamic Type reflow review.
  - `xcode-build` — App Store archive fails on a missing provisioning profile;
    SPM resolution / strict-concurrency build failure.
  - `privacy-reviewer` — pre-submission `PrivacyInfo.xcprivacy` + nutrition-label
    audit; adding an analytics SDK that collects device data.
  - `simulator-qa` — verify a new onboarding flow renders/behaves correctly on
    the simulator before sign-off; check empty/error states visually.
  - `ios-test-runner` — run the simulator test suite and triage failures; enforce
    XCTestCase for a SwiftData model test.
- **Leave the existing 18 .NET/QA/PO queries and the React/Python negatives
  unchanged.**
- **Reconcile the existing Swift `none` query** — *"App crashes on launch after
  the iOS 18 update — find out why and fix it."* This is runtime-crash debugging,
  which no Apple agent cleanly owns (`xcode-build` is build/signing, not runtime
  debugging). **Decision: keep it `none`.** Do not silently relabel; if the eval
  shows the model consistently routes it to an Apple agent, flag that in the
  report for a follow-up decision rather than changing ground truth to match the
  model.

### 2. Measure (one pass, read-only)

```bash
python3 tools/agent-evals/scripts/trigger_eval.py \
  --agent-path .claude/agents/swift-reviewer.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --model claude-opus-4-8 --runs-per-query 2 --verbose
```

`trigger_eval.py` records `majority_pick` (the actually-chosen agent) for *every*
query in a single pass, not just the named target — so one invocation yields a
full confusion matrix across all 9 agents. `--agent-path` only selects whose
precision/recall is printed; the per-query winners cover everyone.

`--runs-per-query 2` (trimmed from the default 3) to reduce Opus token spend.

### 3. Analyze → short report

Produce a lightweight markdown report: per-Apple-agent **recall** (wins its own
queries) and **precision** (doesn't steal a sibling's or a negative), the
confusion table, and flagged misroutes. Watch especially:
- `swift-reviewer` vs `ui-reviewer` (overlapping "review Swift UI code" surface),
- any Apple agent capturing the `none` Swift crash query.

Save to `docs/research/ios/2026-06-14-apple-agent-routing-results.md`
(`docs/research/ios/` already exists for iOS research).

### 4. Optimize — only if needed

For any Apple agent that demonstrably misroutes, run the autonomous description
loop over the **combined** eval set:

```bash
python3 tools/agent-evals/scripts/optimize_description.py \
  --agent-path .claude/agents/<agent>.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --max-iterations 5 --runs-per-query 2 --model claude-opus-4-8 --verbose --apply \
  --output report.json
```

The loop splits train/held-out and keeps the best by **test** score, so it
cannot overfit or silently break the .NET siblings. After any `--apply`,
**re-measure** to confirm the fix and zero regression on the existing 21
queries. If everything routes cleanly in step 2, change nothing — the eval-set
addition is the only deliverable.

### 5. Ship

Commit the extended `routing-evals.json` (+ any applied description fixes) and
the report on a branch → PR, matching the repo's merge-PR workflow. `doctor`
must stay at 0 errors throughout.

## Verification

- `python3 tools/agent-evals/scripts/doctor.py --repo .` → 0 errors.
- Post-optimize re-run: existing .NET/QA/PO queries still route correctly (no
  regression); each Apple agent wins its own queries.
- Every new eval item is a substantive, specialist-warranting task (not trivial).

## Risks & mitigations

- **Token cost.** ~33 queries × 2 runs on Opus 4.8, single measurement pass.
  Mitigated by one-pass measurement and the trimmed run count. Optimize step
  runs only on agents that fail.
- **`claude` CLI availability.** The eval shells out to `claude -p`; it must be
  installed and authed. Verify before spending anything; if unavailable, stop
  and report rather than partially run.
- **Description churn / overfitting.** Mitigated by the held-out gate
  (keep-best-by-test-score) and a mandatory re-measure after `--apply`.

## Open questions

None blocking. The Swift-crash-query label is intentionally fixed as `none`
pending eval evidence (see step 1).
