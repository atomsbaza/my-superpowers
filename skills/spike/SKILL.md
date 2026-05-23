---
model: opus
name: spike
description: Runs a time-boxed technical investigation to answer a specific unknown before implementation begins. Use when you need to validate a technical approach, evaluate a library or API, investigate feasibility, or answer "can we do X?" before committing to building it. Produces a written findings report with a clear recommendation.
---

# Technical Spike

A spike answers one specific technical question so you can make an informed implementation decision. Unlike a prototype (which produces throwaway code), a spike produces a **written findings report** with a clear recommendation.

## When to use

- "Can WatchConnectivity do X?" — feasibility question
- "Should we use library A or B?" — evaluation question
- "How does this API work?" — exploration question
- "What's the performance impact of X?" — measurement question
- "Is approach X even possible on this platform?" — constraint question

## Process

1. **Clarify the question** — if the spike goal is vague, sharpen it to one specific question before starting. A spike with two questions is two spikes.

2. **Set a timebox** — agree on the time limit (default: 2 hours). If the answer isn't clear within the timebox, document what was found and escalate.

3. **Explore the codebase** — read existing code, CLAUDE.md, and relevant docs to understand the current context before investigating.

4. **Investigate** — read documentation, test the API, write the minimum code needed to answer the question. Use the existing project's stack — don't introduce new dependencies just for a spike.

5. **Write the report** using the template below.

6. **Save** to `docs/spikes/YYYY-MM-DD-<slug>-spike.md`

7. **Present the recommendation** — state clearly: go / no-go / needs more investigation.

8. **Update Logseq wiki** if the spike resolves a key unknown in the project page.

## Spike report template

```markdown
# Spike: [Question Title]

**Date:** YYYY-MM-DD
**Timebox:** X hours
**Status:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete
**Project:** [project name]

## Question

The single specific question this spike answers:
> "Can we / should we / how do we [X]?"

## Why this matters

What decision does this unblock? What happens if we don't answer it?

## Investigation

### What was tried
1. [Step taken + what was learned]
2. [Step taken + what was learned]
3. [Proof of concept / test code if written]

### Findings
[Clear description of what was discovered — facts, not opinions]

### Evidence
[Code snippets, benchmark results, API responses, or links to docs that support the findings]

## Recommendation

**Decision:** GO | NO-GO | NEEDS MORE INVESTIGATION

**Rationale:** [Why this recommendation follows from the findings]

**If GO — implementation notes:**
- [Key constraint or pattern to follow]
- [Gotcha discovered during spike]

**If NO-GO — alternatives:**
- [Alternative A — brief assessment]
- [Alternative B — brief assessment]

## Open questions
[Anything that came up during the spike that's out of scope but worth tracking]

## Time spent
[Actual time vs timebox]
```

## Rules

- **One question per spike** — if you discover a second question mid-spike, park it and finish the first
- **Timebox is real** — if the timebox is reached, write up what you found and flag it as incomplete rather than extending indefinitely
- **Minimum viable proof** — write only enough code to answer the question; spike code is not production code and should not be merged
- **Recommendation is mandatory** — findings without a recommendation are not complete
- **Save the report** — the value of a spike is the written output, not the investigation itself

## Agent Integrations

### After saving the spike report (Step 6)
Check if `~/Documents/Project Docs/pages/Projects___<ProjectName>.md` exists and the spike Status is `🟢 Complete` before spawning. If both conditions hold, spawn `wiki-updater`. Pass it: the spike file path, the project name, the question answered, and the GO/NO-GO recommendation.

Skip if Status is still `🟡 In Progress` or the page doesn't exist.

> **Before spawning:** If wiki-updater returns empty or errors, note it — the spike report file is the authoritative record regardless.
