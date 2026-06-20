#!/bin/bash
# verify-before-stop Stop hook: regression guard on session end.
# Runs tests only when git-changed files exist. Independent of the loop skill.
#
# Config: $CLAUDE_PROJECT_DIR/.claude/verify-on-stop.json
#   {"verify_cmd": "npm test", "enabled": true}
#
# Input:  JSON from stdin (Claude Code Stop hook protocol)
# Output: JSON {"decision": "block"|"approve", "reason": "..."}

CONFIG="${CLAUDE_PROJECT_DIR:-}/.claude/verify-on-stop.json"
LOG="${CLAUDE_PROJECT_DIR:-}/.claude/verify-before-stop.log"

input=$(cat)
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && printf '%s\n' "$input" >> "$LOG" 2>/dev/null || true

# No config file — hook is inactive.
if [ ! -f "$CONFIG" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Read config.
enabled=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d.get('enabled', True))" 2>/dev/null || echo "True")
verify_cmd=$(python3 -c "import json; d=json.load(open('$CONFIG')); print(d.get('verify_cmd', ''))" 2>/dev/null || echo "")

if [ "$enabled" = "False" ] || [ -z "$verify_cmd" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Check for git-changed files. If none, nothing to verify.
cd "$CLAUDE_PROJECT_DIR"
changed=$(git diff --name-only HEAD 2>/dev/null; git diff --name-only --cached HEAD 2>/dev/null)
if [ -z "$changed" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

changed_count=$(echo "$changed" | grep -c . || true)

# Run verification.
verify_output=$(eval "$verify_cmd" 2>&1)
verify_exit=$?

if [ "$verify_exit" -eq 0 ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Tests failed — block the stop and show what broke.
truncated=$(printf '%s' "$verify_output" | tail -60)
truncated="${truncated:0:4000}"

reason=$(python3 -c "
import json, sys
output = sys.stdin.read()
msg = ('REGRESSION DETECTED before session end.\n'
       '$changed_count changed file(s) in this session caused test failures.\n\n'
       'Test output:\n' + output + '\n\n'
       'Fix the regression before stopping. The session will end automatically once tests pass.')
print(json.dumps(msg))
" <<< "$truncated")

echo "{\"decision\": \"block\", \"reason\": $reason}"
exit 0
