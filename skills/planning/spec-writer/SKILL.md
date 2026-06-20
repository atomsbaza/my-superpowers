---
name: spec-writer
description: >
  Spec-first development: turn a feature request into a structured spec (requirements,
  acceptance criteria, test skeletons) before any code is written. Optionally gates
  implementation via a PreToolUse hook that blocks source-file edits until the spec is
  approved. Use when the user says "write a spec", "spec-first", "plan before coding",
  or starts a feature that benefits from upfront clarity. Pairs with /tdd and /loop.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
disable-model-invocation: false
---

# Spec Writer

Write the spec before touching code. The spec is a lightweight artifact that captures
*what* the feature does and *how to know it's done* — not how to implement it.

## When spec-writer activates

Invoke explicitly with `/spec-writer <feature>` or when asked to plan before coding.
Do not spec-write for trivial changes (typos, config tweaks, renaming).

## Step 1 — Understand the request

Ask at most two clarifying questions if genuinely ambiguous:
- Who uses this feature and what do they want to achieve?
- Are there any explicit constraints (performance, security, compatibility)?

Do not ask for implementation details — that's for later.

## Step 2 — Write the spec file

Save to `.claude/active-spec.md`. Use this template:

```markdown
# Spec: <Feature Name>

**Status:** DRAFT — awaiting approval
**Created:** YYYY-MM-DD
**Requested by:** <user or ticket>

## Problem

One paragraph: what problem does this solve and for whom?

## Requirements

Written in EARS (Easy Approach to Requirements Syntax):
- WHEN <trigger>, THE SYSTEM SHALL <response>
- THE SYSTEM SHALL <capability>
- THE SYSTEM SHALL NOT <constraint>

Keep to 3–8 requirements. Each must be testable.

## Acceptance Criteria

Given/When/Then format — one scenario per AC:

**AC1: <name>**
- Given: <precondition>
- When: <action>
- Then: <observable outcome>

**AC2: <name>**
...

## Out of Scope

Explicitly list what this spec does NOT cover. Prevents scope creep.

## Test Skeletons

Stub test cases (no implementation) matching the ACs:

```<language>
// AC1: <name>
test('<description>', () => {
  // Given: <setup>
  // When: <action>
  // Then: <assertion — to be implemented>
})
```

## Open Questions

Anything unresolved that could block implementation.

---
<!-- To approve: change Status above to APPROVED and delete this comment -->
```

## Step 3 — Activate the spec gate (optional)

If the user wants implementation blocked until they approve the spec:
```bash
touch "$CLAUDE_PROJECT_DIR/.claude/spec-gate-active"
```
This activates the PreToolUse hook (if wired in settings). Tell the user:
> "I've written the spec to `.claude/active-spec.md`. Review it, change Status to
> `APPROVED`, and the gate will lift automatically. Or run `/spec-writer approve`."

If the user doesn't want the gate, skip this step.

## Step 4 — Present the spec

Show a brief summary:
- Feature: what it does
- N requirements, N acceptance criteria
- Key out-of-scope decisions
- Any open questions that need answers

Then wait for the user to review and approve before writing any code.

## Approval

The spec is approved when `.claude/active-spec.md` contains `Status: APPROVED`.
The hook removes `.claude/spec-gate-active` automatically on approval.

After approval, suggest next steps:
- `/tdd` — implement test-first using the spec's test skeletons
- `/loop` — implement with automated verification
- Or implement directly if the task is simple

## Subcommands

- `/spec-writer <feature>` — write a new spec
- `/spec-writer approve` — mark the current spec approved, lift the gate
- `/spec-writer show` — print the current spec
- `/spec-writer clear` — remove `.claude/active-spec.md` and `.claude/spec-gate-active`

## Setup instructions (for humans)

The spec gate hook requires this in `.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/spec-writer/hooks/gate.sh"
          }
        ]
      }
    ]
  }
}
```
Or copy `~/.claude/skills/spec-writer/settings-snippet.json` and merge it in.
