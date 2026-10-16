# verify-handoff

A small Bash 3.2-compatible verifier for agent handoffs. It checks claims against Git and on-disk evidence; it only reads Git state and never modifies a repository.

## Usage

```sh
tools/verify-handoff/verify-handoff.sh \
  --worktree /path/to/worktree \
  --base origin/main \
  --max-lines 150 \
  --scope 'tools/verify-handoff/*' \
  --claimed-file tools/verify-handoff/verify-handoff.sh \
  --claimed-text 'tools/verify-handoff/README.md:verify-handoff' \
  --cmd 'bash tools/verify-handoff/test-verify-handoff.sh' \
  --full-cmd 'bash tools/verify-handoff/test-verify-handoff.sh' \
  --log-dir /tmp/verify-handoff-logs
```

Repeatable options: `--scope`, `--claimed-file`, `--claimed-text`, `--cmd`, and `--full-cmd`. At least one command is required. `--cmd` and `--full-cmd` are trusted lead input and are executed with `bash -c`; do not pass untrusted strings.

These repeatable values are delimited by option occurrence, not by embedded newlines. A value containing a literal newline is invalid usage and exits `2`.

The verifier prints one PASS/WARN/FAIL line per check, writes combined command output to a per-command log, and shows only that log path plus its last five lines. The final line is `SUMMARY: <n> pass, <n> warn, <n> fail`.

## Failure modes targeted

1. Handoff claims that do not match files or fixed text actually on disk.
2. Hand-picked commands that do not prove the full suite passed.
3. Test/build runners that exit zero while printing known failure verdicts.

## Checks and policy

- `SIZE`: added plus deleted lines and untracked-file lines must not exceed `--max-lines` (default 150).
- `SCOPE`: every changed/untracked path must match one `--scope` glob; omitted scopes produce WARN.
- `CLAIMED FILE` / `CLAIMED TEXT`: claims must be visible in the changed/untracked set or worktree files.
- `COMMAND`: command exit status is checked, and known failure phrases are checked even when status is zero.
- `COMMAND` zero tests: output containing `Ran 0 tests`, `collected 0 items`, `no tests ran`, or `No test files found` is FAIL, even when status is zero.
- `COMMAND` checked nothing: zero-exit output with `(0 changed file` or ` 0 files changed` and no failure phrase is WARN instead of PASS.
- `FULL SUITE`: absent `--full-cmd` warns; `--require-full` promotes that warning to FAIL.

## Exit codes

- `0`: no FAIL; WARN is allowed.
- `1`: at least one FAIL, or the worktree/base could not be inspected.
- `2`: invalid usage.
