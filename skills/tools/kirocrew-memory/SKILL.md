---
name: kirocrew-memory
description: Read and update the Kiro Crew memory (preferences, active projects, daily history, learning log) from Claude Code. Use when starting work on a project Kiro Crew may know about, when the user says "check/ask Kiro memory", and when syncing what a session learned back into Kiro Crew.
---

# Kiro Crew memory (read + write)

Kiro Crew keeps its own memory under `~/.kiro/crew/`. Claude's auto-memory (`~/.claude/projects/*/memory/`) is a separate store; neither syncs to the other, so this skill is the bridge. The sync policy (when to write, what goes where) lives in `~/.claude/rules/memory-sync.md`; this skill is the how-to.

## Read (safe, no setup)

`kirocrew` prints config warnings on stderr; add `2>/dev/null` to keep only the memory text.

```sh
kirocrew memory show projects        # short ACTIVE state per project: status, blockers, next step
kirocrew memory show preferences     # the user's standing rules for Kiro Crew
kirocrew memory show history --since 2026-10-01
kirocrew memory search "<term>"      # vector + keyword; add --layer history for keyword-only over the markdown layers
kirocrew memory list | stats
```

Read `projects` before resuming a project that may have Kiro Crew activity (upstream PRs, SpendLens, KiroCrew contributions) and check it agrees with Claude's own memory and the repo. Treat both as point-in-time notes: when they disagree with the code or git, believe the code, and say so.

## Write (always through the helper)

The helper backs both files up first, then writes. Use Kiro Crew's bundled interpreter:

```sh
PY=/Applications/KiroCrew.app/Contents/Resources/backend-dist/kirocrew-backend-arm64/bin/python3.12
H=~/.claude/skills/kirocrew-memory/kc_memory.py

# 1. learning log: append one block (Thai, Found / Done / Lesson), lessons that generalize
$PY -s -P $H log <<'ENTRY'
## 2026-10-04 — <title>
- Found: ...
- Done: ...
- Lesson: ...
ENTRY

# 2. projects.md: replace (or insert) ONE project section; short active state, not a session log
$PY -s -P $H project <<'SECTION'
## <Project> — <what> (<dates>, **<status>**)
- สถานะ / blocker / ขั้นถัดไป ...
SECTION
```

- `project` replaces the section whose heading text (before the first ` (`, ` —` or ` --`) matches, else inserts it before `## Archive`. It is a compare-and-swap via `MemoryStore.write_projects` (reindexes search); exit code 3 means the file changed underneath, so re-read it and redo the edit, never force.
- Supersede a stale fact explicitly in the section ("Supersedes: ..."); finished work moves to `## Archive` per the user's `pref.memory_growth_policy`.
- Verify afterwards: `kirocrew memory show projects` and `kirocrew memory search --layer history "<term>"`.
- Preferences: do not hand-edit. Only add one if the user states a new standing rule, via `MemoryStore().add_preference(...)` (check its signature first), and tell the user.
- If the interpreter path is gone: `readlink -f ~/.local/bin/kirocrew`, then `<dir>/python3.12`.

## Never

- Edit the SQLite stores, episodes or `memory_stores/` directly (no command removes an episode; supersede it in projects.md).
- Read or search credential folders in `~/.kiro` or `~/.kiro/crew`.
- Put secrets, tokens, or the user's private email/addresses in either memory.
- Post anything to an outside service as part of a sync.
