#!/bin/bash
# circuit-breaker Stop hook: loop verification + stuck-detection.
# Drop-in replacement for loop/hooks/verify.sh.
#
# Adds to loop-state.json:
#   max_consecutive_failures: N (default 3)
#   consecutive_failures:     current streak count
#   last_error_hash:          md5 of last failure output (detects stuck)
#
# Input:  JSON from stdin (Claude Code Stop hook protocol)
# Output: JSON {"decision": "block"|"approve", "reason": "..."}

STATE="${CLAUDE_PROJECT_DIR:-}/.claude/loop-state.json"
LOG="${CLAUDE_PROJECT_DIR:-}/.claude/circuit-breaker.log"

input=$(cat)
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && printf '%s\n' "$input" >> "$LOG" 2>/dev/null || true

# No state file — not in a loop, approve.
if [ ! -f "$STATE" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# --- Read state ---
py_read() {
  python3 -c "import json; d=json.load(open('$STATE')); print(d.get('$1', $2))" 2>/dev/null || echo "$2"
}

iteration=$(py_read iteration 0)
max=$(py_read max 10)
verify_cmd=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('verify_cmd',''))" 2>/dev/null || echo "")
max_cf=$(py_read max_consecutive_failures 3)
consecutive=$(py_read consecutive_failures 0)
last_hash=$(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('last_error_hash',''))" 2>/dev/null || echo "")

# --- Advance iteration counter ---
iteration=$((iteration + 1))
python3 - "$STATE" "$iteration" <<'PY' 2>/dev/null || true
import json, sys
path, n = sys.argv[1], int(sys.argv[2])
with open(path) as f: d = json.load(f)
d['iteration'] = n
with open(path, 'w') as f: json.dump(d, f)
PY

# --- No verify command or iteration cap ---
if [ -z "$verify_cmd" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

if [ "$iteration" -gt "$max" ]; then
  echo "{\"decision\": \"approve\", \"reason\": \"LOOP_CAP_REACHED (iteration $iteration exceeded max $max). Summarise what was accomplished and what remains.\"}"
  exit 0
fi

# --- Run verification ---
cd "$CLAUDE_PROJECT_DIR"
verify_output=$(eval "$verify_cmd" 2>&1)
verify_exit=$?

if [ "$verify_exit" -eq 0 ]; then
  # Pass — reset circuit breaker state.
  python3 - "$STATE" <<'PY' 2>/dev/null || true
import json, sys
with open(sys.argv[1]) as f: d = json.load(f)
d['consecutive_failures'] = 0
d['last_error_hash'] = ''
with open(sys.argv[1], 'w') as f: json.dump(d, f)
PY
  echo "{\"decision\": \"approve\", \"reason\": \"LOOP_APPROVED: $verify_cmd passed on iteration $iteration.\"}"
  exit 0
fi

# --- Verification failed: check for stuck loop ---
truncated=$(printf '%s' "$verify_output" | tail -60)
truncated="${truncated:0:4000}"

# Hash the error to detect same-error repetition.
current_hash=$(printf '%s' "$verify_output" | md5 2>/dev/null || printf '%s' "$verify_output" | md5sum | cut -d' ' -f1)

if [ "$current_hash" = "$last_hash" ]; then
  consecutive=$((consecutive + 1))
else
  consecutive=1
fi

# Update state with new consecutive count and hash.
python3 - "$STATE" "$consecutive" "$current_hash" <<'PY' 2>/dev/null || true
import json, sys
path, n, h = sys.argv[1], int(sys.argv[2]), sys.argv[3]
with open(path) as f: d = json.load(f)
d['consecutive_failures'] = n
d['last_error_hash'] = h
with open(path, 'w') as f: json.dump(d, f)
PY

# --- Circuit break: same error N times → escalate to human ---
if [ "$consecutive" -ge "$max_cf" ]; then
  reason=$(python3 -c "
import json, sys
output = sys.stdin.read()
msg = ('CIRCUIT_BREAK: same error repeated $consecutive times in a row (threshold: $max_cf).\n'
       'The loop is stuck — human input needed.\n\n'
       'Repeated failure output:\n' + output + '\n\n'
       'Summarise what you tried, why it is stuck, and what options remain.')
print(json.dumps(msg))
" <<< "$truncated")
  echo "{\"decision\": \"approve\", \"reason\": $reason}"
  exit 0
fi

# --- Normal loop continuation ---
reason=$(python3 -c "
import json, sys
output = sys.stdin.read()
msg = ('LOOP_VERIFY_FAIL (iteration $iteration/$max, consecutive failures: $consecutive/$max_cf)\n'
       'Test output:\n' + output + '\n\nFix the above failures and continue.')
print(json.dumps(msg))
" <<< "$truncated")

echo "{\"decision\": \"block\", \"reason\": $reason}"
exit 0
