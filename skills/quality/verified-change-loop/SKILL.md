---
name: verified-change-loop
description: Use when a code change is handed to someone else (another agent, a subagent, a contractor) or before you accept a non-trivial change into a shared branch or pull request - defines the gates and the evidence each one needs (handoff check, design read, test discrimination, UI evidence, fork-PR realities, ledger), never who does the work
---

# Verified Change Loop

**Status: candidate (drafted 2026-10-16 from two real runs: a large upstream PR and a small upstream issue fix). Revisit after a few uses; see the falsifier at the end.**

This skill says what must be true before a change is accepted and what evidence shows it. It does not say who does the work, with which model, tool, pane or hook: the harness or the user decides that. "You" below is whoever is accountable for accepting the change.

Companions, not repeated here: `verification-before-completion` (evidence before claims), `test-verdict-triage` (reading a test verdict), `learning-harness` (analysing CI failures), `receiving-code-review` (handling reviewer or bot findings), `safe-pr-publish` (the push step), `tdd`.

## Gates

| # | Must be true | Evidence you hold |
|---|---|---|
| 1 Frame | Interpretation, acceptance criteria, files in and out of scope, and risks are written before work starts | A short written brief (see "Handing work to someone") |
| 2 Mechanical check | Claimed files really changed; diff within the size cap and the scope; every command exits 0 with no failure verdict in its output; more than zero tests ran; the full suite was named, not a hand-picked list | Output of `tools/verify-handoff/verify-handoff.sh` (in the my-superpowers repo) or the same checks by hand. A reply is a claim; your own run is evidence |
| 3 Read the real diff | Design is judged, not only tests: standing cost added (polling, listeners, extra requests), behaviour on a transient failure, ordering of the first event, reuse of an existing data source | Notes per question, with file:line |
| 4 Tests discriminate | Each new test fails on the pre-change source and passes with the change | Failing test names on the restored original file, plus `shasum` of the changed file before and after the swap (they must match) |
| 5 Independent look | Security, data loss, concurrency, migrations and money get a reviewer who is not the author | Their findings, each checked against the code before you act |
| 6 Visible evidence | For UI: every affected surface in its meaningful variants, each image opened and compared with the assertion it supports; simulated data is labelled as simulated | The images and the harness verdict; show them to the user and get explicit approval before attaching |
| 7 Integrate | The repository's own commit rules (count, title style, attribution) hold; the branch is rebased on a fresh base; relevant tests rerun on the rebased tree | Commit list and test output |
| 8 Publish | The user asked for the push or PR; the PR body follows the repository template; live state is read back afterwards (checks, comments, body renders) | `gh` output; see `safe-pr-publish` |
| 9 Record | One ledger line (below) | The line |

A green check that checked nothing is not green: `0 changed files`, `Ran 0 tests` and `collected 0 items` are findings, not passes.

## Handing work to someone (anyone)

The brief states: goal; files in and out of scope; acceptance criteria; design constraints (standing costs it must not add, behaviour on transient failure, timing of the first event, the existing source to reuse); the tests to write first and the exact commands; stop conditions (a size cap, anything unclear, missing evidence); "no git writes, no push" when that applies.

The reply must contain: changed files; commands with real output; for each new test the names that fail on the pre-change file, with `shasum` before and after; what was not run; remaining risks. Verify it, do not relay it.

Running `verify-handoff` with `--scope` needs one workspace per author: two authors sharing one tree make each other's scope fail. Cap the rounds (three is a sensible default); after the cap, report to the user instead of a fourth identical round.

## After a push to a fork

- Workflows may wait for a maintainer to approve them, so "run until green" is bounded. A readiness check that says "awaiting maintainer approval" is not a code failure.
- Review bots update their comments in place for each head. Check which head SHA a comment reviewed before acting on it.
- A fork PR cannot attach media from the CLI. The user drags files into the description; do not commit media to the branch.
- Before blaming the base branch for a failure, rerun on a clean worktree at the base. A git-ignored build directory in your own tree has caused false blame.
- List the user-visible surfaces from the diff before taking screenshots, not after a bot asks for them. For KiroCrew, `docs/ui-evidence-pod-e2e.md` in my-superpowers has the procedure.
- Rebase, never merge the base in. Mark the PR ready only when the user says so.

## Meta loop

- One ledger line per finished task: `date | project | task | author | rounds | escalated | lead_fixes | gate_miss`. The file lives where the project's `AGENTS.md` says. Counts and one-line causes only; no secrets, no personal data.
- A `gate_miss` or failure that repeats twice becomes a script check, a test or a written constraint, not more prose (`principle-encode-lessons-in-structure`).
- A periodic sweep over the ledger and failure notes may propose changes; the user approves them. Some schedulers expire recurring jobs: check that the job still exists.

## Pitfalls seen in real runs

- A guard run with an unsplit file list ran zero tests but looked green.
- The named "full suite" left out a directory.
- A doc table lost cells in a rebase: compare cell counts per row against the base.
- A UI spec with guessed selectors failed; read the accessibility snapshot from the first failing run instead. Wait for menu animations to settle before a screenshot.
- A new always-on poll was added to decide one menu row; the existing data source and an event were enough.

## Falsifier

If after three uses the ledger shows no fall in repeated `gate_miss` causes or in rounds to acceptance, or the skill is not loaded when the situation arises, shorten it or delete it.
