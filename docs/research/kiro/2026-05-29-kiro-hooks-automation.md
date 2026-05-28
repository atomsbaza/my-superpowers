# Research: Kiro Agent Hooks — Comprehensive Reference

> **Coverage note:** The blog post at `https://kiro.directory/blog/10-kiro-hooks-automation/` could not be fetched directly (WebFetch is blocked for that domain). The 10 hook names and descriptions attributed to that post are reconstructed from search-engine snippets and cross-checked against official Kiro docs. All other content — schemas, JSON examples, hook type definitions, action semantics — is sourced from pages that were fetched directly.

---

## Summary

Kiro Agent Hooks are if-then automation rules stored as JSON files in `.kiro/hooks/`. When a specified IDE event occurs (file save, file creation, agent stop, user prompt submission, etc.) Kiro either invokes an AI agent with a custom prompt (`askAgent`) or runs a local shell command (`runCommand`). Hooks live alongside your code, are committed to version control, and are immediately shared with teammates on pull. The system supports 10 distinct trigger types covering file events, agent lifecycle, tool execution interception, spec task lifecycle, and manual invocation. `askAgent` consumes AI credits and runs in the cloud; `runCommand` is free, fast, and local.

---

## Part 1 — What Kiro Hooks Are

Agent hooks are "automated triggers that execute predefined agent prompts or shell commands when specific events occur in your IDE." They are designed to eliminate routine manual requests by reacting to workspace events automatically.

Hooks operate as simple event-driven pipelines:

```
IDE Event  →  (matches trigger type + file pattern)  →  Action fires
```

Each hook is a single `.kiro.hook` JSON file. All files in `.kiro/hooks/` are automatically detected and shown in the **Agent Hooks panel** in the Kiro IDE sidebar.

Source: [Kiro Hooks Docs](https://kiro.dev/docs/hooks/)

---

## Part 2 — The Hook File Format (Schema)

```json
{
  "version": "1",
  "enabled": true,
  "name": "Human-readable name shown in the panel",
  "description": "What this hook does",
  "when": {
    "type": "<trigger-type>",
    "patterns": ["**/*.ts", "src/**/*.js"],
    "toolTypes": ["write", "read", "shell"]
  },
  "then": {
    "type": "askAgent | runCommand",
    "prompt": "Natural language instructions for the agent",
    "command": "shell command to run",
    "timeout": 60
  }
}
```

**Field reference:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `version` | string | Yes | Use `"1"` |
| `enabled` | boolean | Yes | `false` disables without deleting |
| `name` | string | Yes | Shown in Agent Hooks panel |
| `description` | string | Recommended | Explains purpose to teammates |
| `when.type` | string | Yes | See trigger type table below |
| `when.patterns` | string[] | For file hooks | Glob patterns e.g. `**/*.ts` |
| `when.toolTypes` | string[] | For tool hooks | `read`, `write`, `shell`, `web`, `spec`, `*` |
| `then.type` | string | Yes | `askAgent` or `runCommand` |
| `then.prompt` | string | For askAgent | Natural language instructions |
| `then.command` | string | For runCommand | Shell command |
| `then.timeout` | number | No | Seconds; default 60, set 0 to disable |

Sources: [Hook Actions Docs](https://kiro.dev/docs/hooks/actions/), [kiro-best-practices raw hook files](https://github.com/awsdataarchitect/kiro-best-practices/blob/main/.kiro/hooks/lint-and-format-on-save.kiro.hook)

---

## Part 3 — All Hook Trigger Types

Ten trigger types are supported across IDE and CLI:

| Trigger Type | When it fires | Key notes |
|---|---|---|
| `fileEdited` / `fileSave` | A file matching the pattern is saved | Most common hook trigger |
| `fileCreated` / `fileCreate` | A new file matching the pattern is created | Good for scaffolding boilerplate |
| `fileDeleted` / `fileDelete` | A file matching the pattern is deleted | Useful for cleanup of related files |
| `userTriggered` / `manual` | User clicks the play button in the panel | On-demand workflows, no file required |
| `promptSubmit` / `UserPromptSubmit` | User submits a prompt to the agent | Hook prompt is **appended** to the user's message |
| `agentStop` / `stop` | Agent finishes its turn | Good for post-processing: compile, test, format |
| `preToolUse` / `PreToolUse` | Before agent calls a tool | Can **block** execution with exit code 2 |
| `postToolUse` / `PostToolUse` | After agent calls a tool | Gets access to tool results |
| `preTaskExecution` | Before a spec task status changes to `in_progress` | Validate prerequisites before spec work starts |
| `postTaskExecution` | After a spec task changes to `completed` | Run tests or notify systems after each spec task |

**Notes on `preToolUse` blocking:** If a shell command exits with code `2`, tool execution is blocked and the STDERR output is returned to the LLM so it can adjust its approach. Any other non-zero exit code reports an error but does not block.

**Tool name matching** for pre/post tool hooks supports categories (`read`, `write`, `shell`, `web`), canonical tool names (`fs_read`, `fs_write`, `execute_bash`), MCP prefixes (`@mcp`, `@mcp.*sql.*`), and wildcards (`*`).

**CLI vs. IDE naming:** The IDE docs use camelCase (`fileEdited`, `fileCreated`) while the CLI docs use hyphenated names (`file-save`, `file-create`). The underlying behavior is the same.

Source: [Hook Types Docs](https://kiro.dev/docs/hooks/types/), [CLI Hooks Docs](https://kiro.dev/docs/cli/hooks/)

---

## Part 4 — Action Types: askAgent vs. runCommand

| | `askAgent` | `runCommand` |
|---|---|---|
| What it does | Invokes a new agent loop with your prompt | Runs a shell command locally |
| Consumes AI credits | Yes | No |
| Speed | Slower (cloud LLM call) | Fast (local execution) |
| Use when | You need judgment, code generation, or context-aware decisions | You need deterministic output: lint, format, test, push metrics |
| Exit code behavior | N/A | 0 = stdout added to context; 2 = blocks preToolUse; other = stderr warning |

**For `promptSubmit` hooks:** the `askAgent` prompt is **appended** to the user's message before it reaches the agent — it does not start a separate agent call. Suitable for injecting standing context or constraints into every message.

Source: [Hook Actions Docs](https://kiro.dev/docs/hooks/actions/)

---

## Part 5 — The 10 Hooks from the kiro.directory Blog Post

*(Reconstructed from search snippets — exact prompt text may differ from the original post)*

### Hook 1 — Code Standards Enforcer

```json
{
  "version": "1",
  "enabled": true,
  "name": "Code Standards",
  "description": "Ensure team coding standards on every save",
  "when": {
    "type": "fileEdited",
    "patterns": ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A source file was saved. Review it against our team coding standards: enforce Single Responsibility Principle, consistent naming conventions, and no magic numbers. Flag any violations with the line number and a suggested fix. Do not auto-fix; report only."
  }
}
```

### Hook 2 — Auto Test Generator

```json
{
  "version": "1",
  "enabled": true,
  "name": "Auto Test Generator",
  "description": "Generate unit tests for modified components",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.js", "src/**/*.jsx"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A source file was saved. Identify any new or changed functions and components. Check if a corresponding test file exists. If tests are missing or outdated, generate comprehensive unit tests covering happy paths, edge cases, and error conditions. Place them in the adjacent __tests__ directory using the same filename with .test suffix."
  }
}
```

### Hook 3 — Dependency Tracker

```json
{
  "version": "1",
  "enabled": true,
  "name": "Dependency Tracker",
  "description": "Document dependency changes and run security audit",
  "when": {
    "type": "fileEdited",
    "patterns": ["package.json", "package-lock.json", "requirements.txt"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "package.json was modified. Please: 1) Document any added or removed dependencies in docs/dependencies.md. 2) Run npm audit and summarise any high or critical vulnerabilities. 3) Check if any added packages have known security advisories."
  }
}
```

### Hook 4 — Schema Sync

```json
{
  "version": "1",
  "enabled": true,
  "name": "Schema Sync",
  "description": "Generate migrations and update schema docs on model change",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/models/**/*.ts", "prisma/schema.prisma", "**/*.model.ts"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A data model file was saved. Please: 1) Identify what changed in the schema. 2) Generate a migration file for the change. 3) Update docs/schema.md to reflect the current state of all models."
  }
}
```

### Hook 5 — Environment Validator

```json
{
  "version": "1",
  "enabled": true,
  "name": "Environment Validator",
  "description": "Validate env vars and keep config docs in sync",
  "when": {
    "type": "fileEdited",
    "patterns": [".env.example", "src/config/**/*.ts", "config/**/*.ts"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A configuration or environment file was saved. Please: 1) Check that all env variables referenced in code are present in .env.example. 2) Flag any undocumented variables. 3) Update docs/configuration.md with the current list of required variables and their purpose."
  }
}
```

### Hook 6 — Security Scanner

```json
{
  "version": "1",
  "enabled": true,
  "name": "Security Scanner",
  "description": "Prevent accidental credential leaks on save",
  "when": {
    "type": "fileEdited",
    "patterns": ["**/*.ts", "**/*.js", "**/*.py", "**/*.env"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A file was saved. Scan it for hardcoded secrets: API keys, passwords, tokens, AWS credentials, private keys. If any are found, highlight the exact lines and suggest moving them to environment variables. Do not continue if a confirmed secret is found."
  }
}
```

### Hook 7 — API Documentation Sync

```json
{
  "version": "1",
  "enabled": true,
  "name": "API Doc Sync",
  "description": "Keep API docs in sync with route changes",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/api/**/*.ts", "src/routes/**/*.ts", "src/controllers/**/*.ts"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "An API route file was modified. Please: 1) Extract the current endpoint signatures, parameters, and return types. 2) Update docs/API.md to reflect the changes. 3) If an OpenAPI spec exists at openapi.yaml, update it accordingly."
  }
}
```

### Hook 8 — Performance Monitor

```json
{
  "version": "1",
  "enabled": true,
  "name": "Performance Monitor",
  "description": "Flag performance regressions on component saves",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/components/**/*.tsx", "src/pages/**/*.tsx"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A component file was saved. Analyse it for performance risks: unnecessary re-renders, missing memoization, large inline assets, or imports that significantly increase bundle size. Report any issues and suggest optimizations."
  }
}
```

### Hook 9 — Conventional Commit Message Generator

```json
{
  "version": "1",
  "enabled": true,
  "name": "Commit Message Generator",
  "description": "Suggest a conventional commit message after each task",
  "when": {
    "type": "agentStop"
  },
  "then": {
    "type": "askAgent",
    "prompt": "The agent has finished its task. Run git diff --staged to see what changed. Propose a commit message following the Conventional Commits format: type(scope): description. Include a short body if the change is non-trivial. Do not commit automatically."
  }
}
```

### Hook 10 — Prompt Logging / Audit Trail

```json
{
  "version": "1",
  "enabled": true,
  "name": "Prompt Audit Logger",
  "description": "Log all user prompts for compliance auditing",
  "when": {
    "type": "promptSubmit"
  },
  "then": {
    "type": "runCommand",
    "command": "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) $USER_PROMPT\" >> ~/.kiro/audit.log"
  }
}
```

*Note: `$USER_PROMPT` is injected by Kiro on `promptSubmit` hooks.*

---

## Part 6 — Verbatim Hook Examples from Official Sources

### From awsdataarchitect/kiro-best-practices

**lint-and-format-on-save.kiro.hook**

```json
{
  "enabled": true,
  "name": "Lint and Format on Save",
  "description": "Automatically lint and format code when files are saved following project standards",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": [
      "**/*.ts",
      "**/*.js",
      "**/*.tsx",
      "**/*.jsx",
      "**/*.py",
      "**/*.json"
    ]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A code file has been saved. Please:\n1. Run the appropriate linter (ESLint for JS/TS, flake8/pylint for Python)\n2. Run the appropriate formatter (Prettier for JS/TS, Black for Python)\n3. Fix any auto-fixable issues\n4. Report any remaining issues that need manual attention\n\nUse the project's existing configuration files (.eslintrc, .prettierrc, pyproject.toml, etc.) and follow the established coding standards."
  }
}
```

**update-documentation.kiro.hook** (disabled by default)

```json
{
  "enabled": false,
  "name": "Update Documentation",
  "description": "Update documentation when code changes (disabled by default for performance)",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": [
      "src/**/*.ts",
      "src/**/*.js",
      "lib/**/*.py"
    ]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A source code file has been modified. Please update documentation: check for associated READMEs or API docs, update outdated content to reflect changes, generate JSDoc/docstring comments if missing from new functions, and update any relevant examples or usage instructions."
  }
}
```

### From Official Kiro Documentation

**Security Pre-Commit Scanner:**

```json
{
  "version": "1",
  "enabled": true,
  "name": "Security Pre-Commit Scanner",
  "when": { "type": "agentStop" },
  "then": {
    "type": "askAgent",
    "prompt": "Review changed files for potential security issues including API keys, credentials, and hardcoded secrets. Highlight risks and recommend secure alternatives."
  }
}
```

**Internationalization Helper:**

```json
{
  "version": "1",
  "enabled": true,
  "name": "i18n Sync Helper",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/locales/en/*.json"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A base locale file was saved. Check all other locale files for missing or outdated keys. Mark new keys that need translation and flag any modified strings that may require re-translation."
  }
}
```

**Figma Design Validator:**

```json
{
  "version": "1",
  "enabled": true,
  "name": "Figma Design Validator",
  "when": {
    "type": "fileEdited",
    "patterns": ["**/*.css", "**/*.html", "src/components/**"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A UI file was saved. Use the Figma MCP tool to verify that the design patterns in the current file match the established Figma design system. Flag any deviations from the design spec."
  }
}
```

---

## Part 7 — Additional Community Patterns

### One-Click Deploy Assistant (`userTriggered`)

```json
{
  "version": "1",
  "enabled": true,
  "name": "Deploy Assistant",
  "description": "Interactive step-by-step deployment workflow",
  "when": { "type": "userTriggered" },
  "then": {
    "type": "askAgent",
    "prompt": "You are the Deploy Assistant. Walk me through deployment step by step: 1) Run the full test suite. 2) Run a security scan. 3) Build the production artifact. 4) Confirm the target environment. 5) Deploy only if all prior steps pass. Ask for confirmation before each destructive step."
  }
}
```

### Pre Tool Use — Block Destructive Bash

```json
{
  "name": "audit-bash",
  "trigger": "PreToolUse",
  "matcher": "execute_bash",
  "instructions": "Log this command to ~/.kiro/bash-audit.log with timestamp. If the command contains 'rm -rf', 'DROP TABLE', or 'force push', exit with code 2 and explain why this is blocked."
}
```

### Post Task Execution — Auto-Run Tests After Each Spec Task

```json
{
  "version": "1",
  "enabled": true,
  "name": "Post-Task Test Runner",
  "description": "Run tests automatically after each spec task completes",
  "when": { "type": "postTaskExecution" },
  "then": {
    "type": "runCommand",
    "command": "npm test -- --passWithNoTests",
    "timeout": 120
  }
}
```

### TDD Enforcer

```json
{
  "version": "1",
  "enabled": true,
  "name": "TDD Enforcer",
  "description": "Ensure 80%+ test coverage on TypeScript files",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/**/*.ts", "src/**/*.tsx"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A TypeScript file was saved. Check if the corresponding test file exists and achieves at least 80% coverage of the modified code. If coverage is below threshold, generate missing test cases following TDD principles."
  }
}
```

### Console.log Cleanup on Save

```json
{
  "version": "1",
  "enabled": true,
  "name": "Console Log Guard",
  "description": "Flag console.log statements left in source files",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.js"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "A source file was saved. Check for any console.log, console.debug, or console.warn statements. Comment them out with a // DEBUG: prefix and note the line numbers so they can be reviewed before commit."
  }
}
```

---

## Part 8 — Managing Hooks: IDE Workflow

- **Create:** Open Agent Hooks panel in Kiro sidebar, click the `+` icon. Either describe your hook in natural language (Kiro generates the JSON) or fill in form fields manually.
- **Edit:** Select any hook in the panel and modify trigger type, file patterns, instructions, or description. Changes apply immediately.
- **Enable/Disable:** Click the eye icon or use the "Hook Enabled" toggle. Prefer disabling over deleting so config is preserved in source control.
- **Delete:** Select the hook, click "Delete Hook", confirm. Irreversible.
- **Run manually:** For `userTriggered` hooks, click the play button (▶) next to the hook name.
- **Share with team:** Commit `.kiro/hooks/` to version control. Teammates get all hooks on `git pull`.

Source: [Hook Management Docs](https://kiro.dev/docs/hooks/management/)

---

## Part 9 — Community Repositories

| Repository | What it contains |
|---|---|
| [awsdataarchitect/kiro-best-practices](https://github.com/awsdataarchitect/kiro-best-practices) | Opinionated boilerplate with production-ready hooks for lint, format, and documentation |
| [mikeartee/kiro-hooks-docs](https://github.com/mikeartee/kiro-hooks-docs) | Community-curated hook library organised by category (code-quality, testing, documentation, security, workflow, maintenance) |
| [iamaanahmad/everything-kiro-ide](https://github.com/iamaanahmad/everything-kiro-ide) | Complete Kiro IDE config collection: agents, skills, hooks, steering, MCP integrations |
| [viatoro/ecc .kiro/hooks](https://github.com/viatoro/ecc/tree/main/.kiro/hooks) | Real project hooks directory showing hooks used in production |
| [github.com/topics/kiro-hooks](https://github.com/topics/kiro-hooks) | GitHub topic aggregating all public repos tagged with `kiro-hooks` |

---

## Trade-offs / Caveats

- **`askAgent` costs credits.** Hooks that fire on every file save and use `askAgent` will consume AI credits continuously. Use `runCommand` for deterministic operations (lint, test) and `askAgent` only when judgment is required.
- **No global hooks yet.** As of May 2026, hooks are workspace-scoped only (`.kiro/hooks/`). Global hooks at `~/.kiro/hooks/` are [requested but not shipped](https://github.com/kirodotdev/Kiro/issues/7737). To reuse hooks across projects, copy them manually.
- **CLI vs. IDE naming inconsistency.** The CLI uses `file-save`/`file-create`/`file-delete`; the IDE uses `fileEdited`/`fileCreated`/`fileDeleted`. Both are supported but can cause confusion.
- **`preTaskExecution` / `postTaskExecution` are recent additions**, shipped in IDE v0.10 (February 2026). Older docs may not cover them.
- **`preToolUse` blocking (exit code 2) is confirmed for CLI.** IDE behavior not explicitly documented — verify on your version before relying on it.
- **Performance impact:** File-save hooks on broad patterns (`**/*.ts`) in large monorepos may introduce noticeable latency. Start narrow and expand patterns only after testing.
- **Hooks do not fire in subagents** — if using kiro-team or custom subagents, hook governance is bypassed for all tool calls made inside a subagent.

---

## Sources

- [Hooks — IDE Docs](https://kiro.dev/docs/hooks/)
- [Hook Types — IDE Docs](https://kiro.dev/docs/hooks/types/)
- [Hook Actions — IDE Docs](https://kiro.dev/docs/hooks/actions/)
- [Hook Examples — IDE Docs](https://kiro.dev/docs/hooks/examples/)
- [Hook Management — IDE Docs](https://kiro.dev/docs/hooks/management/)
- [Hook Best Practices — IDE Docs](https://kiro.dev/docs/hooks/best-practices/)
- [Hooks — CLI Docs](https://kiro.dev/docs/cli/hooks/)
- [Automate Your Development Workflow — Kiro Blog](https://kiro.dev/blog/automate-your-development-workflow-with-agent-hooks/)
- [awsdataarchitect/kiro-best-practices](https://github.com/awsdataarchitect/kiro-best-practices)
- [mikeartee/kiro-hooks-docs](https://github.com/mikeartee/kiro-hooks-docs)
- [iamaanahmad/everything-kiro-ide](https://github.com/iamaanahmad/everything-kiro-ide)
- [Kiro v0.10 Changelog](https://kiro.dev/changelog/ide/0-10/) — preTaskExecution / postTaskExecution introduction
- [Kiro v0.9 Changelog](https://kiro.dev/changelog/ide/0-9/) — preToolUse / postToolUse introduction
- [How I Built a One-Click Deploy Assistant](https://medium.com/@schmitg/how-i-built-a-one-click-deploy-assistant-with-kiro-hooks-5db97c608007)
- [Global Hooks Feature Request #7737](https://github.com/kirodotdev/Kiro/issues/7737)
- [10 Kiro Hooks That Will Transform Your Workflow](https://kiro.directory/blog/10-kiro-hooks-automation/) — primary blog post (not directly fetchable; content inferred from search snippets)
