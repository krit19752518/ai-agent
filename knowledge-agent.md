# 🧠 Antigravity Agentic SDLC: Knowledge Base (Phase 1)

เอกสารนี้รวบรวมแนวคิด การออกแบบสถาปัตยกรรม (Design Patterns) และแนวทางปฏิบัติที่ดีที่สุด (Best Practices) จากการทำ **PHASE 1: FOUNDATION & CONTEXT LAYER** เพื่อใช้เป็นมาตรฐานอ้างอิงในการพัฒนาและวางโครงสร้างโปรเจกต์ AI Multi-Agent ในอนาคต

---

## 1. การจัดการสถานะของเอเจนต์ (Agent State Management with LangGraph)

### 📌 แนวคิดการออกแบบ
การทำ Multi-Agent SDLC ต้องการระบบที่สามารถจัดเก็บข้อมูลบริบท (Context) ของการทำงานที่ไหลผ่านแต่ละ Node ของขบวนการได้อย่างสมบูรณ์ โดยอิงหลักการ **Cyclic Workflows & Human-in-the-loop**

### 💡 แนวทางปฏิบัติที่ดีที่สุด (Best Practices)
1. **การปรับเปลี่ยนมาใช้ `Pydantic BaseModel` (พัฒนาจากเดิมที่ใช้ `TypedDict`)**: เพิ่มความรัดกุมในการตรวจสอบชนิดข้อมูล (Type Safety), การให้ค่าตั้งต้น (Default Values), และแก้ปัญหา linter อย่าง Pyrefly ได้อย่างเด็ดขาด
2. **แยกสถานะควบคุมและข้อมูลบริบท (State Separation)**:
   - **Control State (สถานะควบคุม)**: ข้อมูลสำคัญในการเลือกเส้นทาง (Routing) เช่น `linear_issue_id`, `risk_score`, `approval_status` ( gate สำหรับมนุษย์ตรวจสอบ )
   - **Context State (ข้อมูลบริบท)**: ข้อมูลดิบที่ถูกแปลงให้อยู่ในรูปของ Markdown เช่น `issue_details`, `db_schema`, `pr_diff` เพื่อให้พร้อมนำไปป้อนเป็น System Instruction ให้กับ Agent ถัดไป
3. **เก็บบันทึกประวัติการตัดสินใจ (Audit Trail)**: มีคีย์ `logs` เพื่อจัดเก็บพฤติกรรมและการทำงานของ Agent ย้อนหลังเพื่อใช้ทำรายงานหรือวิเคราะห์ข้อผิดพลาด

---

## 2. การควบคุมโมเดลภาษาขนาดใหญ่ (Deterministic Gemini Configuration)

### 📌 แนวคิดการออกแบบ
ในการพัฒนาซอฟต์แวร์แบบ Agentic SDLC เราไม่ต้องการการตอบกลับที่มีความสร้างสรรค์สูงเกินไป (Low Creativity) แต่ต้องการ **ความแม่นยำทางตรรกะและโครงสร้างโค้ดที่ถูกต้อง (High Determinism)**

### 💡 แนวทางปฏิบัติที่ดีที่สุด (Best Practices)
1. **ตั้งค่า Temperature ต่ำมาก (0.1)**: ลดการสร้างข้อมูลเท็จ (Hallucination) ช่วยให้ผลลัพธ์การเขียนโค้ดและการวิเคราะห์ตารางข้อมูลมีความสม่ำเสมอ
2. **จับคู่โมเดลตามภารกิจ (Model Specialization)**:
   - **Gemini 2.5 Pro**: ใช้สำหรับงานวิเคราะห์เชิงลึก, ตรวจจับความขัดแย้งของข้อกำหนดระบบ (BA Agent), ออกแบบสถาปัตยกรรมและ API Specification (SA Agent)
   - **Gemini 2.5 Flash**: ใช้สำหรับงานที่ต้องการความเร็วสูงและปริมาณข้อมูลจำนวนมาก เช่น การสร้างโค้ดตัวอย่าง (Dev Boilerplate Generator), การสแกน Log หาข้อผิดพลาด (DevOps Agent)

---

## 3. สถาปัตยกรรมทางเดินข้อมูลบริบทแบบอ่านอย่างเดียว (Read-only MCP Data Pipeline)

### 📌 แนวคิดการออกแบบ
การเปิด "ตา" ให้ AI สามารถมองเห็นข้อมูลภายในระบบจริง (Linear, GitHub, Database) ต้องแลกมาด้วยความเสี่ยงเรื่องความปลอดภัยทางข้อมูล ทางแก้วิกฤตนี้คือ **"ห้ามมีคำสั่งเขียนหรือแก้ไขข้อมูลใดๆ (Strict Read-only)"**

### 💡 แนวทางปฏิบัติที่ดีที่สุด (Best Practices)
1. **ใช้งานผ่าน Model Context Protocol (MCP)**:
   - เชื่อมต่อ MCP Server (เช่น `@linear/mcp-server` และ `@modelcontextprotocol/server-github`) ผ่านโปรโตคอลมาตรฐาน stdio transport
   - การสปอว์น MCP Server ในรูปของ Subprocess แบบไดนามิกช่วยลดทรัพยากรการเปิดพอร์ตเครือข่ายทิ้งไว้
2. **แปลง JSON เป็น Markdown Clean Text (Token Optimization)**:
   - ข้อมูลดิบที่ได้จาก API มักมาในรูปแบบ JSON ที่มี Metadata ซ้ำซ้อนและไร้ประโยชน์สำหรับโมเดล (เช่น ID ภายใน, วันที่อัปเดตย่อย)
   - ต้องเขียน Parser ใน Python เสมอเพื่อทำความสะอาดและจัดเรียงข้อมูลให้อยู่ในรูป Markdown Table หรือ List แบบกระชับ ซึ่งช่วยลด Token Usage ลงได้มากกว่า **50-70%**
3. **การเข้าถึงฐานข้อมูลแบบปกป้องข้อมูลดิบ (Strict Data Privacy)**:
   - การเข้าถึงโครงสร้างฐานข้อมูล (DDL) ต้องใช้ SQL Query ที่เจาะจงเฉพาะตารางระบบ `information_schema` เท่านั้น
   - **กฎเหล็ก**: ห้าม SELECT ข้อมูลในแถว (Row Data) ออกมาเด็ดขาด เพื่อป้องกันไม่ให้ข้อมูลผู้ใช้งาน (เช่น รหัสผ่าน, อีเมล, ข้อมูลธุรกรรม) รั่วไหลไปสู่โมเดล
   - ตั้งค่าระดับ Connection Session ให้เป็น `readonly=True` ในโค้ด Python เพื่อเป็น Failsafe ด่านสุดท้ายป้องกันคำสั่ง DML (INSERT, UPDATE, DELETE)

---

## 4. โครงสร้างแพ็กเกจและการจัดการความขัดแย้งของ Linter (Package Structure & Pyright Fix)

### 📌 แนวคิดการออกแบบ
เมื่อพัฒนาโปรเจกต์ Python ที่มีโครงสร้างโฟลเดอร์แบบ `src/` ควบคู่ไปกับสคริปต์รันที่วางอยู่ด้านนอก ปัญหาคลาสสิกที่มักพบคือกราฟนำเข้าโมเดลเกิดความสับสน (Import Resolution Fail) และตัววิเคราะห์โค้ด (เช่น Pyright, Pyrefly) จะรายงานความผิดพลาดเตือนสีแดงในหน้าจอเอดิเตอร์

### 💡 แนวทางปฏิบัติที่ดีที่สุด (Best Practices)
1. **จัดโฟลเดอร์ให้มี `__init__.py` เสมอ**: ถึงแม้ Python 3 จะรองรับ Namespace Package แล้ว แต่ลินเตอร์ของเครื่องมือพัฒนาโค้ดยังต้องการไฟล์นี้ในการสร้าง Package Tree
2. **บูตสแตรปเส้นทาง (`sys.path` injection)**:
   ในสคริปต์หลัก (เช่น `main.py`) ที่อยู่ด้านนอกแพ็กเกจ ให้รันคำสั่งแทรก Project Root เข้าไปในระบบค้นหาพาธเสมอ:
   ```python
   import os
   import sys
   project_root = os.path.dirname(os.path.abspath(__file__))
   if project_root not in sys.path:
       sys.path.insert(0, project_root)
   ```
3. **เพิ่มคอนฟิก `pyrightconfig.json` หรือ `pyproject.toml`**:
   ประกาศให้ลินเตอร์มองเห็นรูทในการค้นหาที่ระดับโปรเจกต์ เพื่อขจัดข้อผิดพลาด `missing-import` ปลอมในเอดิเตอร์:
   ```json
   {
     "extraPaths": ["."]
   }
   ```
   และเพิ่มใน `pyproject.toml` (กรณีใช้ร่วมกับเครื่องมือ Poetry):
   ```toml
   [tool.pyright]
   extraPaths = ["."]
   ```

---

## 5. การกำกับดูแลโดยมนุษย์และการป้องกันระบบ (Human-in-the-Loop & Governance Gateway)

### 📌 แนวคิดการออกแบบ
ระบบ Agentic SDLC ที่มีการทำงานระดับโปรดักชัน หรือมีความเสี่ยงในการแก้ไขโค้ด/Deploy จำเป็นต้องมี "จุดแวะพัก" (Interrupt) ให้มนุษย์ (Tech Lead / QA) เป็นผู้อนุมัติก่อนการเปลี่ยนแปลงสำคัญ เพื่อคงกฎ "AI assists, human decides" อย่างเคร่งครัด

### 💡 แนวทางปฏิบัติที่ดีที่สุด (Best Practices)
1. **ใช้ LangGraph `interrupt_before`**: กำหนดจุดแวะพักก่อน Node ที่มีความเสี่ยงสูง (เช่น `prod_deploy`) เพื่อหยุดการทำงานของ Graph ชั่วคราว
2. **การจัดเก็บสถานะด้วย MemorySaver/SqliteSaver**: ใช้ Checkpointer เพื่อบันทึกสถานะของ Graph ไว้ในหน่วยความจำหรือฐานข้อมูล ทำให้สามารถ Resume กลับมาทำต่อได้หลังจากมนุษย์กดยืนยัน (Approve/Reject)
3. **สร้าง Governance API Gateway**: พัฒนา FastAPI Endpoint (เช่น `POST /api/agent/review`) สำหรับรับสัญญาณและ Comment จากหน้า UI ภายนอก แล้วใช้คำสั่ง `update_state` และ `stream(None)` ของ LangGraph เพื่อปลดล็อกและเดินเครื่องต่อ

---

## 6. ความทนทานของระบบและการจัดการข้อผิดพลาด (Resilience, Retry & Failover)

### 📌 แนวคิดการออกแบบ
โมดูลต่างๆ เช่น การดึง Schema จาก Database หรือการคุยกับภายนอกผ่าน MCP มีโอกาสที่ Network จะหลุด หรือ Service ดาวน์ ระบบ Agentic ที่ดีต้องไม่ล่ม แต่ต้องมีแผนสำรอง (Fallback) ที่ให้ทำงานต่อไปได้

### 💡 แนวทางปฏิบัติที่ดีที่สุด (Best Practices)
1. **Exponential Backoff Retry**: เมื่อเกิดข้อผิดพลาดในการเชื่อมต่อ (เช่น `psycopg2.OperationalError`) ให้พยายามเชื่อมต่อใหม่ 3 ครั้ง โดยเพิ่มระยะเวลาหน่วง (0.5s, 1s, 2s)
2. **In-Memory Mock Fallback**: หากลองครบตามจำนวนแล้วยังไม่สำเร็จ ให้สลับไปใช้ข้อมูลจำลอง (Mock Data) อัตโนมัติ (เช่น `MOCK_FALLBACK_SCHEMA`) เพื่อให้ Workflow หลักไม่ถูกบล็อกและ Agent ตัวอื่นๆ ยังสามารถทำงานต่อไปได้
3. **การบังคับใช้ Pydantic BaseModel (Strict Typing)**:
   - เปลี่ยนจากการใช้ `TypedDict` เป็น `Pydantic BaseModel` ใน `AgentState` เพื่อความเสถียร (Type Safety) และเข้ากันได้ดีเยี่ยมกับการตรวจสอบ (Validation) ของเครื่องมือ Linter
   - การลด Token ขาออก (Token Optimization): ตั้งค่า `max_output_tokens=200` ในระดับ LLM Configuration (เช่น `GeminiCore`) เพื่อควบคุมขนาดข้อความที่เอเจนต์สร้างขึ้น ช่วยให้ประหยัดงบประมาณและทำให้ผลลัพธ์กระชับตรงประเด็น
