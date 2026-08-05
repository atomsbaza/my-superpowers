---
name: research-verify
description: Research a tool/API/system, then verify the draft against a live ground truth (installed CLI, live docs, running system) before publishing. Use when research output will be relied on operationally (a how-to-use guide, an API reference, an onboarding doc) rather than just informational — anywhere a stale or hallucinated claim would actually break someone's workflow. Trigger on "/research-verify <topic>" or intent like "research X and verify it" / "make sure the guide is accurate before saving it".
---

# research-verify

Research is not enough when the output will be *acted on* — a synthesized draft (especially from a tool like NotebookLM that has no way to run the real system) routinely contains stale version-pinned specifics and outright invented details that read as confident and plausible. This skill adds a mandatory fact-check-against-reality pass before anything gets published, and only then splits and files the result.

Use this instead of the plain `research` skill whenever the deliverable is something someone will follow step-by-step (install commands, CLI flags, config keys, a support matrix) rather than just read for background.

## Workflow

### 1. Research

Produce a draft using whichever source fits the topic:
- Web/API research on a tool or system → the `notebooklm` skill (deep mode for broad topics, fast mode for narrow ones), or the `research` skill / a `research` subagent for web-only sourcing.
- Save the raw synthesized draft to a scratch location first — do not publish yet. If using `notebooklm generate report`, download it; if using `ask`, save as a note and extract the answer text.

State the draft's provenance up front (source count, collection method, date) — this becomes the published doc's provenance line later.

### 2. Identify ground truth to verify against

Before verifying, name the actual source(s) of truth for this topic — not "the internet" but something checkable:
- An installed CLI's own `--help` / `--version` / `--default-config` output
- The tool's live docs site (fetch it fresh, don't rely on the research draft's cached copy)
- A running service's actual API response
- The project's GitHub issues/discussions for "is this bug still real" claims

If no checkable ground truth exists for a claim (e.g. a third-party blog's opinion), that claim should be flagged as unverifiable in the final doc rather than silently trusted or silently dropped.

### 3. Verify with a live-access agent

Hand the draft to an agent that can actually reach the ground truth from step 2, not just read the draft:

- **If `HERDR_ENV=1`:** use the `herdr-workflow` skill's "Verify a document against live system state" recipe — split a pane in the *current* Herdr workspace (do not create a new one unless the topic concerns a different project/cwd), start a capable agent (Codex or Claude, whichever has the best tool access for this ground truth — e.g. Codex for a locally-installed CLI it can run `--help` against), and prompt it with the file path plus explicit verification instructions: what to cross-check, what to report (checks-out list, wrong/invented list, gaps, pass/fail verdict).
- **If Herdr is not available:** use the `Agent` tool with `subagent_type: "general-purpose"` (or `code-reviewer` if the ground truth is a codebase) and the same prompt shape — the agent still needs Bash/WebFetch/WebSearch access to reach the real system, not just the draft file.

Do not skip this step because the draft "looks right." Confident, well-formatted prose is exactly what a synthesis tool produces whether or not the specifics are true.

### 4. Fix and re-verify

Apply the agent's confirmed findings yourself directly (Edit tool) — do not have the verifying agent edit the file, since it doesn't have the surrounding context of what else changed.

Re-run step 3 against the **same** agent/pane (reuse, don't restart — it already has the review context and will catch regressions introduced by your own fix, including over-corrections). Cap this at 3 rounds; if still failing after 3, surface the unresolved disagreement to the user rather than looping indefinitely or shipping a doc you know is wrong.

Stop when the agent gives an explicit pass/clean verdict.

### 5. Decide single-file vs. chaptered

- **Single file** if the guide covers one coherent topic and stays under roughly 150 lines / 4-5 sections. Follow the flat convention already used in `docs/research/<topic>/YYYY-MM-DD-<slug>.md`.
- **Chaptered** if the guide has 5+ natural top-level sections or would exceed ~150 lines. Create `docs/research/<topic>/<subtopic>/` with:
  - `README.md` — provenance, executive summary, table of contents linking every chapter, a short "how to use this" note
  - `chapterNN-<slug>.md` per section, each ending with a Previous/Next link line
  - `appendix-verification-notes.md` — a table of every issue step 3/4 found and fixed, plus a one-paragraph takeaway on what kind of mistake this source tends to make (this is the single highest-value artifact for future edits to the doc — don't skip it)

Match the exact heading/link style of an existing chaptered set (e.g. `docs/research/knowledge-bases/`) rather than inventing a new format.

### 6. Publish

1. Write the file(s) under `docs/research/<topic>/` in the `my-superpowers` repo (create the topic folder if it doesn't exist).
2. Add an entry to `docs/research/README.md`'s categorized index — a new numbered category if none fits, otherwise append to the closest existing one.
3. Mirror a **summary-with-pointer** note into the Obsidian vault at `~/Documents/Obsidian Vault/Projects/my-superpowers/<Title>.md` — `type: reference`, `parent: "[[Projects/my-superpowers]]"` frontmatter, a condensed quick-reference (not the full content — the repo file is the source of truth), and a `## Related` section linking back to `[[Projects/my-superpowers/Docs & Research]]` and `[[Projects/my-superpowers]]`. Match the frontmatter/section style of existing notes in that folder (e.g. `Skills Catalog.md`) rather than inventing a new one.
4. Update `Projects/my-superpowers/Docs & Research.md` in the vault: bump the report/folder counts and add a line for the new topic with a wikilink to the note from step 3.
5. If the work is significant enough to be a project-level milestone (not just an addenda to Docs & Research), delegate the `Projects/my-superpowers.md` top-level update to the `wiki-updater` agent instead of editing it inline.

### 7. Report back

Tell the user: what got fixed during verification (short list, not the full appendix), where the files landed (repo path + vault path), and whether anything remains flagged as unverifiable rather than silently dropped.

## Anti-patterns

- **Skipping verification because the source "looked deep"** (many sources, long report) — source count says nothing about whether individual specifics are current or invented.
- **Having the verifying agent also apply its own fixes** — it doesn't have full context on the rest of the document; direct edits belong to the orchestrating agent.
- **One verification round and done** — the fix pass itself can introduce new errors (over-corrections), especially when a fix broadly rewords a section instead of changing only the specific wrong claim. Always re-verify after fixing.
- **Publishing a single giant file "because splitting is extra work"** — a 150+ line undifferentiated doc is worse for both human skimming and agent context budget than the same content in linked chapters.
