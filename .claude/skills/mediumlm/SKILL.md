---
name: mediumlm
description: Research a topic on Medium using the user's own logged-in Medium session (cookies extracted from Chrome). Searches Medium, fetches full article text including member-only content, and produces a chat summary, a saved research note, and optionally NotebookLM artifacts. Activates on explicit /mediumlm <topic> or intent like "research X on Medium" / "what does Medium say about X".
---

# mediumlm

Drives the `mediumlm` CLI (installed from
`/Users/pisitkoolplukpol/Work/mediumlm`, editable install via
`pip3 install -e ".[dev]"`) to research a Medium topic using the
user's own session — see that project's
`docs/superpowers/specs/2026-07-14-mediumlm-design.md` for the full
design and rationale.

## Prerequisites

1. `mediumlm --help` must run without error (confirms the package is
   installed). If not: `cd /Users/pisitkoolplukpol/Work/mediumlm && pip3 install -e ".[dev]"`.
2. `python3 -m playwright install chromium` must have been run once on
   this machine.
3. Chrome must be open and logged into Medium the first time cookies
   are extracted (or whenever they go stale).

If the system `pip3`/`pytest`/`mediumlm` aren't on PATH, prepend
`/Users/pisitkoolplukpol/Library/Python/3.9/bin` to PATH before running
any `mediumlm` command.

## Workflow for `/mediumlm <topic>`

1. **Check the session.** Run `mediumlm cookies check`.
   - Exit code `0` + `"authenticated": true` — proceed.
   - Any other outcome — stop and tell the user to open Chrome,
     confirm they're logged into medium.com, then run
     `mediumlm cookies extract`. Do not proceed with a stale session —
     never silently continue as if it worked.
   - Note on exit codes: `cookies check` returns `1` for two different
     situations — a genuine "not authenticated" (valid JSON on stdout,
     `"authenticated": false`) and an operational error (empty stdout,
     an `error: ...` line on stderr — e.g. missing cookie file, network
     failure, browser crash). Read stdout/stderr, don't rely on the
     exit code alone to tell the user what to fix.

2. **Search.** Run `mediumlm search "<topic>" --limit 8`. This returns
   a JSON array of `{title, url}`. If it returns an empty array,
   report that plainly to the user — do not fabricate results.
   `search` can also fail outright (non-zero exit, `error: <message>`
   on stderr, empty stdout) when Medium's search page itself didn't
   load (e.g. rate-limited) — this is distinct from a genuine empty
   array and must be treated as a hard failure to report, not retried
   silently.

3. **Fetch.** For each relevant result (or all of them, for a narrow
   topic), run `mediumlm fetch <url>`. Each call returns JSON:
   `{url, title, access, access_reason, markdown}`.
   - `access: "full"` — use the markdown as the article's real content.
   - `access: "preview"` — the article was NOT fully read. Label it
     clearly in every output as "preview only" and state the
     `access_reason` (`blocked`, `cookies_expired`, or `not_member`).
     Never blend preview-only content into a summary as if it were
     the full article.
   - Any command that fails prints `error: <message>` on stderr with
     empty stdout and exit code `1` — treat this as a hard stop for
     that command (don't retry in a loop; report the error).

4. **Produce all three outputs:**
   - **Chat answer** — synthesize a summary/answer to the user's
     question directly from the fetched (full-access) article text.
   - **Saved research note** — write to
     `docs/research/medium/<topic-slug>-<YYYY-MM-DD>.md`. If the
     current project already has a `docs/` convention, put it there;
     otherwise default to `~/Work/docs/research/medium/`. Include: the
     list of sources with URLs and their `access` status, key
     excerpts, and the synthesized summary.
   - **NotebookLM artifacts — only if the user explicitly asks** for a
     podcast/audio overview, mind map, or study guide. In that case,
     invoke the existing `notebooklm` skill: create a notebook, add
     each fetched article (by URL, or by pasting the fetched markdown
     as a text source if the URL alone won't render for NotebookLM),
     then generate the requested artifact type.

## Error handling — do not paper over these

- `cookies check` fails → stop, tell the user to re-extract. Do not
  proceed.
- `search` returns zero results → say so; do not invent articles.
- Any `fetch` result with `access != "full"` → label it explicitly in
  every output that uses it, with its `access_reason`.
- Repeated fetch/search failures in one run → stop and report the
  failure; do not retry in a loop (Medium's bot detection is exactly
  what a retry loop would trip further).

## Scope

This is for the user's own personal research against their own Medium
account, at normal single-topic, on-demand volume — not bulk scraping.
See the design spec's Error Handling section for the account-risk
rationale.
