---
name: orchestrating-workflow
description: >
  Orchestrates the full principal engineer workflow from requirements to reviewed
  code. Chains skills in order: analyzing-requirements -> authoring-adrs ->
  designing-systems -> designing-database-schema -> implementing-dotnet ->
  writing-tests -> reviewing-code. Use when the user asks for a full workflow,
  end-to-end feature delivery, complete SDLC, full development cycle, or wants
  to go from requirements to working code in one session.
---

## Purpose

Run the full principal engineer workflow as a coordinated sequence. Each skill builds on the output of the previous. The workflow enforces the principal engineer's non-negotiables: no code before an ADR, no merge before tests and review pass.

## Workflow Stages

```
[START]
    │
    ▼
[1] analyzing-requirements
    └─► workflow-state.json: stage = "requirements_analyzed"
    │
    ▼
[2] authoring-adrs
    └─► workflow-state.json: stage = "adrs_complete"
    │   docs/decisions/NNNN-*.md created
    │
    ▼
[3] designing-systems  ──────────────────────────────┐
    └─► workflow-state.json: stage = "system_designed" │
    │   docs/design/system-design.md created           │ (if persistence involved)
    │                                                  ▼
    │                                    [3b] designing-database-schema
    │                                        └─► stage = "schema_designed"
    │
    ▼
[4] implementing-dotnet
    └─► workflow-state.json: stage = "implemented"
    │   Source files created/modified
    │
    ▼
[5] writing-tests
    └─► workflow-state.json: stage = "tested"
    │   Test files created
    │
    ▼
[6] reviewing-code
    └─► workflow-state.json: stage = "reviewed"
    │
    ▼
[END — feature ready for merge]
```

## State Management

The workflow uses `workflow-state.json` in the project root as the shared contract. Initialize it at the start of the workflow:

```json
{
  "stage": "started",
  "started_at": "<ISO timestamp>",
  "feature": "<feature name from user>",
  "requirements_analysis": null,
  "design": null,
  "schema": null,
  "implementation": null,
  "tests": null,
  "review": null,
  "history": [
    {"stage": "started", "at": "<ISO timestamp>"}
  ]
}
```

Update `history` on every stage transition:
```json
{"stage": "<new stage>", "at": "<ISO timestamp>", "summary": "<one sentence>"}
```

## Gates (Enforced, Not Bypassed)

| Gate | Condition to Proceed |
|---|---|
| Requirements → ADRs | `requirements_analysis` has at least one `recommended_adrs` entry |
| ADRs → Design | At least one ADR file exists in `docs/decisions/` |
| Design → Implementation | `docs/design/system-design.md` exists |
| Implementation → Tests | All implementation files listed in `workflow-state.json` |
| Tests → Review | At least one unit test file and one integration test file exist |
| Review → Done | `review.verdict` is `approved` or `approved_with_comments` |

If a gate cannot be passed (e.g., requirements are too vague to generate an ADR), stop and ask the user for clarification. Never skip a gate silently.

## Conditional Routing

After `analyzing-requirements`, check:

- **Persistence involved?** If `requirements_analysis.non_functional_requirements` mentions data storage or `bounded_contexts` has entities: run `designing-database-schema` as part of step 3.
- **OceanBase partitioning needed?** If any entity is an event/log table or high-write table: ensure `designing-database-schema` skill adds partitioning DDL.
- **External APIs?** If requirements mention integrations: add contract tests in `writing-tests` step.
- **Auth involved?** If requirements include authentication or authorization: add an ADR for the auth mechanism and flag to `reviewing-code` to check authorization on all endpoints.

## Entry Modes

### Manual (default)
User describes requirements in conversation. Ask for the feature requirements if not already provided.

### Handoff (from PO workflow)
If `po-to-engineer-handoff.json` exists in the working directory:
1. Read the file.
2. Check `open_questions_resolved`. If `false`, stop and tell the user:
   > "The PO workflow has unresolved open questions. Resolve them and set `open_questions_resolved: true` in `po-to-engineer-handoff.json` before continuing."
3. If `true`, load requirements from `prd_path` and stories from `stories_path` (read those files from disk — do not paste content into the conversation).
4. Set `feature` in `workflow-state.json` to `product_name` from the handoff file.
5. Skip the manual requirements prompt — proceed directly to `analyzing-requirements` with the loaded PRD and stories as input.

## Running the Workflow

When the user invokes this skill:

1. Check for `po-to-engineer-handoff.json`. If found, use Handoff mode. Otherwise, use Manual mode.
2. Greet with the workflow overview. In Manual mode, ask for the feature requirements if not already provided.
3. Initialize `workflow-state.json`.
4. Run each skill in sequence, waiting for completion before proceeding.
5. At each stage transition, print a one-line status update to the conversation:
   ```
   ✅ Stage complete: requirements_analyzed — 3 bounded contexts, 12 FRs, 4 ADRs recommended
   ```
6. If any stage produces a BLOCKER finding or an unanswerable open question, pause and surface it to the user before continuing.
7. On completion, print a final summary:

```markdown
## Workflow Complete

| Stage | Status | Output |
|---|---|---|
| Requirements Analysis | ✅ | workflow-state.json |
| ADRs | ✅ | docs/decisions/0001-*.md, 0002-*.md |
| System Design | ✅ | docs/design/system-design.md |
| Database Schema | ✅ | Infrastructure/Migrations/XXXXXX_Init.cs |
| Implementation | ✅ | 8 files created |
| Tests | ✅ | 24 unit tests, 6 integration tests |
| Code Review | ✅ | 0 blockers, 1 major, 2 nits |

**Verdict:** Approved with comments. Address 1 MAJOR before merge.
```

## Error Recovery

If the workflow is interrupted (session ends mid-stage), restart by reading `workflow-state.json`:

```
workflow-state.json exists, stage = "implemented"
→ Skip to writing-tests, read implementation files from state
```

Always resume from the last completed stage, not from the beginning.

## Output

The workflow itself does not write code files — it orchestrates the skills that do. Its only direct output is:
- `workflow-state.json` (initialized and maintained throughout)
- Stage transition status messages in the conversation
- Final summary report

In Handoff mode, `po-to-engineer-handoff.json` is consumed (read-only) as input. It is not modified by this workflow.
