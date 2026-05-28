# Research Skill — Clarify Before Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the `/research` skill so it asks 3 clarifying questions (audience, goal, scope) before invoking the research agent, then reshapes the agent prompt using those answers.

**Architecture:** Single-file edit to `~/.claude/skills/research/SKILL.md`. Insert a new "Step 1.5" between topic parsing and agent invocation. Update the agent-invocation step to reshape the prompt using the answers. No code, no tests — this is a prompt/skill markdown file.

**Tech Stack:** Markdown (Claude Code skill file).

---

### Task 1: Edit the research SKILL.md

**Files:**
- Modify: `/Users/pisitkoolplukpol/.claude/skills/research/SKILL.md`

- [ ] **Step 1: Open and review the current SKILL.md**

Read `/Users/pisitkoolplukpol/.claude/skills/research/SKILL.md` end-to-end before editing so the edits land in the correct sections.

- [ ] **Step 2: Insert a new "Gather context" step between Step 1 (Parse the topic) and Step 2 (Generate slug)**

Renumber the existing Step 2 onward (slug → 3, invoke agent → 4, save → 5, summary → 6). Insert this new section as Step 2:

```markdown
### 2. Gather context before researching

Before invoking the research agent, ask the user these three questions **one at a time** (separate messages, wait for each answer before asking the next). Use the `AskUserQuestion` tool when offering choices; otherwise plain text questions are fine.

1. **Audience** — "Who will read this research? (e.g., yourself, your team, an external stakeholder)"
2. **Goal** — "What decision or action will this research inform?"
3. **Scope** — "Any specific angle to focus on, or areas to exclude?"

Keep each question short. Accept brief or vague answers — do not re-ask for more detail. If the user says "skip" or "no preference" for any question, record that and move on.

If the user has already provided some of this context in their original `/research` invocation (e.g., they wrote "/research X for my team to decide Y"), do not re-ask for that piece — only ask for the missing ones.
```

- [ ] **Step 3: Update the (renumbered) Step 4 — "Invoke the research agent" — to use the gathered context**

Replace the existing prompt template with a reshaping instruction. The new section body should read:

```markdown
### 4. Invoke the research agent

Synthesize the topic and the three answers (audience, goal, scope) into a single focused research brief. Do NOT just concatenate them — rewrite the research question so it reflects the audience, the decision it will inform, and any scope constraints.

Example:
- Raw topic: "how can Kiro CLI be better"
- Audience: "Kiro product team"
- Goal: "send as feedback to influence their roadmap"
- Scope: "focus on CLI gaps vs IDE, skip pricing"
- Reshaped brief: "Research specific feature gaps between Kiro CLI and Kiro IDE that affect developer productivity. Focus on capabilities available in the IDE but missing from the CLI. Exclude pricing analysis. Output will be read by the Kiro product team as roadmap feedback, so findings must be concrete and actionable."

Use the `Agent` tool with `subagent_type: "research"`. Pass the reshaped brief as the prompt:

> "Research the following topic and produce a structured markdown report following your standard methodology: <reshaped brief>"

Wait for the agent to return the full report.

> **Note:** If you see "Agent type 'research' not found", fall back to `subagent_type: "general-purpose"` with these instructions in the prompt:
>
> *You are a web research agent. Decompose the topic into 3-5 sub-questions, WebSearch each, WebFetch the top 2-3 results per question, then synthesize a markdown report with sections: Summary, Key Findings (with inline citations), Trade-offs / Caveats, Sources. Always cite URLs. Flag conflicts. Mark content older than 1 year as potentially outdated.*
```

- [ ] **Step 4: Update the frontmatter `description` to reflect the new behaviour**

Change the existing description line in the frontmatter:

```yaml
description: Web research on a given topic. Invokes the research subagent, saves a structured report to docs/research/ if that directory exists in the project, and returns a concise summary. Trigger on /research <topic>.
```

to:

```yaml
description: Web research on a given topic. Asks the user for audience, goal, and scope before researching; invokes the research subagent with a focused brief; saves a structured report to docs/research/ if that directory exists; returns a concise summary. Trigger on /research <topic>.
```

- [ ] **Step 5: Verify all step numbers in the document are sequential and references are consistent**

Read the full file once more. Confirm:
- Steps are numbered 1 → 6 with no gaps or duplicates
- The "Output format example" section still references the correct file naming convention (no changes needed there)
- The "Error handling" section is still valid (no changes needed there)

- [ ] **Step 6: Manual verification by invoking the skill**

In a new conversation, run `/research test topic about Rust async runtimes`. Verify:
- Claude asks the audience question first (and only that question)
- After answering, Claude asks the goal question
- After answering, Claude asks the scope question
- After all three answers, Claude invokes the research agent with a reshaped brief (visible in the tool call) that incorporates the answers — not just the raw topic

If any of these fail, return to the relevant step and adjust the SKILL.md wording.

- [ ] **Step 7: No commit step**

`~/.claude/skills/research/` is not in a git repository (it lives in the user's Claude config dir, not in `/Users/pisitkoolplukpol/Work`). No commit needed. If the user later wants this version-controlled, they can add the file to a personal dotfiles repo separately.

---

## Self-Review

- **Spec coverage:** All three spec requirements (ask 3 questions, reshape prompt, keep format unchanged) are covered by Steps 2–4. ✓
- **Placeholder scan:** No TBDs, all code/markdown blocks are complete. ✓
- **Consistency:** Step renumbering (old 2→3, 3→4, etc.) is internally consistent. ✓
