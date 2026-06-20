#!/bin/bash
# Loop skill Stop hook: the "checker" in maker-checker.
# Runs the project's verify command independently of Claude's self-report.
# Returns block+failure output to force another turn, or approve when passing.
#
# Input:  JSON from stdin (Claude Code hook protocol)
# Output: JSON {"decision": "block"|"approve", "reason": "..."}
#
# State file: $CLAUDE_PROJECT_DIR/.claude/loop-state.json
#   {"iteration": N, "max": 10, "verify_cmd": "npm test", "task": "..."}

STATE="${CLAUDE_PROJECT_DIR:-}/.claude/loop-state.json"
LOG="${CLAUDE_PROJECT_DIR:-}/.claude/loop-hook.log"

# Log raw input for debugging (silent on failure).
input=$(cat)
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && printf '%s\n' "$input" >> "$LOG" 2>/dev/null || true

# No state file means loop skill hasn't been initialized — let session end normally.
if [ ! -f "$STATE" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# --- Read state ---
read_field() {
  python3 -c "import json,sys; d=json.load(open('$STATE')); print(d.get('$1', ${2:-''}))" 2>/dev/null || echo "${2:-}"
}

iteration=$(read_field iteration 0)
max=$(read_field max 10)
verify_cmd=$(read_field verify_cmd "")

# --- Advance iteration counter ---
iteration=$((iteration + 1))
python3 - "$STATE" "$iteration" <<'PY' 2>/dev/null || true
import json, sys
path, n = sys.argv[1], int(sys.argv[2])
with open(path) as f: d = json.load(f)
d['iteration'] = n
with open(path, 'w') as f: json.dump(d, f)
PY

# --- No verify command: nothing to check, approve ---
if [ -z "$verify_cmd" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# --- Iteration cap: stop looping, let Claude summarise ---
if [ "$iteration" -gt "$max" ]; then
  echo "{\"decision\": \"approve\", \"reason\": \"LOOP_CAP_REACHED (iteration $iteration exceeded max $max). Summarise what was accomplished and what still fails.\"}"
  exit 0
fi

# --- Run the checker (ground truth) ---
cd "$CLAUDE_PROJECT_DIR"
verify_output=$(eval "$verify_cmd" 2>&1)
verify_exit=$?

if [ "$verify_exit" -eq 0 ]; then
  # Verification passed — allow the stop.
  echo "{\"decision\": \"approve\", \"reason\": \"LOOP_APPROVED: $verify_cmd passed on iteration $iteration.\"}"
  exit 0
fi

# --- Verification failed — block and inject failure output ---
# Truncate to last 60 lines / 4000 chars to keep context lean.
truncated=$(printf '%s' "$verify_output" | tail -60)
truncated="${truncated:0:4000}"

# Escape for JSON.
reason=$(python3 -c "
import json, sys
output = sys.stdin.read()
msg = 'LOOP_VERIFY_FAIL (iteration $iteration/$max)\nTest output:\n' + output + '\n\nFix the above failures and continue.'
print(json.dumps(msg))
" <<< "$truncated")

echo "{\"decision\": \"block\", \"reason\": $reason}"
exit 0
