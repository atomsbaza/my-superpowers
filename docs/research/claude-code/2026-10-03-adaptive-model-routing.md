# Research: Adaptive Model Routing for Claude Code (Haiku / Sonnet / Opus)

> Audience: self (agent/workflow builder). Goal: route each task to the cheapest model that can do it well, inside Claude Code multi-agent workflows (Architect, Engineer, QA, Code Reviewer). Scope: tier design, routing rules, escalation, Claude Code mechanics, and what was applied to this machine.

## Provenance and evidence quality

- **Origin:** a ChatGPT conversation (shared link, titled "ตรวจสอบข้อเท็จจริง" / fact-check) started from an Instagram Reel that claimed a "Junior / Middle / Senior / Goat" model-tiering scheme with per-task costs. ChatGPT could not open the Reel, so **the claims in the clip itself were never seen or verified**. The substantive content came from the follow-up turn ("go into more detail, I'll use this with Claude Code").
- **ChatGPT's verdict on the clip: "partly true".** The idea of routing by difficulty is supported; the clip's specific cost figures ($0.79, $0.27, $0.05) and the claim that the four-level split picks the right model in every situation are **unverified**.
- **Second pass (2026-10-03):** the Claude Code mechanics below were re-checked against the current official docs (`code.claude.com/docs/en/sub-agents`, `.../model-config`, and Anthropic's "Choosing a Claude model and effort level in Claude Code" post) by a read-only agent. Caveat: the fetch tool returns model-summarised excerpts, not raw page text, so exact wording is not guaranteed. Re-read the pages before depending on an edge case.
- **Pricing** (Haiku 4.5 $1/$5, Sonnet 5.5 $2/$10, Opus 5.5 $4/$20 per 1M input/output tokens) is **source-reported by the ChatGPT conversation, not independently checked here.** Prices drift; confirm on Anthropic's pricing page.
- Several secondary sources the conversation cited (Medium, SitePoint, a tech blog on the "harness") are practitioner write-ups, not controlled studies.

## Summary

Use a small, expensive-model-sparing hierarchy: **Haiku** for read-only and mechanical work, **Sonnet** for implementing from a clear brief, **Opus** for architecture and hard diagnosis, and **Opus plus an independent reviewer** for security, data integrity, and major migrations. Choose the tier by **ambiguity and risk, not by how important the task feels.** Static `model:` pins in each agent file give a sensible default per role, but a router (the main agent) must override per task, because a single role such as "architect" sometimes gets an easy job and sometimes a hard one. Escalate on **evidence** (failing tests, failed QA, reviewer disagreement), and before escalating, check whether the failure was really missing context or unrun tests, since a larger model does not fix those. Anthropic's own guidance agrees: if Claude had the context and tried clearly but was still wrong, pick a larger model; if it skipped a file or did not run tests, raise effort or fix the process.

---

## 1. The four-tier model

| Tier | Typical model | Task shape | Examples |
|---|---|---|---|
| 1. Simple / routine | Haiku | clear steps, low judgment | text/doc edits, summarize logs and errors, generate unit tests that follow an existing pattern, explain code, locate files |
| 2. Standard engineering | Sonnet | needs context, edits several places | new API endpoint, business logic, refactor a function, integration tests |
| 3. Complex reasoning | Opus | cross-system analysis, ambiguous problems | design a new system, debug across services, concurrency and race conditions, plan a high-impact migration |
| 4. Critical / expert review | Opus + independent review | high blast radius | security vulnerability review, data-integrity analysis, architecture trade-offs, wide-impact change review |

This is a **workflow design aid, not a capability ranking.** The right model for a task type depends on measured results for that task type; the tiers are a starting hypothesis to be tuned with your own pass/fail data.

## 2. Static routing: agent files with a pinned `model:`

Put one agent per role in `.claude/agents/` and pin the default model in frontmatter.

```text
.claude/
├── agents/
│   ├── architect.md
│   ├── engineer.md
│   ├── qa.md
│   ├── code-reviewer.md
│   └── explorer.md
└── settings.json
```

`explorer.md` (read-only investigation, Haiku):

```markdown
---
name: explorer
description: Explore the codebase, locate relevant files, and summarize existing patterns. Use for read-only investigation.
model: haiku
tools: Read, Grep, Glob
---

You are a codebase exploration agent.

Your responsibilities:
- Locate relevant files and existing implementations.
- Identify dependencies and coding conventions.
- Summarize findings with file paths and line references.
- Identify uncertainties and report them to the parent agent.

Constraints:
- Do not modify any files.
- Do not implement features.
- Keep the report concise and evidence-based.
```

`engineer.md` (implementation, Sonnet):

```markdown
---
name: engineer
description: Implement well-defined software tasks, features, and bug fixes.
model: sonnet
---

You are a software engineer working in an existing codebase.

Before implementing:
- Read relevant files and project instructions.
- Follow established architecture and conventions.
- Confirm the task scope and acceptance criteria.

During implementation:
- Make focused changes.
- Avoid unrelated refactoring.
- Add or update tests.
- Run relevant checks.

After implementation:
- Summarize changed files.
- Report tests executed and results.
- Disclose unresolved issues.
```

`architect.md` (design, Opus):

```markdown
---
name: architect
description: Design architecture and investigate complex technical decisions.
model: opus
---

You are a software architect.

Responsibilities:
- Analyze requirements and constraints.
- Inspect existing architecture and dependencies.
- Compare design alternatives and trade-offs.
- Identify scalability, reliability, security, and maintainability risks.
- Produce an implementation plan with clear acceptance criteria.

Do not implement code unless explicitly requested.
Ground recommendations in the actual codebase.
Clearly separate verified facts from assumptions.
```

**Limit of static pinning:** the conversation's own caveat is that an architect handed a task that only needs a structure explanation could run on Sonnet or Haiku. The pin fixes the role's default, not the task's difficulty. That gap is what dynamic routing closes.

## 3. Dynamic routing: the main agent as router

`model: haiku` in a file is static. To pick a model per task, add a step where the main agent analyzes the task and decides which agent to delegate to and on which model.

```text
Main Agent / Router  (analyzes task, context, risk, acceptance criteria)
        │
   Task classification: Simple · Standard · Complex · Critical
        │
  ┌─────┴─────┬───────────┬────────────┐
 Haiku      Sonnet       Opus      Opus + independent review
 explore,   implement,   architecture,   security, data integrity,
 summarize, bug fix      hard debugging  major migration
 routine test
        │
 Verification and escalation: tests, QA, review → if they fail, analyze why, then raise capability only if warranted
        │
 Final result with verification evidence
```

### 3.1 Routing table

| Task condition | Start with | Approach |
|---|---|---|
| Find files, read code | Haiku | read-only |
| Summarize error or log | Haiku | pass on only the cause found |
| Single-point edit with a clear pattern | Sonnet | implement + test |
| Multi-file change inside one feature | Sonnet | plan first, then implement |
| Architecture change | Opus | analyze alternatives before editing |
| Debug with unknown cause | Sonnet, then Opus | escalate if analysis does not succeed |
| Security / data integrity | Opus | add an independent review |
| Failing test caused by complex logic | Sonnet, then Opus | root-cause analysis |

### 3.2 Classification factors

- **Complexity:** number of files and coupling between components.
- **Ambiguity:** how clear the requirement is.
- **Risk:** impact if the code is wrong.
- **Verification:** whether tests or static analysis can check the result.
- **Context:** how much must be read and understood.

Worked example from the source: a one-file change that computes money or transaction correctness can carry **more** risk than a multi-file refactor that already has strong test coverage. File count alone is a poor tier signal.

### 3.3 Escalation discipline

1. Escalate when verification fails and the cause is not obvious, or when reviewers disagree.
2. First ask what actually failed:
   - Missing context, files not read, or tests not run → fix the process or raise **effort**, not the model.
   - Context was present, the attempt was clear, and the answer was still wrong → raise the **model**.
3. Report the final result with its verification evidence (tests run, review outcome).

## 4. What the official docs say (re-verified 2026-10-03)

Claude Code mechanics that routing depends on. Source pages: `sub-agents`, `model-config`, and the model/effort blog post. Values come from an agent that read the pages through a summarising fetcher.

**Subagent `model:` values.** A model alias (`sonnet`, `opus`, `haiku`, `fable`), a full model ID (same values as `--model`), or `inherit` (use the main conversation's model). If omitted, the model is chosen by the order below.

**Precedence, highest first:**

1. The per-invocation `model` parameter on the Agent/Task tool.
2. The definition's `model` frontmatter (`inherit` selects the main model).
3. The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable.
4. The main conversation's model.

`CLAUDE_CODE_SUBAGENT_MODEL_FORCE` forces one model on every subagent (exact semantics not read). **Consequence for routing:** a router that sets `model` on each Agent call wins over the file's pin, so "frontmatter = default, call-site = override" is the supported pattern.

**Built-in subagents.**

- *Explore* uses the main model; if the main model is the top tier it runs on whatever the `opus` alias resolves to on subscription, Console, or `ANTHROPIC_BASE_URL` gateway setups, and stays on the main model on Bedrock, Google Cloud, Foundry, and similar providers.
- *Plan* inherits the main model.
- *general-purpose* follows `CLAUDE_CODE_SUBAGENT_MODEL` if set, else the main model.
- *statusline-setup* uses Sonnet and *claude-code-guide* uses Haiku.

**Effort.** Per-subagent `effort` frontmatter is supported (`low|medium|high|xhigh|max`, depending on model), overriding the session level; default is inherit. The `effortLevel` setting accepts `low|medium|high|xhigh` and works in user, project, local, and managed settings, but **a top-level `effortLevel` in user settings does not apply to Opus 5.5 or newer**; use per-model settings or `/effort`. Anthropic's effort guide: `low` for quick exchanges, `medium` for day-to-day scoped work (default on Opus 5.5 and Sonnet 5.5), `high` for bug fixes and work where verification or edge cases matter, `max` for hard problems run unattended such as finding security vulnerabilities.

**Anthropic's own selection guidance.** "Start with the defaults, then reach for the dials." Smaller models suit precisely describable edits, mechanical changes, and questions about code already in context. Larger models suit subtle bugs, unfamiliar domains, and architecture. The diagnosis rule in §3.3 comes from this guidance.

### 4.1 Correction: `availableModels` does NOT work in user settings

The conversation's source list included a docs mirror describing `availableModels` as a way to restrict selectable models. Re-verification shows:

- It is **managed/policy settings only.** In user, project, local, or `--settings` it is **ignored with a warning**. The same applies to `enforceAvailableModels`.
- When it is active, it also constrains subagent models (frontmatter, the Agent tool's `model`, teammate models, `CLAUDE_CODE_SUBAGENT_MODEL`). If a pinned family alias is blocked, the subagent falls back to the newest allowed version of that family (v2.1.222 onward), else to the inherited model. Other kinds of unavailability (for example an outage) are not documented.
- Entries match a family (`sonnet`), a version prefix (`claude-sonnet-4-5`), or a full ID; a prefix also matches later IDs that extend it by one segment.

**Practical effect:** you cannot hide a model by editing `~/.claude/settings.json`. Realistic ways to avoid a model are to keep `model` set to the desired alias, pin every agent explicitly, and not select it in `/model`, or to deploy a managed-settings file (a system-level, admin change).

## 5. Applied on this machine (2026-10-03)

- **Rule file:** `~/.claude/rules/model-routing.md`, loaded every session. Contains the routing table, the five factors, and escalate-on-evidence. Review is made Sonnet-first, with Opus only for concurrency, security, data-loss surfaces, or conflicting findings, to match the existing tier policy rather than defaulting to Opus review.
- **Pins added** to agents that previously inherited the main model: `qa-execution-operator` → haiku; `qa-incident-investigator`, `qa-requirements-risk-analyst`, `qa-test-architect`, `quality-engineering` → opus. These five are plain files in `~/.claude/agents/` (Kiro import), not symlinks into this repo.
- **Existing tiers** (unchanged): Opus for debugger, security-engineer, solution-architect, sre, swift-reviewer, tech-lead, ai-engineer; Sonnet for engineer, code-reviewer, docs, research, ui-reviewer and similar; Haiku for wiki-updater.
- **Default session model:** `"model": "sonnet"` in `~/.claude/settings.json`.
- **Fable guard (hook, not a setting):** since `availableModels` cannot be set in user settings, `~/.claude/hooks/no-fable-subagent.sh` runs as a PreToolUse hook on `Agent|Task`. It blocks (exit 2) a subagent that would run on Fable, either through an explicit `model` or by inheriting a Fable main session. It resolves the model in the documented order (call-site `model`, then the agent file's frontmatter, then the main model, read from the transcript with `settings.json` as fallback) and honours the same `orchestrator-off` escape hatch as `orchestrator-only.sh`. A hook only blocks use; Fable stays selectable in `/model`. Verified with nine synthetic payloads; **not yet verified against a live `Agent` call**, so the payload field names (`tool_input.model`, `subagent_type`) and whether a settings change reloads without a new session are assumptions.
- **Cleanup:** the ineffective `availableModels` entry that was briefly added to user settings was removed.

## 6. Open questions and how to resolve them

1. **Do the tiers hold for your tasks?** Log first-pass success per tier on real work (tests green on first attempt, review findings per change) and adjust the routing table from data, not from the clip's cost figures.
2. **Does the router actually follow the rule?** The rule file is advice to the main agent. Verify by checking which `model:` each Agent call used over a few sessions; if drift shows, consider a hook that logs or enforces it.
3. **Per-task effort vs. model.** Subagent `effort` frontmatter exists; test whether raising effort on Sonnet closes gaps before paying for Opus.
4. **Pricing.** Re-check the per-token prices before using them in any cost estimate.

## Sources

Cited by the conversation (not all re-read):

- Claude Code sub-agents docs: `code.claude.com/docs/en/sub-agents`
- Claude Code model configuration: `support.claude.com/en/articles/11940350-claude-code-model-configuration`; `code.claude.com/docs/en/model-config`
- Claude Code FAQ: `support.claude.com/en/articles/12386420-claude-code-faq`
- Anthropic: "Choosing a Claude model and effort level in Claude Code" (claude.com/blog, 2026-07-07)
- Anthropic: "Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents" (claude.com/blog, 2026-06-18)
- Practitioner write-ups: pasqualepillitteri.it (Claude Code harness architecture, 2026 guide); sitepoint.com (Claude Code 2.5 features); medium.com/@adnanmasood ("Right-Sizing the Frontier": LLM routing and token-per-dollar); securityboulevard.com (Claude Code marketplace plugins, 2026-06)
- Docs mirrors on GitHub (RobGruhl/anthropic-docs-mirror, pleaseai/claude-code-docs, seanGSISG/claude-code-docs): treat as secondary, they lag the live docs.
