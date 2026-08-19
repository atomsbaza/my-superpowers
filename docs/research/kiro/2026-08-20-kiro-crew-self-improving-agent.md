# รายงาน: ทำให้ AI agent/Crew เรียนรู้และพัฒนาความสามารถต่อเนื่องจากประสบการณ์ได้คล้ายคนจริง

**วันที่อ้างอิง:** 20 สิงหาคม 2026<br>
**ขอบเขต:** Kiro Crew, agent memory, lessons, skills, reflection, experience replay, evaluation, specialization และ security/governance

## บทสรุปผู้บริหาร

แนวทางที่ปลอดภัยและทดลองได้จริงไม่ใช่การปล่อยให้ agent “แก้ตัวเอง” หรือแก้ system prompt แบบอิสระ แต่คือการสร้างวงจร:

> **ทำงาน → บันทึกประสบการณ์ → ตรวจผลด้วย evaluator → สะท้อนบทเรียน → สร้าง candidate lesson/skill → ทดสอบ regression → ให้มนุษย์อนุมัติ → publish แบบมีขอบเขต → monitor/rollback**

ข้อสรุปหลักมี 7 ข้อ:

1. **Memory อย่างเดียวไม่ใช่การเรียนรู้** — ต้องมี retrieval ที่เหมาะกับบริบท, evaluator ที่เชื่อถือได้ และกลไกป้องกัน negative transfer
2. **แยก raw episode, lesson, workflow และ skill ออกจากกัน** — raw trajectory เป็นหลักฐาน ไม่ควรถูกฉีดเข้า prompt ในฐานะคำสั่งโดยตรง
3. **Reflection ต้อง grounded กับผลลัพธ์จริง** — self-critique ที่ไม่มี test, tool result หรือ human feedback อาจเพียงสร้างคำอธิบายที่ฟังดูดีแต่ผิด
4. **Skill evolution ควรเริ่มจาก candidate skill** — skill ใหม่ต้องมี provenance, scope, evidence, confidence, expiry และ rollback
5. **การประเมินต้องใช้ held-out tasks** — ถ้าทดสอบเฉพาะงานที่ agent เคยเห็น อาจวัดแค่การจำหรือ prompt drift ไม่ใช่การเรียนรู้ที่ถ่ายโอนได้
6. **Multi-agent specialization ช่วยลดภาระและเพิ่มการตรวจสอบได้ แต่เพิ่มต้นทุนและความเสี่ยงของ cascading hallucination**
7. **การเรียนรู้ที่มีผลต่อ tool, policy, security หรือข้อมูลภายนอกต้องมี human approval เสมอ**

Kiro Crew มี substrate ที่เหมาะสมอยู่แล้ว ได้แก่ memory หกชั้น, lessons, semantic/episodic retrieval, skills, custom agents, snapshots, scheduling และ security controls แต่เอกสารทางการยังไม่ยืนยันว่า Kiro มี native pipeline สำหรับ **candidate skill promotion, structured trajectory store, evaluator-based regression gate หรือ per-skill rollback** ดังนั้นส่วนเหล่านี้ควรถือเป็นสิ่งที่ต้องสร้างหรือยืนยันเพิ่มเติม

---

## 1. วิธีอ่านหลักฐาน

รายงานนี้ใช้ป้ายกำกับดังนี้:

- **Evidence** — ข้อค้นพบโดยตรงจากงานวิจัยหรือเอกสารทางการ
- **Inference/Proposal** — การอนุมานและข้อเสนอสำหรับการทดลองกับ Kiro Crew
- **Current Kiro Crew capability** — สิ่งที่ยืนยันได้จากเอกสาร Kiro Crew
- **Needs verification** — สิ่งที่ยังไม่พบหลักฐานชัดเจน หรืออาจเปลี่ยนตามรุ่น

แหล่งที่เผยแพร่ก่อนวันที่ **20 สิงหาคม 2025** ติดธง **`[อาจล้าสมัย: >1 ปี]`** แม้แนวคิดจะยังมีประโยชน์ก็ตาม ผลการทดลองจาก paper ไม่ควรถูกตีความเป็น performance guarantee ของ Kiro Crew หรือโมเดลรุ่นปัจจุบัน

---

# 2. Key Findings

## 2.1 Memory ที่ดีต้องมีหลายชนิด ไม่ใช่ vector database เดียว

### Evidence

งาน **Generative Agents** เสนอ memory stream, retrieval, reflection และ planning โดย retrieval พิจารณาอย่างน้อย:

- ความเกี่ยวข้องกับ task ปัจจุบัน
- ความใหม่หรือ recency
- ความสำคัญของเหตุการณ์

จากนั้น reflection จะสกัดข้อสรุประดับสูงกว่าจาก observations และ reflection เดิม ก่อนนำไปใช้ใน planning ([Generative Agents](https://arxiv.org/html/2304.03442)) **[อาจล้าสมัย: >1 ปี]**

งาน **ExpeL** แยกการเรียนรู้เป็น 3 ขั้น:

1. เก็บ trajectory ทั้ง success และ failure
2. สกัด insight ที่ถ่ายโอนข้าม task
3. retrieve trajectory หรือ insight ที่เกี่ยวข้องกับ task ใหม่

งานนี้สนับสนุนแนวคิดว่า episodic experience และ abstract lesson ควรทำงานร่วมกัน ไม่ใช่แทนที่กัน ([ExpeL](https://arxiv.org/html/2308.10144v2)) **[อาจล้าสมัย: >1 ปี]**

งาน **Agent Workflow Memory** เน้นการสกัด workflow ที่นำกลับมาใช้ซ้ำได้ แล้วเลือกให้เฉพาะ workflow ที่เกี่ยวข้องเข้าสู่ context ในงาน web navigation รายงานการปรับปรุง relative success rate บน Mind2Web และ WebArena แต่ผลดังกล่าวเป็นผลในสภาพแวดล้อมเฉพาะของงานวิจัย ([Agent Workflow Memory](https://arxiv.org/abs/2409.07429)) **[อาจล้าสมัย: >1 ปี]**

### Current Kiro Crew capability

Kiro Crew ระบุ memory หกชั้นอย่างชัดเจน:

1. **Preferences** — วิธีทำงานและความชอบของผู้ใช้
2. **Projects** — context ของงานหรือ project
3. **Recent history** — ประวัติล่าสุดที่มี time-based decay
4. **Semantic memory** — ข้อเท็จจริงแบบ structured key-value
5. **Episodic memory** — เหตุการณ์หรือ snippet จากอดีต
6. **Lessons** — correction และ rule ที่มี priority สูง

เอกสาร Kiro ระบุว่า semantic memory ใช้ SQLite และ optional FAISS พร้อม hybrid retrieval ที่ผสม vector score กับ keyword score ส่วน episodic memory มี decay, deduplication, cap และ MMR diversity reranking นอกจากนี้ยังมี consolidation ตามจำนวนข้อความและช่วง idle ([Kiro Crew Memory](https://kiro.dev/docs/crew/features/memory/))

Kiro ยังแยก **Knowledge Library** ออกจาก automatic memory สำหรับเอกสารภายนอกที่ต้องการ curate และค้นหาในภายหลัง

### Inference/Proposal

ให้กำหนดบทบาทของข้อมูลแต่ละชนิดดังนี้:

| ชนิดข้อมูล | ใช้เก็บอะไร | ไม่ควรใช้ทำอะไร |
|---|---|---|
| Raw episode | trajectory, tool output, error, evaluator result | ไม่ควร inject เป็นคำสั่งโดยตรง |
| Episodic memory | เหตุการณ์สั้น ๆ ที่อาจช่วย task คล้ายกัน | ไม่ควรถือว่าเป็นกฎถาวร |
| Semantic memory | ข้อเท็จจริงที่ตรวจสอบแล้ว | ไม่ควรเก็บความเห็นชั่วคราวเป็น fact |
| Lesson | กฎการทำงานหรือ correction | ไม่ควรสร้างจาก failure ครั้งเดียว |
| Workflow | ลำดับขั้นตอนทั่วไปที่นำกลับมาใช้ซ้ำได้ | ไม่ควรผูกกับ environment version เดียวโดยไม่ระบุ scope |
| Skill | ขั้นตอนหรือ capability ที่ agent เรียกใช้ | ไม่ควรให้สิทธิ์ tool กว้างกว่าที่จำเป็น |
| Knowledge Library | เอกสารภายนอกที่ curate แล้ว | ไม่ควรปะปนกับประสบการณ์สดที่ยังไม่ตรวจสอบ |

รูปแบบ retrieval ที่เสนอ:

```text
query
  → semantic relevance
  → lexical relevance
  → task-family match
  → environment/version match
  → evaluator success history
  → recency/expiry
  → trust, provenance และ risk filter
  → top-k context
```

สิ่งสำคัญคือ **relevance ไม่เท่ากับ truth** การ retrieve ได้ดีเพียงอย่างเดียวไม่เพียงพอ ต้องตรวจว่า memory นั้นสำเร็จใน environment ที่ใกล้เคียงและยังไม่หมดอายุ

---

## 2.2 Reflection มีประโยชน์เมื่อเชื่อมกับ feedback ที่ตรวจสอบได้

### Evidence

**Reflexion** แยกบทบาทเป็น Actor, Evaluator และ Self-Reflection model โดยแปลง reward หรือ feedback เป็นข้อความ reflection แล้วบันทึกใน episodic memory รายงานผลดีขึ้นในหลาย task แต่ paper เองก็ระบุข้อจำกัด เช่น การพึ่งพาความสามารถ self-evaluation ของ LLM, ความเสี่ยงติด local minima และการไม่มี formal guarantee ([Reflexion](https://arxiv.org/html/2303.11366v4)) **[อาจล้าสมัย: >1 ปี]**

**Self-Refine** ใช้ LLM เดียวเป็น generator, feedback provider และ refiner โดยทำ generate → critique → refine ซ้ำ รายงานว่าได้ผลดีขึ้นเฉลี่ยประมาณ 20 percentage points ใน 7 งาน แต่ผลลัพธ์ขึ้นกับ task และ evaluator มาก ([Self-Refine](https://arxiv.org/abs/2303.17651)) **[อาจล้าสมัย: >1 ปี]**

**Voyager** ใช้ environment feedback, execution error และ self-verification เพื่อปรับ code ที่ใช้เป็น action policy ก่อนบันทึกเป็น skill ([Voyager](https://arxiv.org/html/2305.16291)) **[อาจล้าสมัย: >1 ปี]**

### Inference/Proposal

Reflection ควรสร้าง output แบบมีโครงสร้าง ไม่ใช่ข้อความยาวทั่วไป:

```text
1. What happened?
2. What was expected?
3. What evidence proves success or failure?
4. What was the failure signature?
5. What is the smallest reusable correction?
6. When does this correction apply?
7. When must it not be applied?
8. What test can falsify this correction?
```

ลำดับความน่าเชื่อถือของ feedback ควรเป็น:

1. deterministic validator หรือ test result
2. tool/environment state
3. execution error และ exit code
4. independent evaluator agent
5. self-reflection ของ actor ตัวเดิม
6. ความรู้สึกว่า “คำตอบดูดี”

**ข้อเสนอ:** อย่า promote lesson หรือ skill จาก self-reflection เพียงอย่างเดียว ต้องมีอย่างน้อยหนึ่งในสิ่งต่อไปนี้:

- test ผ่าน
- state transition ถูกต้อง
- evaluator อิสระยืนยัน
- human review
- สำเร็จซ้ำใน task ที่ต่างกัน

---

## 2.3 Experience replay ควร replay “บทเรียนที่มีเงื่อนไข” ไม่ใช่คัดลอก trajectory ทั้งหมด

### Evidence

**AgentRR: Get Experience from Practice** เสนอ record-and-replay สำหรับ agent:

1. บันทึก interaction trace และ internal decision process
2. สรุปเป็น structured experience ที่มี workflow และ constraints
3. replay experience ใน task ที่คล้ายกัน
4. ใช้ check function เป็น trust anchor เพื่อตรวจ completeness และ safety ([AgentRR](https://arxiv.org/abs/2505.17716)) **[อาจล้าสมัย: >1 ปี]**

**Contextual Experience Replay** เสนอ dynamic memory buffer ที่สะสมและสังเคราะห์ประสบการณ์เกี่ยวกับ environment dynamics และ decision patterns รายงานผลบน WebArena และ VisualWebArena แต่ยังเป็นหลักฐานใน benchmark เฉพาะ ไม่ใช่หลักฐานว่า replay จะปลอดภัยในระบบ production ทุกชนิด ([Contextual Experience Replay](https://arxiv.org/abs/2506.06698)) **[อาจล้าสมัย: >1 ปี]**

### Inference/Proposal

ควรมี replay 3 ระดับ:

1. **Prompt replay**<br>
   นำบทเรียนหรือ workflow summary เข้า context ราคาถูก แต่เสี่ยงใช้ผิดบริบท

2. **Workflow replay**<br>
   นำโครงร่างขั้นตอนกลับมาใช้ โดยแทนค่าที่เปลี่ยน เช่น repository, path, entity หรือ date

3. **Environment replay**<br>
   รัน trace ใน cloned/sandbox environment เพื่อตรวจว่า procedure ยังใช้ได้จริง

สำหรับ task ที่มี side effect ควรใช้ระดับ 2 หรือ 3 ไม่ควรทำ exact replay กับ production โดยตรง

ควรเก็บทั้ง:

- successful episodes
- failed episodes
- near-miss
- invalid action
- evaluator disagreement
- security rejection

Failure episode มีประโยชน์มาก เพราะช่วยให้ agent รู้ว่า **วิธีใดไม่ควรใช้ และภายใต้เงื่อนไขใด**

---

## 2.4 Skill evolution ควรเป็น procedural learning ที่มีวงจรอนุมัติ

### Evidence

Voyager มี skill library ที่เก็บ executable programs โดย:

- สร้าง skill จาก task ที่ทำสำเร็จ
- สร้าง description และ index ด้วย embedding
- retrieve skill ที่เกี่ยวข้อง
- compose skill เล็กเป็น skill ใหญ่
- ใช้ environment feedback และ self-verification ก่อนบันทึก

ผู้วิจัยรายงานว่า skill library ช่วยให้เกิด zero-shot generalization ไปยัง task ใหม่ใน Minecraft แต่เป็นระบบเฉพาะโดเมนและมี self-verification ที่ออกแบบขึ้นเอง ([Voyager](https://arxiv.org/html/2305.16291)) **[อาจล้าสมัย: >1 ปี]**

**MetaGPT** ใช้ role specialization, SOP, structured communication และ executable feedback โดยแบ่ง Product Manager, Architect, Project Manager, Engineer และ QA Engineer งานวิจัยรายงานว่า role และ executable feedback ช่วยใน software-development benchmark ของตน แต่การเพิ่ม agent ก็เพิ่ม token, latency และจุดที่อาจเกิด cascading hallucination ([MetaGPT](https://arxiv.org/html/2308.00352)) **[อาจล้าสมัย: >1 ปี]**

### Current Kiro Crew capability

Kiro Crew skills เป็น Markdown files ที่:

- ตั้งเป็น always-on หรือ on-demand ได้
- เรียกใช้ผ่าน keyword triggers
- แก้ผ่าน dashboard หรือ filesystem
- การแก้ไขมีผลกับ invocation ถัดไป

ดูเอกสารทางการได้ที่ [Kiro Crew Skills](https://kiro.dev/docs/crew/capabilities/skills/)

Kiro Crew ยังรองรับ custom agents ที่กำหนด:

- model
- system prompt
- tools
- MCP servers
- approval mode

และระบุ use case เช่น agent ที่มี read-only tool สำหรับ reviewer หรือ agent ที่มี scope จำกัด ([Kiro Crew Agents](https://kiro.dev/docs/crew/capabilities/agents/))

### Inference/Proposal: lifecycle ของ skill

```text
raw episode
   ↓
candidate workflow/skill
   ↓
quarantine + static/security checks
   ↓
test ใน held-out tasks
   ↓
human approval
   ↓
canary scope
   ↓
live skill
   ↓
monitor + expiry/review
   ↓
deprecated หรือ rollback
```

ตัวอย่าง metadata ที่ควรมี:

```yaml
name: candidate-repository-test-repair
description: Repair a failing test after inspecting the failure output
triggers: [test failure, failing test]
always: false

# ข้อเสนอเพิ่มเติม ไม่ใช่ field ที่เอกสาร Kiro ยืนยันว่ารองรับโดยตรง
status: candidate
scope: repository-x
required_tools: [read_file, run_tests]
forbidden_tools: [network_write, production_deploy]
provenance: episode-2026-08-20-001
environment_version: commit-or-image-id
evidence:
  successful_runs: 4
  failed_runs: 1
validator: pytest-exit-code
confidence: 0.91
expires: 2026-11-20
rollback: snapshot-id
```

ควรเริ่มจาก skill ที่ใช้ **read-only tools** ก่อน แล้วจึงค่อยขยายไปยัง write tools หลังผ่านการอนุมัติและ regression test

---

## 2.5 Agent specialization ช่วยจัดระเบียบความรับผิดชอบ แต่ไม่ใช่หลักฐานว่า “หลาย agent ดีกว่าเสมอ”

### Evidence

MetaGPT ชี้ว่าการกำหนด role ที่ชัดเจนและส่งมอบ structured artifact ลดความกำกวมเมื่อเทียบกับการสนทนาแบบอิสระ แต่ paper ก็ระบุปัญหา cascading hallucination จากการ chain LLM หลายตัว ([MetaGPT](https://arxiv.org/html/2308.00352)) **[อาจล้าสมัย: >1 ปี]**

### Inference/Proposal

รูปแบบที่เหมาะกับการทดลอง:

| Role | หน้าที่ | สิทธิ์ที่เสนอ |
|---|---|---|
| Orchestrator | แตก task, เลือก workflow, ตรวจ dependency | ไม่มี production write |
| Researcher/Retriever | ค้น memory/knowledge และรวบรวมหลักฐาน | read-only |
| Executor | ทำ action ใน sandbox | เฉพาะ tool ที่จำเป็น |
| Evaluator | รัน test ตรวจ state และจัดประเภท failure | read/test-only |
| Curator | สร้าง candidate lesson/skill | เขียน quarantine store เท่านั้น |
| Human approver | อนุมัติ promotion และ high-impact action | อำนาจอนุมัติ |
| Monitor | ตรวจ regression, drift, security events | read-only |

ทุก handoff ควรใช้ schema เช่น:

```json
{
  "task_id": "...",
  "status": "success|failure|blocked",
  "evidence": ["test:...", "tool_result:..."],
  "assumptions": [],
  "next_action": "...",
  "risk": "low|medium|high",
  "requires_approval": true
}
```

**ไม่ควร** ให้ agent ทุกตัวอ่านและเขียน memory เดียวกันได้เต็มรูปแบบ เพราะจะทำให้:

- lesson ที่ผิดถูก reinforce
- agent หนึ่งแก้ความเชื่อของอีก agent โดยไม่มี provenance
- prompt injection แพร่ผ่าน shared memory
- การหาต้นตอของความผิดพลาดทำได้ยาก

---

## 2.6 Evaluation ต้องวัดการถ่ายโอนและการไม่ถอยหลัง

จากหน้า SWE-bench ที่คุณส่งมา จุดสำคัญคือ benchmark ไม่ได้ตรวจเพียงรูปแบบ patch แต่เอา patch ไปใช้กับ repository จริงแล้วรัน test ใน Docker เพื่อดูว่า issue ถูกแก้จริงหรือไม่ ([SWE-bench Evaluation Guide](https://www.swebench.com/SWE-bench/guides/evaluation/))

นี่เป็นแนวคิดสำคัญสำหรับ Kiro Crew: **ประเมิน state หรือ outcome ที่ตรวจสอบได้ ไม่ใช่ประเมินแค่คำตอบที่ฟังดูถูก**

### Evidence จาก benchmark

**AgentBench v3** แบ่งการประเมิน agent เป็น 8 environment และแยกสาเหตุของ failure เช่น:

- Context Limit Exceeded
- Invalid Format
- Invalid Action
- Task Limit Exceeded
- Complete

เนื้อหาที่คุณส่งมายังชี้ว่า repetition เป็นสาเหตุสำคัญของ TLE โดยมากกว่า 90% ของ trajectory ที่เป็น TLE มีคำตอบช่วงท้ายที่มี Rouge-L similarity สูงในบางเงื่อนไข ([AgentBench v3](https://arxiv.org/html/2308.03688v3), revision 4 ตุลาคม 2025)

**WebArena** แสดงให้เห็นว่า agent ที่ดูเก่งใน task ย่อยอาจล้มเหลวในงาน web ที่ยาวและมีหลายขั้นตอน โดย baseline GPT-4 ที่รายงานใน paper ทำ end-to-end task success ได้ 14.41% เทียบกับ human performance 78.24% จึงเหมาะกับการใช้เป็น stress test ของ planning, exploration และ failure recovery ไม่ใช่เป็นตัวเลขอ้างอิงของโมเดลปัจจุบัน ([WebArena](https://arxiv.org/html/2307.13854v4)) **[อาจล้าสมัย: >1 ปี]**

SWE-bench paper ฉบับ ICLR 2024 เป็น benchmark สำหรับ issue จริงและ test-based grading แต่เป็น benchmark software engineering ไม่ใช่ benchmark สำหรับ continual memory โดยตรง ([SWE-bench paper](https://openreview.net/forum?id=VTF8yNQM66)) **[อาจล้าสมัย: >1 ปี]**

### Inference/Proposal: benchmark สำหรับ Kiro Crew

เริ่มจากชุดงานเล็กที่ควบคุมได้:

- 10 task families
- family ละ 4–10 variants
- deterministic validator
- แยก train/online, validation และ held-out test
- มี security canary tasks
- freeze model, prompt, tool schema และ environment version

แขนการทดลอง:

| Arm | Memory | Reflection | Replay | Skill promotion |
|---|---|---|---|---|
| A | ไม่มี | ไม่มี | ไม่มี | ไม่มี |
| B | episodic/semantic read-only | ไม่มี | ไม่มี | ไม่มี |
| C | memory + evaluator | มี | ไม่มี | ไม่มี |
| D | memory + evaluator | มี | มี | ไม่มี |
| E | memory + evaluator | มี | มี | human-approved skill |
| F | E + specialized agents | มี | มี | human-approved skill |

อย่าเปรียบเทียบเฉพาะค่าเฉลี่ยรวม ควรรายงานแยกตาม:

- task family
- ความยาว trajectory
- tool ประเภทต่าง ๆ
- environment version
- first-seen vs repeated task
- success และ failure mode

---

# 3. ตารางเปรียบเทียบ Research กับ Kiro Crew

| ประเด็น | Evidence จากงานวิจัย/มาตรฐาน | Current Kiro Crew capability | Needs verification |
|---|---|---|---|
| Memory | episodic retrieval, reflection และ planning ช่วย transfer ได้ในบาง benchmark | memory หกชั้น, semantic/episodic retrieval, decay, MMR, consolidation | ปรับ policy ของ automatic consolidation และ implicit lessons ได้ละเอียดแค่ไหน |
| Lessons | Reflexion/ExpeL สนับสนุนการเก็บ verbal feedback และ insight | lessons มี priority สูงและถูก inject แยกเป็น Learned corrections | workflow สำหรับ candidate lesson → approval → live ยังไม่ยืนยัน |
| Workflow replay | AWM, AgentRR และ CER สนับสนุน reusable workflow/experience | มี episodic memory และ skills เป็น substrate | native structured experience store, replay API และ check function ยังไม่ยืนยัน |
| Skill evolution | Voyager ใช้ skill library และ iterative verification | skills เป็น Markdown, trigger ได้, แก้แล้วมีผล invocation ถัดไป | native versioning, provenance, test gate, per-skill rollback |
| Specialization | MetaGPT สนับสนุน role, SOP และ structured handoff ในบางงาน | custom agents กำหนด model, prompt และ tool scope ได้ | shared memory isolation และ role-to-role typed protocol |
| Evaluator | SWE-bench ใช้ execution/test; AgentBench แยก failure modes | Kiro มี tool runner/scheduling primitives | evaluator harness สำหรับ A/B, held-out regression และ result schema |
| Snapshot | reproducibility ต้อง reset environment และ version state | Kiro snapshot/restore รวม memory artifacts | atomic rollback ของ skill/lesson รายตัว |
| Security | OWASP เน้น prompt injection, excessive agency, poisoning และ least privilege | Kiro มี denied commands, sensitive-path blocking, approval, sandbox, redaction และ audit | การป้องกัน memory poisoning ในระดับ semantic/episodic โดยตรง |
| Scheduling | continual system ต้องมี review/decay loop | Kiro มี cron, webhook และ heartbeat ตามเอกสาร product | การผูก scheduled job เข้ากับ evaluator โดยไม่สร้าง side effect |
| Knowledge curation | external documents ต้องมี provenance และตรวจ injection | Knowledge Library แยกจาก automatic memory | source trust, document approval และ policy ต่อ instruction ที่อยู่ในเอกสาร |

---

# 4. Practical Architecture

## 4.1 แบ่งเป็น 3 planes

```text
┌──────────────────────────────────────────────────────────────┐
│ Execution plane                                               │
│ Task → Context → Planner → Executor → Tool Gateway → Sandbox │
└──────────────────────────────┬───────────────────────────────┘
                               │ trajectory + state + outputs
┌──────────────────────────────▼───────────────────────────────┐
│ Learning plane                                                 │
│ Evaluator → Failure classifier → Reflection → Curator        │
│          → Candidate lesson/workflow/skill                    │
└──────────────────────────────┬───────────────────────────────┘
                               │ candidate artifact
┌──────────────────────────────▼───────────────────────────────┐
│ Control plane                                                  │
│ Provenance → Regression gate → Human approval → Publish       │
│ Snapshot → Monitor → Expiry → Rollback                        │
└──────────────────────────────────────────────────────────────┘
```

## 4.2 การประกอบ context

เมื่อเริ่ม task:

1. อ่าน critical rules และ lessons
2. ระบุ project/environment/version
3. retrieve semantic facts
4. retrieve episodic experiences ที่ task-family ตรงกัน
5. retrieve workflow/skill ที่ scope ตรงกัน
6. retrieve Knowledge Library เฉพาะเมื่อเป็นเอกสารอ้างอิง
7. ตัด memory ที่หมดอายุ, conflict, risk สูง หรือ provenance ไม่ชัด
8. ส่งเข้า planner พร้อมระบุว่าอะไรเป็น **fact**, **experience**, **hypothesis** และ **instruction**

ข้อเสนอสำคัญคืออย่าใส่ memory ทั้งหมดเข้า context ให้ใช้ `top-k` และจำกัด token budget ต่อชนิดข้อมูล

## 4.3 Experience record

หากต้องการทำ experiment อย่างจริงจัง ควรมี structured record แยกจากข้อความ memory:

```json
{
  "experience_id": "exp-2026-08-20-001",
  "task": {
    "family": "repository-test-repair",
    "input_hash": "...",
    "difficulty": "medium"
  },
  "environment": {
    "repo_revision": "...",
    "tool_schema_version": "...",
    "sandbox_image": "..."
  },
  "trajectory_ref": "immutable-log://...",
  "outcome": {
    "status": "success",
    "validator": "pytest",
    "tests_passed": 42,
    "tests_failed": 0
  },
  "failure_signature": null,
  "reflection": {
    "summary": "...",
    "evidence_refs": ["test-output:...", "tool-call:..."]
  },
  "derived_artifact": {
    "kind": "candidate_skill",
    "id": "skill-candidate-..."
  },
  "governance": {
    "source": "agent|human|external-document",
    "scope": "repository-x",
    "confidence": 0.91,
    "risk": "low",
    "expires_at": "2026-11-20",
    "approval": "pending"
  },
  "lifecycle": "quarantine"
}
```

`trajectory_ref` ควรชี้ไปยัง immutable log และมีการ redact ข้อมูลลับ ไม่ควรฝัง raw credential หรือข้อมูลส่วนบุคคลใน lesson/skill

---

# 5. Learning Loop ที่เสนอ

## ขั้นที่ 1: Retrieve

เลือก memory ตาม:

- task similarity
- task family
- project/environment
- version
- historical success
- recency
- trust/provenance
- risk

ให้ retrieve ทั้ง success และ failure แต่แสดงสถานะให้ agent เห็นชัดเจน

## ขั้นที่ 2: Plan และ Act

Agent ต้อง:

- อ้างอิง evidence ที่ retrieve มา
- ระบุ assumption
- ใช้ tool ตาม least privilege
- checkpoint ก่อน side effect
- หยุดเมื่อพบ ambiguity หรือ policy conflict

## ขั้นที่ 3: Evaluate

ใช้ evaluator หลายชั้น:

1. deterministic validator
2. test/state checker
3. independent critic
4. human review สำหรับ high-impact outcome

Evaluator ต้องคืน structured result:

```json
{
  "success": false,
  "failure_type": "invalid_action",
  "evidence": ["tool returned 403", "state unchanged"],
  "retryable": true,
  "severity": "medium",
  "critique": "..."
}
```

## ขั้นที่ 4: Reflect

Reflection ต้องอ้างอิง observation และ evaluator evidence ไม่ใช่เดาจากความรู้สึก

ผลลัพธ์ควรเป็น:

- correction
- precondition
- negative condition
- expected benefit
- test/falsifier

## ขั้นที่ 5: Curate

Curator แปลงประสบการณ์เป็น artifact ที่เหมาะสม:

- fact ที่เสถียร → semantic memory
- user preference → lesson/preferences
- วิธีแก้เฉพาะเหตุการณ์ → episodic memory
- workflow ที่ทำซ้ำได้ → candidate workflow
- capability ที่มี test และ scope → candidate skill
- เอกสารภายนอก → Knowledge Library

## ขั้นที่ 6: Regression gate

รัน:

- task ที่เคยแก้ได้
- task ที่เคยล้มเหลว
- held-out task
- adversarial task
- security canary
- task ที่มีชื่อ/บริบทคล้ายแต่ต้องใช้วิธีต่างกัน

## ขั้นที่ 7: Human approval

ต้องมีมนุษย์อนุมัติก่อน:

- skill ที่เรียก tool
- lesson ที่มีผลข้าม project
- policy หรือ security instruction
- memory ที่มีข้อมูลส่วนบุคคลหรือความลับ
- workflow ที่มี external side effect
- การเปลี่ยน role หรือ tool permission

## ขั้นที่ 8: Publish และ monitor

หลังอนุมัติ:

1. สร้าง snapshot
2. publish แบบ canary scope
3. monitor success, regression, security events และ cost
4. กำหนด expiry/review date
5. rollback หากพบ failure หรือ drift

---

# 6. Phased Experiment Plan

## Phase 0 — Baseline และ observability

**เป้าหมาย:** รู้ว่า agent ปัจจุบันล้มเหลวอย่างไร

ทำสิ่งต่อไปนี้:

- สร้าง 30–100 deterministic tasks
- แบ่ง task family และ difficulty
- freeze model, prompt, tool schema และ environment
- log ทุก tool call, observation, result และ evaluator output
- จัดประเภท failure ตาม AgentBench เช่น invalid format, invalid action, TLE/repetition
- ห้าม live memory write ในรอบ baseline

**Exit gate:** มี baseline success rate, latency, token/cost และ failure distribution ครบ

## Phase 1 — Retrieval-only

เปรียบเทียบ:

- ไม่มี memory
- episodic memory
- semantic memory
- episodic + semantic
- Kiro memory กับ Knowledge Library แยกกัน

ยังไม่ให้ agent สร้าง lesson หรือ skill ใหม่

**วัด:** retrieval precision@k, task success, negative transfer และ token overhead

**Exit gate:** retrieval ช่วย held-out task โดยไม่ทำให้ task เดิมแย่ลง

## Phase 2 — Evaluator และ grounded reflection

เพิ่ม:

- deterministic evaluator
- failure classifier
- reflection ที่ต้องอ้าง evidence
- candidate lesson ที่ยังไม่ live

ให้ feedback จาก failure ถูก replay ใน task ที่คล้ายกัน

**Exit gate:** reflection ช่วยลด failure แบบเดิม และไม่เพิ่ม hallucinated correction

## Phase 3 — Candidate workflow/skill

เปลี่ยน recurring lesson ให้เป็น candidate skill:

- เริ่มจาก read-only tool
- จำกัด scope ต่อ repository หรือ task family
- เพิ่ม precondition และ postcondition
- ทดสอบอย่างน้อยหลาย task และหลาย environment state
- ให้มนุษย์ approve ก่อน activate

**Exit gate ตัวอย่าง:**

- success rate บน held-out เพิ่มขึ้นตาม threshold ที่ pre-register ไว้
- regression ไม่เกิน 2 percentage points
- ไม่มี critical security finding
- candidate ผ่าน static/tool-scope review
- มี snapshot และ rollback path

ตัวเลขข้างต้นเป็น **ข้อเสนอเริ่มต้น** ไม่ใช่มาตรฐานสากล ควรปรับตามความเสี่ยงของงาน

## Phase 4 — Agent specialization

ทดลองเพิ่ม:

- planner/orchestrator
- executor
- evaluator
- curator

เปรียบเทียบกับ single agent โดยวัดทั้ง quality และ cost

**Exit gate:** quality gain ต้องมากกว่าค่าใช้จ่ายด้าน tokens, latency และ communication failure

## Phase 5 — Continuous operation

จึงค่อยเพิ่ม:

- cron/heartbeat สำหรับ review
- memory decay และ expiry
- periodic regression
- snapshot rotation
- red-team task
- canary release
- incident/rollback process

ห้ามเริ่มจาก autonomous self-modification เต็มรูปแบบ

---

# 7. Metrics และ Benchmarks

## 7.1 Metrics หลัก

ให้วัดอย่างน้อย:

### Task success

\[
SR = \frac{\text{จำนวน task ที่ผ่าน validator}}{\text{จำนวน task ทั้งหมด}}
\]

### Learning gain

\[
\Delta SR = SR_{\text{after}} - SR_{\text{before}}
\]

ต้องรายงานแยก:

- seen-task improvement
- unseen-task transfer
- cross-domain transfer

### Regression

\[
Regression = \max(0, SR_{\text{before,heldout}} - SR_{\text{after,heldout}})
\]

### Negative transfer

สัดส่วน task ที่ผลแย่ลงเพราะ memory หรือ skill ที่ retrieve มา

### Memory utility

วัดว่า memory ที่ถูก retrieve:

- ถูกนำไปใช้จริงหรือไม่
- ช่วยลดจำนวน steps หรือไม่
- เพิ่ม success หรือไม่
- ทำให้เกิด invalid action หรือไม่

### Candidate promotion precision

\[
Precision_{\text{promotion}}
=
\frac{\text{candidate ที่หลัง publish แล้วยังผ่านเกณฑ์}}
{\text{candidate ที่ publish ทั้งหมด}}
\]

### Efficiency

- จำนวน steps
- tokens
- latency
- model calls
- tool calls
- retry count
- cost
- context size

### Reliability

- invalid format rate
- invalid action rate
- TLE rate
- repetition/loop rate
- evaluator disagreement
- recovery success rate

### Safety

- prompt injection success rate
- poisoned memory acceptance rate
- sensitive-data leakage rate
- unsafe tool call block rate
- false approval rate
- unauthorized scope expansion
- rollback time

## 7.2 Benchmark ที่เหมาะสม

### ระดับ 1: Kiro microbench

เหมาะที่สุดสำหรับเริ่มต้น:

- test หรือ script ที่มีผลลัพธ์ deterministic
- isolated repository
- local web app
- database sandbox
- mock MCP server

### ระดับ 2: Interactive agent benchmarks

- AgentBench สำหรับแยก failure modes ของ multi-turn agent ([AgentBench v3](https://arxiv.org/html/2308.03688v3))
- WebArena สำหรับ long-horizon web planning และ functional correctness **[อาจล้าสมัย: >1 ปี]**
- ALFWorld หรือ WebShop สำหรับ embodied/web interaction **[อาจล้าสมัย: >1 ปี]**

### ระดับ 3: Software engineering

- SWE-bench Lite สำหรับเริ่มต้น
- SWE-bench Verified หรือ full SWE-bench เมื่อ harness และ cost พร้อม
- ใช้ Docker และ test-based grading ตาม official evaluation guide

### ระดับ 4: General assistant/tool use

- GAIA เหมาะกับงานที่ต้องใช้ web, code, file และ multimodality แต่ version ที่อ้างอิงเป็นปี 2023 และควรถือเป็น historical baseline **[อาจล้าสมัย: >1 ปี]** ([GAIA](https://arxiv.org/html/2311.12983v1))

---

# 8. Security และ Governance Guardrails

## 8.1 Threat model

OWASP ระบุว่า prompt injection อาจมาจากทั้ง user โดยตรงและ external content เช่น webpage, file หรือ retrieved document และอาจนำไปสู่การเปิดเผยข้อมูล, เรียก function ที่ไม่ได้รับอนุญาต หรือสั่งงานระบบภายนอก ([OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)) **[อาจล้าสมัย: >1 ปี]**

OWASP ยังจัด excessive functionality, excessive permission และ excessive autonomy เป็นความเสี่ยงหลักของ agent และแนะนำ least privilege, complete mediation, granular tools และ human approval ([OWASP LLM06: Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)) **[อาจล้าสมัย: >1 ปี]**

OWASP ระบุว่า data/model poisoning อาจเกิดกับ training data, fine-tuning หรือ embedding data และแนะนำ provenance, data versioning, source validation, sandboxing และ anomaly detection ([OWASP LLM04: Data and Model Poisoning](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/)) **[อาจล้าสมัย: >1 ปี]**

NIST AI RMF และ Generative AI Profile เสนอกรอบ Govern, Map, Measure และ Manage สำหรับจัดการความเสี่ยง AI โดย Generative AI Profile เผยแพร่เมื่อ 26 กรกฎาคม 2024 และควรตรวจสอบ revision ล่าสุดก่อนนำไปใช้เป็น policy ทางการ ([NIST AI RMF GenAI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)) **[อาจล้าสมัย: >1 ปี]**

## 8.2 Kiro Crew security controls ที่ยืนยันได้

Kiro Crew ระบุ defense-in-depth ที่ runtime boundary ได้แก่:

- owner lock
- denied commands
- governance ceiling แบบ Policy ∩ Profile
- sensitive-path blocking
- tool approval
- MCP schema/input validation
- OS sandbox
- output redaction
- audit trail และ audit verification

บน macOS เอกสารระบุการใช้ Seatbelt เป็น OS-level sandbox ([Kiro Crew Security](https://kiro.dev/docs/crew/security/))

สิ่งเหล่านี้เป็น **runtime guardrails** ที่ดี แต่ไม่ควรสรุปว่าแก้ memory poisoning ได้ทั้งหมด เพราะ memory ที่ถูกพิษอาจทำให้ agent เลือก action ที่ดูถูกต้องแต่ผิดเป้าหมายได้โดยไม่ชน denied-command rule

## 8.3 Memory-specific controls

OWASP Agent Memory Guard เสนอแนวคิดเกี่ยวกับการตรวจ integrity ของ persistent memory ด้วย hashing, policy ต่อ read/write, anomaly detection, snapshot และ rollback แต่ควรถือเป็นโครงการ/implementation reference ที่ยังต้องประเมิน maturity ไม่ใช่ control ที่รับรองความปลอดภัยโดยอัตโนมัติ ([OWASP Agent Memory Guard](https://owasp.org/www-project-agent-memory-guard/))

ข้อเสนอสำหรับ Kiro Crew:

1. **Untrusted-by-default**<br>
   ข้อความจาก user, web, file, tool output และ agent อื่นเป็น data ไม่ใช่ system instruction

2. **Typed memory writes**<br>
   อนุญาตเฉพาะ field ที่กำหนด เช่น fact, evidence, scope, expiry และ confidence

3. **ห้าม memory เปลี่ยน security policy โดยอัตโนมัติ**<br>
   ห้ามให้ข้อความในเอกสารสร้าง allowlist, เพิ่ม tool permission หรือปิด approval

4. **Provenance ทุก record**<br>
   เก็บ source, timestamp, environment version, agent identity และ evaluator evidence

5. **Quarantine ก่อน publish**<br>
   raw episode และ candidate artifact ไม่ควรมีผลกับทุก session

6. **Conflict resolution แบบ human review**<br>
   memory ที่ขัดกับ lesson หรือ policy ต้องหยุดและส่งให้มนุษย์ตรวจ

7. **Scope isolation**<br>
   แยก memory ต่อ user, project, repository, tenant และ environment เท่าที่ทำได้

8. **Expiry และ review date**<br>
   workflow ที่ขึ้นกับ version ของ API, repository หรือ policy ต้องหมดอายุได้

9. **Snapshot ก่อน promotion**<br>
   snapshot memory และ skill ก่อนเปลี่ยน live state

10. **Canary release**<br>
    skill ใหม่ควรใช้เฉพาะ task family หรือ project เดียวก่อน

11. **Red-team memory poisoning**<br>
    ทดสอบกรณี external document เขียนว่า “ignore previous rules”, ฝังคำสั่งในโค้ด, สร้าง false lesson หรือพยายามดึงข้อมูลจาก memory อื่น

12. **Bounded autonomy**<br>
    จำกัดจำนวน retries, steps, tokens, network calls และค่าใช้จ่ายต่อ task

13. **Dual approval สำหรับความเสี่ยงสูง**<br>
    policy/security change หรือ external side effect สำคัญควรต้องมีผู้อนุมัติสองคนหรือ approval ระดับทีม

---

# 9. Failure Modes และวิธีลดความเสี่ยง

| Failure mode | สาเหตุ | Mitigation |
|---|---|---|
| Stale memory | fact หรือ workflow หมดอายุ | TTL, version matching, review date |
| Retrieval ผิดบริบท | task คล้ายกันแต่ precondition ต่างกัน | filter ด้วย task family, environment และ scope |
| Memory embellishment | agent เติมรายละเอียดที่ไม่มีใน episode | evidence refs, immutable raw log |
| Self-evaluation bias | actor ให้คะแนนตัวเองสูงเกินจริง | independent evaluator และ deterministic validator |
| Negative transfer | lesson ที่ถูกใน repo A ผิดใน repo B | scope isolation และ held-out counterexamples |
| Skill overgeneralization | skill สำเร็จเฉพาะ state เดียว | precondition/postcondition และ parameterized test |
| Repetition/loop | agent ทำ action เดิมซ้ำ | loop detector, max retry, failure classification |
| Cascading hallucination | agent หลายตัวส่งต่อข้อมูลผิด | structured handoff, source provenance, evaluator |
| Prompt injection | instruction ฝังใน web/file/memory | content/data separation, least privilege, approval |
| Poisoned memory | user หรือ document สร้าง false lesson | quarantine, confidence threshold, human review |
| Benchmark contamination | test task ถูกใช้เป็น memory | split by template/repo/domain/time และ retrieval audit |
| Prompt drift | ผลดีขึ้นเพราะ prompt เปลี่ยน ไม่ใช่ memory | freeze prompt และทำ paired A/B |
| Model drift | provider เปลี่ยน model behavior | pin model/version และบันทึก model metadata |
| Cost explosion | reflection/replay/agents เพิ่ม call | budget ต่อ task, adaptive escalation |
| Rollback ไม่ครบ | snapshot restore กระทบ state อื่น | ทดสอบ restore ใน clone และมี artifact-level deactivation |

---

# 10. Trade-offs

## External memory vs context bloat

Memory ช่วยข้าม session แต่เพิ่มโอกาส retrieve ข้อมูลผิดและทำให้ context ยาวขึ้น จึงควรใช้ top-k, decay, MMR และ scope filter แทนการ replay ประวัติทั้งหมด

## Reflection vs hallucinated certainty

Reflection ช่วยให้ agentอธิบายและแก้ไขได้ แต่ agent อาจสร้างเหตุผลย้อนหลังเพื่อปกป้อง action ที่ผิด จึงควรให้ evaluator result มีอำนาจเหนือ narrative

## Skill reuse vs rigidity

Skill ทำให้เร็วและลด token แต่มีความเสี่ยง lock-in วิธีเดิมและใช้ไม่ได้กับ environment ใหม่ ควรเก็บ precondition, version และ negative examples

## Multi-agent quality vs cost

Specialization ช่วยแยก executor กับ evaluator แต่เพิ่ม communication overhead, latency และ failure surface ไม่ควรเพิ่ม agent หากไม่มีหน้าที่ตรวจสอบที่แตกต่างกันอย่างชัดเจน

## Human approval vs autonomy

Human approval ลดความเสี่ยงแต่เพิ่ม latency และอาจกลายเป็น bottleneck วิธีสมดุลคือ:

- auto-accept เฉพาะ low-risk episodic summary
- human approval สำหรับ lesson ที่มีผลกว้าง
- mandatory approval สำหรับ skill ที่เรียก tools หรือแก้ policy
- dual approval สำหรับ security/high-impact action

## Automatic memory vs curated knowledge

Automatic memory เหมาะกับประสบการณ์สดและ user correction ส่วน Knowledge Library เหมาะกับเอกสารที่ต้อง curate การนำเอกสารภายนอกเข้าคลังโดยไม่ตรวจ provenance จะเปลี่ยน library เป็นช่องทาง memory poisoning

---

# 11. สิ่งที่ยังต้องตรวจสอบกับ Kiro Crew

1. มี API native สำหรับเก็บ full trajectory แบบ structured และ immutable หรือไม่
2. สามารถแยก raw episode ออกจาก automatic episodic memory ได้หรือไม่
3. สามารถปิดหรือ quarantine implicit lessons ระหว่าง controlled experiment ได้หรือไม่
4. สามารถกำหนด candidate → approved → live lifecycle ของ skill ใน dashboard โดยตรงหรือไม่
5. มี skill versioning และ rollback ราย skill หรือจำเป็นต้อง restore ทั้ง snapshot
6. snapshot/restore เป็น atomic และรักษา provenance/audit timeline อย่างไร
7. สามารถผูก Task Runner หรือ cron เข้ากับ deterministic evaluator ใน sandbox ได้อย่างไร
8. สามารถจำกัด memory ต่อ project/agent/tenant ได้ละเอียดเพียงใด
9. custom agent แต่ละตัว share memory กันอย่างไร และป้องกัน cross-scope leakage อย่างไร
10. Kiro มี native A/B evaluation และ held-out regression gate หรือจำเป็นต้องสร้าง evaluator ภายนอก
11. tool approval ครอบคลุมการแก้ skill/lesson โดยตรงหรือเฉพาะ tool call
12. audit log ระบุความสัมพันธ์ระหว่าง memory write, skill promotion และ tool action ได้ละเอียดแค่ไหน

---

# 12. ข้อเสนอแนะสำหรับการเริ่มทดลอง

ลำดับที่แนะนำ:

1. ใช้ **Kiro episodic + semantic memory แบบ read-only**
2. เพิ่ม **deterministic evaluator**
3. เก็บทั้ง success และ failure episode
4. สร้าง reflection แบบมี evidence
5. สร้าง candidate lesson แต่ยังไม่ activate อัตโนมัติ
6. เพิ่ม candidate skill แบบ read-only และ human approval
7. ทำ held-out regression test
8. จึงค่อยทดลอง custom agents และ multi-agent specialization
9. ใช้ snapshot ก่อนทุก promotion
10. เพิ่ม red-team memory poisoning และ prompt injection ก่อนนำไปใช้กับ tool ที่มี side effect

สถาปัตยกรรมนี้ทำให้ Crew “เรียนรู้จากประสบการณ์” ได้ในระดับ external memory, procedure และ workflow โดยไม่ต้องแก้ model weights และไม่ทำให้การเรียนรู้กลายเป็นช่องทางให้ข้อมูลผิดหรือคำสั่งอันตรายกลายเป็นกฎถาวร

---

# Sources

## Current Kiro Crew documentation

1. Kiro Crew Memory — memory layers, retrieval, decay, lessons, consolidation, Knowledge Library และ snapshots<br>
   https://kiro.dev/docs/crew/features/memory/

2. Kiro Crew Skills — Markdown skills, triggers, always-on/on-demand และ next-invocation loading<br>
   https://kiro.dev/docs/crew/capabilities/skills/

3. Kiro Crew Agents — custom agents, model/prompt/tool scope และ approval modes<br>
   https://kiro.dev/docs/crew/capabilities/agents/

4. Kiro Crew Security — denied commands, governance, sandbox, approval, redaction และ audit<br>
   https://kiro.dev/docs/crew/security/

5. Kiro Crew Task Runner<br>
   https://kiro.dev/docs/crew/features/task-runner/

6. Kiro Crew Subagents<br>
   https://kiro.dev/docs/crew/features/subagents/

7. Kiro Crew Knowledge<br>
   https://kiro.dev/docs/crew/features/knowledge/

8. Kiro Crew Snapshot & Restore<br>
   https://kiro.dev/docs/crew/features/snapshot/

## Research: memory, reflection, replay และ skills

9. Generative Agents: Interactive Simulacra of Human Behavior, 2023<br>
   **[อาจล้าสมัย: >1 ปี]**<br>
   https://arxiv.org/html/2304.03442

10. ExpeL: LLM Agents Are Experiential Learners, 2023<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/html/2308.10144v2

11. Reflexion: Language Agents with Verbal Reinforcement Learning, 2023<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/html/2303.11366v4

12. Self-Refine: Iterative Refinement with Self-Feedback, 2023<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/abs/2303.17651

13. Voyager: An Open-Ended Embodied Agent with Large Language Models, 2023<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/html/2305.16291

14. MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework, revision 2024<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/html/2308.00352

15. Agent Workflow Memory, 2024<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/abs/2409.07429

16. Get Experience from Practice: LLM Agents with Record & Replay, 2025<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/abs/2505.17716

17. Contextual Experience Replay for Self-Improvement of Language Agents, ACL 2025<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/abs/2506.06698

## Benchmarks

18. AgentBench, revision 4 October 2025<br>
    https://arxiv.org/html/2308.03688v3

19. SWE-bench Evaluation Guide<br>
    https://www.swebench.com/SWE-bench/guides/evaluation/

20. SWE-bench: Can Language Models Resolve Real-world GitHub Issues?, ICLR 2024<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://openreview.net/forum?id=VTF8yNQM66

21. WebArena: A Realistic Web Environment for Building Autonomous Agents, 2024<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/html/2307.13854v4

22. GAIA: A Benchmark for General AI Assistants, 2023<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://arxiv.org/html/2311.12983v1

## Security and governance

23. OWASP LLM01:2025 Prompt Injection<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://genai.owasp.org/llmrisk/llm01-prompt-injection/

24. OWASP LLM04:2025 Data and Model Poisoning<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/

25. OWASP LLM06:2025 Excessive Agency<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://genai.owasp.org/llmrisk/llm062025-excessive-agency/

26. OWASP Agent Memory Guard<br>
    https://owasp.org/www-project-agent-memory-guard/

27. NIST AI Risk Management Framework: Generative AI Profile, published 26 July 2024<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

28. NIST AI Risk Management Framework 1.0, 2023<br>
    **[อาจล้าสมัย: >1 ปี]**<br>
    https://www.nist.gov/itl/ai-risk-management-framework

รายงานนี้จัดทำในแชตตามคำขอ และไม่มีการสร้าง แก้ไข ลบ หรือ append ไฟล์ในเครื่อง.
