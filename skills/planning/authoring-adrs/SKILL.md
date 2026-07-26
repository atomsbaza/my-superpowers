---
name: authoring-adrs
description: >
  Authors Architecture Decision Records (ADRs) in MADR format for architecturally
  significant or hard-to-reverse decisions. Use when the user asks to record an
  architecture decision, create an ADR, document a technology choice, or capture
  a design decision. Also invoked automatically by the orchestrating-workflow skill
  after requirements analysis. Reads recommended ADRs from workflow-state.json and
  outputs one .md file per decision into docs/decisions/.
---

## Purpose

Make architecture decisions explicit, traceable, and reviewable. An undocumented decision is a debt that compounds over time. This skill produces append-only ADR files using MADR format, the standard for .NET ecosystem projects.

## Input

Accept ADR requests from any of:
- `workflow-state.json` → `requirements_analysis.recommended_adrs` (automated chain)
- Direct user prompt: "ADR for X" or "document decision to use Y"
- Explicit list of decisions to capture

If no decisions are identified, ask: "What decision do you need to document? State the problem and the options you considered."

## MADR Format

Load and follow the template at `reference/adr-template.md`.

Each ADR must contain:

1. **Title** — short, imperative sentence: "Use Pomelo EF Core for OceanBase persistence"
2. **Status** — `proposed | accepted | deprecated | superseded`
3. **Context and Problem Statement** — the situation that forces a decision. Include constraints.
4. **Decision Drivers** — the forces and criteria weighting the choice (bullet list)
5. **Considered Options** — every option evaluated (not just the winner)
6. **Decision Outcome** — the chosen option with a one-paragraph justification
7. **Pros and Cons of Options** — a sub-section per option with ✅ Good / ❌ Bad bullets
8. **Consequences** — positive consequences, negative consequences, risks accepted
9. **Links** — related ADRs, PRs, or external references

## Numbering and File Names

1. Check `docs/decisions/` for the highest existing ADR number.
2. Increment by 1 for each new ADR.
3. File name format: `NNNN-kebab-case-title.md` (e.g., `0003-use-pomelo-efcore-for-oceanbase.md`)
4. Create `docs/decisions/` if it does not exist.

## ADRs to Always Create for Common Scenarios

When requirements analysis indicates these concerns, author an ADR proactively:

| Scenario | ADR Title |
|---|---|
| Database technology | "Use [DB] as primary persistence store" |
| ORM / data access | "Use [ORM] for database access" |
| Authentication | "Use [mechanism] for authentication" |
| Messaging / events | "Use [broker] for async messaging" |
| API style | "Use [REST/gRPC/GraphQL] for [API name]" |
| Caching | "Use [strategy] for caching [resource]" |
| Distributed transactions | "Use outbox pattern for cross-service consistency" |
| Testing strategy | "Use Testcontainers for integration test isolation" |

## Process

For each decision:

1. Draft the full ADR using the MADR template.
2. Fill every section — no empty sections, no "TBD".
3. For options: list at minimum 2 alternatives even if the choice is obvious (documents what was ruled out).
4. For OceanBase-related decisions, always note MySQL-mode compatibility constraints.
5. Cross-link to related ADRs using `[ADR-NNNN](NNNN-title.md)`.
6. Write the file to `docs/decisions/NNNN-title.md`.
7. Update `workflow-state.json` → append to `history` with `{"stage": "adr_authored", "file": "docs/decisions/NNNN-title.md"}`.

## Output

- One `.md` file per ADR written to `docs/decisions/`
- Print a summary table to the conversation: ADR number, title, chosen option, status
- Update `workflow-state.json` stage to `"adrs_complete"` when all recommended ADRs are authored
