# Orchestrator-Only Setup

How to configure Claude Code so the main model can think, plan, diagnose, and
review — but cannot touch files. All edits go through a delegated subagent
instead. This is a personal-machine configuration (not part of this repo's
`install.sh`); this doc exists so it can be replicated on another machine or
handed to someone else verbatim.

---

## 1. What this setup does

In this configuration, the top-tier main model (referred to below by its
model-name prefix, `claude-fable-*`) acts as **orchestrator only**: it thinks,
plans, diagnoses, reviews, and delegates. It is not allowed to call `Edit`,
`Write`, or `NotebookEdit` directly. Every file mutation is performed by a
dedicated subagent (`sonnet-writer`, defined below) that the main model must
delegate to.

The enforcement mechanism is a **PreToolUse hook**, not a prompt instruction.
A prompt instruction ("don't edit files yourself") is advisory — the model can
forget it, rationalize around it under pressure, or simply not apply it
consistently across a long session. A hook runs unconditionally, outside the
model's control, on every matching tool call. It cannot be forgotten or argued
out of.

**Cost rationale**: the expensive top-tier model's value is judgment —
diagnosing root causes, weighing tradeoffs, reviewing output, deciding what to
delegate and to whom. Producing the actual file diff is mechanical work that a
cheaper model does just as well. Reserving the expensive model for judgment
and routing all artifact production to a cheaper model (Sonnet here) cuts cost
without touching quality, because the step that needed the expensive model
never touched a file in the first place.

---

## 2. How it works

### Hook mechanics

- The hook fires on `PreToolUse` for `Edit|Write|NotebookEdit`, **before**
  Claude Code's permission checks run. Exiting with code `2` blocks the tool
  call; the hook's stderr becomes the message shown to the model, steering it
  to delegate instead of retrying the same call.

### Identifying the caller

- The hook's JSON input includes `agent_id` **only** when the call originates
  from a subagent. A call from the main agent has no `agent_id` field at all
  — that absence is how the hook tells "main agent" apart from "subagent."

### Model gating

- Enforcement applies **only** when the live session model matches
  `claude-fable-*`. Other main models (Opus, Sonnet, Haiku) are completely
  unaffected — this is a Fable-specific guardrail, not a general "main agent
  can't edit" rule.
- The live model is read from the session transcript: the hook input's
  `transcript_path` is scanned for the last main-thread (`isSidechain != true`)
  assistant entry's `.message.model`. Reading from the transcript (rather than
  a static setting) means the gate correctly tracks mid-session `/model`
  switches — if you switch away from Fable mid-session, enforcement turns off
  immediately; switch back, and it turns on again.
- If the transcript can't be read, the hook falls back to the `model` key in
  `~/.claude/settings.json`.
- If neither is readable, the hook **fails open** (allows the edit). A
  misconfigured or unreadable environment should not silently brick file
  writes.

### Exemptions

- **Subagents are always allowed** — they're the delegation target; blocking
  them would defeat the whole design.
- **Writes under `~/.claude/projects/*/memory/*` are always allowed** —
  Claude Code's own persistent memory system needs to keep writing there
  regardless of who or what triggers it.
- **Escape hatch**: `touch ~/.claude/hooks/orchestrator-off` disables all
  enforcement immediately (checked first, before anything else runs). Remove
  the file (`rm ~/.claude/hooks/orchestrator-off`) to re-enable.

### Why simpler alternatives don't work

- **CLAUDE.md instructions** ("you are orchestrator-only, delegate all
  edits") are not enforced by anything — they're advisory text the model can
  ignore under compaction pressure, ambiguity, or just habit.
- **Permission deny rules** and **`--disallowedTools`** apply session-wide.
  Since a subagent invocation runs inside the same session, a blanket deny on
  `Edit`/`Write` would block the subagent too — which is exactly the tool it
  needs to do its job. Only a hook that can distinguish "main agent" from
  "subagent" (via `agent_id`) can thread this needle.

---

## 3. Installation

### Prerequisite

`jq` must be installed — the hook script uses it to parse JSON.

```bash
# macOS
brew install jq

# Debian/Ubuntu
sudo apt-get install jq
```

### Step 1 — Create the hook script

Create `~/.claude/hooks/orchestrator-only.sh` with this exact content:

```bash
#!/bin/bash
# Orchestrator-only: block Edit/Write/NotebookEdit from the main agent,
# but ONLY when the main session model is Fable (claude-fable-*).
# Subagent calls carry agent_id and are always allowed.
# Escape hatch: `touch ~/.claude/hooks/orchestrator-off` disables enforcement.

if [ -f "$HOME/.claude/hooks/orchestrator-off" ]; then
  exit 0
fi

INPUT=$(cat)

# Subagents may always edit.
AGENT_ID=$(echo "$INPUT" | jq -r '.agent_id // empty')
if [ -n "$AGENT_ID" ]; then
  exit 0
fi

# Allow the main agent's persistent memory system to write its files.
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
case "$FILE_PATH" in
  "$HOME/.claude/projects/"*/memory/*)
    exit 0
    ;;
esac

# Determine the live session model from the transcript (records the actual
# model per assistant turn, including /model switches). Fall back to the
# configured default in settings.json; fail open if neither is readable.
MODEL=""
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
  MODEL=$(jq -r 'select(.type=="assistant" and .isSidechain!=true) | .message.model // empty' "$TRANSCRIPT" 2>/dev/null | tail -1)
fi
if [ -z "$MODEL" ] && [ -f "$HOME/.claude/settings.json" ]; then
  MODEL=$(jq -r '.model // empty' "$HOME/.claude/settings.json" 2>/dev/null)
fi

case "$MODEL" in
  claude-fable-*)
    echo "Main agent ($MODEL) is orchestrator-only. Delegate this edit to a subagent (e.g. sonnet-writer)." >&2
    exit 2
    ;;
esac

exit 0
```

Make it executable:

```bash
chmod +x ~/.claude/hooks/orchestrator-only.sh
```

### Step 2 — Wire the hook into settings.json

Merge (do **not** overwrite) this fragment into `~/.claude/settings.json`. If
the file already has a `hooks` key, merge the `PreToolUse` array entry in
alongside whatever is already there — replacing the whole file will destroy
any other settings (permissions, other hooks, env vars, etc.) already
configured.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/orchestrator-only.sh"
          }
        ]
      }
    ]
  }
}
```

After editing, validate the JSON is well-formed before restarting:

```bash
jq . ~/.claude/settings.json
```

If `jq` prints an error instead of the file's contents, fix the JSON before
proceeding — a broken `settings.json` can prevent Claude Code from starting.

### Step 3 — Create the sonnet-writer agent

Create `~/.claude/agents/sonnet-writer.md` with this exact content:

```markdown
---
name: sonnet-writer
description: Implements all code and file changes. Use whenever files need to be written or edited — features, fixes, refactors, configs, docs, even one-line edits. The main agent is orchestrator-only and must delegate every file mutation here.
model: sonnet
---

You are an implementation specialist. Write clean, correct, production-ready code.

- Follow the surrounding code's style, naming, and idiom.
- Make exactly the requested change; do not improve adjacent code that wasn't asked about.
- After editing, verify your change compiles/parses where cheap to do (e.g. `jq` for JSON, `bash -n` for shell).
- Report what you changed, file by file, and anything you noticed but did not touch.
```

### Step 4 — Restart Claude Code

Hooks are loaded once at session startup. Editing `~/.claude/hooks/` or
`~/.claude/settings.json` while a session is already running has no effect on
that session — quit and restart Claude Code to pick up the change.

---

## 4. Verification

The hook script reads JSON from stdin and can be tested standalone, without a
live session, by piping sample input directly to it.

**1. Fable main-agent edit → blocked (exit 2)**

```bash
echo '{"tool_input":{"file_path":"/tmp/x.txt"},"transcript_path":"/tmp/fake-transcript.jsonl"}' \
  | bash ~/.claude/hooks/orchestrator-only.sh; echo "exit: $?"
```

For this to actually resolve to `claude-fable-*`, the referenced transcript
must exist and end with a main-thread assistant line naming a Fable model. You
can fabricate one:

```bash
echo '{"type":"assistant","message":{"model":"claude-fable-5"}}' > /tmp/fake-transcript.jsonl
```

Expected: the script prints the delegate-to-`sonnet-writer` message to stderr
and exits `2`.

**2. Non-Fable transcript → allowed (exit 0)**

```bash
echo '{"type":"assistant","message":{"model":"claude-opus-4-8"}}' > /tmp/fake-transcript-opus.jsonl
echo '{"tool_input":{"file_path":"/tmp/x.txt"},"transcript_path":"/tmp/fake-transcript-opus.jsonl"}' \
  | bash ~/.claude/hooks/orchestrator-only.sh; echo "exit: $?"
```

Expected: exit `0` — Opus (or any non-Fable model) is unaffected.

**3. Call carries agent_id (i.e. a subagent) → allowed (exit 0)**

```bash
echo '{"agent_id":"sonnet-writer","tool_input":{"file_path":"/tmp/x.txt"},"transcript_path":"/tmp/fake-transcript.jsonl"}' \
  | bash ~/.claude/hooks/orchestrator-only.sh; echo "exit: $?"
```

Expected: exit `0` — subagents are always allowed, regardless of model.

**4. Memory path → allowed (exit 0)**

```bash
echo '{"tool_input":{"file_path":"'"$HOME"'/.claude/projects/some-project/memory/notes.md"},"transcript_path":"/tmp/fake-transcript.jsonl"}' \
  | bash ~/.claude/hooks/orchestrator-only.sh; echo "exit: $?"
```

Expected: exit `0` — the memory-write exemption applies even for a
Fable main-agent call.

---

## 5. Recommended companion: model-tier policy

The orchestrator-only hook only stops Fable from editing directly — it says
nothing about which model a delegated subagent actually runs on. **A subagent
with no `model:` frontmatter inherits the main session's model.** If Fable
delegates to an agent defined without an explicit `model:` key, that agent
runs on Fable too — silently defeating the cost rationale in section 1. Give
every agent an explicit `model:` frontmatter field so this can't happen by
omission.

### Tiers

- **Fable** — orchestration and judgment only. Planning, diagnosis, review,
  delegation. Never assigned to an artifact-producing agent.
- **Opus** — high-stakes analysis where a wrong call is expensive to
  discover later: debugging, silent-failure hunting, dependency auditing,
  concurrency review.
- **Sonnet** — all artifact production: implementation, tests, refactors,
  routine reviews, docs, PR descriptions. This is the default workhorse tier.
- **Haiku** — mechanical, low-ambiguity work: wiki/doc sync, changelogs, bulk
  renames.

### Guiding rules

- **Tier by ambiguity, not importance.** A task being "important" doesn't
  justify an expensive model if the work itself is mechanical (e.g. a
  release's changelog matters, but writing it from commit history is Haiku
  work). Reserve the expensive tiers for tasks where the model has to
  exercise judgment under uncertainty.
- **Escalate on disagreement, not by default.** Start an agent at the
  cheapest tier that plausibly fits; escalate to the next tier only when that
  agent's output is actually wrong or contested — not preemptively "to be
  safe."

---

## 6. Caveats & troubleshooting

- **Hooks are snapshotted at session startup.** Editing
  `~/.claude/hooks/orchestrator-only.sh` or the `hooks` block in
  `~/.claude/settings.json` requires a full restart of Claude Code to take
  effect; the currently running session keeps using whatever was loaded when
  it started.
- **Running a cheap model as the main session is not blocked.** Model gating
  only fires for `claude-fable-*`. If you intentionally run Sonnet, Opus, or
  Haiku as the main/orchestrator model, this hook does nothing — that's by
  design, not a gap, since the cost rationale in section 1 doesn't apply when
  the main model is already cheap.
- **The transcript schema is undocumented internal state.** `message.model`
  and `isSidechain` were verified by inspection against Claude Code v2.1.209.
  These are internal fields, not a documented public API — a future Claude
  Code release could change their names or structure. If that happens, the
  `jq` lookup returns empty, `MODEL` stays unset, the settings.json fallback
  is tried, and if that also fails to resolve, the hook fails open (allows
  the edit) rather than breaking file writes outright. Confirm this is still
  the case after any major Claude Code upgrade by re-running the section 4
  verification commands.
- **The memory-write exemption assumes the default path.** The `case`
  pattern matches `$HOME/.claude/projects/*/memory/*`. If your installation
  uses a non-default `CLAUDE_CONFIG_DIR` or projects root, update the glob to
  match, or the memory system's writes will be blocked when the main model is
  Fable.
- **If an edit is blocked unexpectedly**: first check whether
  `~/.claude/hooks/orchestrator-off` exists from a previous debugging session
  (its mere presence disables everything, silently) — `rm` it if so. Then run
  the hook manually with the failing call's actual `file_path` and
  `transcript_path` (captured from Claude Code's hook debug output, or
  reconstructed per section 4) to see exactly which branch it takes.
