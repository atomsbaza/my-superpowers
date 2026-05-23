---
model: sonnet
name: session-summary
description: Generates a summary of the current work session from git history, changed files, and conversation context. Use at the end of a work session, when returning to a project after a break, or when you want to know "where did I leave off?". Updates the Logseq wiki with progress.
---

# Session Summary

Generate a concise summary of what happened in this work session so you can pick up exactly where you left off — whether that's tomorrow or next month.

## Process

1. **Read git history** since the last summary or last 24h:
   ```bash
   git log --oneline --since="24 hours ago"
   # or since last tag / last session marker
   ```

2. **Check working state:**
   ```bash
   git status                          # uncommitted changes
   git stash list                      # anything stashed
   git diff --stat HEAD                # what's modified
   ```

3. **Read recent files** — skim the most recently modified source files to understand what was being worked on

4. **Check for open TODOs** in recently changed files:
   ```bash
   git diff HEAD~5..HEAD | grep -E "TODO|FIXME|HACK|WIP"
   ```

5. **Write the summary** using the template below

6. **Save** to `docs/sessions/YYYY-MM-DD-session.md` (create directory if needed)

7. **Update Logseq wiki** — add a journal entry or update the project page:
   - Open `~/Documents/Project Docs/pages/Projects___<ProjectName>.md`
   - Add to `## Implementation Progress`: `- YYYY-MM-DD: [one-line summary of what was done]`

## Summary template

```markdown
# Session: YYYY-MM-DD
**Project:** [project name]
**Duration:** [approximate if known]

## What was done
- [Completed item 1]
- [Completed item 2]

## Current state
[1-2 sentences describing exactly where the code is right now — what works, what's half-done]

## In progress / next action
- [ ] [The very next thing to do — specific enough to start immediately]
- [ ] [Second priority]

## Blockers
- [Anything that's blocking progress, or "None"]

## Open decisions
- [Any unresolved technical choice that needs to be made]

## Commits this session
[paste from git log --oneline]

## Notes
[Anything else worth remembering — gotchas discovered, links, context]
```

## Rules

- **"Next action" must be immediately actionable** — "implement X" not "work on feature Y"
- **Current state must be honest** — "half-implemented, doesn't compile" is useful; "good progress" is not
- **Keep it under 1 page** — if it's longer, you're journaling, not summarizing
- **Save the file** — a summary that exists only in the terminal is useless next session
- **Update the wiki** — the Logseq project page is the long-term record; session files are the short-term scratchpad

## Agent Integrations

### After saving the session summary file (Step 6)
Check if `~/Documents/Project Docs/pages/Projects___<ProjectName>.md` exists before spawning. If it exists, spawn `wiki-updater`. Pass it: the session summary file path, the project name, and the one-line summary of what was done.

If the page does not exist, add a note under **Notes** in the summary: "No Logseq page found for `<ProjectName>` — wiki not updated." Skip the spawn.

> **Before spawning:** Skip for throwaway / exploration sessions with no meaningful commits or changes. If wiki-updater returns empty or reports no update made, surface that explicitly — the session is not fully recorded.
