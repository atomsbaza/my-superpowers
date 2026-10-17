---
description: รายการ workflow runs ทั้งหมด (ACTIVE / DONE / PARKED)
agent: orchestrator
---
List every folder under `docs/workflow/`. For each run read its `log.md` and
report: slug, status (ACTIVE = no `DONE:`/`PARKED:` line; DONE; PARKED — with
its reason), the last completed stage, the last activity date, and its branch
or worktree if it ran isolated. End with: which run is ACTIVE, which PARKED
runs are resumable, and anything stale (no activity for 7+ days).
