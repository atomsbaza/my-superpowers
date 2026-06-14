# my-superpowers

Personal collection of AI coding agent skills and agents for Claude Code.

## Structure

```
.claude/agents/  Claude Code agent definitions  (→ ~/.claude/agents/)
.claude/skills/  Claude Code skills — .NET / QA / PO  (→ ~/.claude/skills/)
skills/          Cross-platform skills           (→ ~/.claude/skills/)
docs/            Research reports, session logs, and design specs
  research/
    claude-code/ Claude Code research
    dotnet/      .NET / C# development research
    docklock/    DockLock research
    ios/         iOS / Xcode / Swift research
    kiro/        Kiro CLI research (archived)
    mcp/         MCP server research
    sonarqube/   SonarQube / .NET code-quality research
  sessions/      Work session summaries
  superpowers/   Plans and specs for this repo
tools/           Repo tooling (not installed)
  agent-evals/   Measure & improve agent definitions (A/B vs baseline, benchmark)
```

Skills use the open [AgentSkills](https://agentskills.io/specification) standard. Agent definitions are flat `.md` files in `.claude/agents/`.

## Install

```bash
git clone git@github.com:atomsbaza/my-superpowers.git ~/Work/my-superpowers
cd ~/Work/my-superpowers && chmod +x install.sh && ./install.sh
```

The script symlinks agents and skills into place.

| Tool | Skills | Agents |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/` |
| Codex CLI | `~/.agents/skills/` | — |

---

## Skills (cross-platform)

### Planning
> Use before writing any code — design, investigate, document decisions.

| Skill | What it does |
|---|---|
| `brainstorming` | Explore intent and design before implementation |
| `writing-plans` | Turn a spec into a step-by-step implementation plan |
| `spike` | Time-boxed investigation to answer "can we do X?" |
| `prototype` | Build throwaway prototypes to explore designs |
| `adr` | Capture architecture decisions as ADR documents |

### Execution

| Skill | What it does |
|---|---|
| `executing-plans` | Inline plan execution with checkpoints and status protocol |
| `subagent-driven-development` | Execute plans task-by-task with fresh subagents + 2-stage review |
| `dispatching-parallel-agents` | Run independent tasks in parallel |

### Quality & Review

| Skill | What it does |
|---|---|
| `scrutinize` | Outsider sanity check — "should this exist and does it do what it claims?" |
| `requesting-code-review` | Two-stage review: spec compliance first, then code quality |
| `receiving-code-review` | Handle review feedback rigorously, not blindly |
| `improve-codebase-architecture` | Find refactoring and architecture opportunities |
| `verification-before-completion` | Run checks before claiming work is done |

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

### Communication

| Skill | What it does |
|---|---|
| `session-summary` | Summary of current work session from git + context |
| `handoff` | Compact conversation for another agent to pick up |
| `management-talk` | Rewrite technical content for leadership audiences |

### Tools

| Skill | What it does |
|---|---|
| `research` | Web research — audience/goal/scope interview, then searches, fetches, and synthesizes a cited report saved to `docs/research/<topic>/` |
| `find-skills` | Discover and install new skills |
| `writing-skills` | TDD-based guide for creating new skills |

---

## Agents

Claude Code agent definitions live in `.claude/agents/` (one flat `.md` each).

| Agent | What it does |
|---|---|
| `principal-dotnet-engineer` | Solo full-SDLC agent for C# .NET 8/10: requirements → design → implementation → tests → review. OceanBase, EF Core, MediatR, Serilog, xUnit, Testcontainers. |
| `qa-dotnet-engineer` | Full QA lifecycle: risk analysis, ISTQB manual test cases, Reqnroll BDD, Playwright E2E, NBomber performance, defect reports. |
| `po-agent` | Language-agnostic Product Owner: vision, BRD, PRD, user stories, acceptance criteria, backlog prioritization (RICE/WSJF/MoSCoW/Kano), sprint plans, roadmaps, release notes. |

Measure and improve these definitions with [`tools/agent-evals/`](tools/agent-evals/) — an A/B evaluation engine plus autonomous improvement loops.

#### Principal .NET Engineer Skills (`.claude/skills/`)
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

#### QA .NET Engineer Skills (`.claude/skills/`)
| Skill | What it does |
|---|---|
| `analyzing-requirements-for-qa` | BRD/PRD → risk-scored testable inventory (SFDIPOT + EP/BVA, P0/P1/P2) |
| `creating-test-plan` | Risk-based test plan with pyramid, entry/exit criteria, environment strategy |
| `generating-manual-test-cases` | ISTQB-format manual test cases with technique selection guide |
| `generating-bdd-scenarios` | Reqnroll `.feature` files + C# step definition stubs |
| `analyzing-codebase-for-test-gaps` | Grep-based scan for untested methods, missing exception paths, OceanBase issues |
| `generating-automation-scripts` | POM + Playwright E2E + Testcontainers integration + Bogus data factories |
| `generating-performance-tests` | NBomber steady-state, spike, soak, OceanBase pool pressure tests |
| `reporting-test-results` | ISTQB defect reports, executive summary, Go/No-Go recommendation |
| `orchestrating-qa-workflow` | Chains all 8 QA skills via .qa-workflow-state.json |

#### Product Owner Skills (`.claude/skills/`)
| Skill | What it does |
|---|---|
| `writing-product-vision` | Vision board, Geoffrey Moore positioning statement, JTBD, north star themes |
| `writing-brd` | Business Requirements Document with problem, goals, stakeholders, risks |
| `writing-prd` | Product Requirements Document with personas, user journeys, FRs, NFRs |
| `writing-user-stories` | INVEST-quality stories via SPIDR splitting from epics or PRD |
| `writing-acceptance-criteria` | Gherkin Given/When/Then ACs covering happy path, validation, auth, edge cases |
| `prioritizing-backlog` | RICE / WSJF / MoSCoW / Kano prioritization with scoring worksheets |
| `planning-sprint` | Sprint goal, story selection, capacity planning, risk/dependency mapping |
| `writing-roadmap` | Outcome-based Now/Next/Later or OKR roadmap with exclusions |
| `writing-release-notes` | Customer-facing release notes from sprint deliverables or commit history |
| `orchestrating-po-workflow` | Chains all 9 PO skills via .po-workflow-state.json |

---

## Credits

Several skills adapted from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.
Several skills adapted from [thananon/9arm-skills](https://github.com/thananon/9arm-skills) by Thananon.
