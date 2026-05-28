# Research Agent Design

**Date:** 2026-05-24
**Status:** Approved

## Overview

A web research capability for Claude Code consisting of two components:

1. A custom subagent (`~/.claude/agents/research.md`) that does the actual research loop using `WebSearch` and `WebFetch`
2. A `/research` skill (`~/.claude/skills/research/`) that provides manual invocation, output formatting, and file persistence

The agent is also available for proactive use — Claude Code can spawn it autonomously when it needs external context before making a recommendation.

## Components

### 1. Research Subagent (`~/.claude/agents/research.md`)

**Frontmatter:**
```yaml
model: sonnet
name: research
description: >
  Web research agent. Use proactively when external context is needed before
  recommending a library, framework, or approach, or when the user asks to
  "research X", "look up X", or "find out about X". Returns a structured
  markdown report with cited sources.
tools: WebSearch, WebFetch
```

**System prompt behavior:**

The agent follows a four-phase loop:

1. **Decompose** — break the topic into 3-5 specific sub-questions
2. **Search** — `WebSearch` each sub-question, prioritize official docs, GitHub repos, authoritative sources
3. **Fetch** — `WebFetch` top 2-3 results per sub-question, extract relevant content only
4. **Synthesize** — produce structured markdown report

**Output format:**
```markdown
# Research: <topic>

## Summary
3-5 sentence overview of findings.

## Key Findings
- Finding with inline citation [Source](url)

## Trade-offs / Caveats
- Any conflicts, limitations, or outdated information noted

## Sources
- [Title](url) — one-line description
```

**Guardrails:**
- Always cite URLs; never state facts without a source
- Mark content older than 1 year as potentially outdated
- Flag conflicting results rather than picking one silently
- If topic is too broad, ask one clarifying question before proceeding

### 2. Research Skill (`~/.claude/skills/research/`)

**Entry point:** `skill.md`

**Manual trigger:** `/research <topic>`

**Behavior:**
1. Accept topic from args
2. Invoke the research subagent via `Agent` tool with the topic
3. If `docs/research/` directory exists in the project, save output to `docs/research/YYYY-MM-DD-<slug>.md`
4. Return a concise summary (3-5 sentences) to the main conversation with a link to the saved file

**Slug generation:** lowercase, hyphens, max 40 chars (e.g., `nextjs-app-router-caching`)

## Data Flow

```
User: /research <topic>
  → skill.md orchestrates
    → Agent(research subagent, tools: WebSearch + WebFetch)
      → Phase 1: decompose topic into sub-questions
      → Phase 2: WebSearch each sub-question
      → Phase 3: WebFetch top results
      → Phase 4: synthesize structured report
    → returns markdown report
  → skill saves to docs/research/YYYY-MM-DD-<slug>.md (if dir exists)
  → skill returns summary + file path to main conversation
```

## Error Handling

- **WebSearch fails or returns no results:** agent notes this in the report and tries alternative search terms before giving up
- **WebFetch fails on a URL:** skip that source, note it as unreachable, continue with others
- **Topic too broad:** agent asks one clarifying question rather than producing a shallow report
- **No `docs/research/` directory:** skill prints the full report inline instead of saving to file — no silent failure, no auto-creating directories in unknown repos
- **Agent returns empty/malformed output:** skill surfaces the raw output rather than swallowing it

## Testing

Manual verification checklist (no automated tests needed for agent/skill files):

- [ ] `/research "Next.js app router vs pages router"` — produces structured report with citations
- [ ] `/research "react"` (intentionally broad) — agent asks a clarifying question
- [ ] Proactive spawn: ask Claude Code "which is better, Zod or Yup?" — research agent should be spawned automatically
- [ ] Run in a project with `docs/research/` dir — file is saved with correct name
- [ ] Run in a project without `docs/research/` dir — report printed inline, no error
- [ ] One unreachable URL in results — report notes it, continues without crashing

## Files to Create

```
~/.claude/agents/research.md         # subagent definition
~/.claude/skills/research/
  skill.md                           # skill orchestration prompt
```

No code files. Both components are markdown prompt files following existing conventions in `~/.claude/agents/` and `~/.claude/skills/`.
