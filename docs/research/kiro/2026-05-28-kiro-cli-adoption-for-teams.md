# Research: Adopting Kiro CLI as a Development Team

> **Audience:** Developer and work team at a company already using Kiro
> **Goal:** Practical adoption — understand what Kiro CLI can do today and how to use it effectively as a team
> **Scope:** Kiro CLI only — excludes IDE plugin and Kiro Web
> **Date:** 2026-05-28

---

## Executive Summary

Kiro CLI (kiro.dev) is AWS's terminal-native AI coding agent, currently at version 2.4.0 (May 20, 2026). It is purpose-built for spec-driven development workflows — turning natural language prompts into structured requirements, design documents, and parallel-executable implementation tasks before writing any code. For teams already using Kiro, the CLI extends the same `.kiro/` configuration directory (steering files, skills, custom agents, MCP servers) into the terminal and CI/CD pipelines. The tool has strong autonomous investigation and multi-step fix capabilities, a solid team-sharing model via committed configuration, and a credit-based pricing model with both individual and team tiers. Key caveats for .NET/C# teams: C# code intelligence requires manual Roslyn LSP setup, and context window compaction bugs can interrupt long sessions. Compared to Claude Code CLI and GitHub Copilot CLI, Kiro's structural spec workflow is its primary differentiator for complex feature work, but adds friction for maintenance and brownfield tasks.

---

## Key Findings by Area

### 1. Kiro CLI Capabilities

The current version is **2.4.0**, released May 20, 2026. [CLI Changelog — Kiro](https://kiro.dev/changelog/cli/)

**Core modes:**
- **Interactive chat mode** — conversational terminal loop, syntax-highlighted TUI by default since 2.0.0
- **Headless mode** — non-interactive, API-key-authenticated execution for CI/CD pipelines (added in 2.0.0, April 13, 2026)

**Built-in tool suite the agent can invoke autonomously:** [Built-in Tools — Kiro](https://kiro.dev/docs/cli/reference/built-in-tools/)
- File operations: `read`, `write`, `glob`, `grep`
- Code intelligence: `code` (symbol search, LSP, AST pattern matching)
- System: `shell` (bash), `aws` (AWS CLI calls)
- Web: `web_search`, `web_fetch`
- Agent delegation: `subagent` (parallel), `delegate` (background async)
- Experimental: `knowledge` (cross-session memory), `thinking` (chain-of-thought), `todo` (step tracking)

**Recent notable additions:**
- 2.4.0: Conversation rewind, `/effort` level control (5 levels of model thinking depth)
- 2.3.0: OAuth for HTTP MCP servers (Slack, GitHub, Figma)
- 2.2.0: Adaptive thinking across turns; fixed silent subagent dispatch failures
- 2.1.0: Skills invokable as slash commands; device-flow auth for SSH/container environments; RHEL support
- 2.0.0: Windows 11 native support; headless CI/CD mode; subagent task dependency graph

**Code intelligence:**
- Tree-sitter indexing for 18 languages (zero setup, millions of tokens supported)
- Optional LSP integration via `/code init` for references, go-to-definition, rename, diagnostics
- C# is supported for Tree-sitter indexing

---

### 2. Spec-Driven Development with Kiro CLI

The spec workflow is Kiro's central differentiator. [Specs — Kiro](https://kiro.dev/docs/specs/)

**Three-phase pipeline:**
1. **Requirements** — structured using EARS notation (`WHEN [condition] THE SYSTEM SHALL [behavior]`), generating testable acceptance criteria
2. **Design** — technical architecture, component diagrams, sequence flows
3. **Tasks** — discrete implementation units with real-time status tracking

**Two workflows:**
- **Requirements-First / Design-First**: Approval gates between each phase; developer reviews and edits before proceeding
- **Quick Plan mode**: Generates all three artifacts in one pass with no gates, for well-understood features

**Parallel task execution:** When you run all tasks, Kiro analyzes the dependency graph, groups independent tasks into "waves," and executes them concurrently. This is automatic — no configuration required.

**Important scoping note:** The three-phase spec creation wizard is described primarily in IDE docs. The `.kiro/` folder containing spec artifacts is shared between IDE and CLI, so a team member who generated a spec in the IDE can hand it off to a CLI user for task execution. Verify CLI-only spec creation against current docs.

**Writing effective specs:**
- One feature per spec
- EARS-formatted requirements with measurable acceptance criteria
- Design documents that specify *why* (not just *what*)
- Tasks sized for single-session implementation
- Reserve specs for complex features, risky refactors, and cross-service changes
- Use "Vibe mode" (chat without spec enforcement) for small fixes

---

### 3. Agent and Autonomous Workflow Capabilities

**Documented real-world example — root cause in 33 seconds:** [Root cause in 33s — Kiro Blog](https://kiro.dev/blog/root-cause-in-33s/)
- Task: Diagnose why P99 build times exceeded 25-30 minutes across 381 packages (550K monthly runs)
- Agent chain: codebase overview → search → file reads → subagent delegation → fix
- Finding: Config parser re-initialized on every function call (80% of CPU)
- Outcome: P99 times dropped from 30+ min to under 1 minute. 10 turns, 33 seconds
- Agent wrote 80-90% of required code changes directly

**Subagent delegation:** The `subagent` tool runs parallel focused agents within a session; `delegate` sends long-running tasks to background agents, freeing the main session.

**When to use autonomous vs. interactive mode:**
- **Autonomous (headless/delegate):** CI/CD quality gates, overnight refactors, batch analysis tasks, well-defined specs with no ambiguity
- **Interactive:** Exploratory investigation, spec writing (where human approval gates add value), tasks requiring judgment calls on architecture

**Note on autonomous agent rollout:** The "execute 10 tasks concurrently" autonomous capability was initially launched for Kiro Web with CLI support described as "coming in the coming weeks." Verify current CLI availability against the changelog before planning workflows that depend on it.

---

### 4. Team Adoption and Onboarding

**The `.kiro/` directory is the team's shared brain — commit it to version control.**

**Configuration scope hierarchy:**
- `~/.kiro/` — global (per-developer machine); deploy via MDM or Group Policy for org-wide defaults
- `.kiro/` at project root — project-scoped; committed to the repo

**Steering files** (`.kiro/steering/*.md`):
- `product.md` — business context, users, objectives
- `tech.md` — frameworks, libraries, constraints
- `structure.md` — file organization, naming, imports, architecture
- Auto-load in every chat session

**AGENTS.md standard support:** Kiro recognizes AGENTS.md files in `~/.kiro/steering/` and the workspace root — always included without explicit configuration.

**Skills** (`.kiro/skills/`): Portable instruction packages for reusable workflows. Examples: `/pr-review`, `/run-tests`. Commit to repo so all team members share the same slash commands.

**Custom agents** (`.kiro/agents/`): Pre-configured agents with pre-approved tools, restricted file paths, and loaded context. Useful patterns:
- A `backend` agent that only sees `src/api/**` and has shell access for `dotnet` commands
- A `reviewer` agent pre-loaded with your style guide steering
- A `devops` agent with AWS CLI access and infrastructure steering

**Important gotcha:** Steering files do NOT auto-load in custom agents — they require explicit glob-pattern references in the agent config. Teams who forget this will find custom agents unaware of project conventions.

**Onboarding a new developer:**
1. Clone repo (gets `.kiro/` with steering, skills, agents)
2. Run `curl -fsSL https://cli.kiro.dev/install | bash`
3. Authenticate (standardize on one method — see Known Limitations)
4. Optional: copy org-wide global steering to `~/.kiro/steering/`
5. Run `kiro-cli` in project root — steering auto-loads

---

### 5. Integration with .NET / C# Projects

**Built-in support (no setup):**
- Tree-sitter C# parsing supported — structural understanding, symbol search, pattern matching across `.cs` files
- `dotnet` commands work through the `shell` tool (build, test, run, EF migrations)

**LSP integration — manual setup required:** [Using C#/Roslyn LSP with Kiro-CLI — Jason Penniman](https://www.jasonpenniman.com/roslyn-kiro)
1. `dotnet tool install -g roslyn-language-server --pre-release`
2. Run `/code init` in Kiro CLI
3. Edit `.kiro/settings/lsp.json` — add Roslyn with `--autoLoadProjects --stdio`, `.cs` extensions, `*.csproj`/`*.slnx` patterns, exclude `bin/` and `obj/`
4. On Windows: wrap the command through `cmd /C`

**C# debugger:** `netcoredbg` (open-source) can be configured to let Kiro CLI debug C# applications. [Allowing Kiro-CLI to debug C# — Jason Penniman](https://www.jasonpenniman.com/kiro-netcoredbg)

**No official .NET-specific CLI guidance exists** in the Kiro documentation.

**Recommended team setup for .NET projects:**
- Commit `lsp.json` with Roslyn config to `.kiro/settings/`
- Add `tech.md` steering documenting: .NET version, target framework, EF Core version + migration conventions, DI patterns, test framework (xUnit), nullable reference types setting, code analyzers in use
- Create a `dotnet` custom agent with pre-approved `shell` commands limited to `dotnet build`, `dotnet test`, `dotnet ef`
- Add a `/ef-migration` skill for the standard EF Core migration workflow

---

### 6. Pricing and Licensing

Current pricing as of May 2026: [Pricing — Kiro](https://kiro.dev/pricing/)

| Plan | Price | Credits/month | Key Features |
|---|---|---|---|
| Free | $0 | 50 | Open weight models + Claude Sonnet 4.5 |
| Pro | $20/user | 1,000 | Premium models, overage available |
| Pro+ | $40/user | 2,000 | Premium models, overage available |
| Power | $200/user | 10,000 | Premium models, overage available |

**Overage:** $0.04 per additional credit; **disabled by default** — must be explicitly opted in.

**Team/Enterprise tier adds:**
- Centralized team billing and usage analytics
- Organizational management dashboard
- SAML/SCIM SSO via AWS IAM Identity Center
- Enterprise security and privacy controls
- Usage reporting per team member

**Key warning:** No published table of credits-per-operation. Autonomous spec generation and multi-step agent runs consume significantly more credits than simple chat. Teams on Pro (1,000 credits) may exhaust credits quickly during heavy spec execution weeks.

---

### 7. Comparison with Similar Tools

| Dimension | Kiro CLI | Claude Code CLI | GitHub Copilot CLI |
|---|---|---|---|
| Core model | Spec-first, structured | Conversational, reasoning-heavy | Reactive completion + issue-assigned agent |
| Async/background tasks | Yes (`delegate` tool) | No native async delegation | Yes (GitHub Actions infra) |
| Spec/planning workflow | Native three-phase spec | Requires manual CLAUDE.md setup | No structured spec |
| Team config sharing | `.kiro/` committed to repo | CLAUDE.md | `.github/copilot-instructions.md` |
| CI/CD headless mode | Yes (API key, 2.0.0+) | Yes (API key) | Integrated with GitHub Actions |
| .NET/C# support | Tree-sitter built-in, Roslyn LSP manual | Full with 1M context | IDE-level completions |
| Model lock-in | AWS Bedrock / Claude only | Anthropic only | Multiple models (GPT-4o, Claude, Gemini) |
| Pricing entry (team) | $20/user/month | ~$100-200/user for heavy use | $10/user/month (Copilot Pro) |
| Brownfield/legacy | Friction with spec-first; Vibe mode available | Best-in-class (1M context, no structure required) | Consistent inline completions |

**Where Kiro CLI has an edge:**
- Spec-driven workflow prevents specification drift on complex features
- Parallel task execution with dependency analysis — no equivalent in Claude Code
- `.kiro/` portability: IDE and CLI share identical config, no duplication
- MCP integration is first-class (HTTP OAuth enables Slack, GitHub, Figma)
- Background `delegate` async tasks while continuing interactive work

**Where Kiro CLI falls short:**
- No model choice outside AWS Bedrock/Claude
- Spec-first adds overhead for small fixes and maintenance
- Credit pricing with opaque per-operation costs makes budgeting uncertain vs. Copilot's flat fee
- Claude Code's 1M context with no mandatory structure is better for undocumented legacy codebases

---

### 8. Known Limitations and Gotchas

**Context window compaction bugs (active):**
- [Issue #5485](https://github.com/kirodotdev/Kiro/issues/5485): CLI triggers compaction at only 18% context usage when a 91KB file is added — likely token-counting miscalculation. No workaround documented.
- [Issue #4105](https://github.com/kirodotdev/Kiro/issues/4105): Context summarization triggering after 1-2 messages in fresh sessions — described as "nearly unusable."
- [Issue #4178](https://github.com/kirodotdev/Kiro/issues/4178): No visible context window percentage indicator; users can't tell when they're near the limit.

**Workaround:** Break long investigations into fresh sessions; use `/effort` levels to reduce token consumption on simpler tasks.

**Account/OAuth identity conflicts:**
- Registering via GitHub OAuth and Google OAuth creates two separate accounts. Switching login methods loses subscription association. Resolution requires contacting support.
- **Teams: standardize on a single auth method** (preferably AWS IAM Identity Center for enterprise SSO).

**Steering files don't auto-load in custom agents:**
- Custom agents require explicit glob-pattern references in their config to load steering files. Default chat mode loads them automatically.

**Spec workflow is IDE-primary:**
- The three-phase spec creation wizard references "the Kiro pane" (IDE). CLI users can work with spec artifact files directly and execute tasks, but creation may require the IDE. Verify before planning a CLI-only spec workflow.

**Credit cost opacity:**
- No published credits-per-operation table. Set overage billing to disabled for all accounts until credit usage patterns are understood.

---

## Trade-offs / Caveats

- **Spec workflow vs. maintenance velocity:** For feature-heavy teams, the spec investment pays off. For teams doing mostly bug fixes and incremental maintenance, Vibe mode (chat without spec enforcement) or Claude Code CLI may outperform.
- **Credit pricing unpredictability:** A real concern for team budgeting vs. GitHub Copilot's flat fee. Overage is opt-in and disabled by default — enforce this as a team policy.
- **`.kiro/` config quality degrades over time** unless someone owns it. Stale steering files, outdated agent configs, and skills that reference deleted files silently degrade agent output. Assign a team member to maintain it.
- **Autonomous agent rollout:** The "10 concurrent tasks" capability launched for Kiro Web first. Verify CLI availability in the current changelog before building workflows around it.

---

## Recommended Adoption Checklist

### Week 1 — Individual setup
- [ ] Install: `curl -fsSL https://cli.kiro.dev/install | bash`
- [ ] Authenticate using one standardized team method (pick one: GitHub, Google, or AWS IAM Identity Center — do not mix)
- [ ] Complete one non-trivial interactive task to calibrate credit consumption before committing to a plan tier
- [ ] Read the [built-in tools reference](https://kiro.dev/docs/cli/reference/built-in-tools/) to understand what the agent can do autonomously

### Week 1-2 — Project `.kiro/` setup (team lead)
- [ ] Create `.kiro/steering/product.md`, `tech.md`, `structure.md` with accurate project context
- [ ] For .NET: install `roslyn-language-server`, run `/code init`, configure `.kiro/settings/lsp.json`, commit to repo
- [ ] In `tech.md`: document .NET version, EF Core version + migration conventions, DI pattern, test framework, nullable reference types, code analyzers
- [ ] Create a `backend` custom agent with file path restrictions and pre-approved `dotnet` shell commands (remember to explicitly reference steering files in the agent config)
- [ ] Commit `.kiro/` to version control (excluding any secrets)

### Week 2-3 — Skills and shared workflows
- [ ] Create a `/pr-review` skill encoding your team's PR checklist
- [ ] Create a `/ef-migration` skill for EF Core migration workflow
- [ ] Run a team session: each member clones the repo and verifies steering auto-loads
- [ ] Test Roslyn LSP on each team member's machine (Windows: verify `cmd /C` wrapper works)
- [ ] Set overage billing to **disabled** for all accounts

### Week 3-4 — Spec workflow and CI/CD
- [ ] Pick one medium-complexity feature and run the full spec workflow to calibrate credit consumption
- [ ] If using headless mode for CI/CD: configure API key auth, test in a non-production pipeline first
- [ ] Assign a team member to own `.kiro/` quality — update steering after major architectural decisions

### Ongoing
- [ ] Monitor [kiro.dev/changelog/cli/](https://kiro.dev/changelog/cli/) — multiple releases per month
- [ ] If context compaction issues affect productivity: break long sessions into fresh sessions
- [ ] Estimate credits per developer type before committing to Pro vs. Pro+

---

## Sources

- [CLI Documentation — Kiro](https://kiro.dev/docs/cli/)
- [CLI Changelog — Kiro](https://kiro.dev/changelog/cli/)
- [Built-in Tools Reference — Kiro](https://kiro.dev/docs/cli/reference/built-in-tools/)
- [Steering — CLI — Kiro](https://kiro.dev/docs/cli/steering/)
- [Custom Agents — Kiro](https://kiro.dev/docs/cli/custom-agents/)
- [Agent Skills — Kiro](https://kiro.dev/docs/cli/skills/)
- [Code Intelligence — Kiro](https://kiro.dev/docs/cli/code-intelligence/)
- [Specs Documentation — Kiro](https://kiro.dev/docs/specs/)
- [Spec Best Practices — Kiro](https://kiro.dev/docs/specs/best-practices/)
- [Pricing — Kiro](https://kiro.dev/pricing/)
- [Root Cause in 33s — Kiro Blog](https://kiro.dev/blog/root-cause-in-33s/)
- [Introducing Kiro CLI — Kiro Blog](https://kiro.dev/blog/introducing-kiro-cli/)
- [Introducing Kiro Autonomous Agent — Kiro Blog](https://kiro.dev/blog/introducing-kiro-autonomous-agent/)
- [Using C#/Roslyn LSP with Kiro-CLI — Jason Penniman](https://www.jasonpenniman.com/roslyn-kiro)
- [Allowing Kiro-CLI to debug C# — Jason Penniman](https://www.jasonpenniman.com/kiro-netcoredbg)
- [C# .NET support Issue #423 — GitHub](https://github.com/kirodotdev/Kiro/issues/423)
- [Context compaction bug Issue #5485 — GitHub](https://github.com/kirodotdev/Kiro/issues/5485)
- [Context summarization Issue #4105 — GitHub](https://github.com/kirodotdev/Kiro/issues/4105)
- [AWS Kiro vs Claude Code vs GitHub Copilot — Signal Over Noise](https://signalovernoise.karlekar.cloud/discovery-2026-04-01-kiro-comparison.html)
- [Battle of AI Coding Agents — Lothar Schulz](https://www.lotharschulz.info/2025/09/30/battle-of-the-ai-coding-agents-github-copilot-vs-claude-code-vs-cursor-vs-windsurf-vs-kiro-vs-gemini-cli/)
- [Kiro vs GitHub Copilot — Augment Code](https://www.augmentcode.com/tools/kiro-vs-github-copilot)
- [rommelporras/kiro-config — GitHub](https://github.com/rommelporras/kiro-config)
- [Getting Started with Spec-Driven Development — DEV Community](https://dev.to/aws-heroes/getting-started-with-spec-driven-development-using-kiro-400l)
- [Kiro Pricing Explained 2026 — Nerova.ai](https://nerova.ai/costs-roi/kiro-pricing-explained-2026)
