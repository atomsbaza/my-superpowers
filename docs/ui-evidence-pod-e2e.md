# Taking UI evidence for a KiroCrew PR with pod-e2e

This is a practical how-to for producing screenshots of a UI change in a KiroCrew worktree. It covers the steps and the mistakes we made on a real run (2026-10-16). It is not the reference: the authoritative harness docs are the repo's pod-e2e SKILL.md and `docs/guides/worktree-verification-recipes.md`.

## When to use

Use this when you changed UI under `website/` and the PR needs screenshots that show the change working. In `<worktree-name>` below, use the name of your worktree.

The pod is an isolated gateway with its own home and port. Booting it does not touch the live gateway.

Who runs what: a sandbox that blocks loopback (Codex, for example) cannot reach the pod. The lead runs the harness. The agent can write the spec offline.

## Steps

1. Boot an isolated pod for the worktree:

   ```bash
   kirocrew pod up <worktree-name> --provision --seed sessions-a-few --json
   ```

   `--provision` builds the worktree venv and the SPA dist. It skips `npm ci` when `website/node_modules` already exists. Without `--provision`, pod up refuses with "no built dist" when `src/kiro_crew/static/dist` is missing. The JSON handle it prints includes the port (for example 7969). To list the available seeds, run `kirocrew pod scenarios`.

2. Write the feature-specific spec. Both files are untracked. Create `.pod-test.sh` in the worktree root containing:

   ```bash
   PLAYWRIGHT_SPEC=".pod-e2e/<worktree-name>.spec.py"
   ```

   Then write that spec under `.pod-e2e/`. It is plain Python, with no imports. These names are in scope: `page`, `context`, `base_url`, `token`, `artifact_dir`, `expect`, `expect_true` and `record(name, ok, detail)`. Each `record()` call writes a row to `verdict.jsonl`, and a failing row fails the run. The spec only runs after the smoke phase passes.

3. Run the harness from the worktree root. It needs a Playwright Python, set through `KIROCREW_PW_PY`:

   ```bash
   KIROCREW_PW_PY=<python of a venv with playwright==1.61.0> \
     bash src/kiro_crew/apps/builtins/dev_fleet/skills/pod-e2e/scripts/pod-e2e.sh <worktree-name> --keep
   ```

   The venv needs `playwright==1.61.0` and `playwright install chromium`. Keep it outside the repo. We used `~/Work/.qoder-pr-work/pw-venv`. `--keep` leaves an already-up pod running.

4. Read the results. Artifacts go to `~/.kirocrew-pods/.e2e-artifacts/<worktree-name>/`:
   - `verdict.jsonl`: the `record()` rows.
   - `playwright.log`: includes an accessibility snapshot at the point of failure.
   - `fe-smoke.png`, and `fe-spec-FAIL.png` when the spec fails.
   - The spec's own screenshots.

   Repeat steps 2 to 4 until the verdict and the images both show what you need.

## Gotchas

- **Do not guess selectors.** Our first run of a guessed spec failed because the seeded app lands directly on a seeded chat ("Pinned work"). Read the accessibility snapshot in `playwright.log` and take selectors and accessible names from it.
- **Wait before a menu screenshot.** A screenshot taken right after opening a menu caught it mid-animation: translucent, with text showing through. Wait until the menu's computed opacity is 1 and its bounding box is unchanged over two animation frames, then wait about 300 ms more.
- **Viewport.** The harness fixes the browser context at 1600x1000. A spec can call `page.set_viewport_size()`. We used 1440x900.
- **Order prefixes.** Name screenshots `01-`, `02-`, `03-` so the order in the PR is obvious.
- **Simulated states.** States that need a live agent, such as a workflow run, can be produced by stubbing the endpoint with `page.route(...)`. State this plainly in the PR as simulated data. Take the empty or "before" state from the real gateway, without a stub.
- **Look at every PNG.** Open each one and compare it with the assertion it supports. A green verdict with a stale or half-faded frame is not evidence.
- **Browser lock.** The Playwright MCP browser can be locked by a stale Chrome. The harness does not need it.

## Handing the images to the PR

- A fork PR cannot use `gh pr create --attach`: the upload returns 404.
- Show the images to the user first. Wait for explicit approval. Silence is not approval.
- After approval, the user drags the images into the PR description on the web.
- Do not commit media.
- The dashboard token (`kirocrew pod token <worktree-name>`) is a secret. Never paste it into docs or PRs.

## Clean up

1. Run `kirocrew pod down <worktree-name>`. It stops the pod and deletes its home. The screenshots live outside the pod, so they survive.
2. Delete the untracked `.pod-e2e/` directory and `.pod-test.sh`.
3. Confirm that `git status --porcelain` prints nothing.
