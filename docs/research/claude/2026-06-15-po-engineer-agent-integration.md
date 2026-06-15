# Research: Connecting PO Agent and Engineer Agent via Claude Workflow

## Context

The project already has:
- `po-agent.md` — PO agent (tools: Read, Write, Edit, Glob)
- `principal-dotnet-engineer.md` — engineer agent (tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch)
- `orchestrating-po-workflow` skill — chains all PO skills end-to-end
- `orchestrating-workflow` skill — chains all engineer skills end-to-end

These two pipelines are currently siloed. The user manually triggers one after the other, reading docs in between.

---

## The Gap

```
User triggers PO workflow → PO writes docs → User reads them → User triggers engineer workflow
```

The handoff is manual. There is no automated contract passing PO outputs to the engineer pipeline.

---

## Improvement Plan

### 1. Handoff File (Lightweight Reference, Not Content)

At the end of `orchestrating-po-workflow`, write a handoff artifact:

**`po-to-engineer-handoff.json`**
```json
{
  "product_name": "",
  "prd_path": "docs/requirements/prd-feature-v1.md",
  "stories_path": "docs/requirements/stories-feature-2026-06-15.md",
  "backlog_path": "docs/product/backlog-prioritization-2026-06-15.md",
  "business_goals": [],
  "open_questions_resolved": true,
  "handoff_at": ""
}
```

Pass file paths — not content — so the engineer workflow reads from disk. This prevents the coordinator's context from bloating (artifact-based communication pattern).

### 2. Handoff Mode in `orchestrating-workflow`

Add a new entry point to `orchestrating-workflow/SKILL.md`:

```markdown
## Entry Modes

### Manual (current)
User describes requirements in conversation.

### Handoff (new)
Read `po-to-engineer-handoff.json` from working directory.
Load the PRD from `prd_path`, stories from `stories_path`.
Pass them directly to the `analyzing-requirements` step.
Skip the "describe your requirements" prompt.
```

### 3. Optional: `orchestrating-full-sdlc` Skill

A top-level skill that runs both workflows end-to-end:

```
[START]
    │
    ▼
[1] orchestrating-po-workflow
    └─► .po-workflow-state.json, PRD, stories, backlog
    └─► writes po-to-engineer-handoff.json
    │
    ▼
[GATE] Open questions resolved? User confirms.
    │
    ▼
[2] orchestrating-workflow (handoff mode)
    └─► reads po-to-engineer-handoff.json
    └─► ADRs, system design, schema, code, tests, review
    │
    ▼
[END — from idea to reviewed code]
```

---

## Key Rules

- **Pass file paths, not content.** Engineer reads PRD from disk — not through the conversation. Prevents coordinator context pollution.
- **Tools are not shared.** PO agent and engineer agent have separate tool scopes. The filesystem is the only shared surface — exactly what the handoff file uses.
- **The gate between them is critical.** Unresolved open questions from PO workflow cause wrong assumptions mid-implementation. Always confirm before handing off.

---

## Minimum Viable Changes

Two file edits to wire it up without a new skill:

1. **`orchestrating-po-workflow/SKILL.md`** — add step to write `po-to-engineer-handoff.json` at the end of the final summary step
2. **`orchestrating-workflow/SKILL.md`** — add handoff mode entry point that reads the file

The `orchestrating-full-sdlc` skill is optional — sequential manual trigger with the handoff file still works cleanly.
