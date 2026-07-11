# CLAUDE.md

Guidance for AI coding agents (Claude Code, Codex CLI) working in this repository.

## What this repo is

`my-superpowers` is a **content repository**, not an application. It is a personal
collection of reusable **skills** and **agent definitions** for AI coding agents.
There is nothing to compile or run as a product — the "artifacts" are Markdown
files (`SKILL.md`, agent `.md`) plus a few shell hooks and Python tooling.

Skills follow the open [AgentSkills](https://agentskills.io/specification) standard.
Agents are flat `.md` files with YAML frontmatter (Claude Code's agent format).

`install.sh` symlinks everything into `~/.claude/` (and `~/.agents/` for Codex CLI)
so the skills/agents are usable from any project on the machine.

## Repository layout

```
.claude/
  agents/          Flat agent definitions, one *.md each  (→ ~/.claude/agents/)
  skills/          .NET / QA / Product-Owner / Apple skills (→ ~/.claude/skills/)
skills/            Cross-platform skills, grouped by category (→ ~/.claude/skills/)
  planning/        brainstorming, writing-plans, spec-writer, adr, spike, …
  execution/       loop, tdd-loop, executing-plans, subagent-driven-development, …
  quality/         scrutinize, ponytail, verify-before-stop, circuit-breaker, …
  debugging/       diagnose, post-mortem
  git/             using-git-worktrees, finishing-a-development-branch
  communication/   session-summary, handoff, management-talk, business-impact
  tools/           research, teach, find-skills, writing-skills, writing-great-skills, …
docs/              Research reports, session logs, design specs (reference material)
  research/<topic>/   Cited research output (claude-code, dotnet, ios, mcp, …)
  superpowers/        Plans and specs for this repo itself
  specs/  spikes/  examples/   Design specs, spike outputs, worked examples
teach/             The `teach` skill's format templates (MISSION/GLOSSARY/…)
tools/
  agent-evals/     Repo tooling to measure & improve agent definitions (NOT installed)
install.sh         Symlinks agents + skills into place
ATTRIBUTION.md     Provenance for every skill (adapted vs. original)
```

Both skill roots (`.claude/skills/` and `skills/`) are discovered the same way —
by finding `SKILL.md` — so the flat and category-nested layouts both install. The
category folders under `skills/` are organizational only; they are flattened at
install time.

## File format conventions

### Skills (`SKILL.md`)

Every skill is a directory containing a `SKILL.md` with YAML frontmatter:

```yaml
---
name: brainstorming            # REQUIRED — must exactly match the directory name
description: "…when to use…"    # REQUIRED — this is the routing trigger; say WHEN to use it
model: opus                    # optional
disable-model-invocation: true # optional — user-invoked only (e.g. teach)
allowed-tools: Read, Grep      # optional
argument-hint: "…"             # optional
---
```

- **`name` must equal the directory basename.** Install links by basename, so a
  mismatch (or a duplicate name across roots) silently clobbers another skill.
- **`description` is the trigger**, not a summary. Write it so an agent knows
  *when* to reach for the skill ("Use when…", "…before writing any code").
- Keep the body lean — push long detail into bundled `references/`, `scripts/`,
  or `assets/` subfolders rather than inflating `SKILL.md` (progressive disclosure).
- Any file a skill references (`references|reference|scripts|assets`) must exist.

### Hook-based skills

Some quality/execution skills ship an automated hook plus a settings snippet:

- `hooks/*.sh` — the hook script (e.g. `secrets-guardrail/hooks/redact.sh`)
- `settings-snippet.json` — the block the user pastes into `~/.claude/settings.json`
  to wire the hook (PostToolUse, Stop, PreToolUse, …)

Examples: `secrets-guardrail`, `verify-before-stop`, `circuit-breaker`,
`spec-writer` (PreToolUse gate), `loop` (Stop-hook checker). When editing these,
keep the hook script and its `settings-snippet.json` in sync.

### Agents (`.claude/agents/*.md`)

One flat Markdown file per agent. Frontmatter then the system prompt as body:

```yaml
---
name: principal-dotnet-engineer   # REQUIRED — must match the filename (sans .md)
description: >                     # REQUIRED — triggering context / when to route here
  …use this agent when…
tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
model: opus
skills: all
---
You are a principal .NET software engineer…   # system prompt
```

Same rules: `name` matches the filename, `description` describes *when to route*.

## Validating changes (the closest thing to a test suite)

There is no build. Before committing skill/agent edits, run the static **doctor**
(fast, deterministic, stdlib-only Python 3.9, CI-ready — exits nonzero on errors):

```bash
python3 tools/agent-evals/scripts/doctor.py --repo .
# add --warnings-as-errors to also fail on warnings
```

It verifies, across every agent and skill:
- frontmatter present with `name` + `description` **[ERROR]**
- `name` matches its location (filename / dir basename) **[ERROR]**
- bundled references actually exist somewhere in the repo **[ERROR]**
- no duplicate names (install links by basename → silent clobber) **[ERROR]**
- no references to non-existent subagents **[WARN]**
- description is substantive and states usage context **[WARN]**
- body within the progressive-disclosure budget **[WARN]**
- not over-reliant on rigid ALL-CAPS NEVER/ALWAYS/MUST **[WARN]**
- high description overlap between definitions (routing-conflict risk) **[WARN]**

Run this after any change to a skill or agent. Treat ERROR findings as blocking.

### Improving agent definitions

`tools/agent-evals/` is an A/B evaluation engine (agent **with** vs **without** its
definition on realistic tasks) plus improvement loops. It is repo tooling, **not
installed** by `install.sh`. Use it when tuning an agent's body or description; see
`tools/agent-evals/README.md` and `docs/improving-agents.md`. Not every agent gets
the quantitative engine — only those with objectively verifiable output (code
compiles / tests pass). Subjective-prose agents (`po-agent`) use qualitative review
plus description/triggering evals only.

## Development workflow

1. **Add or edit** a skill (`skills/<category>/<name>/SKILL.md` or
   `.claude/skills/<name>/SKILL.md`) or an agent (`.claude/agents/<name>.md`).
   Match the existing structure and frontmatter conventions exactly.
2. **Run the doctor** (`doctor.py --repo .`) and fix ERRORs.
3. **Update `README.md`** — every skill/agent is listed in a table there. Keep the
   table in sync when adding, removing, or renaming.
4. **Record provenance in `ATTRIBUTION.md`** — state whether the skill is original
   to this repo or adapted from an upstream source (with the source + license).
   The README "Credits" section must agree with `ATTRIBUTION.md`.
5. **Install locally** to try it: `./install.sh` (skips existing) or
   `./install.sh --force` (relinks everything). Restart the AI tool to pick it up.
6. **Commit and push** to the designated feature branch.

## Conventions & guardrails

- **Keep three files in agreement** when the skill/agent set changes: the file
  itself, the `README.md` table, and `ATTRIBUTION.md`. Drift between them is a bug.
- **Never introduce a duplicate `name`** across `.claude/skills/` and `skills/` —
  install collides on basename. The doctor catches this.
- **Descriptions are routing triggers.** When two skills' descriptions overlap
  heavily, agents route ambiguously; the doctor flags overlap as a WARN — resolve it.
- **Prose over rigid directives.** Prefer explaining *why* to stacking ALL-CAPS
  NEVER/ALWAYS/MUST. The doctor warns on over-reliance.
- **`docs/` is reference material**, not installed. Research output lands in
  `docs/research/<topic>/`; specs and plans for this repo live in `docs/superpowers/`.
- **`.gitignore`** excludes `*-workspace/` (agent-evals scratch), local runtime dirs
  (`.gemini/`, `kiro/Global/`), and the usual editor/OS/build noise. Benchmark run
  workspaces are scratch — reviewed, not committed.
- This repo has **no package manager, no lockfile, no CI build**. The only
  executable code is shell hooks (`skills/**/hooks/*.sh`) and the Python tooling in
  `tools/agent-evals/scripts/` (Python 3.9, stdlib only — keep it dependency-free).
