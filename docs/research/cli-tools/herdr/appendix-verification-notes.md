# Appendix: Verification Notes

The first NotebookLM draft of this guide contained several errors that were caught and fixed across two Codex review rounds before this final version. This appendix exists so future edits to this guide can see exactly what kind of mistake a NotebookLM-synthesized doc tends to make, and how each was caught.

## Round 1 findings (6 issues)

| # | Issue | What was wrong | Fix |
| :-- | :-- | :-- | :-- |
| 1 | Install commands | `brew install herdrdev/herdr/herdr` (wrong tap syntax); Windows one-liner was a stale long-form PowerShell/WebClient command | Replaced with `brew install herdr`, `mise use -g herdr`, and the current official `irm ... | iex` one-liner |
| 2 | `ui.sidebar_side` config key | Invented — does not exist in the real default config | Replaced with a pointer to `herdr --default-config` as the version-accurate source of truth |
| 3 | Three-mode keyboard model | Fabricated "Terminal / Prefix / Navigate Mode" framing; ctrl+alt shortcuts presented as defaults when they're an optional binding example | Replaced with the real two-mode model (Prefix Mode + Copy Mode) and correctly labeled ctrl+alt shortcuts as non-default |
| 4 | Agent support matrix | Hardcoded table asserting specific agents (Pi, Kimi, OpenCode, Kilo) always use lifecycle hooks; missing the `agy` agent kind; listed a non-existent "Antigravity CLI" kind | Replaced with hedged guidance pointing at the live `herdr.dev/docs/agents/` page, explaining that hook-vs-manifest depends on whether the integration is installed |
| 5 | "As of v0.7.5" version claim | Unsupported by current docs — likely hallucinated | Removed |
| 6 | "Known issues" (volatile PIDs, global done-state consumption) | Unverifiable against current CLI help or docs | Removed; replaced with issues that are real and correctly scoped (destructive `worktree remove`, mixed config-apply semantics) plus a pointer to check GitHub issues for current bug state rather than trusting a static list |

## Round 2 findings (2 residual issues, after the round-1 fix pass)

| # | Issue | What was wrong | Fix |
| :-- | :-- | :-- | :-- |
| 7 | Windows installer (again) | The round-1 fix replaced one stale command with another stale command | Corrected to the actual current official command |
| 8 | Alternate-screen history note — **an over-correction** | The round-1 fix, in the process of removing unverifiable claims, incorrectly marked the alternate-screen mouse-scroll history retrieval as "not documented or verifiable." This behavior is in fact real and documented in `herdr.dev/docs/agent-automation/` | Rewrote the note to accurately describe the documented behavior and its preconditions, with a link to the source docs |

## Round 3: final pass

Confirmed clean — no remaining material issues. Verdict: **Pass — safe to hand to a new Herdr user.**

## Takeaway for future NotebookLM-drafted guides

The two most common failure modes were: (1) confidently stating **version-pinned specifics** (exact config keys, exact version numbers, exact agent-to-detection-method mappings) that are true at the time the source material was scraped but drift as the tool evolves — the fix in every case was to replace the static claim with a pointer to a live, self-updating source (`--default-config`, `--help`, the docs site) rather than a hardcoded fact; and (2) an **over-correction during the fix pass** — chapter 3's alternate-screen note went from "stated as fact" to "wrongly marked unconfirmed," which needed its own follow-up verification round to catch. A single review pass is not enough; treat AI-generated fixes to AI-generated content as needing the same scrutiny as the original draft.

---

Previous: [Chapter 7 — Keyboard Shortcuts](chapter07-keyboard-shortcuts.md) · Back to [README](README.md)
