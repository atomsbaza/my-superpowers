# Research: subagent-driven-development skill by obra

## Summary

The `subagent-driven-development` (SDD) skill is part of **obra/superpowers**, an open-source software development methodology and Claude Code plugin created by Jesse Vincent and the team at Prime Radiant. It executes structured implementation plans by dispatching a fresh, isolated subagent for each individual task, ensuring context pollution is prevented across long sessions. After each task, two sequential review subagents run — one verifying spec compliance, the other evaluating code quality — before the controller moves to the next task. The skill integrates natively with Claude Code (where it has the deepest support) and also works with Cursor, Codex CLI, Gemini CLI, and others. It is positioned as the execution engine in a larger pipeline: consuming plans from the `writing-plans` skill and handing off to `finishing-a-development-branch` on completion.

---

## Key Findings

- **What it is:** `subagent-driven-development` is a Claude Code skill inside the [obra/superpowers](https://github.com/obra/superpowers) framework — a composable set of skills and methodology for coding agents. It orchestrates task execution via fresh subagents rather than a single long-running context.

- **Who is "obra":** "obra" is the GitHub handle of **Jesse Vincent**, founder of Prime Radiant. The superpowers repo has 89K+ GitHub stars (as of 2026) and is available on Anthropic's official Claude Code plugin marketplace.

- **Core formula:** Fresh subagent per task + Two-stage review (Spec Compliance → Code Quality) = High quality, fast iteration. No human check-ins between tasks unless blocked.

- **Step-by-step workflow:**
  1. Read the implementation plan once; extract all tasks; create a `TodoWrite` tracker.
  2. For each task: dispatch an **Implementer Subagent** with full task text and context (subagent never reads plan files directly — context is passed explicitly).
  3. Implementer builds feature, writes tests, commits, and self-reviews, then reports one of four status codes: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
  4. **Stage 1 — Spec Compliance Review:** A dedicated reviewer reads actual code (not implementer claims) to verify nothing was added or omitted.
  5. **Stage 2 — Code Quality Review:** Only after spec passes, a second reviewer evaluates cleanliness and maintainability.
  6. If either review finds issues, the implementer fixes and that review stage repeats. When clean, mark task complete and loop to next.

- **Model selection strategy:** Optimizes cost by matching model capability to task complexity — cheap/fast for isolated 1-2 file tasks, standard for multi-file coordination, most capable for architecture or broad codebase work.

- **Pipeline position:** SDD consumes output from the `writing-plans` skill and hands off to `finishing-a-development-branch` on completion. It is the execution layer of a full obra/superpowers development pipeline.

- **Claude Code integration:** Uses Claude Code's `Task` tool to dispatch subagents. Available via Anthropic's official plugin marketplace.

- **Where to find it:** [github.com/obra/superpowers](https://github.com/obra/superpowers), Anthropic Claude Code plugin marketplace, [skills.sh](https://skills.sh/obra/superpowers/subagent-driven-development).

---

## Trade-offs / Caveats

- **Platform depth varies:** Claude Code has the deepest integration. Features like allowed-tools sandboxing and automatic updates may not be available on other platforms (Cursor, Codex CLI, Gemini CLI).

- **"No human check-ins" is aggressive:** The only built-in pause point is the `BLOCKED` escalation. Teams wanting manual gates would need to adapt the skill.

- **Two-stage review cost:** Two additional review subagents per task adds API cost and latency. The model selection strategy partially mitigates this.

- **Pipeline dependency:** Designed to consume structured output from `writing-plans`. Ad-hoc use requires manually formatting plans in the expected structure.

- **Star count unverified:** The 89K+ star figure comes from search result summaries and could not be independently verified; treat as approximate.

---

## Sources

- [GitHub — obra/superpowers](https://github.com/obra/superpowers) — Main repository for the superpowers agentic skills framework
- [SKILL.md — subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md) — Official skill definition with full workflow
- [DeepWiki — subagent-driven-development](https://deepwiki.com/obra/superpowers/7.4-subagent-driven-development) — Detailed breakdown of the SDD skill, model selection, and status codes
- [antigravity.codes](https://antigravity.codes/agent-skills/workflow/subagent-driven-development) — Agent skill listing with pipeline context
- [skills.sh](https://skills.sh/obra/superpowers/subagent-driven-development) — Skill registry entry
- [ClaudePluginHub](https://www.claudepluginhub.com/plugins/obra-superpowers-2) — Plugin marketplace listing
