---
name: session-promoter
description: >
  Extracts learnable patterns from the current session and writes them into the project's
  persistent memory system (~/.claude/projects/.../memory/). Captures mistakes corrected,
  preferences revealed, project facts discovered, and decisions made — so future sessions
  start smarter. Use at the end of any session with corrections, decisions, or new facts.
  Invoke with /session-promoter.
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

# Session Promoter

Review the current conversation and extract anything worth remembering in future sessions.
Write each finding as a typed memory entry using the project's auto-memory format.

## What to extract

Look for these patterns in the conversation:

**feedback** — corrections to your approach, or non-obvious approaches the user confirmed:
- User said "no", "don't", "stop doing X", or redirected you
- User accepted an unusual approach without pushback (confirmed pattern)
- You made a mistake that was caught mid-session

**project** — facts about the current project not derivable from the code:
- Decisions made (why, not what — "what" is in the code)
- Constraints, deadlines, stakeholders
- Architecture choices with a "why"

**user** — preferences about how to work with this user:
- Communication style preferences revealed
- Domain knowledge discovered (what they know deeply vs. not)
- Tools and workflows they prefer

## What NOT to promote

- Things already in CLAUDE.md or the codebase
- Ephemeral task details ("I was fixing bug X")
- What code does (the code says that)
- Things you'd know from reading the current files

## Memory file format

Save each memory to:
`~/.claude/projects/<project-slug>/memory/<type>_<slug>.md`

Use this frontmatter:
```markdown
---
name: <kebab-case-slug>
description: <one-line summary used to judge future relevance>
metadata:
  type: feedback | project | user
---

<body: lead with the rule/fact, then **Why:** and **How to apply:** lines>
```

Then add a pointer to `~/.claude/projects/<project-slug>/memory/MEMORY.md`:
```
- [Title](filename.md) — one-line hook
```

## Finding the memory directory

```bash
# Project slug is the working directory path with slashes replaced by hyphens.
# Example: /Users/alice/Work/my-superpowers → -Users-alice-Work-my-superpowers
ls ~/.claude/projects/
```

Pick the matching directory. If `memory/` doesn't exist inside it, create it.

## Process

1. Scan the conversation for extractable patterns (feedback, project facts, user preferences).
2. For each finding, decide the type and draft the memory body.
3. Check if a relevant memory file already exists — update it rather than creating a duplicate.
4. Write or update the file; add/update the MEMORY.md pointer.
5. Report to the user: "Promoted N memories: [titles]"

If nothing extractable was found: "Nothing to promote from this session."

An empty result is a **success state, not a failure** (2026-09-17,
mielony.com cron self-improvement pattern): a reflection pass that finds
something every time is generating content, not reflecting. Do not pad the
report to have something to show.

Every promoted memory must be **checkable**: include (or reference) the
command or observable that would verify the claim ("run `pytest -k foo`",
"the skill fired in session log X"). A proposal without a runnable check is
a wish, not a memory.

Two hard limits, from the same source:

- **Propose, never self-edit instruction sets.** The promoter writes memory
  files; it does not edit skills, hooks, or CLAUDE.md on its own authority.
  Self-editing instruction sets have no audit trail and drift compounds.
  Skill changes go through the maintainer (or this repo's propose-and-stop
  flow).
- **Verify each signal against real files before promoting.** A failure
  pattern, repeated tool call, or "skill loaded but unused" signal from the
  session transcript is a hypothesis — confirm against the on-disk files
  it concerns before writing it down.

## When to use

Invoke `/session-promoter` before ending any session where:
- You were corrected on approach
- A non-obvious decision was made and explained
- A project constraint or preference was revealed
- You learned something about the user's working style
