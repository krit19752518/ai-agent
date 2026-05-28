import os
from llm_factory import get_agent_llm

# โหลด LLM ผ่าน Groq / OpenRouter ที่ตั้งค่าไว้
llm = get_agent_llm(provider="groq")

# ==============================================================================
# 1. นิยามบทบาท (Role-based Agents)
# ==============================================================================

def run_ba_agent(raw_requirement: str) -> str:
    """BA Agent: Requirement Conflict Checker สแกนหาช่องโหว่ทางตรรกะ"""
    print("\n🤖 [BA Agent] 🔍 เริ่มต้นการสแกนหา Requirement Conflicts...")
    system_prompt = """คุณคือ Business Analyst (BA) ระดับผู้เชี่ยวชาญ 
    หน้าที่ของคุณคืออ่าน Requirement แล้วมองหาช่องโหว่หรือจุดคลุมเครือ สรุปเป็นข้อๆ กระชับ"""
    full_prompt = f"{system_prompt}\n\nโปรดวิเคราะห์ Requirement นี้:\n{raw_requirement}"
    
    response = llm.invoke(full_prompt)
    return str(response.content)  # ดึง .content และแปลงเป็น str เพื่อแก้ข้อผิดพลาด bad-return


def run_sa_agent(clean_requirement_analysis: str) -> str:
    """SA Agent: Architecture Review Bot ร่าง API Spec จากข้อมูลของ BA"""
    print("\n🤖 [SA Agent] 🏗️ เริ่มต้นออกแบบและร่างสเปค API Specification...")
    system_prompt = """คุณคือ System Architect (SA) มืออาชีพ 
    หน้าที่ของคุณคือการนำข้อมูลความต้องการระบบและผลวิเคราะห์ของ BA มาออกแบบ Endpoint สำหรับ API 
    ให้ออกมาเป็นรูปแบบ JSON หรือ YAML ตามมาตรฐาน OpenAPI Specification (Swagger) 
    โดยต้องมี Endpoint สำหรับการทำงาน, HTTP Method, Request Body และ Response (ทั้งกรณี Success 200 และ Error 400/500)"""
    full_prompt = f"{system_prompt}\n\nโปรดร่าง API Spec จากผลวิเคราะห์นี้:\n{clean_requirement_analysis}"
    
    response = llm.invoke(full_prompt)
    return str(response.content)  # ดึง .content และแปลงเป็น str เพื่อแก้ข้อผิดพลาด bad-return


def run_qa_agent(ba_analysis: str, api_spec: str) -> str:
    """QA Agent: QA Test Matrix Draftsman ถอดผลวิเคราะห์และ API Spec เป็นตารางทดสอบ"""
    print("\n🤖 [QA Agent] 📊 เริ่มต้นสร้าง QA Test Matrix...")
    system_prompt = """คุณคือ QA Engineer หน้าที่ของคุณคือการนำผลวิเคราะห์ของ BA และสเปค API จาก SA 
    มาแปลงให้อยู่ในรูปแบบ 'Test Matrix Table' (ตารางเคสทดสอบ Markdown) ที่ครอบคลุม Happy Path, Bad Path, และ Edge Case"""
    full_prompt = f"{system_prompt}\n\nผลวิเคราะห์ BA:\n{ba_analysis}\n\nสเปค API จาก SA:\n{api_spec}"
    
    response = llm.invoke(full_prompt)
    return str(response.content)  # ดึง .content และแปลงเป็น str เพื่อแก้ข้อผิดพลาด bad-return

# ==============================================================================
# 2. จัดสถาปัตยกรรม Workflow: BA -> SA -> QA (End-to-End Pipeline)
# ==============================================================================
if __name__ == "__main__":
    print("🚀 [System Start] เริ่มต้นรันกระบวนการ Agentic SDLC Pipeline (BA -> SA -> QA)")
    print("----------------------------------------------------------------------")
    
    # Input Context ของระบบ
    jira_ticket_requirement = """
    ฟีเจอร์: ระบบถอนเงินด่วนผ่านแอปพลิเคชัน
    เงื่อนไข: 
    1. ผู้ใช้ต้องล็อกอินก่อนเข้าสู่หน้าจอถอนเงิน
    2. ถอนเงินขั้นต่ำ 100 บาท ไม่เกิน 50,000 บาทต่อครั้ง
    3. ถ้าระบบธนาคารปลายทางปิดทำการ ให้แสดงข้อความแจ้งเตือนสีแดง
    """
    
    # ──► STEP 1: ส่งไม้ให้ BA สแกนจุดบกพร่องเชิงตรรกะ
    ba_report = run_ba_agent(jira_ticket_requirement)
    print("\n📝 [ผลลัพธ์จาก BA Agent]:\n", ba_report)
    print("\n" + "="*50)
    
    # ──► STEP 2: ส่งรายงานของ BA ให้ SA ไปออกแบบโครงสร้างหลังบ้าน (API Spec) ต่อทันที
    sa_api_spec = run_sa_agent(ba_report)
    print("\n🛠️ [ผลลัพธ์จาก SA Agent (API Spec)]:\n", sa_api_spec)
    print("\n" + "="*50)
    
    # ──► STEP 3: ส่งข้อมูลจากทั้ง BA และ SA ไปให้ QA สรุปแผนทดสอบขั้นสุดท้าย
    qa_test_matrix = run_qa_agent(ba_report, sa_api_spec)
    print("\n📊 [ผลลัพธ์จาก QA Agent (Test Matrix)]:\n", qa_test_matrix)
    print("\n" + "="*50)
    
    print("🏁 [System End] กระบวนการ Pipeline (3 เอเจนต์) ทำงานเสร็จสมบูรณ์!")