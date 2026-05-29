# 🚀 Antigravity Agentic SDLC: Task Allocation & Token Optimizer

ตารางติดตามงานฉบับจัดสรรผู้รับผิดชอบระหว่าง **[Human]** และ **[AI]** เพื่อเพิ่มความปลอดภัยและลดการใช้ Token ที่ไม่จำเป็น

---

## 🏗️ PHASE 1: FOUNDATION & CONTEXT LAYER (Infrastructure Setup)
*สถานะ: [x] สำเร็จแล้วทั้งหมด (ย้ายไปโฟกัสที่การกำหนดบทบาทเฟสถัดไป)*

---

## 🤖 PHASE 2: CORE ROLE-BASED AGENTS IMPLEMENTATION
*เป้าหมาย: พัฒนาตัวตน ตรรกะความคิด และเครื่องมือของ Agent ทั้ง 7 ตัว*

### 📋 Task 2.1: Implement BA Agent (Requirement Conflict Checker)
* [x] **[AI]** เขียน System Instruction ให้ `gemini-2.5-pro` สแกนหาความขัดแย้งทางตรรกะแบบวิพากษ์ (Critical Thinking) *(ปรับใช้เครื่องมือทดแทนผ่าน Groq สำเร็จ)*
* [x] **[AI]** เขียนลอจิกตรวจสอบขอบเขตความจำ (Knowledge Base) เพื่อเช็กเทียบกับตั๋วงานเก่า
* [x] **[Human]** นำโค้ดลอจิกไปสร้างเป็นฟังก์ชันหลัก คุมประเภทโครงสร้าง JSON Output ให้ตรงตามที่ระบบต้องการ

### 📋 Task 2.2: Implement SA Agent (Architecture Review Bot)
* [x] **[Human]** รวบรวมกฎสถาปัตยกรรม (เช่น Folder Structure, Naming Convention) ใส่ไฟล์คอนฟิกเพื่อลดขนาด Token
* [x] **[AI]** เขียนฟังก์ชันเชื่อมโยงข้อมูลให้ SA Agent เข้าถึงเครื่องมืออ่าน Database Schema
* [x] **[AI]** ออกแบบ Prompt สั่งให้ Gemini เจนเนอเรต OpenAPI Specification ในรูปแบบ YAML / JSON *(ทดสอบผ่านระบบ Pipeline ย่อยสำเร็จ)*

### 📋 Task 2.3: Implement UX Agent (State & Component Mapper)
* [x] **[AI]** เขียน Prompt ให้วิเคราะห์ Requirement แยกพฤติกรรม UI ออกเป็น 4 สถานะ (Happy, Empty, Loading, Error)
* [x] **[AI]** เขียนลอจิกสแกนหา Component ในคลังข้อมูล Storybook Metadata เพื่อนำกลับมาใช้ซ้ำ
* [x] **[Human]** ตรวจสอบรูปแบบการพิมพ์คู่มือ (UI Specification Markdown) ว่าอ่านง่ายสำหรับทีมฟรอนต์เอนด์หรือไม่

### 📋 Task 2.4: Implement Dev Agent (Boilerplate Generator)
* [x] **[AI]** ออกแบบ Prompt Template ที่รองรับการป้อนข้อมูลขนาดใหญ่ (API Spec + Folder Structure) ให้ประหยัด Token
* [x] **[AI]** ใช้ `gemini-2.5-flash` เขียนโค้ดสคริปต์เสกไฟล์ Controller, Service และ Unit Test แบบแกะแพทเทิร์นทีม
* [x] **[Human]** เขียนระบบ Safe-Write Check บนเครื่องตัวเองเพื่อบล็อกไม่ให้ AI เขียนไฟล์ทับของเดิม

### 📋 Task 2.5: Implement QA Agent (Test Matrix Architect)
* [x] **[AI]** เขียน System Instruction สวมบทบาท Lead QA และออกแบบ Prompt แปลงข้อกำหนดเป็นแผนการทดสอบ
* [x] **[AI]** เขียนฟังก์ชันรวบรวมบริบทและจัดข้อมูลให้ออกมาเป็นตาราง 4 มิติ (Happy, Unhappy, Edge Case, RBAC) *(รันสกัดออกเป็นตารางทดสอบสำเร็จ)*
* [x] **[Human]** นำเอา Markdown Test Cases ที่ AI เจนฯ ได้ ไปผูกและยิงเข้า Test Management Tool ของทีม

### 📋 Task 2.6: Implement PM Agent (Sprint Risk Radar)
* [x] **[Human]** เขียนสมการหรือตรรกะคณิตศาสตร์สำหรับคำนวณคะแนนความเสี่ยงพื้นฐาน (Risk Score 0-100%) เพื่อประหยัด Token ของ AI (ทำโครงสร้าง/สูตรเบื้องต้นให้สามารถปรับแต่งภายหลังได้เรียบร้อย)
* [x] **[AI]** ใช้ Gemini วิเคราะห์ข้อความในคอมเมนต์ที่เป็นข้อพิพาท (Blocked Context) เพื่อประเมินความเสี่ยงเชิงลึก
* [x] **[AI]** ร่างสรุปรายงานสรุปความเสี่ยงและแนวทางแก้ไข (Risk Summary Report) ออกมาเป็นหัวข้อสั้น ๆ

### 📋 Task 2.7: Implement DevOps Agent (CI & Log Analyzer)
* [x] **[Human]** ทำสคริปต์สกัด Log ตัวปัญหายาว ๆ คัดเอามาเฉพาะส่วนที่พัง (Stack Trace) ส่งต่อให้ AI (ช่วยลด Token ได้กว่า 80%)
* [x] **[AI]** ใช้ `gemini-2.5-flash` แปลงหน้าตาโค้ดพังๆ สรุปออกมาเป็นคำแนะนำวิธีแก้ไขฉบับภาษาไทยเข้าใจง่าย *(เชื่อมโยงแบบจำลองลงในระบบ Workflow หลักแล้ว)*

---

## 🔄 PHASE 3: END-TO-END WORKFLOW INTEGRATION
*เป้าหมาย: ร้อยเรียง Agent ทั้งหมดเข้าด้วยกันผ่าน LangGraph State*

### 📋 Task 3.1: Build the Upstream Workflow (Linear to Dev Boilerplate)
* [x] **[AI]** ร่างผังเส้นทางวิ่งและเงื่อนไข (Nodes & Edges) ในระบบ LangGraph ตั้งแต่รับตั๋วงานจนถึงส่งโค้ด
* [x] **[Human]** ประกอบและตรวจสอบความสอดคล้องของการแชร์ข้อมูลกันผ่านวัตถุกลาง (`AgentState`) 

### 📋 Task 3.2: Build the Downstream Workflow (PR to Release Ready)
* [x] **[AI]** ร่างโค้ดสร้าง Node การทำงานสำหรับฝั่งตรวจสอบ (SA Review -> QA -> DevOps -> PM)
* [x] **[Human]** นำความคิดเห็น (Feedbacks) ของ AI มารวบรวมใส่ตัวแปรกลางเพื่อเตรียมแสดงผลบนหน้าแผงควบคุม

---

## 🚨 PHASE 4: GOVERNANCE & PRODUCTION PROTECTION
*เป้าหมาย: ล็อกความปลอดภัยด้วยระบบกำกับดูแลโดยมนุษย์ 100%*

### 📋 Task 4.1: Implement LangGraph Human-in-the-Loop Interrupt
* [x] **[Human]** เขียนคำสั่งระบุจุดหยุดพักขบวนการทำงาน (`interrupt_before`) ใน LangGraph เพื่อความปลอดภัยสูงสุด
* [x] **[Human]** ติดตั้งจุดจัดเก็บสถานะระบบชั่วคราว (SqliteSaver หรือ Postgres Checkpointer) บน Server เพื่อรองรับการกดยืนยัน

### 📋 Task 4.2: Build Antigravity Governance Gateway Integration
* [x] **[Human]** พัฒนาเส้นทางเชื่อมโยงข้อมูล (API Endpoint `/api/agent/review`) เพื่อรอรับคำสั่งส่งกลับมาจากมนุษย์
* [x] **[AI]** ร่าง Prompt ปรับแต่งแต่งข้อความรายงานสรุปให้อ่านง่าย กระชับสั้นที่สุด เพื่อให้คนกดอนุมัติใน 10 วินาที
* [x] **[Human]** ผูกปุ่มกดสั่งการ (Approve / Reject) บนหน้าจอระบบควบคุมภายนอกเพื่อให้สัญญาณรันต่อหรือตีกลับงาน

---

## 🔧 PHASE 5: MCP & AGENT REFACTORING (📌 กำลังดำเนินการ)
*เป้าหมาย: ปรับโครงสร้างระบบแกนหลักให้เสถียร เชื่อมโยงฐานข้อมูล พร้อมระบบ Retry/Failover*

### 📋 Task 5.1: Database Connection Retry & Failover Logic
* [x] **[AI]** พัฒนาลอจิก Retry 3 ครั้ง + Fallback ไปใช้ In-Memory Mock Schema ใน `db_schema.py` เมื่อเกิด OperationalError
* [x] **[AI]** เขียน Unit Test ใน `tests/test_db_schema.py` เพื่อจำลองกรณี PostgreSQL ออฟไลน์

### 📋 Task 5.2: State Refactoring & Mapping
* [x] **[Human]** แก้ไขโครงสร้าง `AgentState` ใน `src/core/state.py` ให้เป็น Pydantic BaseModel เพื่อความเสถียรของ Type
* [x] **[AI]** อัปเดต Wrapper และการเรียกใช้เอเจนต์ทั้ง 7 ตัว (BA, SA, UX, Dev, QA, PM, DevOps) ให้ดึง/เขียนค่าผ่าน Pydantic State และคุมความยาวใต้ 200 Tokens
* [x] **[AI]** เขียน Unit Test ย่อยจำลองการทำงานของเวิร์กโฟลว์ด้วย Pydantic State และตรวจสอบระดับ Tokens ที่ใช้จริงในระบบทดสอบหลัก

---

## 🎭 PHASE 6: AI WEB RECORD & REPLAY WITH PLAYWRIGHT
*เป้าหมาย: พัฒนาและเชื่อมต่อโมดูล Replay สำหรับรัน Automated Tests จาก UI Action Events*

### 📋 Task 6.1: Update Pydantic AgentState (Task 5.2 Extended)
* [ ] **[Human]** ปรับโครงสร้างไฟล์ `src/core/state.py` เปลี่ยนจาก TypedDict ไปใช้ Pydantic `BaseModel` ร่วมกับ Field เพื่อควบคุมความปลอดภัยของชนิดข้อมูล
* [ ] **[AI]** นำตัวแปรสถานะทั้งหมดของ Agent 7 ตัวจาก `src/workflow.py` มารวบไว้ที่ `src/core/state.py` ให้เป็นที่เดียว
* [ ] **[AI]** เพิ่มฟิลด์ควบคุมการรัน Playwright: `recorded_steps: list[dict]`, `dom_snapshots: list[str]`, `playwright_script: str`, `playwright_logs: str`, `playwright_retry_count: int`
* [ ] **[Human]** เขียน Unit Test `tests/test_state_replay.py` เพื่อตรวจสอบความเสถียรในการสร้างคลาส Pydantic State และการโหลด JSON/Dict เข้าสู่ Model

### 📋 Task 6.2: Upgrade QA Agent (Playwright Script Writer)
* [ ] **[AI]** เขียน System Instruction ชุดใหม่ (`PLAYWRIGHT_SYSTEM_INSTRUCTION`) ใน `src/agents/qa.py` สั่งให้ Gemini 2.5 Pro แปลง DOM Events เป็นโค้ด Python Playwright
* [ ] **[AI]** พัฒนาฟังก์ชัน `generate_playwright_script(recorded_steps: list, dom_snapshots: list) -> str` คุยผ่าน Gemini 2.5 Pro ด้วยพารามิเตอร์ประหยัด Token และ Deterministic (Temp 0.1)
* [ ] **[Human]** เขียน Unit Test `tests/test_qa_playwright.py` ทดสอบส่ง Mock Event (เช่น Click `#submit-btn`) และเช็กว่าผลลัพธ์เป็น Code Script ที่สามารถรันได้จริง

### 📋 Task 6.3: Create Execution Node & Governance Gateway
* [ ] **[AI]** สร้าง Node `qa_playwright_node` และ `playwright_execution_node` ใน `src/workflow.py` 
* [ ] **[AI]** ใน `playwright_execution_node` พัฒนาส่วนรันโค้ด Python ผ่าน `subprocess.run` และดัก Error Stack Trace ส่งเข้าตัวแปร `playwright_logs`
* [ ] **[Human]** ล็อกและลงทะเบียนจุดหยุดรอเพื่อขออนุมัติจากผู้ใช้ `interrupt_before=["playwright_execution_node"]` ใน Graph Compile เพื่อให้สัญญาณ Human Approval (Governance Gateway)
* [ ] **[Human]** เขียน Unit Test `tests/test_playwright_execution.py` ทดสอบการกระตุ้นรันแบบ Mock Run และจับ Error Stack Trace

### 📋 Task 6.4: Fallback & Retry (DevOps Integration)
* [ ] **[AI]** พัฒนาเงื่อนไขวนซ้ำ (Conditional Edge) ใน `src/workflow.py` สำหรับ `playwright_execution_node` หากพังและ `playwright_retry_count < 3` ให้บวกค่า Retry และวิ่งกลับไปให้ QA Agent เขียนสคริปต์ใหม่โดยแนบ Stack Trace ไปด้วย
* [ ] **[AI]** หากลองครบ 3 ครั้งยังพัง ให้โยนสถานะไปยัง `devops_analyzer` เพื่อวิเคราะห์ Root Cause และรายงานผลเป็นภาษาไทย
* [ ] **[Human]** เขียน Integration Test สำหรับตรวจการเกิด Loop ย้อนกลับและข้ามไปยัง DevOps Agent ในกรณีที่พังจนหมดโควตา Retry