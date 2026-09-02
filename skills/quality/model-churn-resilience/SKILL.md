---
name: model-churn-resilience
description: "Use when configuring model IDs, quotas, or limits in persistent agent configs, upgrading a model version, or auditing a stack after a provider removes/renames models or changes rate limits — prevents silent breakage from model churn."
---

# Model Churn Resilience

Providers remove and rename models without warning, and silently change
tool-use and caching behavior on upgrade. Workflows with hardcoded model IDs
fail **silently** — nothing errors, the workflow just gets worse or stops.

## Why it matters

- GitHub Copilot removed 6 models overnight (Opus/Sonnet 4.5/4.6, Gemini 3.1
  Pro) — workflows referencing them by ID broke without errors.
- Anthropic net-cut Claude Code weekly limits ~17% (promo 150% → permanent
  125%, with comparison-date arbitrage in the announcement). Budget drift is
  the same failure class as model removal.
- Model upgrades can silently change tool-use behavior (e.g. forced tool use
  in newer model versions), invalidate prompt caches, or make older models
  unable to read newer models' reasoning blocks.

## Rules

1. **Never hardcode model IDs in persistent configs.** Reference models
   through named constants or alias indirection that lives in one place.
   Constants with meaningful ceilings (quota watchdogs using CEILINGS
   constants, not model names) survive churn; string literals don't.
2. **Pin, then diff behavior.** When upgrading a model, pin the exact version
   and diff behavior on the tasks you care about (tool-use format, caching
   hits, reasoning-block compatibility) — don't assume continuity.
3. **Track budget/promo deltas with dates.** Promo vs permanent limits must
   be recorded with the comparison date; vendor "before/after" framing often
   cherry-picks the baseline. The arithmetic works both ways.
4. **Fail loudly at startup.** A persistent workflow should validate its model
   reference against the provider's current model list and refuse to run on a
   missing/renamed ID rather than degrade silently.
5. **Set budget alerts on consumption, not on plan announcements.** Limit
   changes arrive as marketing, not changelog entries.

## References

- X-scout knowledge digest 2026-09-02 (items 19; sources: byteiota.com,
  explainx.ai, claudefa.st, 2026-09-01/02) — curated in
  `docs/research/agentic-ai/2026-09-02-model-churn-and-agent-sandboxes.md`.
