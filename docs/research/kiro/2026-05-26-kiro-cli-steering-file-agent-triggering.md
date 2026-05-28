# Research: Kiro CLI — Steering Files and Prompt-Driven Agent Control

## Summary

Steering files in Kiro are markdown documents that inject persistent project context into AI interactions — they do **not** route or trigger specific agents based on user prompt patterns. Agent selection in Kiro is primarily manual. However, Kiro provides four distinct mechanisms that together approximate prompt-sensitive behavior: the `inclusion: auto` steering mode (which matches steering documents to requests using a description field), Agent Skills (which auto-activate against skill descriptions), subagent delegation (parent agents delegate to named subagents based on their descriptions), and the `userPromptSubmit` hook (which injects shell-generated context before every prompt). Understanding which mechanism to use for a given goal is the central design question.

---

## Key Findings

### 1. What Steering Files Are — and Are Not

Steering files provide **persistent knowledge** to Kiro across sessions via markdown documents in `.kiro/steering/` (workspace-level) or `~/.kiro/steering/` (global). They solve the "re-explain everything" problem: once written, Kiro reads them in every subsequent interaction without prompting.

Steering files do **not** route user prompts to different agents. The [agent configuration reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference/) confirms that agent selection is manual — via keyboard shortcut or `/agent swap` commands, not prompt-pattern matching.

### 2. Steering File Format and Syntax

Steering files are standard `.md` files with optional YAML frontmatter at the very top, enclosed in triple dashes. No blank lines are permitted before the frontmatter block. Four inclusion modes are supported:

**Always (default — loads in every interaction):**
```yaml
---
inclusion: always
---

# API Standards
All database operations use Prisma. Never write raw SQL queries.
```

**fileMatch (loads when a file matching the pattern is in context):**
```yaml
---
inclusion: fileMatch
fileMatchPattern: "components/**/*.tsx"
---

# React Component Standards
Use functional components. Co-locate tests in __tests__/ subdirectories.
```

`fileMatchPattern` accepts a single glob string or an array:
```yaml
fileMatchPattern: ["**/*.ts", "**/*.tsx", "**/tsconfig.*.json"]
```

**Manual (on-demand only, via `#steering-file-name` in chat):**
```yaml
---
inclusion: manual
---

# Troubleshooting Guide
[referenced by typing #troubleshooting-guide in a chat message]
```

**Auto (the closest steering has to prompt-pattern matching):**
```yaml
---
inclusion: auto
name: api-design
description: REST API design patterns and conventions. Use when creating or modifying API endpoints.
---

# REST API Standards
...
```

The `auto` mode causes Kiro to evaluate the `description` field against the user's request and include the file when the request is a semantic match. `name` and `description` are both required for `auto` mode.

### 3. The Mechanism Closest to "Which Agent Responds to Which Prompt" — Agent Skills

The mechanism in Kiro that most directly maps prompt content to a specific behavior is **Agent Skills**, not steering files. Skills are stored in `.kiro/skills/` and structured as:

```
skill-name/
├── SKILL.md
└── references/
    └── guide.md
```

`SKILL.md` uses frontmatter:
```yaml
---
name: pr-review
description: Performs a structured pull request review. Use when the user asks to review a PR, check changes, or audit a diff.
---

# PR Review Workflow
1. Run git diff against main
2. Check for test coverage...
```

Two activation paths:
- **Automatic**: Kiro matches the user's request against the skill's `description` field and loads the skill when there is a match.
- **Explicit**: The user types `/skill-name` as a slash command.

The `description` field is the primary activation signal.

### 4. Subagent Delegation — Description-Driven Routing Between Agents

For routing work between multiple full agents, Kiro uses **subagents**. A parent agent can delegate to named subagents via the `subagent` tool. The `description` field of each subagent's configuration is the key signal for when delegation occurs.

Parent agent config:
```json
{
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["aws-fact-checker", "security-scanner"],
      "trustedAgents": ["aws-fact-checker"]
    }
  }
}
```

Each subagent's `description` field drives when delegation fires:
```json
{
  "name": "aws-fact-checker",
  "description": "AWS documentation fact-checker. Use when blog content makes claims about AWS service features, limits, pricing, or configurations that need verification."
}
```

Vague descriptions produce unreliable delegation; specific action-oriented descriptions are essential.

### 5. The `userPromptSubmit` Hook — Context Injection, Not Routing

The `userPromptSubmit` hook fires a shell command **before every prompt is processed**. Its output is injected into conversation context. This is not routing — it cannot redirect to a different agent — but it can dynamically enrich the agent's context based on current state.

```json
{
  "hooks": {
    "userPromptSubmit": [
      {
        "command": "grep -r 'draft: true' content/posts/ | head -5 || echo 'No drafts found'",
        "timeout_ms": 5000,
        "cache_ttl_seconds": 60
      }
    ]
  }
}
```

Other hook types: `agentSpawn`, `preToolUse` (can block tool execution with exit code 2), `postToolUse`, and `stop`.

### 6. Connecting Steering Files to Custom Agents

Steering files do **not** auto-load into custom agents. You must explicitly include them via the agent's `resources` field using a glob:

```json
{
  "resources": [
    "file://.kiro/steering/**/*.md",
    "skill://.kiro/skills/**/SKILL.md"
  ]
}
```

`file://` paths load content at startup. `skill://` paths load only metadata at startup and fetch full content on demand — important for large reference documents.

### 7. File Locations and Priority

| Location | Scope | Override Priority |
|---|---|---|
| `.kiro/steering/` | Current workspace | Highest |
| `~/.kiro/steering/` | All workspaces (global) | Lower |
| `.kiro/agents/` | Current workspace agents | Highest |
| `~/.kiro/agents/` | Global agents | Lower |

The `AGENTS.md` standard (placing a file named `AGENTS.md` in workspace root or `~/.kiro/steering/`) is always included automatically without frontmatter configuration.

---

## Trade-offs / Caveats

- **`inclusion: auto` is documented but has known reliability issues.** GitHub issue [#7787](https://github.com/kirodotdev/Kiro/issues/7787) documents that Kiro's own agent system prompt was unaware of `inclusion: auto` at time of filing. The feature is real, but verify it is working in your Kiro version.

- **`inclusion: fileMatch` has reported bugs.** GitHub issue [#1643](https://github.com/kirodotdev/Kiro/issues/1643) reports that fileMatch based on file extension was not being applied correctly. Issue [#6171](https://github.com/kirodotdev/Kiro/issues/6171) reports global steering files with `fileMatch` not injecting into agent context.

- **Steering files with `inclusion: always` do not auto-inject into subagent context.** GitHub issue [#7131](https://github.com/kirodotdev/Kiro/issues/7131) — this behavior does not currently happen without explicit `resources` configuration.

- **Steering vs. Skills distinction is conceptual.** Steering = "the rulebook" (what standards to follow). Skills = "the procedure" (how to execute a specific task). The two are complementary, not interchangeable.

- **No native prompt-pattern routing exists.** If you want strict "when user says X, invoke agent Y," Kiro does not have this as a declarative feature. The closest approach is combining `inclusion: auto` (for steering context) with well-described Skills (for auto-activation) and subagent delegation (for agent-to-agent handoff).

---

## Practical Setup: Auto-Triggering an SA Agent (Real Example)

This section documents the orchestrator pattern applied to an actual Kiro CLI setup with `chat` and `coder` agents already in place.

### Existing agent setup (baseline)

`~/.kiro/agents/chat.json`:
```json
{
  "name": "chat",
  "description": "Quick chat, questions, and lightweight tasks",
  "model": "anthropic.claude-haiku-3-5-20241022-v1:0",
  "keyboardShortcut": "alt+1"
}
```

`~/.kiro/agents/coder.json`:
```json
{
  "name": "coder",
  "description": "Code implementation, debugging, and multi-file changes",
  "model": "anthropic.claude-sonnet-4-20250514-v1:0",
  "keyboardShortcut": "alt+2"
}
```

### Step 1 — Create the SA agent

`~/.kiro/agents/sa.json`:
```json
{
  "name": "sa",
  "description": "Solution Architect agent. Use when the user wants to design a system, plan architecture, define components or services, choose a tech stack, create a system diagram, write ADRs, or think through scalability and trade-offs.",
  "model": "anthropic.claude-opus-4-7-v1:0",
  "prompt": "You are a Solution Architect. When asked to design a system, always start by clarifying requirements, then define components, data flow, and trade-offs before recommending a stack.",
  "tools": ["read", "write", "thinking", "knowledge", "report"]
}
```

### Step 2 — Create the orchestrator

`~/.kiro/agents/orchestrator.json`:
```json
{
  "name": "orchestrator",
  "description": "Main entry point. Routes to the right specialist automatically.",
  "model": "anthropic.claude-haiku-3-5-20241022-v1:0",
  "tools": ["delegate", "thinking"],
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["sa", "coder", "chat"],
      "trustedAgents": ["sa", "coder", "chat"]
    }
  },
  "prompt": "You are a router. Read the user's request and immediately delegate to the correct agent — do not answer yourself:\n- 'sa' for system design, architecture, ADRs, tech stack decisions\n- 'coder' for writing code, debugging, implementing features\n- 'chat' for quick questions, explanations, lightweight tasks\nDelegate without commentary."
}
```

### Step 3 — Set orchestrator as default

In `~/.kiro/settings/cli.json`, add:
```json
{
  "defaultAgent": "orchestrator"
}
```

### How delegation flows

```
User: "I want to design system xxx"
    ↓
orchestrator (Haiku — cheap, fast routing only)
    ↓ matches "sa" description
delegates to sa agent (Opus)
    ↓
SA agent handles the design work
```

```
User: "Fix the bug in auth.ts"
    ↓
orchestrator
    ↓ matches "coder" description
delegates to coder agent (Sonnet)
```

### Key rules for reliable routing

1. **Write descriptions as `"Use when the user wants to..."`** with concrete action verbs.
2. **Keep descriptions distinct** — overlapping descriptions produce unreliable routing.
3. **The orchestrator should never answer directly** — its only job is to route. State this explicitly in the `prompt` field.
4. **Use a cheap model for the orchestrator** (Haiku) — it only reads one message and calls delegate; Opus/Sonnet here is wasteful.
5. **Match the model ID format** to your existing agents — AWS Bedrock model IDs are region-specific and must match exactly.

---

## Sources

- [Steering — CLI Docs — Kiro](https://kiro.dev/docs/cli/steering/)
- [Steering — IDE Docs — Kiro](https://kiro.dev/docs/steering/)
- [Agent Configuration Reference — Kiro](https://kiro.dev/docs/cli/custom-agents/configuration-reference/)
- [Hooks — CLI Docs — Kiro](https://kiro.dev/docs/cli/hooks/)
- [Agent Skills — CLI Docs — Kiro](https://kiro.dev/docs/cli/skills/)
- [Building Opinionated AI Assistants with Kiro CLI Agents — Mladen Trampic](https://mladen.trampic.info/posts/2025-09-07-creating-kiro-cli-agents/)
- [The difference between Kiro's Steering and AgentSkills — DEV Community / AWS Builders](https://dev.to/aws-builders/aws-differences-between-kiro-steering-and-agentskills-kiro-5f3i)
- [GitHub Issue #7787: inclusion: auto not recognized](https://github.com/kirodotdev/Kiro/issues/7787)
- [GitHub Issue #1643: fileMatch by extension not applied](https://github.com/kirodotdev/Kiro/issues/1643)
- [GitHub Issue #7131: always steering not injected into subagent context](https://github.com/kirodotdev/Kiro/issues/7131)
