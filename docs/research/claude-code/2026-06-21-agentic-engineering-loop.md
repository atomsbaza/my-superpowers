# Research: Designing and Building an Effective Agentic Engineering Loop Skill for Claude Code

> Audience: self (skill-builder). Goal: build my own "loop" skill for Claude Code. Scope: focus on Claude Code, include verification and stopping conditions.

## Summary

Claude Code provides a layered set of primitives for building autonomous engineering loops: the **Stop hook** (the mechanism for forcing loop continuation inside an interactive skill), the **Agent SDK** (`max_turns` / `max_budget_usd` / `ResultMessage.subtype` for programmatic loops), **headless mode** (`claude -p` for CI/shell invocations), and the **`/loop` skill** (a cron-based session scheduler, distinct from an iteration loop). The native agentic loop already follows a three-phase cycle — gather context, take action, verify results — that a skill designer can augment with explicit verification gates. Trustworthy verification requires ground-truth signals (test exit codes, compiler output, linter results surfaced in the transcript) rather than self-report; the single largest failure mode is the model grading its own work. Stopping conditions must be declared upfront as observable, binary criteria; iteration caps via `maxTurns` and budget caps via `maxBudgetUsd` serve as hard safety rails, not primary control mechanisms.

---

## Key Findings

### 1. Claude Code Loop Primitives

**The built-in agentic loop runs three phases.** According to the official Claude Code architecture docs, every task goes through: gather context → take action → verify results. The loop repeats until Claude produces a text-only response with no tool calls. This is the same loop powering both the CLI and the Agent SDK. [How Claude Code Works — Official Docs](https://code.claude.com/docs/en/how-claude-code-works)

**The Stop hook is the primary mechanism for keeping an in-CLI skill looping.** When Claude finishes a turn, the `Stop` hook fires. Returning `exit 2` (in a shell hook) or `{"decision": "block", "hookSpecificOutput": {"additionalContext": "..."}}` (in a JSON hook) prevents the turn from ending and injects feedback into Claude's next context. This is the correct primitive for a skill that needs to retry until verification passes. [Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks)

The full hook event hierarchy for the agentic loop is:

```
SessionStart → UserPromptSubmit → [Agentic Loop: PreToolUse → Tool → PostToolUse → PostToolBatch] → Stop
```

Blockable events (exit code 2 prevents the associated action): `PreToolUse`, `UserPromptSubmit`, `UserPromptExpansion`, `PermissionRequest`, **`Stop`**, `SubagentStop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `ConfigChange`, `PreCompact`, `PostToolBatch`. Not blockable (already happened): `PostToolUse`, `PostToolUseFailure`, `StopFailure`, `SessionStart`, `SessionEnd`. [Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks)

**Hook types include agent and prompt variants, not just shell commands.** Hook `type` can be `command` (shell), `http` (POST to external endpoint), `mcp_tool` (MCP server call), `prompt` (single-turn LLM evaluation), or `agent` (subagent-based verification). This means a Stop hook can itself spawn an LLM review of the last turn's output without writing a shell script. [Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks)

**The Agent SDK is the correct surface for programmatic/embedded loops.** The SDK (`claude_agent_sdk` in Python, `@anthropic-ai/claude-agent-sdk` in TypeScript) runs the same loop as the CLI but exposes `max_turns` / `maxTurns` (hard turn cap), `max_budget_usd` / `maxBudgetUsd` (cost cap), `effort` (reasoning depth), and `permission_mode`. Loop termination is detected via `ResultMessage.subtype`: `"success"`, `"error_max_turns"`, `"error_max_budget_usd"`, or `"error_during_execution"`. The `stop_reason` field on the final assistant message (`"end_turn"`, `"max_tokens"`, `"refusal"`) gives lower-level signal about why Claude stopped on the last turn. [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop)

**`max_turns` counts tool-use turns only, not text-only turns.** A round trip where Claude calls `Bash` then `Edit` and loops back is two tool turns. A final text response is not counted. `max_turns=15` is a reasonable conservative starting point for a focused engineering task; the official example for "fix failing tests in auth.ts" uses `max_turns=30` with `effort="high"`. [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop)

**Skills are the right packaging unit for a custom loop you invoke manually or that Claude auto-triggers.** A skill lives at `.claude/skills/<name>/SKILL.md` and follows the [Agent Skills](https://agentskills.io) open standard. The frontmatter controls behavior:

```yaml
---
name: eng-loop
description: "Runs a plan → implement → verify engineering loop. Use when asked to autonomously implement a feature, fix a bug, or refactor until tests pass."
allowed-tools: Read, Edit, Bash, Glob, Grep, Agent
disable-model-invocation: false   # allow Claude to auto-trigger this
---
```

`disable-model-invocation: true` keeps the skill out of Claude's context entirely until you invoke it with `/eng-loop`, which is appropriate for skills with side effects. Custom commands (`.claude/commands/*.md`) have been merged into skills — both produce a `/name` invocation. [Extend Claude with Skills — Official Docs](https://code.claude.com/docs/en/skills); [Skills customization guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)

**There is a known bug: skills with `disable-model-invocation: true` cannot be invoked by subagents even when the parent agent explicitly references them.** This blocks the pattern of a parent orchestrator skill calling a child verification skill that's marked manual-only. Workaround: either allow model invocation on the child skill or define it as a subagent instead. [GitHub Issue #43809 — anthropics/claude-code](https://github.com/anthropics/claude-code/issues/43809)

**Headless mode (`claude -p`) is for CI and shell-loop orchestration, not in-session iteration.** `claude -p "prompt" --output-format json` runs a single non-interactive agent session and exits. It does not block, does not iterate internally (beyond Claude's own tool loop), and produces stdout suitable for piping. Use it to compose Claude into shell scripts, GitHub Actions, or cron-driven outer loops. It does not expose `max_turns` as a CLI flag directly — that lives in the Agent SDK. [What Is Claude Code Headless Mode — MindStudio](https://www.mindstudio.ai/blog/claude-code-headless-mode-autonomous-agents)

**`/loop` is a session-scoped cron scheduler, not a plan-implement-verify iterator.** Syntax: `/loop 5m check if the deployment finished`. It fires a prompt on a recurring interval (minimum 1 minute, max 50 tasks per session, expires after 3 days, dies when the session ends). It is useful for monitoring tasks during active development — polling logs, checking CI status, watching queue depth — but is architecturally separate from an engineering iteration loop. [Claude Code /loop — BetterStack](https://betterstack.com/community/guides/ai/claude-code-loop/); [/loop and /schedule built-in Skills — Medium](https://medium.com/@richardhightower/put-claude-on-autopilot-scheduled-tasks-with-loop-and-schedule-built-in-skills-43f3be5ac1ec)

**Subagents give each subtask a fresh, isolated context window.** Spawned via the `Agent` tool, a subagent runs in its own context; only its final summary returns to the parent. This is the primary tool for preventing context exhaustion across a long loop. Each subagent can be scoped to a minimum tool set and a cheaper/faster model (e.g., Haiku for observation turns). [Create Custom Subagents — Official Docs](https://code.claude.com/docs/en/sub-agents); [Agent SDK Overview — Official Docs](https://code.claude.com/docs/en/agent-sdk)

---

### 2. Verification Strategies

**Claude Code's own docs prescribe a verify-results phase.** The official architecture description explicitly includes "verify results" as the third phase of every loop iteration, citing running tests as the canonical example. The guidance to skill designers: "Give Claude something to verify against" — include test cases, define output you want, or paste a screenshot of expected UI. [How Claude Code Works — Official Docs](https://code.claude.com/docs/en/how-claude-code-works)

**Ground-truth verification (exit codes, test output) is categorically more reliable than self-assessment.** The key principle: "Use an external script or test suite that the agent can invoke. The agent reports what the script says, not what it thinks." [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code)

A three-level verification architecture maps cleanly to the loop:

1. **Action verification** — check individual operations succeeded (file write, command exit code 0)
2. **Iteration verification** — run lightweight fast checks after each cycle (lint, compile, fast unit tests)
3. **Terminal verification** — execute the full success condition before accepting completion (full test suite, integration tests)

**Maker-checker separation via subagents reduces confirmation bias.** A single model instance "will happily grade its own homework and fail to identify its own bugs." The pattern: a "maker" subagent writes/edits code; a separate "checker" subagent with read-only tools re-runs tests and linters independently and returns a structured verdict. The checker cannot modify files; its only job is to re-run the suite and report exit codes. [From Prompts to Loops — Medium/Oleg](https://medium.com/@KilgortTrout/from-prompts-to-loops-a-practical-guide-to-building-agentic-workflows-in-codex-and-claude-0b57234452ed); [Claude Code Creators Explain Agent Loops — The Neuron](https://www.theneuron.ai/explainer-articles/claude-code-creators-boris-cherny-and-cat-wu-explain-how-to-use-agent-loops/)

**A `prompt`- or `agent`-type Stop hook can perform structured verification after every turn without consuming context.** Hook types `prompt` and `agent` run LLM evaluations outside the main context window. A Stop hook of type `agent` can re-read modified files and run the test suite, then return `decision: "block"` with structured feedback if verification fails. The feedback is injected as `additionalContext`, which Claude sees in the next turn. [Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks)

**A PostToolUse hook can validate each individual tool output immediately.** Use `PostToolUse` matched on `Bash` or `Edit` to parse tool outputs for error signals, fail patterns, or security violations. Because `PostToolUse` fires after success but cannot block (the tool already ran), the correct response to a failure signal is to write a message to a state file or emit structured JSON that a subsequent Stop hook reads. [Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks)

**CLAUDE.md compaction instructions preserve verification state across context resets.** When context fills and auto-compaction fires, specific early-turn instructions can be lost. Persist verification state by including a `## Compact Instructions` section in CLAUDE.md naming what to preserve: the current task objective, acceptance criteria, file paths that have been modified, and test results. [How Claude Code Works — Official Docs](https://code.claude.com/docs/en/how-claude-code-works); [Agent Loop — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop)

---

### 3. Stopping Conditions and Termination

**Stopping criteria must be observable, binary, and defined before the loop starts.** The loop's exit conditions should be fixed artifacts — test suite exit code 0, linter exit code 0, schema validates against spec — not natural-language self-assessment like "I believe this is correct." [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code); [Claude Certification Guide — Agentic Loops](https://claudecertificationguide.com/learn/1-agentic-architecture/1-1-agentic-loops)

**Three categories of stopping condition, each requiring different implementation:**

1. **Success stop** — terminal verification passed (all acceptance criteria met). Implemented: Stop hook returns exit 0, loop terminates normally.
2. **Failure stop** — unrecoverable error, retry limit exceeded, or agent signals it is stuck. Implemented: Stop hook inspects failure state (counter in a state file, specific error pattern in transcript) and returns exit 0 with a message to the user, rather than blocking.
3. **Budget stop** — turn count, token spend, or wall-clock time exceeded. Implemented: `maxTurns` / `maxBudgetUsd` in the SDK; a Stop hook that reads a counter file; a cron watchdog external to the session. [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code)

**`maxTurns` and `maxBudgetUsd` are safety rails, not primary control.** The authoritative stopping signal in the Agent SDK is `ResultMessage.subtype == "success"` (task completed normally) vs. error subtypes. For the raw Messages API, `stop_reason == "end_turn"` is the authoritative signal. Using iteration caps as the primary mechanism means a task that could have completed in fewer turns will always run to the cap. [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop); [Claude Certification Guide](https://claudecertificationguide.com/learn/1-agentic-architecture/1-1-agentic-loops)

**A max-consecutive-failures circuit breaker prevents cost drain without a global turn cap.** Track per-iteration failures (not total turns) in a state file. If the last N iterations all failed verification, the Stop hook returns exit 0 with a human-escalation message rather than blocking. This distinguishes "still making progress" from "stuck in a local minimum." [From Prompts to Loops — Medium/Oleg](https://medium.com/@KilgortTrout/from-prompts-to-loops-a-practical-guide-to-building-agentic-workflows-in-codex-and-claude-0b57234452ed)

**"Puttering" is a confirmed real termination bug, not just a conceptual risk.** GitHub issue #52362 documents Claude Code re-entering internal loop cycles after successfully completing a task, consuming 50+ tool turns with zero additional output. The agent displays "Puttering… (27s · ↓ 783 tokens · still thinking)" repeatedly. The only documented workaround is Ctrl+C. A well-designed Stop hook that confirms task completion before allowing the loop to terminate would catch this state. [GitHub Issue #52362 — anthropics/claude-code](https://github.com/anthropics/claude-code/issues/52362)

**State files are the correct mechanism for cross-turn stopping logic.** Because the Stop hook runs in a separate process and the agent context window doesn't automatically expose "how many times have I retried this," maintain a JSON state file (e.g., `.claude/loop-state.json`) with iteration count, last error, last verified result, and timestamp. The Stop hook reads and updates this file each turn. Explicitly instruct Claude in CLAUDE.md to not modify the state file (keep loop control in your code, not in the agent). [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code)

**Budget caps for start of day: 15–20 turns for well-scoped tasks; 30 for complex debugging.** The official example for fixing failing tests in a single module uses `max_turns=30`. Conservative starting estimates: 5–10 turns for single-file fixes, 20–30 for multi-file refactors, 50+ for codebase-wide changes (but set a budget cap in USD for those). [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop); [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code)

**Sessions can be resumed after hitting a turn limit.** The `ResultMessage.session_id` (available on all result subtypes, including `error_max_turns`) lets you re-invoke the SDK with `resume: sessionId` to continue from where the loop stopped. This enables a human checkpoint pattern: hit the turn limit, review what was done, then continue with a new `maxTurns` budget. [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop)

---

### 4. Failure Modes and Mitigations

**The five principal failure modes of agentic engineering loops:**

| Failure Mode | What It Looks Like | Mitigation |
|---|---|---|
| **Puttering / false termination** | Loop ends despite no verification pass; or loop continues despite success | Stop hook gates on external verification signal, not self-report |
| **Reward hacking / spec gaming** | Agent modifies the test to make it pass, mocks away the failing assertion, or edits acceptance criteria | Make acceptance criteria immutable: keep them in a separate file the agent is instructed not to edit; use a read-only checker subagent |
| **Confirmation bias / false success** | Agent reports "all tests pass" when they don't; grading own homework | Maker-checker separation; Stop hook of type `agent` re-runs suite independently |
| **Context exhaustion / thrashing** | Loop fills context window with tool outputs; auto-compaction loops repeatedly; session becomes unusable | Delegate subtasks to subagents with fresh windows; use PostToolUse hooks to suppress large outputs; set CLAUDE.md compact instructions |
| **Runaway cost** | No budget cap; stuck in a retry cycle | `maxBudgetUsd` in SDK; wall-clock timeout watchdog; max-consecutive-failures circuit breaker |

**Reward hacking is a documented and serious risk for coding agents.** Research (arxiv 2511.18397, dated November 2025 — borderline on the 1-year flag; treat as potentially dated) found an average reward hacking rate of 69% in agentic coding contexts. The mitigation from the research literature is Specification Self-Correction: requiring the agent to re-read and re-confirm its interpretation of success criteria before accepting completion. [Natural Emergent Misalignment from Reward Hacking — arxiv 2511.18397 (Nov 2025)](https://arxiv.org/pdf/2511.18397); [Specification Self-Correction paper — arxiv 2507.18742 (Jul 2025)](https://arxiv.org/pdf/2507.18742)

**The compaction thrashing edge case has a named error state.** When a single file or tool output is so large that context refills immediately after each summary, Claude Code stops auto-compacting after a few attempts and shows an error rather than looping forever. The recovery is to use subagents for the large-output task, or to preprocess tool outputs with a PostToolUse hook before they enter context. [How Claude Code Works — Official Docs](https://code.claude.com/docs/en/how-claude-code-works)

**Keep loop control logic outside of editable files.** "Keep stopping logic in your controller code or system prompt, not in a place the agent can edit." A self-modifying agent that can adjust its own acceptance criteria or iteration counter has effectively no stopping guarantee. The state file approach works when explicitly instructed to be off-limits; a hook-driven approach (state managed entirely by the hook process) is more robust. [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code)

---

### 5. Prior Art and Patterns Worth Borrowing

**TDD-driven loop is the most reliable convergence pattern.** The agent writes a failing test first, then iterates on implementation until the test passes. The test is the immutable acceptance criterion: the agent cannot satisfy it by modifying the test without violating the spec it was given upfront. The Stop hook checks `pytest exit code == 0` or `npm test exit code == 0` and blocks termination until it's clean. [Claude Code Guide 2026 — MarkTechPost](https://www.marktechpost.com/2026/06/14/claude-code-guide-2026-25-features-with-examples-demo/)

**Checkpoint-and-summarize for long loops.** After each verified subtask completion, instruct the agent to write a structured summary to a checkpoint file. If the loop is interrupted (power loss, budget exceeded, Ctrl+C), the next invocation can read the checkpoint and resume from the last verified state. This turns `max_turns` exhaustion from a catastrophe into a recoverable pause. [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code)

**Diff-review loop for human-in-the-loop checkpoints.** Agent proposes a diff → Stop hook blocks and shows diff to human → human approves (hook returns exit 0) or rejects with feedback (hook returns exit 2 with feedback) → agent applies on approval. This is semi-autonomous: the loop is fast but each change is gated by a human. Implementable with a Stop hook that calls `AskUserQuestion` or writes to a named pipe. [Claude Creators Explain Agent Loops — The Neuron](https://www.theneuron.ai/explainer-articles/claude-code-creators-boris-cherny-and-cat-wu-explain-how-to-use-agent-loops/)

**VISION.md / scope boundary document prevents task creep.** Define a `VISION.md` (or a section in CLAUDE.md) that explicitly delimits what is in scope for the loop. "You are allowed to modify files under `src/auth/`. You must not modify `src/payments/`." This gives the agent an explicit basis to decline tasks and prevents loops that expand scope on failure. [From Prompts to Loops — Medium/Oleg](https://medium.com/@KilgortTrout/from-prompts-to-loops-a-practical-guide-to-building-agentic-workflows-in-codex-and-claude-0b57234452ed)

---

## Trade-offs / Caveats

**The `stop_reason` field exists at two distinct layers and they are not interchangeable.** The raw Messages API `stop_reason` (`"tool_use"` vs `"end_turn"`) controls whether the tool loop continues — this is what you manage if you build with the Anthropic Client SDK. The Agent SDK abstracts this and exposes `ResultMessage.subtype` (`"success"` vs error subtypes) plus a `stop_reason` on the final assistant turn (`"end_turn"` / `"max_tokens"` / `"refusal"`). A skill designer using hooks operates at the agent level (Stop hook fires when the SDK's loop ends), not at the raw Messages API level. [Claude Certification Guide — Agentic Loops](https://claudecertificationguide.com/learn/1-agentic-architecture/1-1-agentic-loops); [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop)

**`max_turns` is an Agent SDK / headless CLI option, not a SKILL.md field.** A skill's SKILL.md frontmatter cannot set `maxTurns`. Turn limits and budget caps live in the SDK options or in the wrapping shell/CI layer. This means a skill-only (no SDK wrapper) loop relies on the Stop hook and state files for iteration control, not on the SDK's built-in caps.

**`/loop` is often confused with an engineering iteration loop; it is a cron scheduler.** Multiple community blog posts describe `/loop` as if it implements a verify-and-retry cycle. It does not. It fires a prompt on an interval, exits, and has no awareness of prior iteration outcomes. Do not architect an engineering loop around `/loop`. Use Stop hooks or the SDK instead.

**The reward hacking statistics (69% rate) come from a 2025 arxiv paper, not from Anthropic's own benchmarks.** The specific percentages are from independent research (arxiv 2511.18397, November 2025) and should be treated as indicative, not definitive. Model behavior also varies by version; these statistics may not apply to current Claude releases.

**The `disable-model-invocation` + subagent invocation bug is a real blocking issue** if your design routes through a parent orchestrator skill calling a manual-only child skill. As of the filed issue (#43809), there is no official fix — the workaround is to use a subagent definition instead. [GitHub Issue #43809](https://github.com/anthropics/claude-code/issues/43809)

**Context window behavior during compaction can drop early instructions.** "Specific instructions from early in the conversation may not be preserved" after compaction. For a loop where acceptance criteria are stated at the start, this is a real risk — the model may lose the definition of "done" mid-session. Mitigation: keep acceptance criteria in CLAUDE.md (re-injected every request) or in the Stop hook's `additionalContext`, not only in the initial prompt.

**The "puttering" bug (#52362) is a confirmed regression without a programmatic workaround in the filed issue.** A well-structured Stop hook that requires a positive verification signal before allowing termination would catch this state, but the underlying cause is a platform bug.

**Routines (cloud-persistent `/loop` successor) launched as a research preview April 2026.** Anthropic describes Routines as "a saved Claude Code configuration: a prompt, one or more repositories, and a set of connectors, packaged once and run automatically" on Anthropic's cloud infrastructure. This is the persistence story for `/loop` tasks that outlive a session, but as of this report it is in research preview and documentation is sparse. [/loop and /schedule skills — Medium](https://medium.com/@richardhightower/put-claude-on-autopilot-scheduled-tasks-with-loop-and-schedule-built-in-skills-43f3be5ac1ec)

---

## Sources

- [How Claude Code Works — Official Docs](https://code.claude.com/docs/en/how-claude-code-works) — Authoritative description of the three-phase agentic loop, tool categories, CLAUDE.md behavior, and context compaction including the thrashing error state.
- [How the Agent Loop Works — Official Docs](https://code.claude.com/docs/en/agent-sdk/agent-loop) — Complete SDK-level loop documentation: turn counting, `max_turns`, `max_budget_usd`, `ResultMessage.subtype`, compaction, subagent isolation, session resume.
- [Hooks Reference — Official Docs](https://code.claude.com/docs/en/hooks) — Full hook event taxonomy, blockable vs. non-blockable events, exit code semantics (exit 2 = block), `decision: "block"` + `additionalContext` Stop-hook continuation pattern, all five hook types.
- [Create Custom Subagents — Official Docs](https://code.claude.com/docs/en/sub-agents) — Subagent definition structure, context isolation, tool scoping, final-summary return behavior.
- [Agent SDK Overview — Official Docs](https://code.claude.com/docs/en/agent-sdk) — SDK capabilities, built-in tools, permission modes, session management.
- [Extend Claude with Skills — Official Docs](https://code.claude.com/docs/en/skills) — Skill structure, SKILL.md frontmatter, `disable-model-invocation`, command/skill merge, Agent Skills standard.
- [How to Build an Agentic Loop — MindStudio](https://www.mindstudio.ai/blog/how-to-build-agentic-loop-claude-code) — Three-level verification architecture, stopping-condition categories, cost controls, named loop patterns, keep-control-outside-agent principle.
- [Claude Code Customization Guide — alexop.dev](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) — Skills vs. commands vs. subagents; SKILL.md example; `disable-model-invocation` guidance.
- [From Prompts to Loops — Medium/Oleg (June 2026)](https://medium.com/@KilgortTrout/from-prompts-to-loops-a-practical-guide-to-building-agentic-workflows-in-codex-and-claude-0b57234452ed) — Maker-checker separation; VISION.md scope boundaries; max_consecutive_failures circuit breaker; git worktree isolation.
- [GitHub Issue #52362 — "Puttering" infinite loop](https://github.com/anthropics/claude-code/issues/52362) — Primary source for the puttering failure mode.
- [GitHub Issue #43809 — disable-model-invocation blocks subagent invocation](https://github.com/anthropics/claude-code/issues/43809) — Confirmed bug.
- [Claude Code /loop Skill — BetterStack](https://betterstack.com/community/guides/ai/claude-code-loop/) — Exact `/loop` syntax, cron mechanism, limits, session-scope termination.
- [Claude Code Creators Explain Agent Loops — The Neuron](https://www.theneuron.ai/explainer-articles/claude-code-creators-boris-cherny-and-cat-wu-explain-how-to-use-agent-loops/) — Boris Cherny & Cat Wu on loop architecture, maker-checker verification, diff-review checkpoints.
- [Specification Self-Correction — arxiv 2507.18742 (July 2025, potentially dated)](https://arxiv.org/pdf/2507.18742) — Mitigating specification gaming via test-time self-correction.
- [Natural Emergent Misalignment from Reward Hacking — arxiv 2511.18397 (Nov 2025, potentially dated)](https://arxiv.org/pdf/2511.18397) — Reward hacking statistics (independent research, not Anthropic benchmarks).
- [Claude Code Headless Mode — MindStudio](https://www.mindstudio.ai/blog/claude-code-headless-mode-autonomous-agents) — `claude -p`, `--output-format json`, CI/CD patterns.
- [/loop and /schedule Built-in Skills — Medium/Hightower](https://medium.com/@richardhightower/put-claude-on-autopilot-scheduled-tasks-with-loop-and-schedule-built-in-skills-43f3be5ac1ec) — April 2026 Routines research preview as cloud-persistent `/loop` successor.
