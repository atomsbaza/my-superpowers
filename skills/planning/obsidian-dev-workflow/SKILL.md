---
name: obsidian-dev-workflow
description: Use when working in any project under ~/Work - read the project brief in the Obsidian vault first, then log the session to Terminal Log and record non-obvious decisions in the project's Decisions.md.
---

# Obsidian Dev Workflow

The Obsidian vault is the shared notebook between the user and whatever agent is working. This skill is the contract for reading it before work and writing to it after. It does not say which agent plans, writes or reviews code; the harness or the user decides that.

## Paths

- Vault: `~/Documents/Obsidian Vault` (the folder name has a space: quote it, never shell-expand it unquoted).
- Project brief: `<vault>/Projects/<ProjectName>.md`
- Project decisions: `<vault>/Projects/<ProjectName>/Decisions.md`
- Multi-session plans: `<vault>/Projects/<ProjectName>/Plans/YYYY-MM-DD-<slug>.md`
- Daily session log: `<vault>/Terminal Log/YYYY-MM-DD.md`
- `~/Work/AGENTS.md` points here; each repo's `AGENTS.md` points at its own brief.

## The loop (every non-trivial task)

1. **Context.** Read the project brief and `Decisions.md` before starting. Do not ask the user anything the brief already answers.
2. **Plan.** Short task: plan in chat. Multi-session task: write the plan to the project's `Plans/` folder so the user can audit it.
3. **Do the work.**
4. **Verify** with real command or test output, never intent.
5. **Record**, after completion, all that apply:
   - Append a session note to today's `Terminal Log` file.
   - Any decision a code reader could not infer goes to `Decisions.md`, newest first.
   - A procedure that took more than one attempt to get right becomes a skill or a note, so the next session starts knowing it.

## Formats

Session log. The file may already contain lines written by hooks or by the user. Append below them; never rewrite or reorder existing lines. A time line looks like:

```
- HH:MM–HH:MM (duration) · <session id> · <agent> · done|blocked
```

`blocked` needs a one-phrase reason. Free-form notes may follow the time line.

Decisions:

```markdown
- YYYY-MM-DD — <decision> — <why in one clause>
```

## Rules

- Use file read and write tools for vault paths rather than shell expansion.
- Do not restructure the vault, its maps of content or existing notes without asking.
- Reusable cross-project knowledge belongs in skills, not duplicated in vault notes; vault notes may cross-link with `[[wikilinks]]`.
- The vault is what the user reads and audits. A fact that must survive and be user-visible goes there; an agent's private memory is only fast context.
- Where multi-step work is tracked: decision context in the vault plan, operational state in whatever task tracker the project uses, working files in the repo tree. Partial output from an interrupted run goes to a named stash or is deleted, never left as silent untracked state.
