# Research Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a global web-research subagent invokable via `/research <topic>` and proactively by Claude Code when external context is needed.

**Architecture:** Two markdown files — (1) a subagent definition with `WebSearch` + `WebFetch` tools that runs a decompose→search→fetch→synthesize loop, and (2) a `/research` skill that orchestrates manual invocation, saves output to `docs/research/`, and returns a summary.

**Tech Stack:** Claude Code agent files (`~/.claude/agents/`), skill files (`~/.claude/skills/`), markdown with YAML frontmatter. No code, no dependencies.

---

## File Structure

```
~/.claude/agents/research.md              # subagent definition (system prompt + frontmatter)
~/.claude/skills/research/SKILL.md        # /research skill orchestration
```

Both files follow the existing conventions in those directories — frontmatter with `name`, `description`, `model`, and `tools`, followed by the system prompt body. Skill files use `SKILL.md` (uppercase) as the entry point, matching the pattern of `~/.claude/skills/scrutinize/SKILL.md` and others.

---

### Task 1: Create the research subagent

**Files:**
- Create: `~/.claude/agents/research.md`

- [ ] **Step 1: Write the subagent file**

Create `~/.claude/agents/research.md` with this exact content:

```markdown
---
model: sonnet
name: research
description: Web research agent. Use proactively before recommending a library, framework, or approach when current context lacks information, and when the user asks to "research X", "look up X", or "find out about X". Returns a structured markdown report with cited sources.
tools: WebSearch, WebFetch
---

You are a web research agent. You produce structured, well-cited research reports on topics you are given.

## Methodology

Follow these four phases in order. Do not skip phases.

### Phase 1 — Decompose

Break the topic into 3-5 specific sub-questions. A vague topic like "Next.js app router" becomes:
- What changed from pages router?
- What are the performance implications?
- How does caching behave?
- What are common migration pitfalls?

If the topic is too broad to decompose into clear sub-questions (e.g., "tell me about React"), ask the user ONE clarifying question before proceeding. Do not produce a shallow report.

### Phase 2 — Search

Run `WebSearch` for each sub-question. Prioritize:
- Official documentation
- GitHub repositories and release notes
- Authoritative blog posts (framework authors, well-known engineers)

Deprioritize SEO content farms, listicles, and aggregators.

### Phase 3 — Fetch

Run `WebFetch` on the top 2-3 results per sub-question. Extract only the content relevant to the sub-question. Do not summarize entire pages.

If a fetch fails or returns no useful content, skip it and note the URL as unreachable. Do not stop the whole research.

### Phase 4 — Synthesize

Produce a markdown report in exactly this format:

\`\`\`markdown
# Research: <topic>

## Summary

3-5 sentence overview of findings.

## Key Findings

- Finding stated clearly, with inline citation [Source Title](url)
- Another finding [Source Title](url)

## Trade-offs / Caveats

- Any conflicts between sources, limitations, or outdated information
- Note publication dates when content is older than ~1 year

## Sources

- [Title](url) — one-line description of what this source contributed
\`\`\`

## Guardrails

- **Always cite.** Never state a fact without an inline link to a source. If you cannot find a source, say so explicitly.
- **Flag conflicts.** When sources disagree, surface the disagreement in "Trade-offs / Caveats" — do not silently pick one.
- **Mark stale content.** If a source is older than 1 year, note its date and flag it as potentially outdated.
- **No hallucination.** If WebSearch returns no results for a sub-question, try alternative search terms once. If still nothing, state this in the report rather than inventing content.
```

- [ ] **Step 2: Verify the file is loadable**

Run: `cat ~/.claude/agents/research.md | head -5`
Expected: First 5 lines show the YAML frontmatter starting with `---` and `model: sonnet`.

- [ ] **Step 3: Verify Claude Code recognizes the agent**

In a new Claude Code session, ask: "List available agents." Expected: `research` appears in the list with the description from the frontmatter.

- [ ] **Step 4: Commit (if `~/.claude` is a git repo)**

Run: `cd ~/.claude && git status` — if it is a git repo, run:
```bash
cd ~/.claude && git add agents/research.md && git commit -m "feat: add research subagent"
```
If `~/.claude` is not a git repo, skip the commit step.

---

### Task 2: Create the /research skill

**Files:**
- Create: `~/.claude/skills/research/SKILL.md`

- [ ] **Step 1: Create the skill directory**

Run: `mkdir -p ~/.claude/skills/research`
Expected: directory exists, no error.

- [ ] **Step 2: Write the skill file**

Create `~/.claude/skills/research/SKILL.md` with this exact content:

```markdown
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

### 3. Invoke the research subagent

Use the `Agent` tool with `subagent_type: "research"`. Pass the topic as the prompt. Example prompt:

> "Research the following topic and produce a structured markdown report following your standard methodology: <topic>"

Wait for the agent to return the full report.

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
```

- [ ] **Step 3: Verify the skill is registered**

In a new Claude Code session, check that `research` appears in the available-skills list. Expected: `/research` is invokable.

- [ ] **Step 4: Commit (if `~/.claude` is a git repo)**

Run: `cd ~/.claude && git status` — if it is a git repo:
```bash
cd ~/.claude && git add skills/research/SKILL.md && git commit -m "feat: add /research skill"
```

---

### Task 3: Manual verification

**Files:** none (verification only)

- [ ] **Step 1: Test happy path with file save**

In a directory that has `docs/research/`:
```bash
mkdir -p /tmp/research-test/docs/research && cd /tmp/research-test
```
Start a Claude Code session there and run: `/research Next.js 15 app router caching`

Expected:
- Research subagent spawns
- A file `docs/research/2026-05-24-nextjs-15-app-router-caching.md` is created
- Summary returned in conversation
- Report has the four sections (Summary, Key Findings, Trade-offs, Sources) with inline citations

- [ ] **Step 2: Test happy path without docs/research/**

In `/tmp` (no `docs/research/` dir):
```bash
cd /tmp
```
Run: `/research Zod vs Yup`

Expected:
- Full report printed inline
- Note explains no `docs/research/` dir was found
- No directory created automatically

- [ ] **Step 3: Test broad topic clarification**

Run: `/research react`

Expected: Agent asks one clarifying question (e.g., "React has many facets — are you interested in performance, state management, server components, or something else?") rather than producing a shallow report.

- [ ] **Step 4: Test proactive spawning**

In any Claude Code session, ask: "Which is better for runtime validation in TypeScript, Zod or Yup?"

Expected: Claude Code spawns the `research` subagent automatically (visible in tool calls) before answering, because the description triggers on "before recommending a library".

- [ ] **Step 5: Test unreachable URL handling**

This is hard to force deterministically. Spot-check by running a research topic likely to surface broken or paywalled links (e.g., niche enterprise topics). Expected: report continues, notes the unreachable source, does not crash.

- [ ] **Step 6: Record verification result**

If all steps pass, the implementation is done. If any step fails, debug the specific failure — most likely a frontmatter typo, a wrong tool name, or a path issue. Re-run the failing step after fixing.

---

## Self-review notes

- **Spec coverage:** Architecture (Tasks 1 & 2), research methodology (Task 1 system prompt), data flow (Task 2 workflow), error handling (Task 1 guardrails + Task 2 error handling section), testing (Task 3 manual checklist), file list (File Structure section) — all covered.
- **No placeholders:** all code blocks and frontmatter values are concrete; no TBDs.
- **Type/name consistency:** subagent is `research` in both files; skill is `research` matching the agent name; tools are `WebSearch, WebFetch` consistently; output format is identical across spec, agent file, and skill file.
