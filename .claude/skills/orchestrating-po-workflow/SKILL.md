---
name: orchestrating-po-workflow
description: >
  Orchestrates the complete end-to-end Product Owner workflow from business idea
  through sprint-ready backlog: product vision, BRD, PRD, user stories,
  acceptance criteria, backlog prioritization, sprint plan, and roadmap.
  Persists progress in .po-workflow-state.json to enable resume after
  interruption. Use when starting a product from scratch, running a full
  product inception, or picking up a paused PO workflow. Trigger keywords:
  full PO workflow, product inception, idea to backlog, end to end product,
  run all PO steps, start product from scratch, complete PO pipeline,
  orchestrate product workflow, product kickoff.
---

## Purpose

Chain all PO skills in sequence using `.po-workflow-state.json` to persist progress, enable resume after interruption, and enforce quality gates between stages.

## Workflow Stages

```
[START]
    │
    ▼
[1] writing-product-vision
    └─► phase = "vision"
    │
    ▼
[2] writing-brd
    └─► phase = "brd"
    │
    ▼
[3] writing-prd
    └─► phase = "prd"
    │
    ▼
[4] writing-user-stories
    └─► phase = "stories"
    │
    ▼
[5] writing-acceptance-criteria
    └─► phase = "acceptance_criteria"
    │
    ▼
[6] prioritizing-backlog
    └─► phase = "prioritization"
    │
    ▼
[7] planning-sprint  (optional — skip if no sprint context)
    └─► phase = "sprint_plan"
    │
    ▼
[8] writing-roadmap
    └─► phase = "roadmap"
    │
    ▼
[DONE — backlog ready for development]
```

## State File: `.po-workflow-state.json`

Full schema:
```json
{
  "product_name": "",
  "current_phase": "init",
  "last_artifact": null,
  "summary": "",
  "product_vision": "",
  "target_customer": "",
  "business_goals": [],
  "open_questions": [],
  "sprint_number": null,
  "velocity": null,
  "last_updated": "",
  "error": null,
  "history": []
}
```

## Quality Gates (Enforced — Not Skipped)

| From Stage | Gate Condition | If Not Met |
|---|---|---|
| → BRD | Product name and vision identified | Ask for product name and core problem |
| → PRD | BRD file exists and business goals are defined | Re-run writing-brd |
| → User Stories | PRD functional requirements exist | Re-run writing-prd |
| → Acceptance Criteria | At least one story file exists | Re-run writing-user-stories |
| → Prioritization | Stories exist and business goals are defined | Ensure writing-brd has run |
| → Sprint Plan | Prioritized backlog exists | Run prioritizing-backlog first |
| → Roadmap | PRD and backlog exist | Ensure earlier stages completed |

## Process

### Step 1 — Initialize or Resume

```bash
cat .po-workflow-state.json 2>/dev/null || echo '{"current_phase":"init"}'
```

If `current_phase != "init"`, resume from the last completed phase — skip all completed steps.

If `error` is non-null:
- Print: "Phase `<phase>` failed with: `<error>`"
- Ask: "Retry (r), skip (s), or abort (a)?"
- Honor the user's choice and clear or preserve the error in state.

### Step 2 — Collect Inputs

Ask once (if not already in state):
1. "What is the product or feature name?"
2. "Do you have a business brief, BRD, or vision document? (file path or paste)"
3. "What is the primary business goal and how will you measure success?"
4. "Is there a sprint context? (sprint number, velocity, capacity — or skip)"

### Step 3 — Run Each Stage

For each stage in the workflow:
1. Announce the stage: `Starting: [stage name]`
2. Invoke the corresponding skill (describe what it should do with the current context)
3. Confirm the phase is written to `.po-workflow-state.json` before proceeding
4. Print a one-line status update: `✅ [Stage name] complete — [key artifact path]`

If any skill writes `"error": "<message>"` to state, stop and surface it immediately.

### Step 4 — Conditional Routing

After `current_phase = "acceptance_criteria"`:
- **Sprint planning route:** Run `planning-sprint` only if sprint context was provided (sprint number, velocity)
- **Roadmap route:** Always run `writing-roadmap`
- **Skip sprint plan:** If user says "no sprint context", jump directly to roadmap

After all stages:
- Check `open_questions` in state — surface any unresolved questions to the user

### Step 5 — Final Summary

After all stages complete, print:

```markdown
## PO Workflow Complete

### Product: [product_name]

| Stage | Status | Artifact |
|---|---|---|
| Product Vision | ✅ | docs/product/vision.md |
| BRD | ✅ | docs/requirements/brd-*.md |
| PRD | ✅ | docs/requirements/prd-*.md |
| User Stories | ✅ | docs/requirements/stories-*.md (N stories) |
| Acceptance Criteria | ✅ | Appended to stories |
| Backlog Prioritization | ✅ | docs/product/backlog-prioritization-*.md |
| Sprint Plan | ✅ / ⏭ Skipped | docs/sprints/sprint-N-plan.md |
| Roadmap | ✅ | docs/product/roadmap-*.md |

### Open Questions (Resolve Before Dev Starts)
[List from state.open_questions]

### Recommended Next Steps
1. Resolve open questions listed above
2. Share PRD with engineering for feasibility review
3. Run sprint planning session with the team
4. Demo vision and roadmap to stakeholders
```

## Error Handling Policy

- Never silently continue past a failed stage
- Never skip quality gates unless the user explicitly says to
- If a stage writes an error, surface it with the full error text
- If the state file becomes corrupted, offer to reset to `init` phase and re-collect inputs
