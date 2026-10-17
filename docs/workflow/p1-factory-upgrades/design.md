# design.md — P1 factory upgrades (DESIGN stage, round 2 — 2026-10-17)

**แนวคิดรวมใหญ่: ทั้ง 5 upgrades เป็น prompt/config-only อยู่แล้ว ดีไซน์นี้ไม่เพิ่ม agent ใหม่ · allowlist "แทบ" ไม่แตะ — ยกเว้น 1 จุดที่อยู่ใน scope ชัดเจน: ขยาย scoped allow pattern `docs/workflow/*` → `**/docs/workflow/*` (nested-root-safe) สำหรับ 3 artifact agents (FINDING จาก run นี้ — จำนวน allows คงเดิม แก้แค่ pattern text ดู §4a) · sync-script hardening ยังไม่แตะ — แตะแค่ comment เก่า 1 บรรทัด + ค่าคงที่ `WORKFLOW_DIR` 1 บรรทัด** — ผลคือ doc §5–6 assertions: 20-list และ 4-list ยัง true ทั้งหมด; 16-allows **จำนวน**ยัง true แต่ **pattern text** เปลี่ยน → §6 แก้ wording + re-run assertions พิสูจน์ · ต้องแก้ wording เดียวเพิ่มคือ "safe commits" ของ engineer ใน §5 · กลไกทั้งหมดอาศัย 3 กลุ่มไฟล์: `orchestrator.md` (สัญญาหลัก — **มี repo mirror baseline แล้ว: commit 7e57443**) + prompt ของ 4 subagents ที่มีอยู่แล้ว (engineer, web-ui-reviewer, architect-reviewer, docs) + 1 doc และ 2 บรรทัดใน sync script

**FINDING จาก run นี้ (ปิดแล้วใน §4a + §8):** scoped allow `docs/workflow/*` เป็น relative path — run ที่ project root ซ้อนอยู่ใต้ session cwd (เช่น ~/Work/my-superpowers) เขียน artifact ไม่ได้ → scope ของ P1 ขยายครอบงานขยาย pattern เป็น `**/docs/workflow/*` + บันทึก doc §5/§6 ให้ตรง + probe พิสูจน์จาก nested root

## 0. Seams ที่ดีไซน์นี้ห้ามให้เลียน

| Seam | กติกา |
| --- | --- |
| **Information** | per-file report ของ engineer **ไม่ถูก materialize ลงไฟล์ใดเลย** — enforce ความบอดของ reviewer ได้จริงเพราะไม่มีอะไรให้อ่านไปก่อนได้ |
| **Ownership (git)** | single-writer: agent ที่ verify on disk คือ agent ที่ commit = orchestrator เท่านั้น ทุก commit อยู่บน branch ของ run, never push |
| **Trust** | ไม่เปลี่ยนจาก P0 — web content/tool output เป็น untrusted data, memory write ยังห้ามใน subagents |
| **Platform (Claude ↔ OpenCode)** | แก้ agent ที่ `~/.claude/agents/` → diff+copy กลับ repo `agents/` → รัน `sync-from-claude.py` → ยืนยันด้วย `/api/agent` · **orchestrator.md: repo mirror + diff+copy-back (กฎเดียวกับ agent อื่น) — baseline แล้วที่ repo commit 7e57443** · orchestrator.md ไม่แตะ README agents-table / ATTRIBUTION (สองไฟล์นั้นไว้สำหรับ third-party/install skills) — mirror document ใน doc §4 file tree แทน · กฎ three-file ของ repo AGENTS.md ผูกกับ "agent set เปลี่ยน" ซึ่ง run นี้ไม่เกิด — orchestrator.md ไม่ใช่ agent ใหม่ใน set จึงไม่ trigger |

## 1. Env scaffolding (SCAFFOLD)

**Chosen:** SCAFFOLD เป็น orchestrator-executed step ที่นิยามโดย `plan.md` Task 0 — tech-lead (คนเดียวที่มีข้อมูล codebase พอ) กำหนด install command + baseline sanity + test-suite command พร้อม expected result ลงหัว plan.md · orchestrator รันเองก่อน dispatch engineer (การรัน verification ที่ plan ระบุ = อยู่ในสัญญาเดิม ไม่ฝืด no-artifacts rule) · iOS project → dispatch `quality-engineering` รัน suite (runner เดียวกับ TEST เทียบ baseline ได้ apple-to-apple) · evidence = บรรทัด `SCAFFOLD` ลง log.md พร้อม exit codes จริง · ไฟล์ที่แตะ: orchestrator.md เดียว (stage 5 ใหม่ + PLAN requirement, เลขเดิม 5–8 → 6–9)

**Rejected:** devops-engineer stage (allowlist 16→17 + doc assertions เพื่อรัน 2-3 คำสั่ง) · engineer pre-task (ปน role กับ scope-freeze/contract-first) · orchestrator รัน iOS เอง (baseline กับ TEST คนละ runner)

**Reversibility:** two-way — ลบ stage text ก็จบ **นิยามให้ตรง: two-way ครอบเฉพาะตัวข้อความ design ใน orchestrator.md** · สิ่งที่ SCAFFOLD install ลงเครื่องจริง (packages, tools, env vars) ไม่มี uninstall step ในดีไซน์ — **cleanup ของ env เป็นความรับผิดชอบของ user** · **Interactions:** รันเฉพาะ 2-WAY (1-WAY ใช้ failing-test run เป็น baseline, ROUTINE ใช้ verification run) · เสริมความบอดให้ TEST โดยปริยาย · ไม่เพิ่ม ARTIFACT_WRITERS · Work Board: owner `opencode` ช่วง SCAFFOLD

## 2. Blind reviewer isolation

**Chosen:** Dispatch-layer contract ที่ orchestrator จุดเดียว (ไม่ใช่ permission-layer ไม่ใช่กระจาย 7 prompts) — engineer's per-file report **ไม่ถูกเขียนลงไฟล์ใดและห้าม forward** ให้ reviewer ใด · reviewers ไม่เห็น findings ของกันเองระหว่างรอบ · re-review ได้ **prior findings ของตัวเอง verbatim** เท่านั้น

**Input pins:** code-reviewer/swift/security/perf/dependency ได้ plan.md + changed files · architect-reviewer MODE A: design.md เท่านั้น / MODE B: design.md + plan.md + changed files (semantics คงเดิม) · web-ui-reviewer: screenshots + source + direction sheet

**ต้นทุนที่ยอมรับของ blind design (ตัดสินแล้ว):** engineer's "noticed but did not touch" จาก stage IMPLEMENT จะไม่ถึง REVIEW = **accepted loss โดยเจตนา** — ยอมเสีย signal รองนี้เพื่อกัน bias ของ reviewer · ไม่ forward แม้แต่หมวด noticed-untouched เป็น trigger hints, ไม่สร้าง channel ใหม่ (channel ไหนที่ reviewer อ่านได้ = รูโหว่ของบอดทั้งระบบ)

**ไฟล์ที่แตะ:** orchestrator.md (Blind dispatch ย่อหน้าใน stage REVIEW) + web-ui-reviewer.md + architect-reviewer.md (hardening ป้องกันสองชั้น ยึด template "Inputs you receive") — ไม่แตะ 5 reviewers อื่น (กติกาอยู่ที่ orchestrator จุดเดียว กัน drift)

**Rejected:** permission-layer (engine ไม่มี read-deny ละเอียดพอ + ตัด reviewer จาก repo) · rule ลง 7 prompts (drift 7 จุด) · ซ่อน plan/design (เกินขอบ — เป็นสัญญาที่ตรวจด้วย) · forward noticed-untouched เป็น trigger hints (สร้าง channel ใหม่ เสี่ยง leak สถานะ blind)

**Reversibility:** two-way · **Interactions:** ใช้ทุก lane · MODE A บอดอยู่แล้วโดยโครงสร้าง P0 — ตอนนี้ codify · ไม่ขยับ Work Board owner ใน re-review rounds

## 3. Deterministic fallback lane (ROUTINE)

**Chosen:** risk-door triage กลายเป็น **3 lanes** นิยามในจุดเดียว (UNDERSTAND) + Hard rules ถือกฎ conditional — แก้ taxonomy ซ้ำซ้อนเดิม

- **2-WAY** → full pipeline + both gates + full conditional REVIEW + SCAFFOLD
- **1-WAY** → ข้าม architect gates ทั้งคู่; REVIEW = code-reviewer + triggered conditionals; plan ย่อได้; TEST รัน; ไม่มี SCAFFOLD แยก (contract-first pre-change run = baseline evidence)
- **ROUTINE** (mechanical, reversible, ไม่มี new behavior, ไม่ตรง 2-WAY topics) → **branch ใหม่เสมอ (branch-always — แม้ typo แก้จาก chat, Q1)** → **ONE engineer dispatch (never `general` — unhardened)** พร้อม verification command ใน brief · **ไม่ dispatch code-reviewer — orchestrator อ่าน diff เอง (ศูนย์ dispatch, Q2)** · ไม่มี RESEARCH/DESIGN/PLAN/REVIEW/TEST/docs dispatch · จบด้วย commit + log DONE · กฎ: "ต้องใช้ judgment = ไม่ใช่ ROUTINE — promote ขึ้น (ROUTINE → 1-WAY → 2-WAY) never down"
- **ปิดช่อง `general` (Hard rules sentence ใหม่):** "mechanical single-file = ROUTINE เสมอ · `general` ใช้ได้เฉพาะเป็น subtask ภายใน run ที่ active (1-WAY/2-WAY) — ห้ามใช้ `general` เป็น lane แทน ROUTINE หรือรับงานนอก run"

**ไฟล์ที่แตะ:** orchestrator.md เท่านั้น (UNDERSTAND lanes + Hard rules rewrite: separate REVIEW/TEST บังคับเฉพาะ 1-WAY/2-WAY; never-skip ทุก lane = exit code จริง, orchestrator อ่าน diff, log.md + DONE, branch ใหม่, Work Board task, learnings forced-read, stage-boundary commit + ประโยคปิดช่อง `general`)

**Rejected:** ชี้ lane ไป `general` (known gap — ปิดด้วย Hard rules sentence) · ROUTINE อยู่ branch เดิม (ผิด invariant — Q1 ตัดสิน branch-always) · ROUTINE dispatch code-reviewer เสมอ (~2× ต้นทุน — Q2 ตัดสิน orchestrator อ่านเอง) · คง "always run" (latency 2×, lane ไม่ deterministic) · เขียน lane คนเดียวไม่แตะ Hard rules (กฎเก่าชนะ)

**Reversibility:** two-way ตัวกลไก — แต่ misclassify = one-way-ish; ตัวเก็บ 4 ชั้น: exclusion list + promote-up + branch แยก (ทุก lane) + never push + user merge เอง

## 4. Mermaid diff summary (WRAP-UP)

**Chosen:** docs subagent ผลิต `docs/workflow/<slug>/diff-summary.md` เสมอใน 1-WAY/2-WAY (ROUTINE ข้าม); orchestrator quote verbatim เท่านั้น

**ไฟล์ที่แตะ:** orchestrator.md (WRAP-UP) + docs.md (bullet mermaid convention — durable home ที่ผู้ผลิต) · cross-run learnings: retro hook append pointer เองตาม P0

**Rejected:** orchestrator วาดเอง · engineer วาดตอน IMPLEMENT · convention แค่ใน learnings

**Reversibility:** two-way · **Interactions:** docs มี edit อยู่แล้ว · Work Board: owner docs + Done comment แนบ path

## 4a. Allow-pattern expansion (nested-root-safe) — FINDING-driven

**Chosen:** ขยาย scoped allow จาก `docs/workflow/*` → `**/docs/workflow/*` แก้ที่จุดเดียว: ค่าคงที่ `WORKFLOW_DIR` ใน `sync-from-claude.py` → re-run sync → 3 permission rows ของ research/solution-architect/tech-lead อัปเดตตาม · prompt text ของ 3 agents และ repo mirrors ไม่แก้ (pattern อยู่ที่ script จุดเดียว กัน drift) · จำนวน allow entries คงเดิม (16) — แก้แค่ pattern text · **พิสูจน์ด้วย probe:** dispatch 3 artifact agents เขียน scratch file ใต้ `docs/workflow/` จาก session cwd ที่ซ้อนใต้ project root — write สำเร็จแล้วลบทิ้ง ใน smoke step

**Rejected:** absolute path (hard-code เครื่อง/ผู้ใช้) · ย้ายไปให้ orchestrator เขียนเอง (ขัด artifact-owner chain §7) · แก้ pattern กระจาย 3 rows ใน opencode.json (generated file — sync ทับ)

**Reversibility:** two-way — revert ค่าคงที่ + re-sync

## 5. Commit-on-stop backstop

**Chosen:** Orchestrator เป็น committer เดียว — commit หลัง verify on disk **ทุก stage boundary (per-stage, Q3)**, บน branch ของ run, never push · message `wf(<slug>): <STAGE> — <evidence>` · log.md จด hash เป็น rollback point (loop caps → ~10 commits/run) · cap stop / PARKED = commit สถานะสุดท้ายรวมบรรทัดนั้น · ห้าม squash/rebase เอง — **user squash เองตอน merge (Q3 ปิด: per-stage commits, ไม่ orchestrator-squash, ไม่ minimal)**

**ไฟล์ที่แตะ:** orchestrator.md (section ใหม่ก่อน Hard rules) · engineer.md (rewrite "If asked to commit" → never-commit) · mirror + sync SKIP comment

**Rejected:** engineer commit เมื่อถูกสั่ง (ทำลาย invariant + verify/commit คนละคน) · commit ครั้งเดียวตอน DONE (ไม่มี rollback point) · orchestrator squash ตอน DONE (ทับ history) · minimal เฉพาะ PARKED (ระหว่าง run ไม่มี rollback point) · amend ทับ history

**Reversibility:** two-way กติกา; ผลถาวรเล็ก: history ต่อ run ยาวขึ้น (user squash เอง) · **Interactions:** ทุก lane ใช้ (never-skip ของ ROUTINE) · PARKED ครอบ · report ไม่ถูก materialize อยู่ดี

## Conflict resolutions (4 ข้อ)

1. **Commit ownership — orchestrator ชนะ** ตาม repo AGENTS.md invariant → engineer.md rewrite never-commit
2. **"REVIEW and TEST always run" → 3 lanes conditional** — บังคับเฉพาะ 1-WAY/2-WAY; ROUTINE แทนด้วย engineer dispatch เดียว + never-skip list
3. **SCAFFOLD owner — orchestrator รันเองตาม Task 0 ของ tech-lead; ไม่เพิ่ม stage-subagent/allowlist** · 1-WAY ข้าม · ROUTINE ย่อเหลือ verification run
4. **Blind scope — pin ต่อ reviewer** · withhold: engineer report/claims/known-issues/findings ข้าม reviewer · plan/design ไม่ withhold

Open questions เดิม Q1–Q3 ปิดแล้ว — คำตอบฝังใน §3 (Q1 branch-always, Q2 orchestrator อ่าน diff เอง) และ §5 (Q3 per-stage commits + user squash เอง) ไม่มี section คำถามค้าง — override ได้เฉพาะโดย user

## 6. Pipeline ใหม่ + lanes (mermaid)

2-WAY: research → design + MODE A gate → plan (Task 0) → SCAFFOLD (opencode รัน) → implement (engineer, contract-first) → REVIEW blind dispatch → TEST เทียบ baseline → WRAP-UP (diff-summary + retro + DONE)
1-WAY: plan ย่อ → implement → REVIEW (blind, triggered) → TEST → WRAP-UP (ไม่มี SCAFFOLD แยก)
ROUTINE: branch ใหม่เสมอ → engineer dispatch เดียว → orchestrator อ่าน diff → commit + DONE (เกิน routine = promote ขึ้น 1-WAY; `general` ห้ามรับงานนอก run)

## 7. Work Board owner chain

2-WAY: research → solution-architect → tech-lead → opencode (SCAFFOLD) → engineer → code-reviewer (+conditional) → quality-engineering → docs → opencode (WRAP-UP)
1-WAY: tech-lead → engineer → code-reviewer (+triggered) → quality-engineering → docs → opencode
ROUTINE: engineer → opencode
กติกา: gates/conditional reviewers ไม่ขยับ Owner · orchestrator-run steps ใช้ Owner = opencode · Blocked + reason ตามเดิม

## 8. Checklist สิ่งที่ต้อง ship พร้อมกัน

1. orchestrator.md: **baseline mirror แล้ว (repo commit 7e57443)** — แก้ตามดีไซน์ (lanes + ปิดช่อง `general`, SCAFFOLD, Blind dispatch, WRAP-UP diff-summary, Stage-boundary commits section, Hard rules rewrite, Work Board ข้อ 2) แล้ว diff+copy กลับ `~/.config/opencode/agents/`
2. engineer.md (installed + repo mirror): never-commit rewrite
3. web-ui-reviewer.md (installed + mirror): blind paragraph
4. architect-reviewer.md (installed + mirror): input pins paragraph
5. docs.md (installed + mirror): mermaid convention bullet
6. allow-pattern: `sync-from-claude.py` `WORKFLOW_DIR` → `**/docs/workflow/*` → re-run sync → ยืนยัน 3 rows + nested-root write probe (§4a)
7. sync script: SKIP comment → re-run → verify /api/agent
8. doc §2 mermaid (แก้ edge label `BLOCKER / MAJOR` ที่มี / ด้วย)
9. doc §4 file tree: เพิ่ม row `agents/orchestrator.md` (mirror)
10. doc §5: engineer row "safe commits" → "it never commits"; artifact-agents row: pattern → `**/docs/workflow/*`
11. doc §6: จำนวน (20/4/16) ไม่แก้ — แก้ wording pattern ให้ตรง §4a + re-run assertions
12. doc §11 เขียนใหม่ "Run mechanics (P1)" + **fitness functions**
13. README/ATTRIBUTION/repo AGENTS.md: ไม่แตะ
14. doctor.py ก่อน commit ทุกครั้ง
14a. **executed (gate round 3 fix ทาง a):** doctor.py derive `name` จาก filename สำหรับ OpenCode-native agents ที่ไม่มี `name:` (เช่น orchestrator.md mirror) — rerun แล้ว **0 errors** (27 agents)
6b. **executed:** baseline canonical copy ของ `sync-from-claude.py` → repo `tools/mirror/sync-from-claude.py` (แก้ NIT ของ gate — sync script ไม่มี git baseline มาก่อน)
15. **P1 text assertions (fitness functions, grep-based) — รันคู่ §6 ใน smoke step + เขียนใน doc §11:** engineer.md **ไม่มี** "If asked to commit" · orchestrator.md **มี** Blind dispatch paragraph · web-ui-reviewer.md + architect-reviewer.md **มี** input-pin paragraphs · 3 lanes **มี**ใน orchestrator.md — grep กับ installed **และ** repo mirrors (จับ divergence) — กัน "ลบทิ้งพร้อมกันทั้งสองสำเนา = unblinding เงียบ" ซึ่ง mirror+sync อย่างเดียวกันไม่ได้ · **เพิ่มจาก gate round 2: mirror-parity check — installed agent ทุกไฟล์ต้องมี repo mirror และกลับกัน (set คาดหมาย: 26 ไฟล์ + orchestrator.md) หรือขั้นต่ำ: WRAP-UP assert ทั้งสองสำเนา diff เท่ากัน**
16. cross-run learnings: append mermaid pointer ตอน WRAP-UP

## 9. Tradeoffs rejected (สรุป)

devops-engineer stage · engineer scaffold pre-task · engineer commit เมื่อสั่ง · commit ครั้งเดียวตอน DONE · orchestrator squash ตอน DONE · minimal commit เฉพาะ PARKED · คง always-run · permission-layer blind · rule กระจาย 7 ไฟล์ · orchestrator วาดเอง · convention แค่ learnings · forward noticed-untouched เป็น trigger hints (accepted loss) · absolute-path allow pattern · ROUTINE ใช้ branch เดิม / dispatch code-reviewer

## 10. Risks + first steps

ROUTINE misclassify → exclusion list + promote-up + branch + no-push + user merge · reviewer ขาด input → "say so instead of guessing" + dispatch ครอบ · baseline ช้า → tech-lead size Task 0 · commit แตะ branch อื่น → branch ใหม่ + never push + prefix wf() · prompt drift → diff mirror + sync + assert §6 · unblinding เงียบ → fitness functions ข้อ 15 ทุก smoke step · nested-root write ยังพัง → probe §4a พิสูจน์ก่อน wrap

ลำดับ: (0) baseline mirror orchestrator.md **เสร็จแล้ว (7e57443)** → (1) blind isolation → (2) commit backstop → (3) SCAFFOLD → (4) ROUTINE lane → (5) mermaid summary → (5a) allow-pattern + probe → (6) doc + doctor + re-assert + text assertions + smoke run (~3-3.5 ชม.)

## 11. Reversibility

two-way ทั้งหมด (orchestrator.md มี repo baseline แล้ว) · one-way-ish ที่ยอม: ROUTINE misclassification (bound ด้วย branch+no-push+user merge), engineer never-commit (flow เดิมพัง — ยอม ขัด AGENTS.md อยู่แล้ว), "noticed but did not touch" หายจาก REVIEW (accepted loss §2) · SCAFFOLD env installs (cleanup = user §1) · history ยาวขึ้นต่อ run (user squash เอง) · กลไกกัน regression ของสัญญา P1 = fitness functions (§8 ข้อ 15 + mirror-parity, document ใน doc §11)
