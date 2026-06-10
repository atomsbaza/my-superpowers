# Research: World-Class Claude Code Product Owner (PO) Agent — Definitive Build Reference

> **Audience:** Dev team
> **Goal:** Build the PO agent and its skills
> **Scope:** All of it — make it the best product owner agent
> **Date:** 2026-06-11

---

## Executive Summary

This report provides a complete, immediately-buildable specification for a language-agnostic Product Owner agent built on the Claude Code Agent SDK. It covers six domains: the confirmed SDK mechanics for subagent and skill file structures, the full scope of world-class PO responsibilities drawing on CSPO and SAFe frameworks, best-in-class document templates for every PO artifact, four prioritization frameworks with decision criteria, a complete 10-skill library, and stakeholder communication patterns. The key SDK insight is that a PO agent is most correctly implemented as a filesystem-based subagent (`.claude/agents/po-agent.md`) that orchestrates a library of skills (`.claude/skills/*/SKILL.md`). The `workflow-state.json` pattern is a **design convention**, not an SDK-native concept — flagged throughout.

---

## Key Findings

### Area 1 — Claude Code Agent SDK Mechanics

**Confirmed subagent frontmatter fields:**
`name`, `description`, `tools`, `disallowedTools`, `model`, `skills`, `memory`, `mcpServers`, `initialPrompt`, `maxTurns`, `background`, `effort`, `permissionMode`.

**Critical constraint:** Subagents cannot spawn their own subagents. Do not include `Agent` in a subagent's tools array.

**Tool recommendation for PO agent:** `Read, Write, Edit, Glob` — sufficient for all document work. `Bash` and `Grep` are unnecessary (PO work is document-centric).

**SKILL.md confirmed fields:** `name` (max 64 chars, lowercase+hyphens), `description` (max 1024 chars), `license`, `compatibility`, `metadata`, `allowed-tools`. Claude Code extensions: `argument-hint`, `arguments`, `context: fork`, `model`, `effort`, `disable-model-invocation`, `hooks`, `user-invocable`.

**Progressive loading:** `name` + `description` load at startup (~100 tokens each). Full body loads only on activation. Keep SKILL.md under 500 lines; move templates to `assets/`.

**`workflow-state.json` is a design convention**, not SDK-native. Skills must explicitly read/write this file to share context.

### Area 2 — Product Owner Role and Responsibilities

**Three horizons:** Strategic (vision, roadmap, stakeholder alignment), Tactical (backlog ownership, sprint planning, acceptance), Operational (grooming, clarification, release coordination).

**SAFe PO vs PM distinction:**
- **Product Owner:** Team backlog, stories, 1–3 months ahead, feasibility, delivery quality — works with the Agile team
- **Product Manager:** Program backlog, features, 1–3 PIs ahead, business viability, external-facing — works with business owners

**JTBD framing:** "When [situation], I want to [motivation], so I can [outcome]" — solution-agnostic, survives technology changes. Preferred over demographic personas.

### Area 3 — Document Types

| Document | Answers | Audience |
|---|---|---|
| BRD | Why are we doing this? What business outcome? | Business stakeholders |
| PRD | What will the product do? How will we know it's done? | Engineering, Design, QA |
| User Story | What specific capability does one persona need? | Dev team |
| Acceptance Criteria | When is this story complete? | Dev, QA, PO |
| Roadmap | Where are we going and why? | Everyone |
| Release Notes | What changed and what does it mean for you? | Customers |

### Area 4 — Prioritization Frameworks

**RICE:** `(Reach × Impact × Confidence) / Effort` — best when quantitative data available.

**WSJF (SAFe):** `Cost of Delay / Job Size` — best in SAFe environments, program/PI planning.

**Kano:** Must-be / Performance / Delighter categories — best when customer survey data is available. Recommended allocation: 60% Basic, 30% Performance, 10% Delight.

**MoSCoW:** Must/Should/Could/Won't — best for stakeholder alignment meetings and sprint scope decisions.

**Framework selection:**
- Many features + data → RICE
- SAFe environment → WSJF
- Customer survey data → Kano
- Stakeholder meeting → MoSCoW
- Quick sprint decision → Impact/Effort

### Area 5 — Skills Architecture

10 skills covering the full PO lifecycle. See Blueprint below.

### Area 6 — Stakeholder Communication

- **Engineering:** Grooming sessions, written clarifications in backlog items, sprint review acceptance/rejection with rationale
- **Executives:** Monthly dashboard (OKR health, metrics, risks, decisions needed), 5-sentence sprint summary post-review
- **Customers:** Feature request synthesis via JTBD, user interview findings, beta communication
- **Marketing/Sales:** Go-to-market brief per release (persona, key message, launch date, collateral needed)

---

## Trade-offs / Caveats

- **`workflow-state.json` is a convention, not SDK-native.** Skills must explicitly read/write it.
- **Subagents cannot chain other subagents.** All skills execute within the PO agent's context, or use `context: fork` for isolation.
- **Kano categories shift over time.** What is a delighter today becomes a basic expectation in 12–24 months. Re-survey annually.
- **This blueprint implements a PO (team-backlog focused), not a SAFe Product Manager.** For SAFe environments, extend scope or add a separate PM-level agent.
- **`allowed-tools` in SKILL.md is experimental.** For security boundaries, use `tools` in the agent definition instead.

---

## Recommended PO Agent + Skills Blueprint

### Agent: `.claude/agents/po-agent.md`

Language and technology agnostic. Tools: `Read, Write, Edit, Glob` only.

### 10 Skills

| Skill | Triggers | Output |
|---|---|---|
| `writing-product-vision` | vision, north star, product purpose, vision board | `docs/product/vision.md` |
| `writing-brd` | BRD, business requirements, business case, stakeholder requirements | `docs/requirements/brd-*.md` |
| `writing-prd` | PRD, product spec, feature specification, product requirements | `docs/requirements/prd-*.md` |
| `writing-user-stories` | user stories, decompose epic, split stories, backlog items, tickets | `docs/requirements/stories-*.md` |
| `writing-acceptance-criteria` | acceptance criteria, ACs, definition of done, test scenarios | Appended to story files |
| `prioritizing-backlog` | prioritize, RICE, WSJF, MoSCoW, Kano, rank features, what to build next | `docs/product/backlog-prioritization-*.md` |
| `planning-sprint` | sprint plan, sprint goal, sprint backlog, velocity, capacity | `docs/sprints/sprint-N-plan.md` |
| `writing-roadmap` | roadmap, Now Next Later, product direction, quarterly plan, OKR | `docs/product/roadmap-*.md` |
| `writing-release-notes` | release notes, changelog, what's new, customer announcement | `docs/releases/release-notes-*.md` |
| `orchestrating-po-workflow` | full PO workflow, product inception, idea to backlog, end to end | All of the above, chained |

### Shared State: `workflow-state.json`

```json
{
  "product_name": "string",
  "current_phase": "vision | brd | prd | stories | acceptance_criteria | prioritization | sprint_plan | roadmap",
  "last_artifact": "path/to/last/created/file.md",
  "summary": "one-line description of current product state",
  "product_vision": "one-line vision statement",
  "target_customer": "description of primary persona",
  "business_goals": ["goal 1", "goal 2"],
  "open_questions": ["question 1"],
  "last_updated": "ISO 8601 timestamp"
}
```

### Phase Gate Sequence

`Vision → BRD → PRD → User Stories → Acceptance Criteria → Prioritization → Sprint Plan → Roadmap`

---

## Sources

- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Subagents in the SDK — Claude Code Agent SDK Docs](https://code.claude.com/docs/en/agent-sdk/subagents)
- [Agent Skills Open Standard Specification](https://agentskills.io/specification)
- [SKILL.md Format Reference — agensi.io](https://www.agensi.io/learn/skill-md-format-reference)
- [Build a Claude Code Custom Subagent — digitalapplied.com](https://www.digitalapplied.com/blog/build-claude-code-custom-subagent-step-by-step-2026)
- [RICE Prioritization — Intercom](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/)
- [WSJF — Scaled Agile Framework](https://framework.scaledagile.com/wsjf/)
- [SAFe Product Owner — Scaled Agile Framework](https://framework.scaledagile.com/product-owner)
- [SAFe PM vs PO — LaunchNotes](https://www.launchnotes.com/blog/safe-product-manager-vs-product-owner-key-differences-explained)
- [Kano Model — ProductPlan](https://www.productplan.com/glossary/kano-model)
- [SPIDR Story Splitting — Mountain Goat Software](https://www.mountaingoatsoftware.com/blog/five-simple-but-powerful-ways-to-split-user-stories)
- [JTBD Framework — Userpilot](https://userpilot.com/blog/jtbd-product-management/)
- [Now/Next/Later Roadmaps — Tability](https://www.tability.io/odt/articles/why-now-next-later-roadmaps-are-better-for-okrs)
- [Outcome-Based Roadmaps — Product School](https://productschool.com/blog/product-strategy/outcome-based-roadmap)
- [PRD vs BRD Guide 2025 — dplooy](https://www.dplooy.com/blog/prd-vs-frd-vs-brd-complete-guide-2025-documents-templates-real-world-examples)
- [PRD Templates — Reforge](https://www.reforge.com/blog/product-requirement-document-prd-templates)
- [Stakeholder Communication — Scrum.org](https://www.scrum.org/resources/blog/stakeholder-communication-strategy-part-3-4-steps-stakeholder-engagement)
