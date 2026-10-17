---
description: เริ่ม full workflow (research → design → plan → implement → review → test) ด้วย orchestrator
agent: orchestrator
---
Run the full workflow for this task:

$ARGUMENTS

Before starting, check `docs/workflow/`:

1. A folder whose `log.md` exists but has no `DONE:`/`PARKED:` line is an
   ACTIVE run. If one exists, ask the user whether to (a) resume it,
   (b) queue this new task until it finishes, (c) start this task in a
   separate git worktree, or (d) park the active run and start fresh.
2. If `docs/workflow/<slug>/` for this task's slug already exists, ask
   whether to resume it (continue from the last completed stage in log.md)
   or use `<slug>-2` — never overwrite an existing run.
