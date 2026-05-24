---
name: handoff
description: "Compact the current conversation into a handoff document so another agent/session can continue the work. Use when context is getting large, switching sessions, or wrapping up for the day."
---


# Handoff

Compact the current conversation into a handoff document so another agent/session can continue the work.

## When to Use

- Context window is getting large and work needs to continue
- Switching to a different agent or session
- End of day — capture state for tomorrow
- User says "handoff", "save context", "wrap up for now"

## Process

1. Summarize what was accomplished
2. Capture what's in progress (unfinished tasks, open questions)
3. Note decisions made and their rationale
4. List files modified
5. Identify next steps with enough detail to resume without re-reading everything

## Output Format

Save to `.kiro/handoffs/handoff-{YYYY-MM-DD-HHmm}.md`:

```markdown
# Handoff — {Brief Title}

**Date**: {timestamp}
**Session focus**: {one-line summary}

## Completed

- What was done (bullet points, concise)

## In Progress

- What's partially done
- Current state / where it left off

## Decisions Made

- Decision 1 — rationale
- Decision 2 — rationale

## Modified Files

- path/to/file1.cs — what changed
- path/to/file2.cs — what changed

## Open Questions

- Unresolved items needing human input

## Next Steps

1. Specific actionable next step
2. Another step
3. ...

## Suggested Skills

- skill-name — why it's relevant for next session
```

## Guidelines

- Don't duplicate content already in specs, PRDs, or commits — reference by path
- Keep it scannable — a fresh agent should understand the state in 30 seconds
- Include build/test status if relevant (passing? failing? which tests?)
- Mention any blockers or dependencies on external teams
