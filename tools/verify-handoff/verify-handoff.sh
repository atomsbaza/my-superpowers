#!/usr/bin/env bash
# Mechanically compare a handoff's claims with a worktree's actual contents.
# This tool reads Git state; it never stages, commits, checks out, or stashes.
set -u

usage() {
  cat <<'USAGE'
Usage:
  verify-handoff.sh --worktree <path> --base <ref> \
    [--max-lines N] [--scope <glob> ...] \
    [--claimed-file <path> ...] [--claimed-text <path>:<fixed-string> ...] \
    [--cmd "<shell command>" ...] [--full-cmd "<shell command>"] \
    [--require-full] [--log-dir <dir>]

Verify a handoff against changed/untracked content in a Git worktree.
The tool reads Git state only; it does not mutate the repository.

Options:
  --worktree PATH       Existing Git worktree to inspect (required).
  --base REF            Git ref used to calculate changes (required).
  --max-lines N         Maximum combined added+deleted+untracked lines (default 150).
  --scope GLOB          Repeatable shell-style path pattern; changed paths must match one.
  --claimed-file PATH   Repeatable path that must be changed or untracked.
  --claimed-text SPEC   Repeatable PATH:FIXED-STRING checked with grep -F. The path may
                        not contain a colon; the fixed string may.
  --cmd COMMAND         Repeatable trusted shell command run with bash -c in --worktree.
  --full-cmd COMMAND    Trusted complete-suite command, run like --cmd.
  --require-full        Treat a missing --full-cmd as FAIL instead of WARN.
  --log-dir DIR         Directory for combined command logs (default: private mktemp dir).

Security note: --cmd and --full-cmd are trusted lead input and are run via
`bash -c`; do not pass untrusted text in either option.

Exit codes:
  0  no FAIL (WARN is allowed)
  1  at least one FAIL or inability to inspect the worktree/base
  2  invalid usage

Checks:
  SIZE          Combined changed and untracked line count.
  SCOPE         Every changed/untracked path matches at least one scope glob.
  CLAIMED FILE  Claimed files really changed or are untracked.
  CLAIMED TEXT  Claimed fixed strings exist in files on disk.
  COMMAND       Commands have exit 0 and no known hidden failure verdict.
  FULL SUITE    Full command ran; otherwise WARN, or FAIL with --require-full.
USAGE
}

usage_error() {
  printf 'Usage error: %s\n\n' "$1" >&2
  usage >&2
  exit 2
}

reject_newline() {
  local option_name="$1"
  local option_value="$2"
  case "$option_value" in
    *"$NEWLINE"*)
      usage_error "$option_name value contains a newline"
      ;;
  esac
}

fatal_check() {
  printf 'SETUP: FAIL %s\n' "$1"
  printf 'SUMMARY: 0 pass, 0 warn, 1 fail\n'
  exit 1
}

WORKTREE=
BASE=
MAX_LINES=150
REQUIRE_FULL=0
LOG_DIR=
SCOPE_GLOBS=()
CLAIMED_FILES=
CLAIMED_TEXTS=
COMMANDS=
FULL_COMMANDS=
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0
NEWLINE='
'

while [ $# -gt 0 ]; do
  case "$1" in
    --worktree)
      [ $# -ge 2 ] || usage_error '--worktree requires a path'
      WORKTREE=$2
      shift 2
      ;;
    --base)
      [ $# -ge 2 ] || usage_error '--base requires a ref'
      BASE=$2
      shift 2
      ;;
    --max-lines)
      [ $# -ge 2 ] || usage_error '--max-lines requires a number'
      case "$2" in
        ''|*[!0-9]*) usage_error "--max-lines must be a non-negative integer: $2" ;;
      esac
      MAX_LINES=$2
      shift 2
      ;;
    --scope)
      [ $# -ge 2 ] || usage_error '--scope requires a glob'
      reject_newline '--scope' "$2"
      if [ "${#SCOPE_GLOBS[@]}" -eq 0 ]; then
        SCOPE_GLOBS=("$2")
      else
        SCOPE_GLOBS=("${SCOPE_GLOBS[@]}" "$2")
      fi
      shift 2
      ;;
    --claimed-file)
      [ $# -ge 2 ] || usage_error '--claimed-file requires a path'
      reject_newline '--claimed-file' "$2"
      CLAIMED_FILES="${CLAIMED_FILES:+$CLAIMED_FILES$NEWLINE}$2"
      shift 2
      ;;
    --claimed-text)
      [ $# -ge 2 ] || usage_error '--claimed-text requires path:fixed-string'
      reject_newline '--claimed-text' "$2"
      CLAIMED_TEXTS="${CLAIMED_TEXTS:+$CLAIMED_TEXTS$NEWLINE}$2"
      shift 2
      ;;
    --cmd)
      [ $# -ge 2 ] || usage_error '--cmd requires a shell command'
      reject_newline '--cmd' "$2"
      COMMANDS="${COMMANDS:+$COMMANDS$NEWLINE}$2"
      shift 2
      ;;
    --full-cmd)
      [ $# -ge 2 ] || usage_error '--full-cmd requires a shell command'
      reject_newline '--full-cmd' "$2"
      FULL_COMMANDS="${FULL_COMMANDS:+$FULL_COMMANDS$NEWLINE}$2"
      shift 2
      ;;
    --require-full)
      REQUIRE_FULL=1
      shift
      ;;
    --log-dir)
      [ $# -ge 2 ] || usage_error '--log-dir requires a directory'
      LOG_DIR=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage_error "unknown argument: $1"
      ;;
  esac
done

[ -n "$WORKTREE" ] || usage_error '--worktree is required'
[ -n "$BASE" ] || usage_error '--base is required'
if [ -z "$COMMANDS" ] && [ -z "$FULL_COMMANDS" ]; then
  usage_error 'at least one --cmd or --full-cmd is required'
fi

if [ ! -d "$WORKTREE" ]; then
  fatal_check "worktree is not a directory: $WORKTREE"
fi
if ! git -C "$WORKTREE" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fatal_check "not a Git worktree: $WORKTREE"
fi
if ! git -C "$WORKTREE" rev-parse --verify --quiet "${BASE}^{commit}" >/dev/null 2>&1; then
  fatal_check "base is not a resolvable commit: $BASE"
fi

DATA_DIR="$(mktemp -d "${TMPDIR:-/tmp}/verify-handoff-data.XXXXXX")"
trap 'rm -r -- "$DATA_DIR"' EXIT

if [ -n "$LOG_DIR" ]; then
  if ! mkdir -p "$LOG_DIR" 2>/dev/null; then
    fatal_check "cannot create log directory: $LOG_DIR"
  fi
  LOG_ROOT=$LOG_DIR
else
  LOG_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/verify-handoff-logs.XXXXXX")"
fi

add_path() {
  local candidate="$1"
  local existing
  local existing_index=0
  while [ "$existing_index" -lt "${#CHANGED_PATHS[@]}" ]; do
    existing=${CHANGED_PATHS[$existing_index]}
    if [ "$existing" = "$candidate" ]; then
      return 0
    fi
    existing_index=$((existing_index + 1))
  done
  if [ "${#CHANGED_PATHS[@]}" -eq 0 ]; then
    CHANGED_PATHS=("$candidate")
  else
    CHANGED_PATHS=("${CHANGED_PATHS[@]}" "$candidate")
  fi
}

path_in_set() {
  local needle="$1"
  local candidate
  local candidate_index=0
  while [ "$candidate_index" -lt "${#CHANGED_PATHS[@]}" ]; do
    candidate=${CHANGED_PATHS[$candidate_index]}
    if [ "$candidate" = "$needle" ]; then
      return 0
    fi
    candidate_index=$((candidate_index + 1))
  done
  return 1
}

record() {
  local verdict="$1"
  local label="$2"
  local reason="$3"
  case "$verdict" in
    PASS) PASS_COUNT=$((PASS_COUNT + 1)) ;;
    WARN) WARN_COUNT=$((WARN_COUNT + 1)) ;;
    FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
  esac
  printf '%s: %s %s\n' "$label" "$verdict" "$reason"
}

normalize_repo_path() {
  local input="$1"
  case "$input" in
    "$WORKTREE"/*)
      input="${input#"$WORKTREE"/}"
      ;;
    "$WORKTREE")
      input=.
      ;;
  esac
  printf '%s\n' "$input"
}

scan_scope() {
  local changed_path
  local scope_glob
  local changed_index=0
  local glob_index=0
  while [ "$changed_index" -lt "${#CHANGED_PATHS[@]}" ]; do
    changed_path=${CHANGED_PATHS[$changed_index]}
    changed_count=$((changed_count + 1))
    matched=0
    glob_index=0
    while [ "$glob_index" -lt "${#SCOPE_GLOBS[@]}" ]; do
      scope_glob=${SCOPE_GLOBS[$glob_index]}
      # This case intentionally interprets the caller glob.
      # shellcheck disable=SC2254
      case "$changed_path" in
        $scope_glob)
          matched=1
          break
          ;;
      esac
      glob_index=$((glob_index + 1))
    done
    if [ "$matched" -eq 0 ]; then
      if [ -n "$unmatched" ]; then
        unmatched="$unmatched, $changed_path"
      else
        unmatched=$changed_path
      fi
    fi
    changed_index=$((changed_index + 1))
  done
}

if ! git -C "$WORKTREE" diff --numstat --no-renames "$BASE" -- >"$DATA_DIR/numstat" 2>/dev/null; then
  fatal_check 'could not calculate git diff'
fi
if ! git -C "$WORKTREE" ls-files --others --exclude-standard >"$DATA_DIR/untracked" 2>/dev/null; then
  fatal_check 'could not list untracked files'
fi

CHANGED_PATHS=()
CHANGED_LINES=0
while IFS="$(printf '\t')" read -r added deleted path; do
  [ -n "$path" ] || continue
  add_path "$path"
  case "$added$deleted" in
    ''|*[!0-9]*) : ;;
    *) CHANGED_LINES=$((CHANGED_LINES + added + deleted)) ;;
  esac
done <"$DATA_DIR/numstat"

while IFS= read -r untracked_path; do
  [ -n "$untracked_path" ] || continue
  add_path "$untracked_path"
  untracked_lines="$(awk 'END { print NR }' "$WORKTREE/$untracked_path" 2>/dev/null)" || untracked_lines=0
  case "$untracked_lines" in
    ''|*[!0-9]*) untracked_lines=0 ;;
    *) CHANGED_LINES=$((CHANGED_LINES + untracked_lines)) ;;
  esac
done <"$DATA_DIR/untracked"

if [ "$CHANGED_LINES" -le "$MAX_LINES" ]; then
  record PASS SIZE "changed-lines=$CHANGED_LINES <= max-lines=$MAX_LINES"
else
  record FAIL SIZE "changed-lines=$CHANGED_LINES > max-lines=$MAX_LINES"
fi

if [ "${#SCOPE_GLOBS[@]}" -eq 0 ]; then
  record WARN SCOPE 'skipped: no --scope globs were given'
else
  unmatched=
  changed_count=0
  scan_scope
  if [ -n "$unmatched" ]; then
    record FAIL SCOPE "paths outside scope: $unmatched"
  else
    record PASS SCOPE "all $changed_count changed paths match a scope glob"
  fi
fi

if [ -n "$CLAIMED_FILES" ]; then
  unchanged_claims=
  while IFS= read -r claimed_file; do
    [ -n "$claimed_file" ] || continue
    claimed_file="$(normalize_repo_path "$claimed_file")"
    if ! path_in_set "$claimed_file"; then
      if [ -n "$unchanged_claims" ]; then
        unchanged_claims="$unchanged_claims, $claimed_file"
      else
        unchanged_claims=$claimed_file
      fi
    fi
  done <<CLAIM_FILE_ITEMS
$CLAIMED_FILES
CLAIM_FILE_ITEMS
  if [ -n "$unchanged_claims" ]; then
    record FAIL 'CLAIMED FILE' "claimed but unchanged on disk: $unchanged_claims"
  else
    record PASS 'CLAIMED FILE' 'all claimed files are changed or untracked'
  fi
else
  record WARN 'CLAIMED FILE' 'skipped: no claimed files were given'
fi

if [ -n "$CLAIMED_TEXTS" ]; then
  missing_texts=
  while IFS= read -r claimed_text; do
    [ -n "$claimed_text" ] || continue
    case "$claimed_text" in
      *:*)
        text_path=${claimed_text%%:*}
        fixed_text=${claimed_text#*:}
        ;;
      *)
        if [ -n "$missing_texts" ]; then
          missing_texts="$missing_texts; malformed $claimed_text"
        else
          missing_texts="malformed $claimed_text"
        fi
        continue
        ;;
    esac
    text_path="$(normalize_repo_path "$text_path")"
    if [ ! -f "$WORKTREE/$text_path" ] || ! grep -Fq -- "$fixed_text" "$WORKTREE/$text_path"; then
      if [ -n "$missing_texts" ]; then
        missing_texts="$missing_texts; $text_path"
      else
        missing_texts=$text_path
      fi
    fi
  done <<CLAIM_TEXT_ITEMS
$CLAIMED_TEXTS
CLAIM_TEXT_ITEMS
  if [ -n "$missing_texts" ]; then
    record FAIL 'CLAIMED TEXT' "claimed text missing on disk: $missing_texts"
  else
    record PASS 'CLAIMED TEXT' 'all claimed fixed strings exist on disk'
  fi
else
  record WARN 'CLAIMED TEXT' 'skipped: no claimed text was given'
fi

run_command() {
  local label="$1"
  local command_string="$2"
  local check_label="${3:-COMMAND}"
  local command_log="$LOG_ROOT/$label.log"
  local command_rc=0
  local matched_patterns=
  (
    cd "$WORKTREE" || exit 125
    bash -c "$command_string"
  ) >"$command_log" 2>&1 || command_rc=$?
  if grep -Fq 'TEST FAILED' "$command_log" 2>/dev/null; then
    matched_patterns="${matched_patterns:+$matched_patterns, }TEST FAILED"
  fi
  if grep -Fq '** BUILD FAILED **' "$command_log" 2>/dev/null; then
    matched_patterns="${matched_patterns:+$matched_patterns, }** BUILD FAILED **"
  fi
  if grep -Eq '^FAILED' "$command_log" 2>/dev/null; then
    matched_patterns="${matched_patterns:+$matched_patterns, }^FAILED"
  fi
  if grep -Eq ' FAILED ' "$command_log" 2>/dev/null; then
    matched_patterns="${matched_patterns:+$matched_patterns, } FAILED "
  fi
  if grep -Eq 'Test Case .* failed' "$command_log" 2>/dev/null; then
    matched_patterns="${matched_patterns:+$matched_patterns, }Test Case .* failed"
  fi

  if [ "$command_rc" -ne 0 ]; then
    record FAIL "$check_label" "exit=$command_rc log=$command_log"
  elif [ -n "$matched_patterns" ]; then
    record FAIL "$check_label" "exit=0 log=$command_log; matched failure pattern: $matched_patterns"
  else
    record PASS "$check_label" "exit=0 log=$command_log"
  fi
  printf '  last 5 lines:\n'
  tail -n 5 "$command_log" 2>/dev/null | sed 's/^/  | /'
}

command_number=0
while IFS= read -r command_string; do
  [ -n "$command_string" ] || continue
  command_number=$((command_number + 1))
  run_command "cmd-$command_number" "$command_string"
done <<COMMAND_ITEMS
$COMMANDS
COMMAND_ITEMS

command_number=0
while IFS= read -r full_command; do
  [ -n "$full_command" ] || continue
  command_number=$((command_number + 1))
  run_command "full-$command_number" "$full_command" 'FULL SUITE'
done <<FULL_COMMAND_ITEMS
$FULL_COMMANDS
FULL_COMMAND_ITEMS

if [ -z "$FULL_COMMANDS" ] && [ "$REQUIRE_FULL" -eq 1 ]; then
  record FAIL 'FULL SUITE' 'full suite not run: --require-full was set and no --full-cmd was given'
elif [ -z "$FULL_COMMANDS" ]; then
  record WARN 'FULL SUITE' 'full suite not run: hand-picked commands only'
fi

printf 'SUMMARY: %d pass, %d warn, %d fail\n' "$PASS_COUNT" "$WARN_COUNT" "$FAIL_COUNT"
if [ "$FAIL_COUNT" -ne 0 ]; then
  exit 1
fi
exit 0
