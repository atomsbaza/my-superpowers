---
model: sonnet
name: adr
description: Captures architectural decisions made during coding sessions as structured ADR documents. Use when choosing between significant alternatives (framework, pattern, library, API design, data model), when the user says "ADR this" or "record this decision", or when explaining why X was chosen over Y. Also use to read existing ADRs when asked "why did we choose X?".
---

# Architecture Decision Records

Capture architectural decisions as they happen. Decisions made during coding should live in `docs/adr/` alongside the code — not in memory, Slack, or PR comments.

## When to activate

- User says "ADR this", "record this decision", "let's document why we chose X"
- User chooses between significant alternatives during planning or coding
- User says "we decided to..." or "the reason we're doing X instead of Y is..."
- User asks "why did we choose X?" → read existing ADRs

## Writing a new ADR

1. **Identify the core decision** — one clear choice being made
2. **Gather context** — what problem prompted it? What constraints exist?
3. **Document alternatives** — what else was considered and why rejected?
4. **State consequences** — what becomes easier or harder?
5. **Initialize `docs/adr/`** if it doesn't exist — create the directory + `README.md` index. Ask for confirmation first.
6. **Number it** — scan existing ADRs and increment. Start at 0001.
7. **Present the draft** for user review before writing any file
8. **Write only after approval** → `docs/adr/NNNN-decision-title.md`
9. **Update the index** → append to `docs/adr/README.md`
10. **Update Logseq wiki** → add to the project's `~/Documents/Project Docs/pages/Projects___<ProjectName>.md` under a `## Decisions Log` section: `YYYY-MM-DD: [one-line summary]`

## ADR format

```markdown
# ADR-NNNN: [Decision Title]

**Date:** YYYY-MM-DD
**Status:** accepted
**Project:** [project name]

## Context

What situation or constraint prompted this decision? What forces are at play?
(2–4 sentences)

## Decision

What was decided, stated clearly and directly.
(1–2 sentences)

## Alternatives Considered

### [Alternative 1 name]
- **Pros:** ...
- **Cons:** ...
- **Why rejected:** ...

### [Alternative 2 name]
- **Pros:** ...
- **Cons:** ...
- **Why rejected:** ...

## Consequences

### Positive
- ...

### Negative / Trade-offs
- ...

### Risks
- [risk] — [mitigation]
```

## Reading existing ADRs

When user asks "why did we choose X?":
1. Check `docs/adr/README.md` for the index
2. Read relevant ADR files
3. Present the Context + Decision sections
4. If no ADR found: "No ADR found for that decision. Would you like to record one now?"

## ADR index format (docs/adr/README.md)

```markdown
# Architecture Decision Records

| ADR | Title | Date | Status |
|-----|-------|------|--------|
| [0001](0001-title.md) | Title | YYYY-MM-DD | accepted |
```

## Rules

- Never write files without user approval of the draft
- One decision per ADR — don't bundle multiple choices
- Status must be one of: `proposed` / `accepted` / `deprecated` / `superseded by ADR-NNNN`
- Use the project's own domain vocabulary — not generic terms
- Keep Context under 5 sentences — if it needs more, the decision scope is too large

## Agent Integrations

### After writing the ADR file and updating the index (Steps 8–9)
Check if `~/Documents/Project Docs/pages/Projects___<ProjectName>.md` exists before spawning. If it exists, spawn `wiki-updater`. Pass it: the ADR file path, the project name, and the one-line decision summary. It appends to the `## Decisions Log` section.

If the page does not exist, the ADR file itself is the record — skip the spawn.

> **Before spawning:** Skip if the user rejected the draft (no file was written). If wiki-updater returns empty or errors, note it — the ADR index is still the authoritative record.
