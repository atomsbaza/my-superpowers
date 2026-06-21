#!/bin/bash
# secrets-guardrail PostToolUse hook: redacts credentials from tool output.
# Uses updatedToolOutput to replace what Claude sees (original tool output unchanged).
#
# Input:  JSON from stdin (Claude Code PostToolUse hook protocol)
# Output: JSON {"updatedToolOutput": "..."} to replace output, or {} to pass through

input=$(cat)

# Extract the tool output string via python.
tool_output=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
resp = d.get('tool_response', {})
out = resp.get('output', resp.get('content', ''))
if isinstance(out, list):
    out = ' '.join(item.get('text','') for item in out if isinstance(item, dict))
print(out)
" "$input" 2>/dev/null)

if [ -z "$tool_output" ]; then
  echo '{}'
  exit 0
fi

# Write the redaction script to a temp file to avoid heredoc/subshell issues.
SCRIPT=$(mktemp /tmp/redact_XXXXXX.py)
cat > "$SCRIPT" << 'PYEOF'
import os, re, json, sys

text = os.environ.get('TOOL_OUTPUT', '')
original = text

patterns = [
    (r'sk-ant-[a-zA-Z0-9\-_]{20,}',                                    '[REDACTED:anthropic-key]'),
    (r'sk-(?:proj-)?[a-zA-Z0-9]{20,}',                                  '[REDACTED:openai-key]'),
    (r'(?:ghp|ghs|gho|ghu|ghr|github_pat)_[a-zA-Z0-9]{20,}',           '[REDACTED:github-token]'),
    (r'AKIA[A-Z0-9]{16}',                                                '[REDACTED:aws-key]'),
    (r'Bearer\s+eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]*','Bearer [REDACTED:jwt]'),
    (r'Bearer\s+[a-zA-Z0-9\-_.]{20,}',                                  'Bearer [REDACTED:token]'),
    (r'eyJ[a-zA-Z0-9\-_]{10,}\.[a-zA-Z0-9\-_]{10,}\.[a-zA-Z0-9\-_]{10,}', '[REDACTED:jwt]'),
    (r'mongodb(?:\+srv)?://[^:]+:[^@]+@[^\s"\']+',                      '[REDACTED:connection-string]'),
    (r'(?:postgres|mysql|redis|amqp)://[^:]+:[^@]+@[^\s"\']+',          '[REDACTED:connection-string]'),
    (r'(?m)^([A-Z][A-Z0-9_]*(?:SECRET|KEY|TOKEN|PASSWORD|PASSWD|PWD|CREDENTIAL|AUTH)[A-Z0-9_]*)(\s*=\s*)(\S{16,})',
     r'\1\2[REDACTED]'),
    (r'(?i)(?:secret|token|key|password|passwd|pwd|auth)\s*[=:]\s*[0-9a-f]{32,}',
     '[REDACTED:secret]'),
]

for pattern, replacement in patterns:
    text = re.sub(pattern, replacement, text)

if text != original:
    print(json.dumps({'updatedToolOutput': text}))
else:
    print('{}')
PYEOF

redacted=$(TOOL_OUTPUT="$tool_output" python3 "$SCRIPT")
rm -f "$SCRIPT"

printf '%s' "$redacted"
exit 0
