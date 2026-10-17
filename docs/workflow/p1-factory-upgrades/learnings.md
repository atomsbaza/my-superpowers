# learnings — บทเรียนสะสมของ factory (อ่านก่อนทุก stage)

- แก้ prompt/agent files: grep หา text จริงในไฟล์ก่อน edit เสมอ — line-wrap ในไฟล์ไม่ตรงกับที่จำ (เจอซ้ำ 3 ครั้งใน P0)
- Notion: ใช้ id จาก url ใน response — field `id` ของ create-pages อาจไม่ตรงกับ page จริง
- Permission probe: match wildcard ทั้ง action และ resource (rule เป็น pattern เช่น `my-memory_*`, `playwright_*`)
- แก้ installed agents (~/.claude/agents) แล้ว diff+copy กลับ repo `agents/` ทุกครั้ง — repo มีหลาย session แกะพร้อมกัน
- mermaid ในไฟล์: quote ป้ายที่มีวงเล็บ, ใช้ &#60;/&#62; แทน <>, ห้าม / เปล่าใน edge labels
- จบ turn: ตรวจ artifact จริงก่อนรายงานเสร็จ (doctor.py, /api/agent, mcp list, git rev-list)
