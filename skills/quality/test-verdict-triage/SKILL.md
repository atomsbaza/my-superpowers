---
name: test-verdict-triage
description: Use after a multi-minute or full-suite test run (pytest, CI, xcodebuild) finishes and before you call the result passed, failed, or a regression - reads the verdict from the log, separates real regressions from pre-existing failures and load flakes, and reports what was not run
---

# Test Verdict Triage

**Status: candidate (drafted 2026-10-13 from `learning-log.md`; Opus-reviewed once). Promoted into skills/ on 2026-10-13 at the user's request; revisit after a few real uses (see falsifier below).**

Companion to `verification-before-completion` (run the full command, read the output) and `learning-harness`
(keep baseline, targeted and regression evidence separate; use `success | failed | blocked | rejected`). This skill adds
the steps between "the run finished" and "I report a verdict".

Status mapping to `learning-harness`: regression -> `failed`; pre-existing or environment failure -> reported
separately, `blocked` if it stops the verdict; no verdict signal -> `blocked`.

## When to use / not

Use before reporting a branch green, opening a PR, or blaming a change for a failure. A small change on a large repo
may use targeted checks while iterating (see `ci-quality-gates`), but the full suite is required before the green
claim. Skip for doc-only changes with no suite.

## Steps

1. **Run the whole suite and note the machine load.** Repo-wide guard tests (registry, parity and sanitizer-list
   tests) sit far from the changed files, so a curated batch misses them. Run in the background, log to disk (not
   `/tmp`, it was wiped mid-task), do not edit the tree during the run, and record `uptime` and any other heavy
   sessions: load ~300 from another session made one suite 3x slower. A targeted run is never a full-suite result.
2. **Take the verdict from the log.** Three outcomes:
   - **FAIL** if any of these appear anywhere: `** TEST FAILED **`, `** BUILD FAILED **`, a `Failing tests:` section,
     any `Test Case ... failed`, `Restarting after unexpected exit`, `: Fatal error:` (xcodebuild); a non-zero pytest
     exit (1 failed, 2 interrupted, 3 internal error, 4 usage error) or a worker crash / "node down" line (pytest-xdist).
     Strict by design: a case that failed then passed on retry is still reported, with the retry noted.
   - **PASS** only if a success signal is present (`** TEST SUCCEEDED **`, also check `** TEST EXECUTE SUCCEEDED **`
     for `test-without-building`; pytest exit 0 with the expected count) **and** none of the FAIL signals appear.
   - **NO RESULT** (report as `blocked`) if neither: hung, killed, timed out, or pytest exit 5 (no tests collected).
   A total far below the usual count is a reason to look for the restart line before trusting the run. Swift Testing
   prints a different per-case format than `Test Case ... failed`; rely on the summary signals for it.
3. **Compare each failure against clean `main` under the same conditions.** `git fetch origin`, then
   `git worktree add --detach <dir> $(git merge-base HEAD origin/main)` (or rebase the branch onto the fetched
   `origin/main` first); remove it afterwards with `git worktree remove <dir>`. A fresh worktree has no untracked
   artifacts (build output, symlinks, venv): recreate them there, or the comparison is not equal. Fails on both =
   pre-existing or environment, report separately. Fails only on the branch = regression.
4. **Rerun the remaining failures alone, one file at a time, several times** (the source used 3 runs). Passes alone
   = **likely** load flake, report it as such. If the same file passes on clean main under the same load, treat it as
   a regression candidate (a slower change can fail only under load). Do not batch heavy files into one process on
   rerun: that gave 59 false failures once.
5. **Prove the harness before blaming the product.** See `learning-harness` (separate observation from hypothesis).
   Concretely: data seeded, flag took effect, same harness at a tiny size. Say "I don't know yet" over a guess.
6. **Check what a delegate did to the tree** before trusting its green (see `verification-before-completion`, "Agent
   delegation"). One delegate "fixed" a test by moving an untracked build directory out of the worktree.
7. **Report** pass/fail counts, the load at run time, the clean-main comparison, which failures were flakes (with the
   reruns that showed it), and what was not run.

## Evidence (source: `~/.kiro/crew/workspace/learning-log.md`, append-only; dates and titles, line numbers as of 2026-10-13)

| Step | Source |
|---|---|
| 1, 3, 6 | 2026-10-12 "Qoder ACP": hand-picked batch missed 16 regressions (l.695); full suite 173,494 tests, 17 failed on main too, 9 load flakes passed alone (l.694); agent moved `website/dist` (l.695, the later entry puts the real symlink at `src/kiro_crew/static/dist`) |
| 1 | 2026-10-13 "เปิด PR Qoder": another session's simulator work pushed load to ~300, suite 3x slower; `/tmp` files deleted mid-task (l.718) |
| 2 | Claude memory `feedback_test_runner_verdict`: runner printed "ALL TESTS PASSED" over a failed UI test and over a crash restart; its rule has the third outcome "NO RESULT" |
| 3 | l.720: "ก่อนโทษ branch ให้เทียบกับ main สะอาดโดยใช้เงื่อนไขเดียวกัน" (with the dist-symlink location as the example of a hidden condition) |
| 4 | l.718: batched heavy files gave 59 false failures; 2026-10-13 "xc-test.sh" (l.714): SchemaMigration failed in the full run, passed alone 3/3, "น่าจะ flake ภายใต้โหลด" (hedged, so the skill says "likely") |
| 5 | Claude memory `feedback_verify_harness_before_reporting`: unseeded harness reported as a perf finding, retracted |

Also in Claude memory: `feedback_run_full_suite_before_green`, which also records that a cheap agent running a wide
test set independently caught regressions the lead's batch missed.

## Candidate conditions (per `learning-harness`)

- **Applies when:** a multi-minute or multi-file run decides whether work is reported green.
- **Does not apply when:** the project defines a stricter verdict contract (use that), or the run is a tiny local check.
- **Falsifier:** if steps 3-4 reclassify nothing across several consecutive PRs, the extra cost is not paying off;
  fold step 2 into `verification-before-completion` and drop the rest.
- **Limits:** evidence comes from two stacks (pytest/xdist on KiroCrew, xcodebuild on Apple apps). The pytest signals
  above are standard pytest behaviour, not yet exercised in a logged incident. The `TEST EXECUTE` variant, the
  retry behaviour and Swift Testing output were not verified against a real run. Other stacks are not covered.
  Occurrence counts came from keyword search of Lesson lines and may be incomplete.
