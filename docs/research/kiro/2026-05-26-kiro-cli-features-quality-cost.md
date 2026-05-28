# Research: Kiro CLI — Complete Feature Overview Optimized for Quality and Cost

## Summary

Kiro CLI (current version 2.4.0, May 2026) is a terminal-first agentic AI tool built on Claude models via Amazon Bedrock. It shares the same agent infrastructure as the Kiro IDE — steering files, MCP servers, hooks, custom agents — but is purpose-built for terminal workflows without IDE context switching. Cost is controlled through a credit-multiplier system: model choice, reasoning effort level, the thinking tool toggle, and how context is loaded are the four primary levers. The IDE-exclusive spec/requirements workflow (requirements.md / design.md / tasks.md) is not available in the CLI; the closest analogs are the `/plan` agent, `/spawn` for parallel tasks, and skills with `$ARGUMENTS` placeholders.

---

## Key Findings

### 1. Full Built-in Tool List

Every built-in tool is available by default; cost arises not from the tool itself but from the tokens its results add to the context window. [Built-in Tools Reference](https://kiro.dev/docs/cli/reference/built-in-tools/)

| Tool | Purpose | Cost/Context Note |
|---|---|---|
| `read` | Read files, folders, images | Adds file content to context |
| `glob` | File discovery with glob patterns | Low token overhead |
| `grep` | Regex content search | Low token overhead |
| `write` | Create and edit files | No context overhead |
| `shell` | Execute bash commands | Output can be large — use allowedTools to restrict |
| `aws` | Make AWS CLI calls | Output size varies |
| `web_search` | Search the web | Possible usage limits apply |
| `web_fetch` | Fetch URL content | Adds page content to context — can be expensive |
| `code` | Symbol search + LSP integration | Low overhead |
| `tool_search` | Lazy-load MCP tools on demand | Key context-saver (see MCP section) |
| `delegate` / `subagent` | Spawn parallel/background agents | Each subagent has its own context window; not free |
| `knowledge` | Semantic search across indexed content | On-demand, does not occupy context continuously |
| `thinking` | Visible reasoning chain | Additional tokens per response — see below |
| `todo` | Manage to-do lists | Minimal overhead |
| `report` | Submit GitHub issues | Minimal overhead |
| `introspect` | Answer Kiro CLI feature questions | Minimal overhead |
| `session` | Temporarily override CLI settings | Minimal overhead |

Tools are configured in the `toolsSettings` block. All file-operating tools support `allowedPaths`, `deniedPaths`, and `denyByDefault`. Shell supports command allowlists via regex. Web tools support URL trust/block lists.

**Cost-conscious note:** `web_fetch` results and large `shell` output are the easiest tools to accidentally blow your context window with. Restrict with `deniedPaths` or command allowlists.

---

### 2. Model Selection and Cost/Quality Matrix

CLI uses a credit-multiplier pricing model. "Auto" is the 1.0x baseline; all other models are priced relative to it. The Spec/Vibe request pricing applies only to the IDE. [Models — CLI Docs](https://kiro.dev/docs/cli/models/)

| Model | Context Window | Cost Multiplier | Best Use Case |
|---|---|---|---|
| Claude Opus 4.7 | 1M tokens | 2.2x | Adaptive reasoning, architectural complexity, large codebases |
| Claude Opus 4.6 | 1M tokens | 2.2x | Multi-million-line codebases, sustained debugging |
| Claude Opus 4.5 | 200K tokens | 2.2x | Complex multi-system problems |
| Claude Sonnet 4.6 | 1M tokens | 1.3x | Iterative development, token-efficient agentic work |
| Claude Sonnet 4.5 | 200K tokens | 1.3x | General agentic coding with extended autonomy |
| Claude Sonnet 4.0 | 200K tokens | 1.3x | Predictable baseline behavior |
| **Auto** | — | **1.0x** | General development; dynamically chooses optimal model per task |
| Claude Haiku 4.5 | 200K tokens | 0.4x | Speed-focused work, rapid iteration, credit conservation |
| DeepSeek 3.2 | 128K tokens | 0.25x | Multi-step reasoning at reduced cost |
| MiniMax M2.5 | 200K tokens | 0.25x | Frontier-class coding at low cost |
| GLM-5 | 200K tokens | 0.5x | Repository-scale agentic work |
| MiniMax M2.1 | 200K tokens | 0.15x | Multilingual programming |
| Qwen3 Coder Next | 256K tokens | 0.05x | Maximum cost-effectiveness for long sessions |

**Strategy:** Auto is the recommended default — it dynamically picks the best model and costs less than manually selecting Sonnet 4.5. Escalate to Opus only when Auto stalls on architectural complexity. Use Haiku (0.4x) or Qwen3 (0.05x) for rapid exploratory iterations, scaffolding tasks, or CI/CD automation where absolute quality is secondary. Switch models mid-session via `/model`.

**Opus 4.7 uniquely features adaptive thinking** — it automatically calibrates reasoning effort based on task complexity without manual configuration, available since v2.2.0+.

---

### 3. Thinking Tool — Cost and Quality

The thinking tool is an **experimental feature** that makes the model's reasoning chain visible. Enable it via `kiro-cli settings chat.enableThinking true` or `/experiment` in-session. [Thinking Tool — Experimental Docs](https://kiro.dev/docs/cli/experimental/thinking/)

- **Quality impact:** Positive for complex problems — you can inspect reasoning steps, catch flawed assumptions early, validate architectural decisions.
- **Cost impact:** Explicit documentation states it "consumes additional tokens" and produces "more verbose" responses. The reasoning chain is not free — it increases credit usage on every response where thinking activates.
- **Interaction with `/effort`:** The `/effort` command (v2.4.0) sets reasoning effort across five levels (low, medium, high, xhigh, max) independently of the thinking tool toggle. Thinking tool surfaces the chain visibly; `/effort` controls how deep the chain goes. For pure cost savings, keep effort at `low` or `medium` for non-critical tasks.

**Cost-conscious recommendation:** Disable thinking for routine tasks (code completion, simple refactors, file writes). Enable it specifically for debugging complex logic, architectural planning, or code review — scenarios where understanding the reasoning is itself valuable. Do not enable it globally in CI/CD agents.

---

### 4. Spec/Requirements Features — CLI vs IDE

**The full spec-driven workflow (requirements.md / design.md / tasks.md with approval gates) is an IDE-only feature.** The IDE's v0.12 release added parallel task execution and "Analyze Requirements" for catching logical inconsistencies. None of this is available in the CLI. [Specs — IDE Docs](https://kiro.dev/docs/specs/)

CLI analogs for structured development:

- **`/plan`** — Invokes the Plan agent, which breaks down complex ideas into structured steps. The closest CLI equivalent of spec planning.
- **`/guide`** — Invokes the Guide agent for documentation-grounded answers.
- **`/spawn`** — Launches parallel agent sessions (`delegate` / `subagent` tools) for running independent work concurrently.
- **Skills with `$ARGUMENTS`** — You can encode requirements templates as skills, with `$ARGUMENTS` substituting user-provided context. This gives a lightweight spec-like workflow through skill invocation.

If spec-driven development is a hard requirement, use the IDE. If working CLI-only, combine `/plan` for upfront decomposition with skills for enforcing consistent implementation patterns.

---

### 5. Context Window Management

The core constraint: context files consume tokens on **every request**, regardless of whether the model references them. [Context Management — CLI Docs](https://kiro.dev/docs/cli/chat/context/)

**Four context loading strategies (cheapest to most expensive):**

| Mechanism | Behavior | Cost Profile |
|---|---|---|
| `knowledge` base | Indexed, semantically searched on-demand | Load only what's relevant per query |
| Skill `references/` | Loaded only when instructions reference them | On-demand — not in every request |
| `/context add` | Session-only, always active | Always in context window during session |
| Agent `resources` | Always active every request | Permanent context cost |

**Key rule:** Files are capped at 75% of the model's context window. Files exceeding this are silently dropped. The experimental **Context Usage Percentage** feature (enable via `/experiment`) shows color-coded usage in the prompt: green (<50%), yellow (50–89%), red (90–100%).

**Practical levers:**
- `/context show` — inspect current allocation percentages
- `/compact` — condense conversation history mid-session to reclaim space
- `/knowledge` — index large codebases for semantic search rather than loading them as resources
- `tool_search` (MCP) — loads MCP tools lazily on-demand rather than all upfront; preserves context window for larger tool registries

**Cost-conscious recommendation:** Move frequently-used files to `resources`, use `knowledge` bases for large codebases, and avoid broad glob patterns like `file://**/*.md` in resources. For one-off files, use `/context add` so they don't consume tokens across sessions.

---

### 6. MCP (Model Context Protocol) Support

MCP is a first-class feature in Kiro CLI, not an afterthought. [MCP — CLI Docs](https://kiro.dev/docs/cli/mcp/)

**Configuration hierarchy** (highest to lowest priority):
1. Agent-level `mcpServers` block in agent JSON
2. Workspace-level: `.kiro/settings/mcp.json`
3. Global-level: `~/.kiro/settings/mcp.json`

**Server types supported:**
- Local/command-based: runs via system command (e.g., `npx`, `uvx`)
- HTTP-based remote servers with URL and optional headers
- OAuth-protected HTTP servers — v2.3.0 added OAuth Client ID config; Kiro handles the browser-based OAuth flow automatically

**`tool_search` tool** (v2.1+): Loads MCP tools on-demand rather than injecting all tool descriptions into context at startup. For MCP servers with many tools (30+ tools), this can recover substantial context space. The downside is the model must call `tool_search` before it can use a tool it hasn't seen yet.

**Tool validation rules:** Tool names must not exceed 64 characters (including server prefix), must match `^[a-zA-Z][a-zA-Z0-9_]*$`, and descriptions cannot be empty. Descriptions exceeding 10,000 characters slow responses but don't break functionality.

**`includeMcpJson`** in agent config: Boolean toggle for whether an agent inherits globally-configured MCP servers. Set to `false` for narrow-purpose agents to prevent unnecessary tool exposure.

---

### 7. Session Management

Sessions are automatically persisted to a SQLite database at `~/.kiro/` after every conversation turn, scoped per-directory. [Session Management — CLI Docs](https://kiro.dev/docs/cli/chat/session-management/)

**Resume options:**
- `kiro-cli chat --resume` — most recent session
- `kiro-cli chat --resume-picker` — interactive picker
- `kiro-cli chat --resume-id <UUID>` — specific session by UUID
- `/chat resume` — in-session command

**In-session management:**
- `/chat new` — start a fresh conversation
- `/session-id` — print current UUID
- `/chat save <path>` — export session to JSON
- `/chat load <path>` — import session from JSON
- `/chat save-via-script` / `/chat load-via-script` — pipe session JSON through custom scripts (enables Git Notes integration, cloud sync, etc.)

**Rewind and branching** (v2.4.0): `/rewind` jumps back to an earlier turn and branches into a new conversation thread without destroying the original. The original thread is preserved.

**Tangent mode** (experimental): `/tangent` or Ctrl+T creates a checkpoint to explore a side topic, then returns to the main thread. Distinct from `/rewind` in that tangents are scoped explorations rather than true branching.

**No built-in cloud sync or cross-device search.** Sessions are local SQLite, per-directory.

---

### 8. Cost Monitoring

Kiro CLI uses a credit-multiplier system. [CLI Billing — Related Questions](https://kiro.dev/docs/cli/billing/related-questions/)

**Available visibility tools:**
- `/usage` slash command — displays billing and credits information in-session
- `/tools` command — shows estimated token counts per tool and per origin, making MCP server context costs visible
- `kiro-usage` Python package on PyPI — third-party tool for usage analysis

**Credit metering:** Credits are metered to two decimal places (minimum 0.01 per task). The model multiplier applies per task: Auto at 1.0x is the cheapest Claude option. Qwen3 Coder Next at 0.05x is 44x cheaper than Opus.

**There is no per-token cost visibility in the CLI itself.** Cost is expressed in credits, not tokens or dollars, making it harder to reason about individual tool calls. The `/tools` estimated token count display is the closest proxy.

---

### 9. Hooks System — Complete Reference

Five hook types are supported, configured in the `hooks` block of an agent configuration. [Hooks — CLI Docs](https://kiro.dev/docs/cli/hooks/)

| Hook | Trigger | Tool Context | Exit Code Behavior | Key Use Cases |
|---|---|---|---|---|
| `agentSpawn` | Agent activates | None | Exit 0: STDOUT injected into agent context | Environment setup, loading dynamic context, validation |
| `userPromptSubmit` | User submits a prompt | None | Exit 0: STDOUT added to conversation context | Prompt enrichment, input sanitization, context injection |
| `preToolUse` | Before a tool executes | Full tool parameters | **Exit 2: blocks execution, error returned to LLM** | Security gates, access control, audit logging |
| `postToolUse` | After a tool completes | Tool input + response | Exit 0: STDOUT added to context | Result logging, filtering sensitive data, validation |
| `stop` | After each assistant turn ends | None | — | Code compilation, test runs, formatting, cleanup |

**Configuration options per hook:**
- `timeout_ms` — default 30,000ms; increase for slow compilation steps in `stop` hooks
- `cache_ttl_seconds` — cache hook output to avoid re-running on every trigger; set to 0 to disable; `agentSpawn` is never cached
- Tool matchers — all hooks except `stop` support glob-style matching: exact names (`fs_read`), wildcards (`write_*`), or MCP namespace patterns (`@git/status`)

**Cost note:** `agentSpawn` and `userPromptSubmit` hooks that return substantial STDOUT inject that text into the context window. Keep hook output concise or use them only for critical context.

---

### 10. CLI-Specific Features vs Kiro IDE

Features present in CLI but absent (or IDE-primary):

| Feature | CLI | IDE |
|---|---|---|
| Terminal-native workflow | Native | N/A |
| SSH/remote development | Native (`--resume` over SSH, device flow auth v2.1+) | Limited |
| Headless/CI-CD mode | Yes — API key auth, available since v2.0 | No |
| RHEL support | Yes (v2.1+) | Limited |
| Windows 11 native | Yes (v2.0+) | Yes |
| Custom agents | Yes | Yes |
| Spec workflow (requirements.md/design.md/tasks.md) | No — `/plan` agent only | Full feature |
| Parallel spec task execution | Partial — via `delegate`/`subagent` tools | Full (wave-based dependency graph) |
| `/effort` reasoning control | Yes (v2.4.0) | No |
| `/rewind` branching | Yes (v2.4.0) | No |
| `/tangent` checkpointing | Yes (experimental) | No |
| `/compact` context compaction | Yes | No |
| `tool_search` lazy MCP loading | Yes | No |
| `KIRO_HOME` env variable | Yes (v2.3.0) | No |
| Custom session storage scripts | Yes | No |
| Context Usage Percentage indicator | Yes (experimental) | No |
| LSP integration via `/code` | Yes | Native |
| Git workspace checkpointing | Yes (experimental `/checkpoint`) | No |

**Shared features (configure once, use everywhere):** Steering files, MCP server configs, agent definitions, and skills are identical between CLI and IDE. Global configs in `~/.kiro/` apply to both.

---

## Trade-offs / Caveats

- **Pricing model:** CLI uses credit multipliers (Auto=1.0x, Haiku=0.4x, Opus=2.2x, Qwen3=0.05x). The Spec/Vibe request pricing ($0.20/$0.04 per request) is IDE-specific. Do not apply IDE pricing logic to CLI cost estimates.

- **Spec workflow is IDE-only.** Multiple search results conflate Kiro IDE specs with CLI capabilities. The CLI has `/plan` and `delegate`/skills as substitutes — they are not equivalent. If your workflow depends on requirements.md approval gates, the CLI alone is insufficient.

- **Auto model selection is opaque.** The Auto mode dynamically selects models but does not surface which model it chose for a given task. If reproducibility matters (e.g., CI/CD), explicitly pin a model rather than relying on Auto.

- **Experimental features can be removed.** Knowledge bases, thinking tool, tangent mode, checkpointing, and context usage percentage are all marked experimental and "may change or be removed at any time." Do not build critical production automation around them without a fallback.

- **Subagent cost is not free.** Each `delegate`/`subagent` invocation runs a separate Kiro session with its own context window. Orchestrator patterns that spawn many subagents multiply credit consumption. Design subagent scopes to be narrow and focused.

- **`always` steering and subagent injection bug** (known, pre-existing): Steering files with `inclusion: always` are not reliably injected into subagents. See `2026-05-26-kiro-cli-steering-file-agent-triggering.md` for context.

- **Context 75% drop is silent.** Files that exceed the 75% context window allocation are automatically dropped without warning unless you have the experimental Context Usage Percentage indicator enabled.

- **Open-weight models (DeepSeek, MiniMax, GLM, Qwen3) are low-cost but lower-quality** for complex reasoning. Use them for well-defined, structured tasks (code formatting, test generation, documentation) rather than architectural decisions.

- **MCP tool description length** affects performance. Descriptions over 10,000 characters slow responses. Trim verbose tool descriptions when using heavily tooled MCP servers.

---

## Sources

- [Models — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/models/) — Complete model roster, context windows, cost multipliers, and quality guidance
- [Built-in Tools Reference — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/reference/built-in-tools/) — Full tool list with configuration options
- [Thinking Tool — Experimental Docs (kiro.dev)](https://kiro.dev/docs/cli/experimental/thinking/) — What the thinking tool does, cost implications, configuration
- [Hooks — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/hooks/) — All five hook types, trigger points, exit code behavior, and use cases
- [Custom Agents Configuration Reference (kiro.dev)](https://kiro.dev/docs/cli/custom-agents/configuration-reference/) — Full agent JSON schema: tools, models, hooks, MCP, resources
- [MCP — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/mcp/) — MCP server types, configuration hierarchy, OAuth support, tool_search behavior
- [Context Management — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/chat/context/) — Context window rules, the 75% cap, /context commands, knowledge vs resources
- [Session Management — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/chat/session-management/) — SQLite persistence, resume commands, export/import, custom scripts
- [Slash Commands Reference — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/reference/slash-commands/) — Complete slash command list with descriptions
- [Experimental Features — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/experimental/) — Knowledge, thinking, tangent, checkpointing, context usage percentage
- [Skills — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/skills/) — Skill structure, activation mechanisms, slash command invocation
- [Steering — CLI Docs (kiro.dev)](https://kiro.dev/docs/cli/steering/) — Steering file inclusion modes, global vs workspace scope
- [CLI Changelog (kiro.dev)](https://kiro.dev/changelog/cli/) — v2.0 through v2.4.0 feature additions and bug fixes
- [Understanding Kiro Pricing — Kiro Blog (kiro.dev)](https://kiro.dev/blog/understanding-kiro-pricing-specs-vibes-usage-tracking/) — Credit system explanation; Spec/Vibe distinction (IDE-specific)
- [CLI Billing Related Questions (kiro.dev)](https://kiro.dev/docs/cli/billing/related-questions/) — Confirms CLI uses credit multipliers, not Spec/Vibe request pricing
- [Introducing Kiro CLI — Kiro Blog (kiro.dev)](https://kiro.dev/blog/introducing-kiro-cli/) — CLI vs IDE positioning and use cases
- [Kiro CLI vs Sonnet/Haiku Comparison — DevelopersIO](https://dev.classmethod.jp/en/articles/kiro-cli-claude-opus-4-5-sonnet-4-5-haiku-4-5/) — Practical quality comparison (note: different license tiers used per model; treat as directional only)
- [Specs — IDE Docs (kiro.dev)](https://kiro.dev/docs/specs/) — Spec-driven development workflow; IDE-only, referenced for CLI contrast
