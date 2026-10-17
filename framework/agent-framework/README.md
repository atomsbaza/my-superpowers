# Agent Framework — OpenCode V2 Software Factory

A portable package of the OpenCode V2 multi-agent software factory: one
`orchestrator` agent running a research → design → plan → implement → review →
test → wrap-up pipeline through 24 specialist subagents, with engine-level
permission hardening and per-agent model pins (OpenCode Go Plus).

This folder is the **canonical distribution copy**. The live install lives in
`~/.config/opencode/` on each machine. Deep documentation:
[`docs/opencode-workflow-setup.md`](../../docs/opencode-workflow-setup.md)
(hardening mapping, verification semantics, parallel-run rules, known gaps).

Packaged: 2026-10-17 · model pins as of that date · requires OpenCode V2.

---

## What you get

| Piece | File(s) here | Installs to | What it does |
| --- | --- | --- | --- |
| Orchestrator | `orchestrator.md` | `~/.config/opencode/agents/orchestrator.md` | Primary agent: 3-lane pipeline (2-WAY / 1-WAY / ROUTINE), blind reviewer dispatch, stage-boundary commits, Work Board integration, learnings forced-read |
| Sync script | `sync-from-claude.py` | `~/.config/opencode/sync-from-claude.py` | Mirrors Claude-side agents into OpenCode's config + appends the hardening (skill/MCP permission denies), artifact-write scoping, and the per-agent MODEL map (15 pins) |
| `/wf` | `commands/wf.md` | `~/.config/opencode/commands/wf.md` | Start a full workflow run (asks about active runs + slug collisions first) |
| `/wf-status` | `commands/wf-status.md` | `~/.config/opencode/commands/wf-status.md` | Pipeline status for one run (or the newest) |
| `/wf-list` | `commands/wf-list.md` | `~/.config/opencode/commands/wf-list.md` | Every run with status (ACTIVE / DONE / PARKED) and staleness |

The 24 specialist workers themselves come from **this repo's `agents/`**
(installed by `./install.sh`) — they are not duplicated here. The same goes for
the 177 skills. One repo install covers both Claude Code and OpenCode.

## Prerequisites

1. **OpenCode V2** signed in to a provider (`/connect`).
2. **OpenCode Go Plus** subscription (model pins target `opencode-go/*` —
   $40/month). Without it, remove the `MODEL` map from the sync script or
   accept session-model inheritance.
3. This repo cloned, with `agents/` present (`./install.sh --force` installs
   workers + skills to `~/.claude/`).
4. MCP servers you want (optional): `playwright` (interaction review),
   `notion` (Work Board), `my-memory` (retro hook), `xcodebuildmcp` (iOS
   test runs). Hardening denies are harmless if a server is absent.

## Install on a new machine

```sh
# 1. Live config dir
mkdir -p ~/.config/opencode/agents ~/.config/opencode/commands

# 2. Copy this package (adjust REPO to your clone)
REPO=~/Work/my-superpowers/framework/agent-framework
cp "$REPO/orchestrator.md"      ~/.config/opencode/agents/
cp "$REPO/sync-from-claude.py"  ~/.config/opencode/
cp "$REPO"/commands/*.md        ~/.config/opencode/commands/

# 3. Generate opencode.json's agents map (hardening + model pins) from the
#    Claude-side agents. Back up first if the file already exists.
cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.pre-factory
python3 ~/.config/opencode/sync-from-claude.py
# → "agents written: 24; skipped: ['haiku-engineer', 'qa-execution-operator']"

# 4. Verify (see the doc's §6 for the full assertion list)
opencode api get /api/agent      # 24 subagents + orchestrator (primary, 16 allows, model gpt-6-luna)
opencode api get /api/command    # wf, wf-status, wf-list present
```

Then in OpenCode: `/connect` your providers, and `/wf <task>` starts the
pipeline. The orchestrator classifies every task into a lane at UNDERSTAND:

- **2-WAY** (auth, payments, migrations, schema, interfaces, boundaries,
  data flows) → full pipeline with independent architect gates
- **1-WAY** (routine, reversible) → light review, no architect gates
- **ROUTINE** (one mechanical change) → single engineer dispatch, orchestrator
  reads the diff itself

Every run writes `docs/workflow/<slug>/` in the target repo
(`learnings.md`, `log.md`, `research.md`, `design.md`, `plan.md`,
`diff-summary.md`) and closes with a `DONE:` line in `log.md`.

## Maintenance (existing machine)

- **Edit prompts on the live files**, then mirror back to this repo — every
  prompt file has TWO copies that must stay identical:
  | Live | Canonical mirror in this repo |
  | --- | --- |
  | `~/.config/opencode/agents/orchestrator.md` | `framework/agent-framework/orchestrator.md` + `agents/orchestrator.md` (pre-P1 baseline; see git log) |
  | `~/.config/opencode/sync-from-claude.py` | `tools/mirror/sync-from-claude.py` |
  | `~/.config/opencode/commands/*.md` | `framework/agent-framework/commands/` |
  | Claude-side workers `~/.claude/agents/*.md` | `agents/*.md` |
- After editing any `~/.claude/agents/*.md`, re-run
  `python3 ~/.config/opencode/sync-from-claude.py` — it regenerates the
  `agents` key of `opencode.json` (hand edits there are lost on every sync;
  per-agent permission/model changes go in the script's `hardening()` and
  `MODEL` sections).
- `diff` both copies after every edit; run `doctor.py` (repo) before
  committing agent/skill edits — ERROR findings block.
- **Model pins**: Go's roster and limits rotate — re-verify quarterly against
  <https://opencode.ai/v2/docs/console/go/>. `#variant` effort suffixes do not
  resolve for these models today (no catalog variants).

## Key design decisions (why it looks like this)

- **Workflow files live outside `opencode.json`** (Markdown agent + commands +
  hardening in the sync script) — the sync rewrites the `agents` key wholesale.
- **Orchestrator is coordination-only** — it dispatches, verifies on disk, and
  commits; it never produces artifacts itself.
- **Engineer never commits** — the orchestrator is the sole committer, at
  stage boundaries, on the run's branch, never pushing.
- **Reviewers are blind** — they receive spec/plan artifacts and changed
  files, never the implementer's report or each other's findings.
- **Memory writes stay out of subagents** — a subagent digesting untrusted
  content must never reach the memory store (injection channel).

Full rationale and trade-off tables: the doc linked at the top.
