---
description: ดูความคืบหน้า workflow run (ระบุ slug ได้ ไม่งั้นใช้ run ล่าสุด)
agent: orchestrator
---
Read `docs/workflow/$ARGUMENTS/log.md` (or, when no slug is given, the most
recently modified run in `docs/workflow/`) and report the pipeline status:
current stage, completed stages with their evidence paths, open review/test
findings, retries used vs the caps, and the recommended next action. If
multiple runs exist, list them first and say which one is ACTIVE
(no `DONE:`/`PARKED:` line in log.md).
