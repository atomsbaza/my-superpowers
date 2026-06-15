# Example: PO → Engineer End-to-End Workflow

This example shows how the `orchestrating-po-workflow` and `orchestrating-workflow` skills connect automatically, taking a product idea all the way to reviewed code without manual handoff.

## What It Does

```
[User] product idea
    │
    ▼
orchestrating-po-workflow
    ├─ writing-product-vision
    ├─ writing-brd
    ├─ writing-prd
    ├─ writing-user-stories
    ├─ writing-acceptance-criteria
    ├─ prioritizing-backlog
    ├─ planning-sprint  (optional)
    ├─ writing-roadmap
    └─► writes po-to-engineer-handoff.json
    │
    ▼
[User] resolve open questions → set open_questions_resolved: true
    │
    ▼
orchestrating-workflow  (reads po-to-engineer-handoff.json automatically)
    ├─ analyzing-requirements  ← loads PRD + stories from disk
    ├─ authoring-adrs
    ├─ designing-systems
    ├─ designing-database-schema  (if persistence needed)
    ├─ implementing-dotnet
    ├─ writing-tests
    └─ reviewing-code
```

## How to Run It

### Step 1 — Run the PO workflow

```
/orchestrating-po-workflow
```

The PO agent walks through vision → BRD → PRD → stories → acceptance criteria → backlog → roadmap. At the end it writes `po-to-engineer-handoff.json` in your project root.

### Step 2 — Resolve open questions

Open `po-to-engineer-handoff.json` and review `open_questions` from `.po-workflow-state.json`.
When all are resolved, set:

```json
"open_questions_resolved": true
```

### Step 3 — Run the engineer workflow

```
/orchestrating-workflow
```

The engineer workflow detects `po-to-engineer-handoff.json` and enters **Handoff mode** automatically:
- Reads the PRD and stories from disk (no manual copy-paste)
- Skips the requirements prompt
- Flows straight into requirements analysis → ADRs → design → code → tests → review

---

## The Handoff File

`po-to-engineer-handoff.json` is the bridge between the two workflows.

```json
{
  "product_name": "My Feature",
  "prd_path": "docs/requirements/prd-my-feature-v1.md",
  "stories_path": "docs/requirements/stories-my-feature-2026-06-16.md",
  "backlog_path": "docs/product/backlog-prioritization-2026-06-16.md",
  "business_goals": [
    "Reduce onboarding time by 30%"
  ],
  "open_questions_resolved": true,
  "handoff_at": "2026-06-16T10:00:00Z"
}
```

**Rules:**
- The engineer workflow reads file paths from this file and loads content from disk — it never receives the full PRD text through the conversation. This keeps the context window clean.
- `open_questions_resolved: false` blocks the engineer workflow with an explicit error. Fix open questions before proceeding.
- The engineer workflow does not modify this file. It is produced by the PO workflow and consumed read-only.

---

## Without the Full Workflow

You can also run the workflows manually in sequence. The handoff file still provides a clean interface:

```bash
# After PO workflow completes, edit the handoff file manually if needed
# Then trigger the engineer workflow — it auto-detects the file
```

If `po-to-engineer-handoff.json` does not exist, `orchestrating-workflow` falls back to asking you for requirements directly (Manual mode). No changes needed.

---

## Skills Involved

| Skill | Role |
|---|---|
| `orchestrating-po-workflow` | Runs all PO stages, writes `po-to-engineer-handoff.json` |
| `orchestrating-workflow` | Reads handoff file, runs all engineer stages |

See each skill's `SKILL.md` for full details:
- `.claude/skills/orchestrating-po-workflow/SKILL.md`
- `.claude/skills/orchestrating-workflow/SKILL.md`
