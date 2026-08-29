# my-superpowers

Personal collection of AI coding agent skills and agents for Claude Code.

## Structure

```
agents/          Claude Code agent definitions  (→ ~/.claude/agents/)
skills/          All skills, grouped by category (→ ~/.claude/skills/)
  qa/            .NET QA engineer skills
  product-owner/ Product Owner skills
  dotnet/        .NET implementation skills
  apple/         Swift/SwiftUI/XcodeBuildMCP skills
  knowledge-base/ Book/research-derived knowledge bases
  (plus planning/ execution/ quality/ debugging/ git/ communication/ tools/ design/)
docs/            Research reports, session logs, and design specs
  research/
    claude-code/ Claude Code research
    dotnet/      .NET / C# development research
    docklock/    DockLock research
    ios/         iOS / Xcode / Swift research
    kiro/        Kiro CLI research (archived)
    knowledge-bases/ Engineering knowledge-base research (NotebookLM, 108 sources)
    mcp/         MCP server research
    sonarqube/   SonarQube / .NET code-quality research
  sessions/      Work session summaries
  superpowers/   Plans and specs for this repo
tools/           Repo tooling (not installed)
  agent-evals/   Measure & improve agent definitions (A/B vs baseline, benchmark)
```

Skills use the open [AgentSkills](https://agentskills.io/specification) standard. Agent definitions are flat `.md` files in `agents/`.

## Install

```bash
git clone git@github.com:atomsbaza/my-superpowers.git ~/Work/my-superpowers
cd ~/Work/my-superpowers && chmod +x install.sh && ./install.sh
```

The script installs independent copies of agents and skills into place, so AI tools do not load them directly from this repository.

| Tool | Skills | Agents |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/` |
| Codex CLI | `~/.agents/skills/` | — |

To install one skill independently—for example, `book-to-skill` for Codex—run:

```bash
cd ~/Work/my-superpowers
./install.sh --skill book-to-skill --codex-only
```

This installs an independent copy at `~/.agents/skills/book-to-skill`. Add `--force` to replace an existing installation.

Use `--claude-only` or `--codex-only` when installing to just one AI tool.

Repo-level instructions for both tools live in [`CLAUDE.md`](CLAUDE.md); `AGENTS.md` is a symlink to it so Codex CLI picks up the same guidance.

### Orchestrator-only setup (optional)

For a portable Claude Code configuration where the expensive main model (Fable) is hook-enforced to orchestrate only — thinking, planning, and reviewing, but never touching files directly — see [`docs/orchestrator-only-setup.md`](docs/orchestrator-only-setup.md). All edits are delegated to a `sonnet-writer` subagent; the guide covers install steps, verification tests, and a model-tier policy (Fable/Opus/Sonnet/Haiku).

---

## Skills (cross-platform)

### Learning & Pairing
> Use when you want to learn while building: keep the human involved in decisions, work in small slices, and validate with inspectable evidence.

| Skill | What it does |
|---|---|
| `learning-pairing` | English-only, evidence-driven AI pair programming with Observe / Guided / Practice modes, explicit checkpoints, validation, and learning recap |

#### Kiro Crew manual installation

`install.sh` installs copies for Claude Code and Codex CLI. It does not modify Kiro Crew. To use this portable skill with Kiro Crew, copy only its `SKILL.md` into the destination machine's Kiro Crew skills directory:

```bash
cd ~/Work/my-superpowers
mkdir -p "$HOME/.kiro/crew/skills/learning-pairing"
cp skills/learning-pairing/SKILL.md \
  "$HOME/.kiro/crew/skills/learning-pairing/SKILL.md"
```

Then start a new session or reload skills if the runtime requires it, and invoke `$learning-pairing` or say `Use learning pairing for this task`. The skill is behavioral guidance only; it does not include KiroCrew production code, Pairing Preflight, credentials, or runtime state. Do not copy the entire `$HOME/.kiro/crew` directory to another machine.

### Planning
> Use before writing any code — design, investigate, document decisions.

| Skill | What it does |
|---|---|
| `brainstorming` | Explore intent and design before implementation |
| `spec-writer` | Spec-first: feature request → structured spec + ACs + test skeletons, gates code until approved |
| `writing-plans` | Turn a spec into a step-by-step implementation plan |
| `spike` | Time-boxed investigation to answer "can we do X?" |
| `prototype` | Build throwaway prototypes to explore designs |
| `adr` | Capture architecture decisions as ADR documents |
| `codebase-design` | Deep module design vocabulary — seams, interfaces, testability heuristics |
| `domain-modeling` | Build/sharpen ubiquitous language; writes `CONTEXT.md` and ADRs as you design |
| `grill-with-docs` | Relentless design interview that also writes ADRs and glossary entries as it goes |
| `grill-me` | Relentless plan/design interview, resolving each branch of the decision tree until shared understanding |
| `to-issues` | Break a PRD into independently-grabbable vertical-slice GitHub Issues |
| `scale-audit` | Score an architecture proposal against the Order of Magnitude Playbook — flags premature complexity and names the load trigger for the next tier |
| `quarterly-evolution` | Turn "we need to fix X" into a fundable quarterly proposal: entropy audit, business outcome, deferral cost, and success condition |
| `loop-architect` | Design phase before running a loop: read project structure, verify scope, break into tasks, generate a complete four-component Loop Prompt ready for `/loop` |

### Execution

| Skill | What it does |
|---|---|
| `executing-plans` | Inline plan execution with checkpoints and status protocol |
| `loop` | Engineering loop: implement → verify (Stop-hook checker) → repeat until tests pass or cap hit |
| `tdd-loop` | TDD with automated loop verification: write failing test → implement → loop until green |
| `subagent-driven-development` | Execute plans task-by-task with fresh subagents + 2-stage review |
| `dispatching-parallel-agents` | Run independent tasks in parallel |
| `benchmark-sprint` | Parallel agent fleet tests N architectural variants simultaneously and returns a comparison report — 3 days of manual benchmarking in 20 minutes |
| `tdd` | Red-green-refactor loop, integration-test-first workflow |

### Quality & Review

| Skill | What it does |
|---|---|
| `scrutinize` | Outsider sanity check — "should this exist and does it do what it claims?" |
| `ponytail` | Force the laziest solution that works — YAGNI, stdlib over custom, native over deps (lite/full/ultra) |
| `verify-before-stop` | Always-on regression guard: runs tests on git-changed files before every session end |
| `circuit-breaker` | Loop Stop hook with stuck-detection: escalates to human when the same error repeats N times |
| `secrets-guardrail` | PostToolUse hook that redacts API keys, tokens, and passwords from all tool output |
| `requesting-code-review` | Two-stage review: spec compliance first, then code quality |
| `receiving-code-review` | Handle review feedback rigorously, not blindly |
| `improve-codebase-architecture` | Find refactoring and architecture opportunities |
| `verification-before-completion` | Run checks before claiming work is done |
| `good-enough` | Detects the Esthetics Trap — finds the value ceiling, audits remaining effort as VALUE vs AESTHETICS, and recommends ship/defer |
| `pragmatic-review` | Scores a proposal against the Engineering Diagnostic Matrix (scale strategy, tech choice, quality definition, reaction to AI) and outputs concrete adjustments |
| `security-review` | Security checklist for auth, user input, secrets, API endpoints, and payment/sensitive features |
| `security-auditor` | OWASP Top 10 vulnerability audit expert, with remediation/checklist/OWASP reference bundles and secret-scanning scripts |
| `ai-agent-security` | Threat-model and defensive review for prompt injection, RAG, tool abuse, data exfiltration, and AI security gates |
| `code-review` | Read-only two-axis diff review with evidence-backed confidence and impact thresholds |
| `code-review-quality` | Context-driven code review focused on quality, testability, and maintainability, with a structured output schema |
| `ci-quality-gates` | Design and audit CI quality gates, evidence, failure handling, staged rollout, and rollback readiness |
| `performance` | Web performance audit and optimization — load time, page speed |

### Debugging

| Skill | What it does |
|---|---|
| `diagnose` | Disciplined bug investigation loop |
| `post-mortem` | Write the canonical record of a fixed bug |

### Git & Branches

| Skill | What it does |
|---|---|
| `using-git-worktrees` | Isolated workspace setup before plan execution |
| `finishing-a-development-branch` | Guided merge/PR/cleanup when implementation is done |
| `git-advanced-workflows` | Rebasing, cherry-picking, bisect, worktrees, and reflog for clean history and repo recovery |

### Communication

| Skill | What it does |
|---|---|
| `session-summary` | Summary of current work session from git + context |
| `handoff` | Compact conversation for another agent to pick up |
| `management-talk` | Rewrite technical content for leadership audiences |
| `business-impact` | Translate a technical proposal into quantified business terms: revenue at risk, churn %, uptime hours, cost per hour of downtime |

### Design

| Skill | What it does |
|---|---|
| `frontend-design` | Guidance for distinctive, intentional visual design — aesthetic direction, typography, avoiding templated defaults |

### Tools

| Skill | What it does |
|---|---|
| `research` | Web research — audience/goal/scope interview, then searches, fetches, and synthesizes a cited report saved to `docs/research/<topic>/` |
| `research-verify` | Research a tool/API/system, then verify the draft against a live ground truth (installed CLI, live docs) via a fact-checking agent before publishing — for operational docs, not just background reading |
| `teach` | Structured learning framework: manage MISSION, build reference materials, produce beautiful HTML lessons grounded in research, capture learning records |
| `session-promoter` | End-of-session learning extractor: promotes corrections, decisions, and project facts into persistent memory |
| `find-skills` | Discover and install new skills |
| `writing-skills` | TDD-based guide for creating new skills |
| `skill-doctor` | Grades agent setup from real conversation transcripts — efficiency + code-quality + skill-coverage scores, drafted skill improvements, HTML report. Vendored from warpdotdev/common-skills. |
| `writing-great-skills` | Reference vocabulary and principles for writing predictable, well-structured skills |
| `mediumlm` | Research a topic on Medium using the user's own logged-in session — search, fetch full article text, save a research note |
| `notebooklm` | Full programmatic access to Google NotebookLM — create notebooks, add sources, generate podcasts/mind maps/study guides |
| `neuroarxiv` | Check real arXiv prior art before non-trivial architecture decisions; isolate paper reads, score and cluster approaches, then recommend one cited path |
| `oss-contribute` | End-to-end OSS contribution workflow — fork, orient, implement, scrutinize, open a PR |
| `changelog-writer` | Generate changelogs/release notes from commits, PR titles, and issues — Keep a Changelog format, semver suggestions |
| `chrome-extension-development` | Manifest V3 Chrome extension development — security, performance, best practices |
| `herdr-workflow` | Coordinate Codex/Claude/Kiro CLI agents through Herdr — panes, worktree isolation, parallel implementer/reviewer/tester roles, handoff |
| `wayfinder` | Codebase exploration and architecture mapping |
| `xcodebuildmcp-cli` | Reference for driving XcodeBuildMCP from the CLI for Apple platform builds |
| `graphify` | Turn any input (code, docs, papers, images, videos) into a persistent knowledge graph with god nodes, community detection, query/path/explain tools |
| `tessera-panes` | Drive and observe a neighboring Tessera pane — discover panes, send keystrokes, poll/stream output |
| `design-patterns-csharp` | Knowledge base from *Design Patterns* (Gang of Four, 1994) and *Design Patterns in C#* (Sarcar, 2018) — all 23 patterns with canonical definitions and C# implementations, Simple Factory/Null Object/MVC, pattern criticisms, anti-patterns, modern C# notes (2025–26) |
| `designing-data-intensive-apps` | Knowledge base from *Designing Data-Intensive Applications* by Martin Kleppmann — storage engines, data models, replication, partitioning, transactions, consistency, batch/stream processing, derived data |
| `graph-engineering-knowledge-base` | Research-synthesized knowledge base on Graph Engineering (NotebookLM deep research, ~140 sources) — graph data models, property graphs vs RDF, ontology (OWL/SHACL/SKOS), Neo4j/Cypher, GraphRAG, distributed graph processing, graph ML/GNNs, multi-agent orchestration graphs |
| `nygard-production-resilience` | Knowledge base from *Release It!* by Michael T. Nygard — stability, capacity, availability, failure containment, observability, safe release |
| `richards-ford-software-architecture` | Knowledge base from *Fundamentals of Software Architecture* by Mark Richards and Neal Ford — architecture characteristics, trade-off analysis, connascence, architecture styles, quanta, fitness functions, risk storming |
| `software-engineering-at-google` | Knowledge base from *Software Engineering at Google* — sustainable software, teams, testing, code review, build systems, dependency management, CI/CD, managed compute |
| `dobovizki-csharp-concurrency` | Knowledge base from *C# Concurrency: Asynchronous and Multithreaded Programming* by Nir Dobovizki — async/await, compiler state machines, thread safety, SynchronizationContext, multithreading patterns, concurrent collections, async streams |
| `fowler-refactoring` | Knowledge base from *Refactoring: Improving the Design of Existing Code* by Martin Fowler — code smells, refactoring mechanics, the Two Hats, the Rule of Three, small steps, composing methods, organizing data, simplifying conditionals |
| `head-first-design-patterns` | Knowledge base from *Head First Design Patterns*, 2nd ed., by Freeman, Robson, Sierra & Bates — all GoF patterns with the book's OO principles, compound patterns, real-world patterns, Java-style worked examples |
| `khononov-ddd` | Knowledge base from *Learning Domain-Driven Design* by Vlad Khononov — subdomains, bounded contexts, context mapping, tactical patterns (Domain Model, Event Sourcing), architectural patterns, EventStorming, microservices |
| `martin-clean-architecture` | Knowledge base from *Clean Architecture* by Robert C. Martin — SOLID, component cohesion/coupling principles, the Dependency Rule, boundaries, use cases and entities |
| `martin-clean-code` | Knowledge base from *Clean Code* and *The Clean Coder* by Robert C. Martin — naming, functions, testing, refactoring, code smells, TDD, professionalism, estimation, craftsmanship |
| `ousterhout-software-design` | Knowledge base from *A Philosophy of Software Design* by John Ousterhout — deep vs shallow modules, information hiding, complexity, tactical vs strategic programming, error handling, comments, cohesion |
| `pragmatic-programmer` | Knowledge base from *The Pragmatic Programmer: From Journeyman to Master* by Andrew Hunt and David Thomas — DRY, orthogonality, tracer bullets, reversibility, Design by Contract, Law of Demeter, programming by coincidence, broken windows |
| `pro-async-dotnet` | Knowledge base from *Pro Asynchronous Programming with .NET* by Richard Blewett and Andrew Clymer — async/await, Task Parallel Library (TPL), SynchronizationContext, ConfigureAwait, concurrent collections, PLINQ, synchronization primitives |
| `tdd-knowledge-base` | Research-synthesized knowledge base on Test-Driven Development (NotebookLM deep research, 89 sources) — Detroit/classicist vs London/mockist styles, testing pyramid, anti-patterns, Transformation Priority Premise, the "Is TDD Dead?" debate |
| `webappsec-defense` | Knowledge base synthesized from *Grokking Web Application Security* by Malcolm McDonald (Manning, 2024) and *Web Application Security: Exploitation and Countermeasures for Modern Web Applications* by Andrew Hoffman (O'Reilly, 2nd ed., 2024) — XSS, CSRF, injection, XXE, authn/authz, session design, threat modeling, CVSS, Zero Trust, dependency security |

---

## Agents

Claude Code agent definitions live in `agents/` (one flat `.md` each).

| Agent | What it does |
|---|---|
| `principal-dotnet-engineer` | Solo full-SDLC agent for C# .NET 8/10: requirements → design → implementation → tests → review. OceanBase, EF Core, MediatR, Serilog, xUnit, Testcontainers. |
| `qa-dotnet-engineer` | Full QA lifecycle: risk analysis, ISTQB manual test cases, Reqnroll BDD, Playwright E2E, NBomber performance, defect reports. |
| `po-agent` | Language-agnostic Product Owner: vision, BRD, PRD, user stories, acceptance criteria, backlog prioritization (RICE/WSJF/MoSCoW/Kano), sprint plans, roadmaps, release notes. |

#### General Development Agents
> Language- and platform-agnostic agents for everyday coding work.

| Agent | What it does |
|---|---|
| `code-reviewer` | Reviews code changes for bugs, logic errors, edge cases, and security issues. |
| `debugger` | Investigates bugs and unexpected behavior, root cause analysis. |
| `dependency-auditor` | Audits a new dependency before it's added: security, maintenance health, license, alternatives. |
| `doc-updater` | Keeps project documentation aligned with implementation after feature/architecture changes. |
| `docs-writer` | Writes READMEs, API docs, inline comments, and changelogs. |
| `nextjs-reviewer` | Reviews Next.js App Router code — server/client boundaries, API routes, middleware, data fetching. |
| `pr-description` | Writes a pull request title and description from git diff and commit history. |
| `refactor` | Refactors code for clarity, maintainability, or performance. |
| `release-checklist` | Runs a pre-release checklist — iOS App Store, web app, or general. |
| `research` | Web research agent — structured markdown report with cited sources. |
| `silent-failure-hunter` | Finds silent failures, swallowed errors, unsafe fallbacks, misleading success states. |
| `sonnet-writer` | Implements all code and file changes — the delegate for an orchestrator-only main model. |
| `test-writer` | Writes unit/integration tests and edge case coverage for existing code. |
| `wiki-updater` | Updates the Obsidian project vault after significant work. |

The Apple/iOS/macOS agents below are platform-specific; the general development
agents above (plus `sonnet-writer`) are available in every project alongside them.

#### Apple / iOS / macOS Agents
> Focused, single-responsibility agents for Apple platform development (iOS 26, macOS 26, Swift 6.3). Prefer XcodeBuildMCP over shell.

| Agent | What it does |
|---|---|
| `swift-reviewer` | Swift 6.3 review: concurrency safety, `@Observable` isolation, Sendable, ARC, Foundation/AppKit/SwiftUI API correctness. |
| `ui-reviewer` | HIG, iOS 26 Liquid Glass, macOS Tahoe, SF Symbols 6, Dynamic Type, accessibility. |
| `xcode-build` | Build failures, code signing, privacy manifests, SPM, archiving. |
| `privacy-reviewer` | `PrivacyInfo.xcprivacy`, `NS*UsageDescription` quality, App Store privacy labels. |
| `simulator-qa` | Verifies the running app via XcodeBuildMCP screenshot/snapshot_ui — golden path and edge states. |
| `ios-test-runner` | Runs `test_sim`, triages results, enforces XCTestCase for SwiftData tests. |

Measure and improve these definitions with [`tools/agent-evals/`](tools/agent-evals/) — an A/B evaluation engine plus autonomous improvement loops.

#### Principal .NET Engineer Skills (`skills/dotnet/`, `skills/planning/`, `skills/quality/`, `skills/tools/`)
| Skill | What it does |
|---|---|
| `analyzing-requirements` | BRD/PRD → bounded contexts, FRs, NFRs, open questions, recommended ADRs |
| `authoring-adrs` | MADR-format Architecture Decision Records |
| `designing-systems` | C4/ASCII diagrams, API contracts, entity model, OceanBase partition strategy |
| `designing-database-schema` | EF Core Fluent API + OceanBase-compatible DDL, utf8mb4, partition migrations |
| `implementing-dotnet` | C# .NET 8/10 code generation with security and logging standards |
| `writing-tests` | xUnit unit tests, Testcontainers integration, WebApplicationFactory API tests, Bogus |
| `reviewing-code` | 3-Golden-Rules review: correctness, security, observability, rollback assessment |
| `orchestrating-workflow` | Chains all 7 principal engineer skills via workflow-state.json |
| `efcore-knowledge-base` | Research-synthesized knowledge base on EF Core performance (NotebookLM deep research, 98 sources) — single vs split query, ExecuteUpdate/ExecuteDelete, Dapper vs EF Core benchmarks, database-agnostic architecture, Hangfire connection-pool exhaustion, Pomelo/OceanBase provider notes |

#### QA .NET Engineer Skills (`skills/qa/`)
| Skill | What it does |
|---|---|
| `analyzing-requirements-for-qa` | BRD/PRD → risk-scored testable inventory (SFDIPOT + EP/BVA, P0/P1/P2) |
| `creating-test-plan` | Risk-based test plan with pyramid, entry/exit criteria, environment strategy |
| `generating-manual-test-cases` | ISTQB-format manual test cases with technique selection guide |
| `generating-bdd-scenarios` | Reqnroll `.feature` files + C# step definition stubs |
| `analyzing-codebase-for-test-gaps` | Grep-based scan for untested methods, missing exception paths, OceanBase issues |
| `generating-automation-scripts` | POM + Playwright E2E + Testcontainers integration + Bogus data factories |
| `generating-performance-tests` | NBomber steady-state, spike, soak, OceanBase pool pressure tests |
| `reporting-test-results` | Evidence-backed ISTQB defect reports, execution summary, and Go/No-Go recommendation |
| `orchestrating-qa-workflow` | Chains all 8 QA skills via .qa-workflow-state.json |

#### Product Owner Skills (`skills/product-owner/`)
| Skill | What it does |
|---|---|
| `writing-product-vision` | Vision board, Geoffrey Moore positioning statement, JTBD, north star themes |
| `writing-brd` | Business Requirements Document with problem, goals, stakeholders, risks |
| `writing-prd` | Product Requirements Document with personas, user journeys, FRs, NFRs |
| `brd-to-prd` | Converts an existing BRD/stakeholder brief into a PRD with user stories, ACs, and edge cases |
| `to-prd` | Turns the current conversation context into a PRD and publishes it to the project issue tracker |
| `prd-to-tdd` | Converts an approved PRD into a Technical Design Document — architecture, API contracts, data model, sequence flows, error handling |
| `writing-user-stories` | INVEST-quality stories via SPIDR splitting from epics or PRD |
| `writing-acceptance-criteria` | Gherkin Given/When/Then ACs covering happy path, validation, auth, edge cases |
| `prioritizing-backlog` | RICE / WSJF / MoSCoW / Kano prioritization with scoring worksheets |
| `planning-sprint` | Sprint goal, story selection, capacity planning, risk/dependency mapping |
| `writing-roadmap` | Outcome-based Now/Next/Later or OKR roadmap with exclusions |
| `writing-release-notes` | Customer-facing release notes from sprint deliverables or commit history |
| `orchestrating-po-workflow` | Chains all 9 PO skills via .po-workflow-state.json |

#### Apple / SwiftUI Skills (`skills/apple/`)
| Skill | What it does |
|---|---|
| `swift-concurrency-expert` | Swift 6.2+ concurrency review + remediation: Sendable, `@MainActor`, actor isolation, data-race fixes, completion-handler → async/await migration |
| `swift-concurrency-pro` | Concurrency correctness, modern async/await API usage, and common pitfalls when reading/writing/reviewing Swift concurrency code |
| `swiftui-patterns` | Modern MV architecture, `@Observable` ownership, `@State`/`@Bindable`/`@Environment` wiring, view decomposition, `.task` data loading |
| `swiftui-navigation` | NavigationStack, NavigationSplitView, sheets, tabs, programmatic routing, deep linking, universal links, custom URL schemes |
| `swiftui-layout-components` | Stacks, grids, lists, forms, `.searchable`, ViewThatFits, Layout protocol, Liquid Glass containers, adaptive multi-platform layouts |
| `swiftui-performance` | Diagnose slow rendering, janky scroll, body-evaluation cost, identity churn, lazy loading, Instruments profiling guidance |
| `swiftdata-pro` | Writes, reviews, and improves SwiftData code — modelling, queries, migrations, persistence — using modern APIs and best practices |
| `ce-test-xcode` | Build and test iOS apps on simulator via XcodeBuildMCP after code changes, before a PR, or to check for crashes |

---

## Credits

**Adapted from [obra/superpowers](https://github.com/obra/superpowers)** by Jesse Vincent (MIT):
`brainstorming`, `writing-plans`, `spike`, `prototype`, `adr`, `subagent-driven-development`,
`executing-plans`, `dispatching-parallel-agents`, `requesting-code-review`, `receiving-code-review`,
`verification-before-completion`, `using-git-worktrees`, `finishing-a-development-branch`,
`writing-skills`, `find-skills`

**Adapted from [thananon/9arm-skills](https://github.com/thananon/9arm-skills)** by Thananon:
`scrutinize`, `post-mortem`

**Adapted from [mattpocock/skills](https://github.com/mattpocock/skills)** by Matt Pocock:
`codebase-design`, `domain-modeling`, `grill-with-docs`, `to-issues`, `writing-great-skills`, `wayfinder`

**Adapted from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)** (MIT):
`ponytail`

**Adapted from [UditAkhourii/neuroarxiv](https://github.com/UditAkhourii/neuroarxiv)** (MIT):
`neuroarxiv`

**Derived from *The Pragmatic Engineering Playbook*** by Bassem Dghaidi (NotebookLM, 2024):
`scale-audit`, `quarterly-evolution`, `good-enough`, `pragmatic-review`, `business-impact`, `benchmark-sprint`

**Derived from *Loop Engineering*** by Bassem Dghaidi (NotebookLM, 2025):
`loop-architect`

**Original work in this repo:**
`loop`, `tdd-loop`, `spec-writer`, `circuit-breaker`, `secrets-guardrail`, `verify-before-stop`,
`session-promoter`, `research`, `diagnose`, `improve-codebase-architecture`, `session-summary`,
`handoff`, `management-talk`, `learning-pairing`

See [ATTRIBUTION.md](ATTRIBUTION.md) for full details.
