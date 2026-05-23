---
model: sonnet
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to a path produced by `mktemp -t handoff-XXXXXX.md` (read the file before you write to it).

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

## Agent Integrations

### After saving the handoff document
Check if `~/Documents/Project Docs/pages/Projects___<ProjectName>.md` exists before spawning. If it exists, spawn `wiki-updater`. Pass it: the handoff file path, the project name, and a one-line summary of what was accomplished and what the next session picks up.

If the page does not exist, add a note under Notes in the handoff doc: "No Logseq page found for `<ProjectName>` — wiki not updated." Skip the spawn.

> **Before spawning:** If wiki-updater returns empty or reports no update, surface that explicitly — a missing wiki entry means the next agent starts cold.
