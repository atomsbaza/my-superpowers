---
name: writing-release-notes
description: >
  Writes customer-facing release notes from sprint deliverables, commit history,
  or a list of completed stories. Produces a structured release announcement
  with new features, improvements, and bug fixes — written in plain language
  from the user's perspective, not engineering jargon. Language- and
  technology-agnostic. Use after a sprint, release, or any product update.
  Trigger keywords: release notes, changelog, what's new, customer announcement,
  release announcement, sprint release, version notes, product update, shipped.
---

## Purpose

Communicate what changed in a release in language customers understand — focused on what they can now do, not what engineers built.

## Input

Accept any of:
- List of completed stories (paste or file path)
- Sprint plan file (read to find committed stories)
- `git log` output or commit messages (read if provided)
- Direct user description of what shipped

Read `.po-workflow-state.json` for product name and version context.

If nothing is provided, ask: "What shipped in this release? Share a story list, sprint plan path, or describe the changes."

## Writing Principles

1. **User perspective, not engineering perspective.** "You can now export reports to PDF" not "Implemented PDF rendering pipeline."
2. **Plain language.** No acronyms, internal code names, or technical jargon unless the audience is developers.
3. **Lead with value.** What can the user do now that they couldn't before?
4. **Honest about fixes.** Bug fixes earn trust. Be specific about what was broken and is now fixed.
5. **No rubber-stamps.** "Various improvements and bug fixes" is not release notes. List them.

## Audience Variants

| Audience | Tone | Level of Detail |
|---|---|---|
| End users / customers | Friendly, benefit-focused | High-level, no implementation details |
| Developers / technical users | Precise, factual | Include API changes, deprecations, migration steps |
| Internal / stakeholders | Factual, linked to goals | Business metrics impact if known |

Default to end-user tone unless the user specifies otherwise.

## Process

### Step 1 — Categorize Changes

Sort each completed item into:
- **New Features:** Capabilities that didn't exist before
- **Improvements:** Existing features that now work better (performance, UX, reliability)
- **Bug Fixes:** Problems that were reported and are now resolved
- **Deprecations / Breaking Changes:** Things that changed in a way that requires user action (developer-facing releases only)
- **Security Fixes:** Vulnerabilities addressed (be careful — do not include exploit details in public release notes)

### Step 2 — Write Each Entry

Format per entry:
- **Feature:** "[Action verb] [what] — [why it matters to the user]"
  - Example: "Export reports to PDF — download any report for offline viewing or sharing."
- **Improvement:** "Improved [what] — [what changed and why it's better]"
  - Example: "Improved dashboard load time — dashboards now load 40% faster on mobile."
- **Bug Fix:** "Fixed [what] — [what the user experienced before vs. now]"
  - Example: "Fixed: search results were sometimes empty when filtering by date range."

### Step 3 — Write the Release Notes Document

```markdown
# Release Notes — [Product Name] v[N.N.N]

> **Release Date:** [YYYY-MM-DD]
> **Version:** [Semantic version or sprint/release identifier]
> **Audience:** [Customers / Developers / Internal]

---

## What's New

> New capabilities you can use starting today.

### [Feature Group Name — optional grouping for large releases]

- **[Feature title].** [1–2 sentence description from user's perspective. What can they do now? Why is it useful?]

- **[Feature title].** [Description]

---

## Improvements

> Things that worked before but now work better.

- **[Area / Feature].** [What changed and the user benefit. Quantify if possible: "40% faster", "50% fewer clicks".]

---

## Bug Fixes

> Problems that were reported and are now resolved.

- **[Area / Feature].** [What the user experienced before. What they will experience now.]

---

## Breaking Changes / Migration Required

> Action required — these changes may affect how you use [Product Name].

- **[Change description].** [What the user must do before upgrading. Link to migration guide if available.]

---

## Security Fixes

> Security improvements in this release.

- [Description at appropriate level — no exploit details in public notes]

---

## Known Issues

> Issues we are aware of and are working on.

- [Issue description and workaround if available]

---

## Upgrade Notes

[Instructions for how to get the new version, if applicable.]

---

## Thank You

[Optional: acknowledge user feedback or contributors if appropriate.]
```

### Step 4 — Write Output File

Version the file from the release identifier.

Save to `docs/releases/release-notes-<version>-<date>.md`. Create directory if needed.

Update `.po-workflow-state.json`:
```json
{
  "last_artifact": "docs/releases/release-notes-<version>.md",
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Quality Rules

1. **Every change has an entry.** "Various improvements" is not acceptable. If an improvement happened, name it.
2. **Bug fix entries state both the old and new behavior.** "Fixed search" is not enough — explain what was broken.
3. **Breaking changes get their own section.** Never bury a breaking change in "Improvements."
4. **Security fix language is calibrated to audience.** Public notes: "Fixed a security issue in [area]." Internal notes: full detail.
5. **Known issues are honest.** Hiding known issues destroys trust. List them with workarounds.
