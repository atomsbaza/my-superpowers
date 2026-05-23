---
name: research
description: Web research on a given topic. Invokes the research subagent, saves a structured report to docs/research/ if that directory exists in the project, and returns a concise summary. Trigger on /research <topic>.
---

# /research

Web research on a topic. Use this skill when the user invokes `/research <topic>`.

## Workflow

### 1. Parse the topic

Take the user-provided topic from the skill arguments. If no topic was provided, ask: "What would you like me to research?"

### 2. Generate a slug for the filename

From the topic, generate a kebab-case slug:
- Lowercase
- Hyphens replace spaces and punctuation
- Maximum 40 characters
- Strip leading/trailing hyphens

Examples:
- "Next.js app router caching" → `nextjs-app-router-caching`
- "Zod vs Yup for runtime validation" → `zod-vs-yup-for-runtime-validation`

### 3. Invoke the research agent

Use the `Agent` tool with `subagent_type: "research"`. Pass the topic as the prompt:

> "Research the following topic and produce a structured markdown report following your standard methodology: <topic>"

Wait for the agent to return the full report.

> **Note:** If you see "Agent type 'research' not found", this means the research agent was registered after this session started. Fall back to `subagent_type: "general-purpose"` and include these instructions in the prompt:
>
> *You are a web research agent. Decompose the topic into 3-5 sub-questions, WebSearch each, WebFetch the top 2-3 results per question, then synthesize a markdown report with sections: Summary, Key Findings (with inline citations), Trade-offs / Caveats, Sources. Always cite URLs. Flag conflicts. Mark content older than 1 year as potentially outdated.*

### 4. Decide whether to save the report

Check whether `docs/research/` exists in the current working directory:

```bash
test -d docs/research && echo "exists" || echo "missing"
```

- **If it exists:** save the report to `docs/research/YYYY-MM-DD-<slug>.md` using today's date. Use the `Write` tool.
- **If it does not exist:** do NOT create the directory. Print the full report inline in the conversation instead. Do not silently swallow the report.

### 5. Return a summary to the user

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
