#!/usr/bin/env bash
# Test harness for tools/verify-handoff/verify-handoff.sh.
set -u

TOOL_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOL="$TOOL_DIR/verify-handoff.sh"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/verify-handoff-tests.XXXXXX")"
FAILURES=0
TESTS=0

trap 'rm -rf "$TMP_ROOT"' EXIT

fail() {
  printf 'not ok %s: %s\n' "$TESTS" "$1"
  FAILURES=$((FAILURES + 1))
}

pass() {
  printf 'ok %s: %s\n' "$TESTS" "$1"
}

assert_output_contains() {
  local output="$1"
  local needle="$2"
  local reason="$3"
  TESTS=$((TESTS + 1))
  case "$output" in
    *"$needle"*)
      pass "$reason"
      ;;
    *)
      fail "$reason (missing: $needle)"
      ;;
  esac
}

assert_output_lacks() {
  local output="$1"
  local needle="$2"
  local reason="$3"
  TESTS=$((TESTS + 1))
  case "$output" in
    *"$needle"*)
      fail "$reason (unexpected: $needle)"
      ;;
    *)
      pass "$reason"
      ;;
  esac
}

assert_equal() {
  local expected="$1"
  local actual="$2"
  local reason="$3"
  TESTS=$((TESTS + 1))
  if [ "$expected" = "$actual" ]; then
    pass "$reason"
  else
    fail "$reason (expected: $expected, actual: $actual)"
  fi
}

make_repo() {
  local repo="$1"
  mkdir -p "$repo/src" "$repo/other"
  cd "$repo" || return 1
  git init -q
  git config user.name 'Verify Handoff Tests'
  git config user.email 'verify-handoff-tests@example.invalid'
  printf 'original\n' > src/a.txt
  printf 'other original\n' > other/a.txt
  git add src/a.txt other/a.txt
  git commit -q -m base
  git rev-parse HEAD
}

run_tool() {
  local repo="$1"
  shift
  (
    cd "$repo" || exit 99
    bash "$TOOL" "$@"
  ) 2>&1
}

# Keep this file and its implementation adjacent for easier review.
if [ ! -x "$TOOL" ]; then
  echo "FATAL: executable tool not found: $TOOL" >&2
  exit 1
fi

# 1. Every expected check passes.
repo="$TMP_ROOT/all-pass"
base="$(make_repo "$repo")" || { echo "FATAL: could not create all-pass repo" >&2; exit 1; }
printf 'original\nchanged\n' > "$repo/src/a.txt"
printf 'marker\n' > "$repo/src/marker.txt"
output="$(run_tool "$repo" \
  --worktree "$repo" --base "$base" --max-lines 10 --scope 'src/*' \
  --claimed-file src/a.txt --claimed-file src/marker.txt \
  --claimed-text 'src/marker.txt:marker' \
  --cmd 'true' --full-cmd 'true')"
assert_equal 0 "$?" 'all-pass invocation succeeds'
TESTS=$((TESTS + 1))
summary_line="$(printf '%s\n' "$output" | tail -n 1)"
assert_equal 'SUMMARY: 6 pass, 0 warn, 0 fail' "$summary_line" 'all-pass summary is exactly six passes'
assert_output_contains "$output" 'SIZE: PASS' 'all-pass checks size'
assert_output_contains "$output" 'SCOPE: PASS' 'all-pass checks scope'
assert_output_contains "$output" 'CLAIMED FILE: PASS' 'all-pass checks claimed files'
assert_output_contains "$output" 'CLAIMED TEXT: PASS' 'all-pass checks claimed text'
assert_output_contains "$output" 'COMMAND: PASS' 'all-pass checks command'
assert_output_contains "$output" 'FULL SUITE: PASS' 'all-pass checks full suite'

# 2. Changed lines above --max-lines fail.
repo="$TMP_ROOT/oversize"
base="$(make_repo "$repo")" || { echo "FATAL: could not create oversize repo" >&2; exit 1; }
seq 1 151 > "$repo/src/a.txt"
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --max-lines 150 --cmd 'true' --full-cmd 'true')"
assert_equal 1 "$?" 'oversize invocation fails'
TESTS=$((TESTS + 1))
case "$output" in
  *'SIZE: FAIL'*) pass 'oversize diff reports size failure' ;;
  *) fail 'oversize diff reports size failure' ;;
esac
assert_output_contains "$output" 'SUMMARY:' 'oversize result has summary'

# 3. A changed path outside all scope globs fails.
repo="$TMP_ROOT/out-of-scope"
base="$(make_repo "$repo")" || { echo "FATAL: could not create out-of-scope repo" >&2; exit 1; }
printf 'changed\n' > "$repo/other/a.txt"
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --scope 'src/*' --cmd 'true' --full-cmd 'true')"
assert_equal 1 "$?" 'out-of-scope invocation fails'
assert_output_contains "$output" 'SCOPE: FAIL' 'out-of-scope file is reported'
assert_output_lacks "$output" 'SCOPE: PASS' 'out-of-scope result has no scope pass'

# 4. Claiming an unchanged tracked file fails.
repo="$TMP_ROOT/claimed-file"
base="$(make_repo "$repo")" || { echo "FATAL: could not create claimed-file repo" >&2; exit 1; }
printf 'changed\n' > "$repo/src/a.txt"
output="$(run_tool "$repo" --worktree "$repo" --base "$base" \
  --claimed-file other/a.txt --cmd 'true' --full-cmd 'true')"
assert_equal 1 "$?" 'unchanged claim invocation fails'
assert_output_contains "$output" 'claimed but unchanged on disk' 'unchanged claimed file is reported'

# 5. Missing fixed claimed text fails even when the file changed.
repo="$TMP_ROOT/claimed-text"
base="$(make_repo "$repo")" || { echo "FATAL: could not create claimed-text repo" >&2; exit 1; }
printf 'changed but no marker\n' > "$repo/src/a.txt"
output="$(run_tool "$repo" --worktree "$repo" --base "$base" \
  --claimed-text 'src/a.txt:FIXED_MARKER' --cmd 'true' --full-cmd 'true')"
assert_equal 1 "$?" 'missing claimed text invocation fails'
assert_output_contains "$output" 'CLAIMED TEXT: FAIL' 'missing claimed text is reported'

# 6. A non-zero command fails without dumping its output.
repo="$TMP_ROOT/cmd-nonzero"
base="$(make_repo "$repo")" || { echo "FATAL: could not create cmd-nonzero repo" >&2; exit 1; }
# shellcheck disable=SC2016  # The loop variable must expand in the tested command.
output="$(run_tool "$repo" --worktree "$repo" --base "$base" \
  --cmd 'echo command-secret; for i in 1 2 3 4 5 6 7 8; do echo fill-line-$i; done; exit 7' \
  --full-cmd 'true')"
assert_equal 1 "$?" 'non-zero command invocation fails'
assert_output_contains "$output" 'COMMAND: FAIL' 'non-zero command is reported'
assert_output_lacks "$output" 'command-secret' 'command output is not printed directly'

# 7. A zero-exit command containing a known failure verdict also fails.
repo="$TMP_ROOT/cmd-hidden-failure"
base="$(make_repo "$repo")" || { echo "FATAL: could not create hidden-failure repo" >&2; exit 1; }
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd 'echo TEST FAILED' --full-cmd 'true')"
assert_equal 1 "$?" 'hidden command failure invocation fails'
assert_output_contains "$output" 'COMMAND: FAIL' 'hidden command failure is reported'
assert_output_contains "$output" 'TEST FAILED' 'matched failure pattern is identified'

# 8. Missing every command is a usage error.
repo="$TMP_ROOT/no-command"
base="$(make_repo "$repo")" || { echo "FATAL: could not create no-command repo" >&2; exit 1; }
output="$(run_tool "$repo" --worktree "$repo" --base "$base")"
assert_equal 2 "$?" 'no command exits 2'
assert_output_contains "$output" 'Usage:' 'no command prints usage'

# 9. Missing --full-cmd warns by default and fails with --require-full.
repo="$TMP_ROOT/full-suite"
base="$(make_repo "$repo")" || { echo "FATAL: could not create full-suite repo" >&2; exit 1; }
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd 'true')"
assert_equal 0 "$?" 'missing full suite still exits zero'
assert_output_contains "$output" 'FULL SUITE: WARN' 'missing full suite warns'
assert_output_contains "$output" 'full suite not run: hand-picked commands only' 'missing full suite reason is printed'
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd 'true' --require-full)"
assert_equal 1 "$?" 'require-full with no full command fails'
assert_output_contains "$output" 'FULL SUITE: FAIL' 'required missing full suite fails'

# 10. Untracked files participate in size and scope checks.
repo="$TMP_ROOT/untracked"
base="$(make_repo "$repo")" || { echo "FATAL: could not create untracked repo" >&2; exit 1; }
mkdir -p "$repo/new"
printf 'one\ntwo\nthree\n' > "$repo/new/untracked.txt"
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --max-lines 2 --scope 'new/*' --cmd 'true' --full-cmd 'true')"
assert_equal 1 "$?" 'oversized untracked invocation fails'
assert_output_contains "$output" 'SIZE: FAIL' 'untracked lines count toward size'
assert_output_contains "$output" 'SCOPE: PASS' 'untracked path is checked against scope'

# 11. A found claimed file returns from path_in_set without leaking newline IFS.
repo="$TMP_ROOT/ifs-regression"
base="$(make_repo "$repo")" || { echo "FATAL: could not create IFS repo" >&2; exit 1; }
printf 'changed\n' > "$repo/src/a.txt"
output="$(run_tool "$repo" \
  --worktree "$repo" --base "$base" --scope 'src/*' \
  --claimed-file src/a.txt \
  --cmd "printf '%s|' a b c" \
  --full-cmd 'true')"
assert_equal 0 "$?" 'IFS regression invocation succeeds'
assert_output_contains "$output" 'CLAIMED FILE: PASS' 'found claimed file is reported'
assert_output_contains "$output" 'SCOPE: PASS' 'scope check also completes in IFS regression'
assert_output_contains "$output" 'COMMAND: PASS' 'IFS regression command is reported'
command_line="$(printf '%s\n' "$output" | grep 'COMMAND: PASS exit=0 log=' | head -n 1)"
TESTS=$((TESTS + 1))
case "$command_line" in
  'COMMAND: PASS exit=0 log='*'')
    command_log=${command_line#'COMMAND: PASS exit=0 log='}
    pass 'IFS regression exposes the command log path'
    ;;
  *)
    fail 'IFS regression exposes the command log path'
    ;;
esac
TESTS=$((TESTS + 1))
if [ -n "${command_log-}" ] && [ -f "$command_log" ]; then
  command_output="$(cat "$command_log")"
else
  command_output='<missing command log>'
fi
assert_equal 'a|b|c|' "$command_output" 'command output proves IFS was not corrupted'

# 12. Literal newlines in repeatable values are rejected rather than silently split.
repo="$TMP_ROOT/newline-option"
base="$(make_repo "$repo")" || { echo "FATAL: could not create newline repo" >&2; exit 1; }
newline_value="$(printf 'true\ntrue')"
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd "$newline_value")"
assert_equal 2 "$?" 'newline command value exits 2'
assert_output_contains "$output" 'Usage error: --cmd value contains a newline' \
  'newline command value names --cmd'

# 13. Scope globs must remain literal even when they match directories in the caller cwd.
repo="$TMP_ROOT/cwd-glob"
base="$(make_repo "$repo")" || { echo "FATAL: could not create cwd-glob repo" >&2; exit 1; }
mkdir -p "$repo/src/sub"
printf 'new\n' > "$repo/src/sub/new.txt"
output="$(run_tool "$repo" \
  --worktree "$repo" --base "$base" --scope 'src/*' \
  --cmd 'true' --full-cmd 'true')"
assert_equal 0 "$?" 'scope glob is not expanded against caller cwd'
assert_output_contains "$output" 'SCOPE: PASS' 'nested changed path matches literal scope glob'

# 14. Changed paths containing glob metacharacters must not undergo pathname expansion.
repo="$TMP_ROOT/literal-glob-path"
base="$(make_repo "$repo")" || { echo "FATAL: could not create literal-glob repo" >&2; exit 1; }
mkdir -p "$repo/src/literal"
printf 'literal\n' > "$repo/src/literal/a*b"
output="$(run_tool "$repo" \
  --worktree "$repo" --base "$base" --scope 'src/*' \
  --cmd 'true' --full-cmd 'true')"
assert_equal 0 "$?" 'literal glob-metacharacter path passes scope'
assert_output_contains "$output" 'SCOPE: PASS' 'literal glob-metacharacter path is preserved'

# 15. Zero-test output fails even when the command exits zero.
repo="$TMP_ROOT/zero-tests"
base="$(make_repo "$repo")" || { echo "FATAL: could not create zero-tests repo" >&2; exit 1; }
for zero_text in 'Ran 0 tests' 'collected 0 items' 'no tests ran' 'No test files found'; do
  output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd "echo '$zero_text'" --full-cmd 'true')"
  assert_equal 1 "$?" "zero-test output '$zero_text' fails the invocation"
  assert_output_contains "$output" "COMMAND: FAIL" "zero-test output '$zero_text' is reported as COMMAND failure"
  assert_output_contains "$output" "ran zero tests: $zero_text" "zero-test output '$zero_text' names the pattern"
done

# 16. A non-zero exit with zero-test output is one FAIL record, reported by its exit code.
repo="$TMP_ROOT/zero-tests-nonzero"
base="$(make_repo "$repo")" || { echo "FATAL: could not create zero-tests-nonzero repo" >&2; exit 1; }
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd "echo 'Ran 0 tests'; exit 3" --full-cmd 'true')"
assert_equal 1 "$?" 'non-zero zero-test command fails the invocation'
assert_output_contains "$output" 'COMMAND: FAIL exit=3 log=' 'non-zero zero-test command reports its exit code'
assert_equal 1 "$(printf '%s\n' "$output" | grep -c '^COMMAND: ')" 'non-zero zero-test command has one COMMAND record'

# 17. Zero-exit output that shows nothing was checked warns instead of passing.
repo="$TMP_ROOT/vacuous"
base="$(make_repo "$repo")" || { echo "FATAL: could not create vacuous repo" >&2; exit 1; }
for vacuous_text in '(0 changed file' ' 0 files changed'; do
  output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd "echo 'x$vacuous_text'" --full-cmd 'true')"
  assert_equal 0 "$?" "vacuous output '$vacuous_text' still exits zero"
  assert_output_contains "$output" 'COMMAND: WARN' "vacuous output '$vacuous_text' is reported as COMMAND warning"
  assert_output_contains "$output" "possibly vacuous: the command checked nothing ($vacuous_text)" "vacuous output '$vacuous_text' names the pattern"
  assert_equal 1 "$(printf '%s\n' "$output" | grep -c '^COMMAND: ')" "vacuous output '$vacuous_text' has one COMMAND record"
done

# 18. A zero-test full command fails the full-suite check.
repo="$TMP_ROOT/zero-tests-full"
base="$(make_repo "$repo")" || { echo "FATAL: could not create zero-tests-full repo" >&2; exit 1; }
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd 'true' --full-cmd "echo 'Ran 0 tests'")"
assert_equal 1 "$?" 'zero-test full command fails the invocation'
assert_output_contains "$output" 'FULL SUITE: FAIL' 'zero-test full command is reported as full-suite failure'
assert_output_contains "$output" 'ran zero tests: Ran 0 tests' 'zero-test full command names the pattern'

# 19. Ordinary command output still passes.
repo="$TMP_ROOT/ordinary-output"
base="$(make_repo "$repo")" || { echo "FATAL: could not create ordinary-output repo" >&2; exit 1; }
output="$(run_tool "$repo" --worktree "$repo" --base "$base" --cmd "echo 'Ran 12 tests'" --full-cmd 'true')"
assert_equal 0 "$?" 'ordinary command output succeeds'
assert_output_contains "$output" 'COMMAND: PASS' 'ordinary command output is still PASS'
assert_output_lacks "$output" 'COMMAND: WARN' 'ordinary command output has no command warning'

printf '\nTest summary: %d assertions, %d failures\n' "$TESTS" "$FAILURES"
if [ "$FAILURES" -ne 0 ]; then
  exit 1
fi
exit 0
