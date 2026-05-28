# Design: Research Skill — Clarify Before Running

**Date:** 2026-05-28
**Scope:** Improve the `/research` global skill to ask three clarifying questions before invoking the research agent, and use the answers to sharpen the research prompt.

---

## Problem

The current `/research` skill takes the user's raw topic and passes it almost verbatim to the research agent. This causes two issues:

1. Broad or ambiguous topics produce generic, unfocused reports.
2. The agent has no context about audience, intent, or scope — so it makes its own assumptions, which often don't match what the user actually needed.

## Design

### Step 0: Parse the topic (unchanged)

Same as current skill — extract topic from skill arguments. If none, ask for one.

### Step 1: Ask three clarifying questions (NEW)

Before invoking the research agent, ask the user these three questions **sequentially** (one message each, wait for answer before the next):

1. **Audience** — "Who will read this research? (e.g., yourself, your team, an external stakeholder like a product team)"
2. **Goal** — "What decision or action will this research inform?"
3. **Scope** — "Any specific angle to focus on, or areas to exclude?"

Keep questions short. Accept brief or vague answers — do not re-ask for more detail.

### Step 2: Reshape the research prompt (NEW)

Using the three answers, rewrite the research question into a focused prompt for the agent. Do not just append the answers — synthesize them into a single well-scoped research brief. For example:

- Raw topic: "how can Kiro CLI be better"
- Audience: "Kiro product team"
- Goal: "send as feedback to influence their roadmap"
- Scope: "focus on CLI gaps vs IDE, skip pricing"
- Reshaped prompt: "Research specific feature gaps between Kiro CLI and Kiro IDE that are most likely to affect developer productivity. Focus on capabilities available in the IDE but missing from the CLI. Exclude pricing analysis. The output will be read by the Kiro product team as roadmap feedback, so findings should be concrete and actionable."

### Steps 3–5: Unchanged

Generate slug, invoke research agent with the reshaped prompt, save to `docs/research/` if it exists, return summary.

---

## What Is Not Changing

- Output format (structured markdown report with Summary, Key Findings, Trade-offs, Sources)
- File naming convention (`YYYY-MM-DD-<slug>.md`)
- Save-or-print logic based on `docs/research/` existence
- Error handling

---

## Success Criteria

- User is asked audience, goal, and scope before any search runs
- The prompt sent to the research agent visibly incorporates all three answers
- The resulting report is noticeably more focused than one produced from the raw topic alone
