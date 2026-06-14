# Apple Agent Routing Validation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate routing/discrimination of the 6 newly-merged Apple agents within the full collection, and fix only descriptions that demonstrably misroute.

**Architecture:** Extend `evals/routing-evals.json` with specialist Apple queries, run one read-only `trigger_eval.py` pass on Opus 4.8 (`runs-per-query 2`) to get a full-collection confusion matrix, write a results report, then run `optimize_description.py --apply` *only* on agents that misroute (held-out gated) and re-measure. No body evals (Apple agents produce subjective output).

**Tech Stack:** Python 3 (stdlib only), the repo's `tools/agent-evals/` scripts, the `claude` CLI (`claude -p`), git/`gh`.

**Branch:** `feat/apple-agent-routing-eval` (already created; spec already committed there).

**Spec:** `docs/superpowers/specs/2026-06-14-apple-agent-routing-eval-design.md`

---

## Notes for the implementer

- This plan edits a JSON data file and runs existing eval scripts — there is no new code to unit-test. "Verification" per task is: the JSON parses, `doctor` stays at 0 errors, and the eval scripts run cleanly. Treat those as the test gates.
- **Cost gate:** Task 2 and Task 4 spend Opus tokens via `claude -p`. Do not run them without confirming with the user first (the user asked to control cost). Tasks 1, 3, 5 are free.
- Every query added MUST be a substantive, specialist-warranting task — trivial queries won't delegate regardless of wording (per `tools/agent-evals/README.md`).

---

## Task 1: Add Apple-agent queries to the routing eval set

**Files:**
- Modify: `tools/agent-evals/evals/routing-evals.json`

- [ ] **Step 1: Confirm the current set parses and note the baseline count**

Run:
```bash
cd /Users/pisitkoolplukpol/Work/my-superpowers
python3 -c "import json; d=json.load(open('tools/agent-evals/evals/routing-evals.json')); print('items:', len(d))"
```
Expected: `items: 21`

- [ ] **Step 2: Add 12 Apple queries (2 per agent) before the negatives block**

In `tools/agent-evals/evals/routing-evals.json`, insert the following objects immediately **after** the `po-agent` block and **before** the three `"expected_agent": "none"` entries. Keep the existing blank-line grouping style. Do not modify any existing entry — including the existing Swift `none` query, which stays `none` by design.

```json
  {"query": "Review this `@Observable` view model — I'm getting actor-isolation warnings and I'm not sure the Sendable conformance on the model I pass into a detached Task is correct under Swift 6 strict concurrency.", "expected_agent": "swift-reviewer"},
  {"query": "Audit this image-cache class for retain cycles — the completion closures capture self strongly and I don't think ARC is ever releasing the cached entries.", "expected_agent": "swift-reviewer"},

  {"query": "Review my SwiftUI settings screen against the iOS 26 HIG — the toolbar treatment, whether the Liquid Glass usage is right, and if the SF Symbols are the correct weights.", "expected_agent": "ui-reviewer"},
  {"query": "Does this custom card layout reflow correctly at the largest Dynamic Type sizes, and is the spacing and control sizing HIG-compliant on macOS Tahoe?", "expected_agent": "ui-reviewer"},

  {"query": "My App Store archive fails with 'no provisioning profile matches' for the distribution build — sort out the signing and the export options so I can ship it.", "expected_agent": "xcode-build"},
  {"query": "Swift Package Manager won't resolve after I bumped a dependency — there's a version conflict and the build can't find the module. Fix the package resolution so it builds.", "expected_agent": "xcode-build"},

  {"query": "I'm submitting to the App Store next week — audit my PrivacyInfo.xcprivacy and the privacy nutrition labels for completeness against what the app actually collects.", "expected_agent": "privacy-reviewer"},
  {"query": "We're adding the Firebase Analytics SDK, which collects device identifiers — what privacy-manifest entries and NSUserTrackingUsageDescription changes do I need before release?", "expected_agent": "privacy-reviewer"},

  {"query": "I just built the new onboarding flow — run it in the simulator and confirm each screen renders and the Continue button advances to the next step before I mark this done.", "expected_agent": "simulator-qa"},
  {"query": "Check how the feed screen looks in the simulator for the empty state and the network-error state — take screenshots and confirm the UI is correct in both.", "expected_agent": "simulator-qa"},

  {"query": "Run the full unit and integration test suite on the simulator and triage whatever fails so I know what's actually broken.", "expected_agent": "ios-test-runner"},
  {"query": "I refactored the sync layer — run the tests on the simulator to confirm I didn't introduce regressions, and make sure the SwiftData model tests are using XCTestCase.", "expected_agent": "ios-test-runner"},
```

- [ ] **Step 3: Verify the JSON still parses and the counts are right**

Run:
```bash
python3 -c "import json; from collections import Counter; d=json.load(open('tools/agent-evals/evals/routing-evals.json')); print('items:', len(d)); print(Counter(x['expected_agent'] for x in d))"
```
Expected: `items: 33` and a counter showing `swift-reviewer: 2, ui-reviewer: 2, xcode-build: 2, privacy-reviewer: 2, simulator-qa: 2, ios-test-runner: 2, principal-dotnet-engineer: 6, qa-dotnet-engineer: 6, po-agent: 6, none: 3`.

- [ ] **Step 4: Verify every `expected_agent` names a real agent file (no typos)**

Run:
```bash
python3 -c "
import json, os
d=json.load(open('tools/agent-evals/evals/routing-evals.json'))
agents={f[:-3] for f in os.listdir('.claude/agents') if f.endswith('.md')}
bad=sorted({x['expected_agent'] for x in d} - agents - {'none'})
print('unknown expected_agent labels:', bad or 'NONE — all valid')
"
```
Expected: `unknown expected_agent labels: NONE — all valid`

- [ ] **Step 5: Run the doctor — collection must stay healthy**

Run:
```bash
python3 tools/agent-evals/scripts/doctor.py --repo .
```
Expected: `0 error(s)` (1 pre-existing `handoff` warning is acceptable and unrelated).

- [ ] **Step 6: Commit**

```bash
git add tools/agent-evals/evals/routing-evals.json
git commit -m "test(agent-evals): add Apple-agent routing queries to the eval set

Two specialist queries per Apple agent (swift-reviewer, ui-reviewer,
xcode-build, privacy-reviewer, simulator-qa, ios-test-runner). Existing
.NET/QA/PO queries and the Swift crash 'none' negative are unchanged.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Measure routing (one read-only pass) — COST GATE

**Files:**
- Create: `tools/agent-evals/apple-routing-workspace/measure-1.txt` (raw output; workspace is gitignored)

- [ ] **Step 1: Confirm with the user before spending Opus tokens**

This step shells out to `claude -p` ~33 queries × 2 runs on `claude-opus-4-8`. Confirm the user wants to proceed now. Do not continue this task otherwise.

- [ ] **Step 2: Confirm the `claude` CLI is available and authed**

Run:
```bash
command -v claude && claude --version
```
Expected: a path and a version (e.g. `2.1.177 (Claude Code)`). If missing, stop and report — do not partial-run.

- [ ] **Step 3: Run the discrimination pass and capture raw output**

`trigger_eval.py` records `majority_pick` for *every* query in one pass, so a single invocation (any `--agent-path`) yields the full confusion matrix; `--agent-path` only selects whose precision/recall is printed.

Run:
```bash
mkdir -p tools/agent-evals/apple-routing-workspace
python3 tools/agent-evals/scripts/trigger_eval.py \
  --agent-path .claude/agents/swift-reviewer.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --model claude-opus-4-8 --runs-per-query 2 --verbose \
  2>&1 | tee tools/agent-evals/apple-routing-workspace/measure-1.txt
```
Expected: a per-query table with columns including PASS/FAIL, `expected_agent`, and `majority_pick`, then a summary. Non-zero exit is fine — we read the table regardless.

- [ ] **Step 4: Sanity-check the output captured the per-query winners**

Run:
```bash
grep -cE "swift-reviewer|ui-reviewer|xcode-build|privacy-reviewer|simulator-qa|ios-test-runner|principal-dotnet-engineer|qa-dotnet-engineer|po-agent|none" tools/agent-evals/apple-routing-workspace/measure-1.txt
```
Expected: a count ≥ 33 (one row per query at minimum). If 0, the run failed — re-check the CLI/auth before re-running.

No commit — the workspace is gitignored scratch output.

---

## Task 3: Analyze and write the results report

**Files:**
- Create: `docs/research/ios/2026-06-14-apple-agent-routing-results.md`

- [ ] **Step 1: Build the confusion table from the captured output**

From `tools/agent-evals/apple-routing-workspace/measure-1.txt`, for each query record `expected_agent` → `majority_pick`. Compute, for each Apple agent:
- **recall** = (its queries where `majority_pick` == that agent) / (its 2 queries)
- **precision** = (queries it won where it was the expected owner) / (all queries it won)

Flag any of: an Apple agent losing its own query; an Apple agent stealing a sibling's or a negative; and specifically inspect the two known-overlap pairs — `swift-reviewer` vs `ui-reviewer`, and `xcode-build` vs `privacy-reviewer` (both descriptions mention privacy manifests). Also note where the existing Swift crash `none` query routed.

- [ ] **Step 2: Write the report**

Create `docs/research/ios/2026-06-14-apple-agent-routing-results.md` with:
- A header (date, model `claude-opus-4-8`, `runs-per-query 2`, eval-set commit SHA from `git rev-parse --short HEAD`).
- A per-agent recall/precision table for the 6 Apple agents.
- The full confusion table (expected → majority_pick) for all 33 queries.
- A "Misroutes & overlaps" section listing every flagged item with the suspected cause (which sibling won and why the descriptions might collide).
- A "Decision" section: list of agents (if any) that need `optimize_description.py` (Task 4), or "all Apple agents route correctly — no description changes needed."
- A note on where the Swift crash `none` query routed and whether ground truth should be revisited (do not change the eval set here; just record the finding).

- [ ] **Step 3: Commit the report**

```bash
git add docs/research/ios/2026-06-14-apple-agent-routing-results.md
git commit -m "docs(ios): Apple-agent routing eval results

Opus 4.8 discrimination pass over the combined routing eval set: per-agent
recall/precision, confusion table, and the optimize decision.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Optimize misrouting descriptions — CONDITIONAL, COST GATE

> Skip this entire task if Task 3's Decision section says all Apple agents route correctly. In that case the eval-set addition + report are the deliverable.

**Files:**
- Modify: `.claude/agents/<misrouting-agent>.md` (frontmatter `description` only, via `--apply`)
- Create: `tools/agent-evals/apple-routing-workspace/optimize-<agent>.json` (report; gitignored)

- [ ] **Step 1: Confirm with the user before spending Opus tokens (per agent)**

Each agent's loop runs up to `--max-iterations 5`, each iteration re-running the eval. Confirm before proceeding.

- [ ] **Step 2: Run the held-out-gated description loop for ONE misrouting agent**

Replace `<agent>` with the specific agent name from Task 3.

Run:
```bash
python3 tools/agent-evals/scripts/optimize_description.py \
  --agent-path .claude/agents/<agent>.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --max-iterations 5 --runs-per-query 2 --model claude-opus-4-8 --verbose --apply \
  --output tools/agent-evals/apple-routing-workspace/optimize-<agent>.json
```
Expected: the loop proposes sharper descriptions, keeps the best by **held-out test** score, and (because `--apply`) writes the winner into the agent's frontmatter. If no proposal beats the baseline on the held-out split, it leaves the description unchanged — that is a valid result.

- [ ] **Step 3: Verify doctor still passes after the rewrite**

Run:
```bash
python3 tools/agent-evals/scripts/doctor.py --repo .
```
Expected: `0 error(s)`.

- [ ] **Step 4: Repeat Steps 1–3 for each remaining misrouting agent**

One agent at a time, so each rewrite is gated and observable independently.

- [ ] **Step 5: Re-measure the whole collection to confirm the fix and no regression**

Run:
```bash
python3 tools/agent-evals/scripts/trigger_eval.py \
  --agent-path .claude/agents/swift-reviewer.md \
  --agents-dir .claude/agents \
  --eval-set tools/agent-evals/evals/routing-evals.json \
  --model claude-opus-4-8 --runs-per-query 2 --verbose \
  2>&1 | tee tools/agent-evals/apple-routing-workspace/measure-2.txt
```
Expected: the previously-misrouting Apple queries now route to their owners, and the existing 21 .NET/QA/PO + negative queries still route as before (no regression). Append a short "Iteration 2" section to the report with the new numbers.

- [ ] **Step 6: Commit the applied description changes + updated report**

```bash
git add .claude/agents/ docs/research/ios/2026-06-14-apple-agent-routing-results.md
git commit -m "fix(agents): sharpen Apple-agent descriptions that misrouted

Applied optimize_description.py winners (held-out gated) for the agents
flagged in the routing report; re-measured with no regression on the
existing .NET/QA/PO routing.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Open the PR

**Files:** none (git/gh only)

- [ ] **Step 1: Final doctor gate**

Run:
```bash
python3 tools/agent-evals/scripts/doctor.py --repo .
```
Expected: `0 error(s)`.

- [ ] **Step 2: Push the branch**

```bash
git push -u origin feat/apple-agent-routing-eval
```

- [ ] **Step 3: Open the PR**

```bash
gh pr create --base main --head feat/apple-agent-routing-eval \
  --title "test(agent-evals): validate Apple-agent routing" \
  --body "Adds specialist routing queries for the 6 Apple agents, measures discrimination on Opus 4.8, and applies any held-out-gated description fixes. Includes the results report under docs/research/ios/. doctor: 0 errors.

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```
Expected: a PR URL.

---

## Self-review (done by plan author)

- **Spec coverage:** §1 eval-set extension → Task 1; §2 measure → Task 2; §3 report → Task 3; §4 conditional optimize + re-measure → Task 4; §5 ship → Task 5. Swift-`none` decision honored (Task 1 Step 2 leaves it unchanged; Task 3 records where it routed without changing ground truth). Verification (`doctor` 0 errors, no regression) appears in Tasks 1/4/5. All spec sections covered.
- **Placeholders:** none — all 12 queries are written out in full; `<agent>` in Task 4 is an intentional per-result substitution, defined by Task 3's output.
- **Consistency:** `runs-per-query 2` and `claude-opus-4-8` used identically across Tasks 2 and 4; eval-set path and agents-dir consistent throughout; item counts (21 → 33) consistent between Task 1 Steps 1 and 3.
