# Research: How Kiro CLI Can Be Made Better and More Useful

## Summary

Kiro is AWS's agentic development platform that reached general availability in November 2025 and has been iterating rapidly into 2026. Its CLI (currently at version 2.4.0) has grown from a basic headless runner to a full-featured terminal agent with subagents, skills, session management, MCP integration, and a polished TUI. The platform's genuine differentiator is its spec-driven development workflow — a three-document process (requirements, design, tasks) that imposes structure around agentic code generation. Despite significant recent progress, recurring gaps remain: Powers (the dynamic MCP context system) are IDE-only and not available in the CLI; the spec workflow still lacks a lightweight fast path for small tasks; CLI/IDE sessions cannot be attached to each other across surfaces; credit-based pricing creates friction for exploratory or heavy agentic usage; and certain enterprise, productivity, and extensibility capabilities lag behind Claude Code and Cursor. This report provides actionable recommendations organized across seven areas.

---

## Key Findings

### 1. Current State of Kiro CLI

Kiro launched in public preview in July 2025 and reached GA on November 17, 2025. The CLI shipped as a named binary (`kiro-cli`) built on VS Code OSS and backed by Anthropic Claude models (Sonnet 4.x, Haiku 4.x, and a proprietary cost-optimized "Auto" model) routed through AWS Bedrock.

**CLI 2.0 (April 13, 2026)** graduated the TUI to default, shipped native Windows 11 support, introduced headless mode (`--no-interactive` + `KIRO_API_KEY`), and added subagent task dependency graphs with a Crew Monitor (`Ctrl+G`).

**CLI 2.1 (April 24, 2026)** added real-time shell output streaming, Tool Search (on-demand MCP tool loading to preserve context), skills invokable as slash commands, and device-flow auth for remote environments.

**CLI 2.3 (May 12, 2026)** added OAuth support for remote MCP servers (Slack, GitHub, etc.), `KIRO_HOME` env var for custom config directories, and remappable TUI keybindings.

**CLI 2.4 (May 20, 2026)** shipped conversation rewind (`/rewind` to branch from any prior turn), five-level reasoning effort control (`/effort low|medium|high|xhigh|max`), and a unified `/settings` menu. Workspace initialization is 88% faster.

**IDE 0.12 (May 6, 2026)** introduced parallel task execution (up to 4x speedup for specs with independent tasks), Quick Plan mode (no approval gates between requirements/design/tasks phases), and requirements analysis that catches logical inconsistencies before implementation.

**Kiro became HIPAA-eligible on May 26, 2026** for IDE and CLI (Kiro Web excluded).

Core primitives as of May 2026:

- **Specs**: Three-document artifacts (`requirements.md`, `design.md`, `tasks.md`) that drive implementation. Recently augmented with Quick Plan, parallel execution, and requirements analysis.
- **Steering**: Markdown rule files in `.kiro/steering/` (workspace scope) and `~/.kiro/steering/` (global scope) — Kiro also detects `AGENTS.md` at the workspace root.
- **Hooks**: File-event, lifecycle, and spec-task event automations configured in `.kiro/hooks/`. Sequential hooks were added in a mid-cycle release.
- **Skills**: Portable instruction packages in `.kiro/skills/` (workspace) or `~/.kiro/skills/` (global), now invokable as `/skill-name` slash commands.
- **Custom Agents**: JSON config files in `.kiro/agents/` with tool allow-lists, model selection, per-tool path restrictions, lifecycle hooks, and keyboard shortcuts.
- **Powers**: Bundles of MCP + steering + hooks that load dynamically based on keyword matching — currently IDE-only, CLI support announced as "coming soon".
- **MCP**: Workspace (`~/.kiro/settings/mcp.json`) and project scope; OAuth added in 2.3; Tool Search in 2.1 loads definitions on demand.
- **Session management**: SQLite-backed auto-save, per-directory sessions, `--resume`/`--resume-picker`/`--resume-id` flags, `/rewind`, and JSON export.

**Pricing** (as of March 2026): Free (50 credits/month), Pro ($20/mo, 1,000 credits), Pro+ ($40/mo, 2,000 credits), Power ($200/mo, 10,000 credits). Overage is $0.04/credit. Credits are shared across IDE and CLI. The "Auto" model is the default and cheapest; Sonnet 4.6 costs 1.3× credits vs. Auto for the same task.

---

### 2. User Pain Points and Community Feedback

From public GitHub issues (2,800+ open issues as of late May 2026), AWS re:Post, developer blogs, and social discussion:

- **Spec workflow overhead for small tasks**: The official best-practices documentation explicitly acknowledges that "overusing specs for simple fixes" (typos, one-line changes) "creates unnecessary overhead," yet the tooling doesn't yet provide a smooth lighter-weight path that still captures artifacts.
- **Powers not available in CLI**: The most impactful new context-management feature (dynamic MCP bundling) is IDE-only, leaving CLI users to manually manage MCP JSON config while IDE users get keyword-activated tool sets.
- **Workflow lock-in inside a spec**: Once a spec is created with a workflow type (Requirements-First vs. Design-First vs. Bugfix), switching requires creating an entirely new spec — a friction point that discourages experimentation.
- **Credit-based pricing limits agentic experimentation**: The free tier's 50 credits/month is very limiting for agentic workflows (which generate many tool calls per task). Users report being rate-limited during exploratory usage before seeing meaningful value.
- **CLI/IDE session divergence**: Sessions are directory-scoped and stored locally; there is no way to start in the IDE and continue in the CLI with the same conversation thread, or vice versa. No cloud sync for sessions exists.
- **Missing machine-readable usage output**: A developer filed [GitHub issue #7826](https://github.com/kirodotdev/Kiro/issues/7826) requesting `kiro-cli --usage` for programmatic consumption of token/credit usage data.
- **Zsh integration bugs**: One report documents Kiro CLI failing to retrieve return values from sequential commands in the same shell session, indicating shell integration gaps.
- **Hook discoverability**: Hooks are powerful but require reading documentation to discover; no `kiro hooks test` or catalog of built-in recipes exists.
- **Configuration sync across devices**: Open GitHub issue requesting settings/config synchronization across machines.
- **Pricing plan gaps**: A request for a mid-tier $100/month plan between Pro+ and Power reflects that the 5× jump from $40 to $200 is too coarse for many teams.

---

### 3. Comparison with Similar AI-Powered CLI Tools

| Capability | Kiro CLI (v2.4) | Claude Code | Cursor | Aider | Copilot CLI |
|---|---|---|---|---|---|
| **Spec-driven dev as first-class primitive** | **Yes (flagship)** | No | No | No | No |
| **Steering / project rules** | Yes (`.kiro/steering/`, AGENTS.md) | Yes (`CLAUDE.md`, skills) | Yes (`.cursorrules`) | Yes (conventions) | Limited |
| **File-event hooks** | Yes (multi-event) | Yes (Pre/Post ToolUse, Stop) | Limited | No | No |
| **Subagents with task dependencies** | **Yes (v2.0+)** | Yes (named, parallel) | Yes (background) | No | No |
| **Skills / shareable instruction bundles** | Yes (`/skill-name`) | Yes (skills) | Limited | No | No |
| **Dynamic MCP context loading (Powers)** | IDE-only (CLI: soon) | No equivalent | No | No | No |
| **MCP OAuth for remote servers** | **Yes (v2.3)** | Partial | Partial | No | No |
| **Session resume / rewind** | Yes (`--resume`, `/rewind`) | Yes (`--continue`, `--resume`) | Yes | Yes | Limited |
| **Headless / CI mode** | Yes (`--no-interactive` + API key) | Yes (`-p`, JSON output) | Limited | Yes | Yes |
| **Reasoning effort control** | **Yes (5 levels, v2.4)** | Yes (`--think`) | Limited | No | No |
| **Real-time shell streaming** | Yes (v2.1+) | Yes | Yes | Yes | Yes |
| **BYO model / local model** | No (AWS-bound) | Partial (Bedrock/Vertex) | Limited | **Yes (any OpenAI-compat)** | No |
| **IDE bidirectional session sync** | No (separate sessions) | Strong (plug-ins) | **Native** | N/A | Partial |
| **HIPAA eligibility** | **Yes (IDE + CLI)** | No | No | No | No |
| **Credit-based pricing (predictable cost)** | Yes (credit tiers) | Pay-per-token | Subscription | Free OSS | Copilot subscription |
| **Inline autocomplete in IDE** | Yes | No (terminal only) | **Yes (flagship)** | No | No |

Kiro leads on spec-driven structure, HIPAA compliance, dynamic context bundling (Powers), and the combination of reasoning effort + subagent dependency graphs in the CLI. Claude Code leads on flexibility and polish for power terminal users. Cursor leads on IDE-CLI native parity. Aider leads on git workflow and BYO model. Copilot leads on shallow-integration corporate environments.

---

## Specific Improvement Recommendations

### A. Bring Powers to the CLI (Highest Priority)

Powers — the dynamic MCP bundling system that activates context on-demand — represent Kiro's strongest contextual ergonomics idea. The fact that they are IDE-only while the CLI ships with manual `mcp.json` config is the single largest feature parity gap between the two surfaces.

**Recommendations:**
- Implement Powers resolution in the CLI using the same keyword-matching trigger model as the IDE.
- Add `kiro powers install <name>`, `kiro powers list`, `kiro powers status` subcommands.
- Make workspace `powers.json` (or extend `mcp.json`) the canonical location, respected by both IDE and CLI.
- Ship first-party Powers for AWS services (S3, CloudWatch, CDK, Lambda) — this is Kiro's largest moat given AWS provenance, and there's no other tool that offers it out of the box.

### B. Lightweight Task Mode for the Spec Workflow

The spec ceremony is the right default for feature development but the wrong default for everything else. The workflow-lock-in issue (no migration between spec types) compounds this.

**Recommendations:**
- Introduce a `kiro fix "<description>"` command that bypasses spec ceremony entirely, runs the agent inline, but emits a retroactive single-file audit log (a micro-tasks.md) for traceability.
- Allow spec workflow-type migration: if a bugfix spec grows into a feature, expose a "convert to Feature Spec" action that preserves existing requirements and synthesizes design/tasks.
- Add a `--light` flag to `kiro spec create` that produces a single combined document (not three) and runs in Quick Plan mode by default.
- Surface spec complexity estimation upfront: before generating the full three docs, show a cost preview ("this spec will likely create ~12 tasks, ~N credits").

### C. Cross-Surface Session Continuity (IDE ↔ CLI)

Today, the IDE and CLI maintain entirely separate session stores. This forces context re-priming when switching surfaces, which is a significant daily friction for developers who start a task in one and need to continue in the other.

**Recommendations:**
- Implement a shared session layer: sessions written by both surfaces into a common format, with a session ID that both surfaces can open.
- When the CLI is launched inside a directory with an active IDE session, offer to attach: "Resume IDE session #abc1234? (started 10m ago)".
- Expose `kiro session sync` for explicit cloud backup of sessions (optional, off by default, respecting enterprise data residency settings).
- The IDE should be able to open a CLI session transcript via `#session:UUID` reference in the chat.

### D. Hooks Developer Experience

Hooks are powerful but their discoverability and debuggability lag behind their capability.

**Recommendations:**
- Ship `kiro hooks test <hook-name>` that simulates a file event without actually triggering a write, and streams what the agent would do.
- Ship `kiro hooks list` showing all active hooks across workspace and global scope, with their trigger conditions.
- Build a hooks catalog (similar to Powers) with ready-made recipes: "on-save lint", "on-spec-task-complete run tests", "on-PR-open generate summary", "on-create add file header".
- Add an `onSessionStart` hook type for agent customization at chat start.
- Add hook dry-run output to the TUI so developers can see which hooks fired and why during a session.

### E. Credit and Cost Transparency

The credit model is opaque during active usage and creates anxiety for users doing heavy agentic tasks.

**Recommendations:**
- Show a real-time credit burn indicator in the TUI status bar during agent execution (like a fuel gauge).
- Add a `--budget <credits>` flag that stops agent execution before hitting a credit ceiling, with a checkpoint prompt.
- Make `kiro usage` a first-class command: show credits consumed today, this session, this spec, and this month, broken down by model and agent type.
- The Free tier's 50 credits is too low to let new users complete a single meaningful spec. Consider a "first spec free" promotion where new users get 200 bonus credits specifically for their first spec execution — tied to conversion, not just sampling.
- Add a mid-tier pricing plan between Pro+ ($40, 2,000 credits) and Power ($200, 10,000 credits) at approximately $80–$100/month (4,000–5,000 credits) to address the pricing gap flagged by users.

### F. MCP Integration Ergonomics

The OAuth support added in 2.3 and Tool Search in 2.1 are the right foundations. The gaps are in developer tooling around MCP management.

**Recommendations:**
- Build out `kiro mcp` subcommands: `add <url>`, `remove <name>`, `test <name>` (validates server connection), `logs <name>` (streams server stderr), `inspect <name>` (lists all exposed tools).
- Ship a `kiro mcp doctor` that detects misconfigured, unreachable, or duplicate MCP servers and suggests fixes.
- For IDE/CLI parity: MCP server configuration set in the IDE should automatically be available in the CLI for the same workspace — currently the scopes are managed separately.
- Document MCP server sandboxing: make it easy to restrict a given server to specific tool patterns or file paths via the existing `allowedTools` mechanism in agent config.

### G. Spec-to-Codebase Traceability

The spec documents are currently decoupled from git history. A requirement can drive 10 commits but there is no link between them.

**Recommendations:**
- Auto-inject a spec/requirement reference into generated commit messages: "feat: implement login form [REQ-2.1, task 3/8 of auth-spec]".
- Add `kiro spec status` to the CLI showing which tasks are complete/pending/in-progress with the git commit SHAs that completed each.
- Enable `kiro spec diff` to show which code was generated from a given spec vs. manually written after the fact.
- For teams using GitHub Actions: ship an official workflow that posts spec task progress as a PR check — so reviewers can see "8/8 spec tasks complete" alongside test results.

### H. Performance and Context Management

**Recommendations:**
- The 88% workspace initialization improvement in 2.4 is great. Continue this work: profile the remaining startup time and set a public target (e.g., sub-1-second cold start in any project under 50k files).
- Expose prompt cache hit rate in `kiro doctor` output — steering files and large context are ideal candidates for Anthropic's prompt caching, and surfacing this gives users a lever for cost control.
- Add context window headroom indicator to the TUI: "Using 34% of context window. Auto-compact will trigger at 85%."
- Implement automatic conversation compaction before hitting context limits (similar to Claude Code's compaction), with a `/compact` slash command for manual triggering.

### I. Enterprise and Team Features

**Recommendations:**
- **Cross-device config sync**: Cloud backup of skills, steering, agent definitions, and settings (not sessions) so developers moving between machines or onboarding teammates start with consistent environments.
- **Audit log mode**: For enterprise (especially now that Kiro is HIPAA-eligible), expose a local structured log of every tool call, file touched, MCP server queried, and model used — with no data leaving the AWS region.
- **Team steering registry**: Allow teams to publish steering files to a private registry (similar to the powers repo pattern) and install them with `kiro steering install @my-org/standards`.
- **API key scoping**: Let enterprise admins create API keys that are restricted to specific agents, tools, or MCP servers — important for CI/CD usage where `--trust-all-tools` is too broad.
- **JetBrains plugin**: The VS Code / Code-OSS pairing is strong, but a large share of enterprise Java and Kotlin developers are on IntelliJ. A JetBrains plugin backed by the same CLI would expand the addressable market significantly.

---

## Trade-offs / Caveats

- **Rapidly moving target**: Kiro shipped CLI versions 2.0 through 2.4 in under six weeks (April–May 2026). Several gaps identified in early comparisons (Windows support, OAuth MCP, session rewind, real-time streaming) have already been closed. Recommendations in this report should be validated against the live [changelog](https://kiro.dev/changelog/) before prioritization.
- **Powers CLI timeline is unspecified**: The "coming soon" language for Powers in CLI has been on the powers page since the feature launched. Given the size of the gap this creates vs. the IDE experience, this should be treated as highest priority.
- **Credit pricing vs. token pricing**: The credit abstraction protects users from raw token costs but makes cost modeling opaque. Competitors like Claude Code use transparent per-token pricing. Kiro's credit system is defensible (it enables model routing and optimization behind the scenes), but it needs much better in-session cost visibility to build user trust.
- **Spec workflow lock-in** is documented as a known limitation by the Kiro team itself. The recommended "convert spec type" feature would need careful design to avoid spec integrity issues.
- **BYO model is not currently on the roadmap** from public information. This is a genuine gap for air-gapped enterprise deployments. Given that Kiro runs on AWS, a path via Amazon Bedrock custom model endpoints would be the most natural implementation without requiring fundamental architecture changes.
- **The competitor comparison** (Claude Code, Cursor, Aider, Copilot) is current as of May 2026. These tools update weekly; re-verify specific claims before using them in public-facing materials.
- **Community pain point data** skews toward vocal/technical users who file GitHub issues or write blog posts. Validate the priority ordering against Kiro's own product telemetry before committing roadmap resources.

---

## Sources

- [Introducing Kiro — kiro.dev/blog](https://kiro.dev/blog/introducing-kiro/)
- [Kiro General Availability Announcement](https://kiro.dev/blog/general-availability/)
- [Kiro CLI 2.0 Changelog](https://kiro.dev/changelog/cli/2-0/)
- [Kiro CLI 2.1 Changelog](https://kiro.dev/changelog/cli/2-1/)
- [Kiro CLI Changelog (all versions)](https://kiro.dev/changelog/cli/)
- [Kiro Changelog (IDE + platform)](https://kiro.dev/changelog/)
- [IDE 0.12: Parallel Task Execution, Quick Plan, Requirements Analysis](https://kiro.dev/changelog/ide/0-12/)
- [Introducing Kiro Powers](https://kiro.dev/blog/introducing-powers/)
- [Powers docs](https://kiro.dev/docs/powers/)
- [Powers GitHub repo](https://github.com/kirodotdev/powers)
- [Kiro Specs docs](https://kiro.dev/docs/specs/)
- [Spec Best Practices](https://kiro.dev/docs/specs/best-practices/)
- [Quick Plan docs](https://kiro.dev/docs/specs/quick-plan/)
- [Kiro Steering docs](https://kiro.dev/docs/steering/)
- [Remote MCP and Global Steering Changelog](https://kiro.dev/changelog/remote-mcp-and-global-steering/)
- [Kiro Hooks docs](https://kiro.dev/docs/hooks/)
- [Kiro Skills docs](https://kiro.dev/docs/cli/skills/)
- [Custom Agent Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference/)
- [Kiro CLI Headless Mode docs](https://kiro.dev/docs/cli/headless/)
- [Session Management docs](https://kiro.dev/docs/cli/chat/session-management/)
- [Kiro Pricing page](https://kiro.dev/pricing/)
- [New Pricing Plans and Auto Agent announcement](https://kiro.dev/blog/new-pricing-plans-and-auto/)
- [Pushing Kiro's Free Tier to Its Limits — DEV Community](https://dev.to/aws/pushing-kiros-free-tier-to-its-limits-5e34)
- [Kiro CLI GitHub Issues](https://github.com/kirodotdev/Kiro/issues)
- [Debugging Kiro's zsh CLI Session Issues](https://www.ernestchiang.com/en/posts/2025/debugging-kiro-zsh-cli-session-issues/)
- [Claude Code vs Kiro comparison — Morph LLM](https://www.morphllm.com/comparisons/kiro-vs-claude-code)
- [AI Coding Agents 2026 comparison — Lushbinary](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- [I Stopped Fighting My AI — DEV Community](https://dev.to/ibrahimpima/i-stopped-fighting-my-ai-how-kiros-agent-hooks-and-steering-files-fixed-my-biggest-frustration-493m)
