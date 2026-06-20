#!/bin/bash
# spec-writer PreToolUse hook: blocks source-file edits until spec is approved.
#
# Gate is active when:  .claude/spec-gate-active sentinel exists
# Gate lifts when:      .claude/active-spec.md contains "Status: APPROVED"
#                       (hook removes sentinel automatically)
#
# Input:  JSON from stdin (Claude Code PreToolUse hook protocol)
# Output: JSON {"decision": "block"|"approve", "reason": "..."}

GATE="$CLAUDE_PROJECT_DIR/.claude/spec-gate-active"
SPEC="$CLAUDE_PROJECT_DIR/.claude/active-spec.md"

input=$(cat)

# Gate not active — allow everything.
if [ ! -f "$GATE" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Gate active: check if spec has been approved.
if [ -f "$SPEC" ] && grep -q "Status: APPROVED" "$SPEC" 2>/dev/null; then
  # Spec approved — lift the gate and allow this tool call.
  rm -f "$GATE"
  echo '{"decision": "approve"}'
  exit 0
fi

# Gate active and spec not approved yet.
# Allow writes to spec/config files; block source-code edits.
tool_name=$(python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('tool_name',''))" 2>/dev/null <<< "$input")
file_path=$(python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null <<< "$input")

# Only gate Edit and Write tool calls.
if [ "$tool_name" != "Edit" ] && [ "$tool_name" != "Write" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Always allow writes to .claude/ (spec, settings, state files).
if [[ "$file_path" == .claude/* ]] || [[ "$file_path" == *"/.claude/"* ]]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Allow writes to doc/config/test files.
case "$file_path" in
  *.md|*.txt|*.json|*.yaml|*.yml|*.toml|*.ini|*.env*|*.gitignore)
    echo '{"decision": "approve"}'
    exit 0
    ;;
  *test*|*spec*|*__tests__*)
    echo '{"decision": "approve"}'
    exit 0
    ;;
esac

# Block source-file edits until spec is approved.
echo '{"decision": "block", "reason": "SPEC_GATE: the spec in .claude/active-spec.md has not been approved yet. Review it, change Status to APPROVED, then continue. Or run /spec-writer approve to approve it now."}'
exit 0
