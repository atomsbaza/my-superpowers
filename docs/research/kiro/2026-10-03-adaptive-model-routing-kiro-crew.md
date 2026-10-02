# Research: Adaptive Model Routing in Kiro Crew

> Audience: self (agent/workflow builder). Goal: translate the Claude Code routing scheme in [`../claude-code/2026-10-03-adaptive-model-routing.md`](../claude-code/2026-10-03-adaptive-model-routing.md) to Kiro Crew. Scope: where Kiro Crew lets you choose a model, what "Auto" already does, cost trade-offs, and a proposed (not applied) mapping for the agents on this machine.

## Provenance and evidence quality

| Source | Trust | Used for |
|---|---|---|
| Docs bundled in the installed app (`KiroCrew.app/.../kiro_crew/docs/*.md`: `agents`, `crew-members`, `session-control`, `subagents`, `configuration`, `agent-spec-fields`) | High: ships with the installed version, read directly 2026-10-03 | every Kiro Crew mechanic below |
| `kiro.dev/docs/models/` (fetched through a summarising tool) | Medium: model list, context sizes, credit multipliers, regions | cost table |
| Local `~/.kiro/agents/*.json` | High: read directly | current model values |
| A ChatGPT conversation "วิจัย Multi Agents Kiro Crew" (shared link; it read the `kirodotdev/KiroCrew` GitHub repo, dated 2026-10-02) | Low-medium: secondary, and some claims did not match the local docs | feature inventory only |

**Installed version:** `kirocrew 0.8.0-insider.4`. The ChatGPT conversation assumed 0.7.2 and attributed Crew Teams, Work Ledger, and Monitor Loops to `main`; this machine is already on 0.8.0 insider, so some of those may exist locally, but I did not verify each one.

### Where the ChatGPT conversation was wrong or loose

- It showed `kirocrew spawn run "Analyze the API architecture"`. The bundled `subagents.md` says the grammar is `spawn <task>` (or `bg <task>`) and "there is no `run` subcommand".
- Its custom-agent example uses `"model": "claude-opus"`. That exact string is copied from the bundled `agents.md` example, so it is an illustration, not proof that the alias is valid for every backend. Earlier research in this repo recommends full versioned IDs for kiro-cli; confirm what your backend accepts (§3).
- Preview status of newer features (Crew Teams, Work Ledger) is the conversation's own caveat; it was not independently checked.

## Summary

Kiro Crew already has a built-in router: the default model is **`auto`**, which defers to the configured provider (and, for Kiro itself, to its automatic per-task routing at a 1.0x credit baseline). So the question differs from Claude Code. There you must build routing yourself; here the choice is **Auto versus an explicit pin per role and per spawn**. A model can be set at six levels (agent JSON, crewmate, session start, session switch, per-spawn override, global default) and there are separate fallback settings. Recommended stance: keep `auto` for general and conductor agents, **pin explicitly only where the role has a clear cost or risk profile** (cheap mechanical workers, expensive analysis), and use the per-spawn `model` and `reasoning_effort` as the "router override", keeping in mind that setting either forces a dedicated process instead of session sharing.

## 1. Where a model can be chosen

Documented in the bundled docs (read 2026-10-03):

| Level | Setting | Effect |
|---|---|---|
| Global default | `agent.model` (config), default `"auto"` | "defers to the agent config, then to Kiro's own default"; a per-session picker overrides it for that session only |
| Agent template | `model` in `~/.kiro/agents/<name>.json` (or markdown frontmatter; project `.kiro/agents/` also works) | the template's pinned model |
| Crew member | Model field | "the template's pinned model, then the global default" |
| Session start | `model` parameter of the session-open tool | pinned as if picked in the dropdown; refused with `model_rejected` if the picker would refuse it |
| Mid-session | `session_set_model` | accepts a canonical key or provider id such as `sonnet` or `opus`; recorded as a pending pick and applied on the target's next turn |
| Per spawn | `spawn_run` `model` and `reasoning_effort` | override for that spawn; **forces the dedicated-process path** |

Stated precedence: a per-session pick always wins over the crewmate's model and reasoning effort, and the crewmate's values win over the global defaults. How the per-spawn `model` ranks against the template's pin is **not stated** in what I read; treat it as the explicit override and test before relying on it.

**Effort:** `agent.reasoning_effort` (`""`, `low`, `medium`, `high`, `xhigh`, `max`; `""` defers to the model default), a per-session override, and per-spawn `reasoning_effort`. Models that do not reason ignore it.

**Fallbacks:** `agent.fallback_model` (used after the active model exhausts its transient-retry budget; `"auto"` = availability-aware routing; `""` disables) and `agent.refusal_fallback_model` (retries one declined message on another model). These keep a pinned model from becoming a single point of failure, which Claude Code's docs do not offer in the same form.

**Harness caveat:** the spec's `model` field reaches each backend by a different channel (for example `set_config_option` after session creation for some harnesses). `model` and `prompt` arrive everywhere; other fields do not. The model vocabulary is owned by the harness, so a valid ID on one backend may be rejected on another.

**Read-only agents:** markdown agent specs are read-only to Kiro Crew on the `kiro` backend (JSON only), and `kirocrew agent reset-model` edits only Kiro-Crew-managed specs. Files named `kirocrew-skill-view-*.json` are generated; do not hand-edit them.

## 2. What Auto costs relative to pins

From the Kiro models page (fetched 2026-10-03; a summarising tool, so re-read before budgeting):

| Model | Context | Credit multiplier |
|---|---|---|
| Auto | none | 1.0x (baseline) |
| Claude Haiku 4.5 | 200K | 0.4x |
| Claude Sonnet 5 | 1M | 1.3x |
| Claude Opus 5.5 | 1M | 2.0x |
| Claude Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | 1M (4.5: 200K) | 2.2x |
| Claude Fable 5.1 | 1M | 6x (Enterprise Preview, US East only) |
| GPT-5.6 Luna / Terra / Sol | 1M | 1.1x / 2.2x / 4.4x (doubled over 272K tokens) |
| DeepSeek 3.2 / MiniMax M2.5 / GLM-5 / Qwen3 Coder Next | 128K to 256K | 0.25x / 0.25x / 0.5x / 0.05x |

Observations:

- Opus 5.5 (2.0x) is cheaper than older Opus versions (2.2x) on Kiro, so "Opus for hard analysis" should pin the newest listed Opus.
- **Sonnet 5.5 is not listed** on Kiro as of this fetch (Sonnet 5 is), so the Claude Code tier "Sonnet 5.5" has no exact Kiro equivalent yet.
- The page's own caveat applies: real consumption also depends on tokens generated, internal thinking depth, and tokenizer differences, so multipliers are a ranking, not a bill.
- **Exact model ID strings for the agent `model` field are not listed on that page.** Pick them from the app's model picker or the Template pane rather than guessing.
- Per-subagent credit attribution was a known gap in the repo's May 2026 Kiro CLI research; re-check before using cost per agent as a metric.

## 3. What is configured on this machine (read 2026-10-03)

| Agent group | `model` value |
|---|---|
| `kirocrew`, `-conductor`, `-guest`, `-heartbeat`, `-knowledge`, `-ledger-conductor`, `-lite`, `-pipeline-conductor`, `-research`, `-security-conductor`, `-worker` | `auto` |
| `knowledge-retrieval-auditor` | `gpt-5.6-luna` (also 3 generated skill-view specs) |
| `qa-execution-operator`, `qa-incident-investigator`, `qa-requirements-risk-analyst`, `qa-test-architect`, `quality-engineering` | `null` (no pin: falls back to the global default, which is `auto` unless changed) |

So today everything runs on Auto except one Luna-pinned auditor. The five `null` agents are the same ones that had no pin on the Claude Code side before the 2026-10-03 change.

## 4. Proposed mapping (not applied)

Nothing under `~/.kiro` was changed. This is a proposal to review before editing.

| Role | Proposal | Reason |
|---|---|---|
| Conductors, main `kirocrew`, guest, heartbeat, lite | keep `auto` | general-purpose; Auto is the 1.0x baseline and already routes per task |
| `qa-execution-operator` | cheap pin (Haiku 4.5, 0.4x) | mechanical, allowlisted execution and reporting |
| `qa-incident-investigator`, `qa-requirements-risk-analyst`, `qa-test-architect`, `quality-engineering` | newest listed Opus (5.5, 2.0x) or keep `auto` until measured | analysis where a miss is expensive; but Auto may already route these well |
| `knowledge-retrieval-auditor` | keep `gpt-5.6-luna` | deliberate existing choice |
| Per-spawn router override | set `model` only when the task class is clear: read-only exploration or summarising → cheap; ambiguous diagnosis or security review → top Opus | each override forces a dedicated process, so do not set it casually |

Escalation and "check context before upgrading" from the Claude Code note carry over unchanged: they are workflow rules, independent of runtime.

## 5. Differences from Claude Code that matter

| Topic | Claude Code | Kiro Crew |
|---|---|---|
| Built-in router | none (you write the rule) | `auto` default; Kiro routes per task |
| Per-call override | `model` on the Agent call (highest precedence) | `model` / `reasoning_effort` on `spawn_run`; precedence vs template pin not stated; forces a dedicated process |
| Mid-session switch | `/model` | `session_set_model` (applied next turn) or the picker |
| Restricting models | `availableModels` is managed-settings only | per-harness vocabulary; no equivalent verified here |
| Fallback | only for `availableModels` blocks | `agent.fallback_model`, `agent.refusal_fallback_model` |
| Effort | per-agent `effort` frontmatter, `effortLevel` setting | `agent.reasoning_effort`, per-session and per-spawn |
| Cost visibility | per-token prices | credit multipliers relative to Auto |
| Concurrency | not a routing concern | `agent.max_subagents` (`0` = auto-sized from memory; explicit values are floored at 3) |

## 6. Open questions

1. What exact model ID strings does the `kiro` backend accept in the JSON `model` field, and is the unversioned `claude-opus` alias valid there?
2. Does a spawn-time `model` override beat the target agent template's pin? Test with a throwaway spawn and read back `session_read_message`, which shows the target's current model.
3. Does Auto beat a manual pin on your own tasks? Run the same QA task on `auto` versus a pinned Opus and compare first-pass results and credits before pinning the four analysis agents.
4. Does `null` fall through to `agent.model` as the docs imply for crew members? Confirm in the Template pane for one of the five `null` agents.
5. Will Sonnet 5.5 appear in the Kiro model list? Until it does, "Sonnet-tier" on Kiro means Sonnet 5.

## Sources

- Bundled docs (installed app, 0.8.0-insider.4): `agents.md`, `crew-members.md`, `session-control.md`, `subagents.md`, `configuration.md`, `agent-spec-fields.md`, `dynamic-subagent-sizing.md`
- `kiro.dev/docs/models/` (model list, context, credit multipliers, Auto)
- Prior research in this repo: [`2026-05-27-kiro-cli-orchestrator-agents-quality-cost.md`](./2026-05-27-kiro-cli-orchestrator-agents-quality-cost.md) (per-agent `model`, versioned IDs), [`2026-08-14-kiro-crew-technical-review.md`](./2026-08-14-kiro-crew-technical-review.md)
- ChatGPT shared conversation "วิจัย Multi Agents Kiro Crew" (secondary; read of the `kirodotdev/KiroCrew` repo dated 2026-10-02)
