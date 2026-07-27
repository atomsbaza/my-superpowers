---
name: oss-contribute
description: End-to-end workflow for contributing to an open-source repository — from picking an issue to a merged-ready PR. Covers fork, codebase orientation, implementation, scrutinize, and PR.
---

# OSS Contribute

Guide the user through a complete open-source contribution: find something valuable to work on, understand the codebase, implement it well, and submit a PR that maintainers will actually want to merge.

## Step 1 — Orient

If the user hasn't provided a repo URL or issue number, ask:
> "Which repo and what kind of contribution — bug fix, tests, feature, docs?"

Then gather context **before touching any code**:

```bash
gh repo view <owner>/<repo>                        # description, stars, language
gh issue list --repo <owner>/<repo> --limit 20    # open issues
gh pr list --repo <owner>/<repo>                  # open PRs — avoid duplicate work
gh api repos/<owner>/<repo>/contents --jq '.[].name'  # top-level structure
```

Read the contributing guide if it exists (`CONTRIBUTING.md`, `CONTRIBUTING.rst`, `.github/CONTRIBUTING.md`). Note: code style, PR conventions, test requirements, CLA.

## Step 2 — Pick a target

Rank candidates by:
1. **Concrete gap with no open PR** — test coverage, a real bug with a reproduction, a missing edge case in the code
2. **Pure logic** — avoids platform/environment gaps (e.g. a macOS contributor can't run Windows-only UI tests)
3. **Small blast radius** — one file, one method, one test class
4. **Good fit for the stack** — play to what you know

Avoid: issues already claimed, features needing design discussion, anything blocked on external tooling you can't run.

State your chosen target as a one-sentence proposal and confirm with the user before implementing.

## Step 3 — Deep read

Read only what the target touches:
- The file(s) you'll change
- The test file(s) for those units
- The types/interfaces your code will use

Use `grep` and `find` rather than reading everything. Note the exact method signatures, naming conventions, and test helper patterns in use.

## Step 4 — Implement

Follow the project's existing style exactly — indent, naming, comment density, test structure.

Before writing any code:
- State your interpretation of what needs to change
- List the files you'll touch and why
- Surface any assumptions that could be wrong

Implement, then self-check:
- Does each assertion actually match what the real code path produces? Trace it explicitly.
- No Windows-only / platform-only code if the contributor is on a different platform — note this gap.
- No production code changes unless required — prefer the smallest scope that delivers value.

## Step 5 — Scrutinize

Run `/scrutinize` on the change before committing. Treat its findings seriously. Fix anything rated Major or above before moving on.

If the project has CI (`.github/workflows/`), note what it checks and whether your change would pass.

## Step 6 — Commit and PR

```bash
git checkout -b <type>/<short-slug>   # fix/, test/, feat/, docs/
git add <specific files>              # never git add -A
git commit -m "<concise message>"
git push -u origin <branch>
```

**Before opening the PR:** ask the user to review the diff locally. Do NOT open the PR automatically — let the user confirm.

PR body must include:
- What the change does (one paragraph)
- Why it matters (the gap it fills)
- Test plan (what the maintainer should run to verify)
- Note any platform limitations (e.g. "tests verified by trace only — targets net10.0-windows")

## Operating rules

- Never open a PR without explicit user approval.
- Never force-push to a repo you don't own.
- If the project has a CLA, flag it — the user must sign it.
- If an issue is already claimed by another contributor, say so and pick a different target.
- Zero findings from `/scrutinize` is the bar to clear before submitting.
