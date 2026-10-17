# research.md — P1 factory upgrades

## แหล่ง: notebook research (4 notebooks: AI-Native SDLC, Shopify AI Workflow, PR Bottleneck, Agent Harnesses) + explore survey

## 5 upgrades + ข้อเท็จจริงจาก codebase

### 1. Env scaffolding (ก่อน IMPLEMENT)
- ทำ: install deps + baseline sanity tests + env check → artifact/log เป็น baseline ของ TEST stage
- Landing: orchestrator stage ใหม่ระหว่าง PLAN–IMPLEMENT หรือ engineer pre-task
- ข้อจำกัดจริง: QE รัน shell ไม่ได้ (non-iOS suite = orchestrator รันเอง) · devops-engineer **ไม่อยู่ใน allowlist** (ใช้ต้องเพิ่ม)
- ต้องตัดสินใจ: 1-way door ข้าม/ย่อ scaffolding? fallback lane รัน scaffolding ไหม?

### 2. Blind reviewer isolation
- ทำ: reviewer ได้เฉพาะ spec/plan artifacts + หน้างาน — **ห้าม forward engineer's per-file report/ผลรายงานของกันเอง**
- web-ui-reviewer blind อยู่แล้วโดยดีไซน์ = template ของ pattern
- ระวัง: ไม่ทับ MODE A/B semantics ของ architect-reviewer · orchestrator เป็นคนคุมสิ่งที่ paste ให้ reviewer

### 3. Deterministic fallback (งานเล็ก lane)
- ทำ: routine/reversible fix → single engineer run + verification (ไม่มี stages) — เป็น lane ที่ 3 ของ risk-door triage
- **ชนกับกฎเดิม**: "REVIEW and TEST always run" ใน Hard rules ต้อง rewrite เป็นเงื่อนไข
- ต้องยังเขียน log.md + DONE marker (ไม่งั้น /wf-status//wf-list มองไม่เห็น) · Work Board ใช้ owner path ย่อ · branch rule ยังผูกหรือยกเว้น — ตัดสินใจใน design
- ห้ามชี้ fallback ไป `general` (default permissions + ทุก MCP — known gap)

### 4. Mermaid diff summary (WRAP-UP)
- ทำ: docs stage ผลิต diff diagram ประกอบ summary — **orchestrator ห้ามผลิตเอง** (no-artifacts rule) → ผ่าน `docs` subagent
- convention (quote labels, &#60; escapes, ไม่มี / เปล่า) ไหลถึง docs ผ่าน forced-read learnings อยู่แล้ว แต่ต้องมีใน **cross-run** learnings ด้วย

### 5. Commit-on-stop backstop
- ทำ: incremental commit ต่อ stage/round + progress ใน log.md (commit hash เป็น evidence) + ครอบ case PARKED
- **CONFLICT ใหญ่**: repo AGENTS.md = "agents never commit; the orchestrator verifies on disk and commits" vs engineer.md "If asked to commit" — ต้องเลือกฝั่ง (แนวโน้ม: orchestrator เป็น committer ตาม AGENTS.md + แก้ engineer wording)
- loop caps (3 review/3 debug) = commit ต่อ round เป็น rollback point ฟรี

## กระทบข้ามไฟล์ (จาก explore)
- เพิ่ม/ลด allowlist ใด ๆ → doc §5–6 assertions (20-list, 4-list, 16-allows) เป็น false ต้องแก้ doc พร้อมกัน + เขียน §11
- engineer.md ทุก edit → mirror ไป repo agents/engineer.md
- SKIP comment ใน sync script เก่า (ยังพูดถึง engineer) — เก็บกวาดพร้อมกัน
- ~/Work/docs/workflow/ มี 10 legacy ACTIVE runs — /wf-list ใน ~/Work จะรายงานผิด; sweep เป็น follow-up แยก
