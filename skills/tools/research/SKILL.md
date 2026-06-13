---
name: research
description: Web research on a given topic. Asks the user for audience, goal, and scope before researching; invokes the research subagent with a focused brief; saves a structured report to docs/research/<tool-subfolder>/ (auto-created by topic) if docs/research/ exists; returns a concise summary. Trigger on /research <topic>.
---

# /research

Web research on a topic. Use this skill when the user invokes `/research <topic>`.

## Workflow

### 1. Parse the topic

Take the user-provided topic from the skill arguments. If no topic was provided, ask: "What would you like me to research?"

### 2. Gather context before researching

Before invoking the research agent, ask the user these three questions **one at a time** (separate messages, wait for each answer before asking the next).

1. **Audience** — "Who will read this research? (e.g., yourself, your team, an external stakeholder)"
2. **Goal** — "What decision or action will this research inform?"
3. **Scope** — "Any specific angle to focus on, or areas to exclude?"

Keep each question short. Accept brief or vague answers — do not re-ask for more detail. If the user says "skip" or "no preference" for any question, record that and move on.

If the user has already provided some of this context in their original `/research` invocation (e.g., they wrote "/research X for my team to decide Y"), do not re-ask for that piece — only ask for the missing ones.

### 3. Generate a slug for the filename

From the topic, generate a kebab-case slug:
- Lowercase
- Hyphens replace spaces and punctuation
- Maximum 40 characters
- Strip leading/trailing hyphens

Examples:
- "Next.js app router caching" → `nextjs-app-router-caching`
- "Zod vs Yup for runtime validation" → `zod-vs-yup-for-runtime-validation`

### 4. Invoke the research agent

Synthesize the topic and the three answers (audience, goal, scope) into a single focused research brief. Do NOT just concatenate them — rewrite the research question so it reflects the audience, the decision it will inform, and any scope constraints.

Example:
- Raw topic: "how can Kiro CLI be better"
- Audience: "Kiro product team"
- Goal: "send as feedback to influence their roadmap"
- Scope: "focus on CLI gaps vs IDE, skip pricing"
- Reshaped brief: "Research specific feature gaps between Kiro CLI and Kiro IDE that affect developer productivity. Focus on capabilities available in the IDE but missing from the CLI. Exclude pricing analysis. Output will be read by the Kiro product team as roadmap feedback, so findings must be concrete and actionable."

Use the `Agent` tool with `subagent_type: "general-purpose"`, passing the research methodology together with the reshaped brief as the prompt:

> *You are a web research agent. Research the topic below and produce a structured markdown report: decompose it into 3-5 sub-questions, WebSearch each, WebFetch the top 2-3 results per question, then synthesize a report with sections: Summary, Key Findings (with inline citations), Trade-offs / Caveats, Sources. Always cite URLs. Flag conflicts. Mark content older than 1 year as potentially outdated.*
>
> *Topic: <reshaped brief>*

Wait for the agent to return the full report.

### 5. Decide where to save the report

The canonical research location is `/Users/pisitkoolplukpol/Work/my-superpowers/docs/research/`.

Check it exists:
```bash
test -d /Users/pisitkoolplukpol/Work/my-superpowers/docs/research && echo "exists" || echo "missing"
```

- **If it does not exist:** print the full report inline instead. Do not silently swallow the report.
- **If it exists:** determine a subfolder from the topic.

**Subfolder logic:**
From the topic, extract the primary tool or technology name (e.g., "Kiro CLI headless mode" → `kiro`, "Claude Code hooks" → `claude-code`, "SwiftUI performance" → `swiftui`, "Next.js caching" → `nextjs`, "Jira MCP server" → `mcp`). Convert to kebab-case. If no clear tool/technology is identifiable, use no subfolder.

Create the subfolder if needed, then save:
```bash
mkdir -p /Users/pisitkoolplukpol/Work/my-superpowers/docs/research/<subfolder>
```

- **With subfolder:** save to `/Users/pisitkoolplukpol/Work/my-superpowers/docs/research/<subfolder>/YYYY-MM-DD-<slug>.md`.
- **Without subfolder:** save to `/Users/pisitkoolplukpol/Work/my-superpowers/docs/research/YYYY-MM-DD-<slug>.md`.

### 6. Return a summary to the user

After saving (or printing), return a concise 3-5 sentence summary of the findings to the main conversation, plus:
- The file path if saved, OR
- A note that the report was printed inline because no `docs/research/` directory was found

## Error handling

- **Agent returns empty output:** surface this to the user with the raw output. Do not pretend the research succeeded.
- **Agent asks a clarifying question:** relay the question to the user verbatim; wait for their answer before re-invoking the agent.
- **File write fails:** surface the error and print the full report inline as a fallback.

## Output format example

When saved to file:

> Research saved to `docs/research/2026-05-24-nextjs-app-router-caching.md`.
>
> **Summary:** [3-5 sentence summary of findings]

When printed inline:

> No `docs/research/` directory found; printing the report inline.
>
> [full report]
