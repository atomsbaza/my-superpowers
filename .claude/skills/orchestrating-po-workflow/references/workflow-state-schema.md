# PO Workflow State Schema Reference

> **File:** `.po-workflow-state.json`
> **Convention:** This is a design convention — not SDK-native. Every skill reads and writes this file explicitly to share context and enable workflow resumption.

## Full Schema

```json
{
  "product_name": "string — product or feature name",
  "current_phase": "init | vision | brd | prd | stories | acceptance_criteria | prioritization | sprint_plan | roadmap",
  "last_artifact": "string | null — path to the most recently created document",
  "summary": "string — one-line description of current product state",
  "product_vision": "string — one-sentence elevator pitch from vision skill",
  "target_customer": "string — primary JTBD summary",
  "business_goals": ["string — goal 1", "string — goal 2"],
  "open_questions": ["string — question 1", "string — question 2"],
  "sprint_number": "number | null — current sprint number if sprint planning is active",
  "velocity": "number | null — team story point velocity",
  "last_updated": "string — ISO 8601 timestamp",
  "error": "string | null — error message if last stage failed",
  "history": [
    {
      "phase": "string — phase name",
      "artifact": "string — file path",
      "completed_at": "string — ISO 8601 timestamp"
    }
  ]
}
```

## Phase Values

| Phase | Set By Skill | Meaning |
|---|---|---|
| `init` | orchestrating-po-workflow | Workflow not yet started |
| `vision` | writing-product-vision | Vision board written |
| `brd` | writing-brd | BRD written |
| `prd` | writing-prd | PRD written |
| `stories` | writing-user-stories | Stories decomposed |
| `acceptance_criteria` | writing-acceptance-criteria | ACs written for all stories |
| `prioritization` | prioritizing-backlog | Backlog ranked |
| `sprint_plan` | planning-sprint | Sprint plan created |
| `roadmap` | writing-roadmap | Roadmap written |

## How Skills Use This File

### Reading State
Every skill that is part of a workflow should read the state file at startup:
```bash
cat .po-workflow-state.json 2>/dev/null || echo '{"current_phase":"init"}'
```

Use `product_name`, `product_vision`, `target_customer`, and `business_goals` to maintain context across skills without re-asking the user.

### Writing State
After completing work, every skill writes its phase and artifact:
```json
{
  "current_phase": "prd",
  "last_artifact": "docs/requirements/prd-order-management-v1.md",
  "last_updated": "2026-06-11T10:30:00Z"
}
```

Always use a partial-update pattern: read the existing state, merge the new fields, write back. Never overwrite the entire file — preserve `history`, `business_goals`, and `open_questions`.

### Error Handling
If a skill cannot complete, it writes:
```json
{
  "error": "writing-brd: could not identify business goals from provided input"
}
```

The orchestrator reads `error` and surfaces it before proceeding.

### History Array
Each completed phase appends to history:
```json
{
  "history": [
    {"phase": "vision", "artifact": "docs/product/vision.md", "completed_at": "2026-06-11T09:00:00Z"},
    {"phase": "brd", "artifact": "docs/requirements/brd-v1.md", "completed_at": "2026-06-11T09:45:00Z"}
  ]
}
```

## Resumption Logic

When `orchestrating-po-workflow` starts and finds an existing state file:

1. Read `current_phase`
2. Find the phase in the sequence: `init → vision → brd → prd → stories → acceptance_criteria → prioritization → sprint_plan → roadmap`
3. Skip all phases up to and including `current_phase`
4. Continue from the next phase
5. If `error` is non-null, surface it and ask: retry / skip / abort

## Example State (Mid-Workflow)

```json
{
  "product_name": "Order Management System",
  "current_phase": "prd",
  "last_artifact": "docs/requirements/prd-order-management-v1.md",
  "summary": "B2B order entry platform replacing manual email workflow",
  "product_vision": "OrderFlow helps B2B operations teams manage customer orders in real time, replacing the email-and-spreadsheet workflow that causes 15% of orders to be delayed.",
  "target_customer": "When a B2B operations coordinator receives a new customer order, they want to enter and track it in one place so they can confirm delivery dates without chasing down status via email.",
  "business_goals": [
    "Reduce order processing errors by 50% in 6 months",
    "Cut average order confirmation time from 2 hours to 15 minutes"
  ],
  "open_questions": [
    "Does the system need to integrate with the existing ERP, or will it be standalone initially?",
    "What is the maximum number of line items per order the system must support?"
  ],
  "sprint_number": null,
  "velocity": null,
  "last_updated": "2026-06-11T10:30:00Z",
  "error": null,
  "history": [
    {"phase": "vision", "artifact": "docs/product/vision.md", "completed_at": "2026-06-11T09:00:00Z"},
    {"phase": "brd", "artifact": "docs/requirements/brd-order-management-v1.md", "completed_at": "2026-06-11T09:45:00Z"},
    {"phase": "prd", "artifact": "docs/requirements/prd-order-management-v1.md", "completed_at": "2026-06-11T10:30:00Z"}
  ]
}
```
