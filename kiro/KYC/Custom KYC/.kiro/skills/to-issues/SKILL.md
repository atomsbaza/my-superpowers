---
name: to-issues
description: "Break a plan, spec, or PRD into independently-grabbable issues using vertical slices (tracer bullets). Use when converting specs into implementation tickets. Pairs with: spec-writer, sa-architect subagents."
---


# To Issues

Break a plan, spec, or PRD into independently-grabbable issues using vertical slices (tracer bullets).

## When to Use

- User wants to convert a spec/PRD into implementation tickets
- Breaking down work into issues for a sprint
- Decomposing a feature into parallelizable work items

## Process

### 1. Gather Context

Work from whatever is in the conversation — a spec, PRD, design doc, or issue reference. If the user points to a `.kiro/specs/` folder, read the requirements.md, design.md, and tasks.md.

### 2. Explore the Codebase

If unfamiliar with the area, read relevant project steering files and existing code to understand:
- Current patterns and conventions
- Domain vocabulary (use it in issue titles)
- Integration points between services

### 3. Draft Vertical Slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL layers end-to-end.

**Vertical slice** = schema + repository + handler + controller + tests in ONE issue
**NOT horizontal** = "create all entities" then "create all handlers" then "create all tests"

Each slice:
- Delivers a narrow but COMPLETE path through every layer
- Is demoable or verifiable on its own (tests pass, endpoint works)
- Can be merged independently

Mark slices as:
- **AFK** — can be implemented without human decisions
- **HITL** — requires human input (architecture decision, design review, external API contract)

### 4. Present & Iterate

Show the breakdown as a numbered list:

```
1. [AFK] Title — brief description
   Blocked by: none
2. [AFK] Title — brief description
   Blocked by: #1
3. [HITL] Title — needs decision on X
   Blocked by: none
```

Ask:
- Does the granularity feel right?
- Are dependency relationships correct?
- Should any slices be merged or split?

Iterate until approved.

### 5. Publish Issues

For each approved slice, create an issue with this structure:

```markdown
## What to Build

Concise description of the vertical slice. Describe end-to-end behavior.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked By

- #issue-number (or "None — can start immediately")

## Technical Notes

- Relevant project: `identification` / `verification` / etc.
- Key files to modify: (brief pointers, not exhaustive)
- Build command: `dotnet build src/Solution.sln`
- Test command: `dotnet test src/Solution.sln`
```

## Guidelines

- Prefer many thin slices over few thick ones
- First slice should be the "tracer bullet" — proves the path works end-to-end
- Database changes go in the first slice that needs them
- Shared infrastructure (new interfaces, DI registration) goes in the earliest slice
- Each slice should have at least one test proving it works
- Use domain vocabulary from the project's steering docs
