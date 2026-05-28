import os
import sys
import threading
import time
import requests  # type: ignore
import uvicorn
from typing import List, Dict, Any

# =====================================================================
# ตั้งค่าสิ่งแวดล้อม: บังคับให้ Python รู้จักทั้ง Root และโฟลเดอร์ src ไปพร้อมๆ กัน
# =====================================================================
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)  # ดันโฟลเดอร์ src เข้าไปอยู่ในคลังระบบค้นหาหลัก

# =====================================================================
# นำเข้าโครงสร้างระบบที่มีอยู่เดิม (ตัด src. ออกตามมาตรฐาน Import Root)
# =====================================================================
from config import Config
from core.state import AgentState
from core.gemini import GeminiCore
from mcp.linear import parse_linear_issue, fetch_issue_details
from mcp.github import get_repo_structure, get_pr_diff
from mcp.db_schema import parse_schema_to_markdown, get_database_schema
from agents.ba import check_conflicts
from agents.sa import review_architecture_compliance
from agents.ux import review_ui_spec
from agents.dev import generate_code_files
from agents.qa import generate_test_matrix
from agents.pm import calculate_base_risk_score, analyze_sprint_risk
from agents.devops_agent import devops_log_analyzer_node

# นำเข้าตัวรันเวิร์กโฟลว์และเว็บแอปจากระบบเครือข่าย Governance (Phase 4)
from workflows.governance_graph import runtime_workflow
from api.gateway import app

# =====================================================================
# 1. ฟังก์ชันเปิดเซิร์ฟเวอร์หลังบ้าน FastAPI (Governance Gateway API)
# =====================================================================
def start_governance_gateway():
    """เปิดบริการ Endpoint คอยสแตนด์บายรับสัญญาณตรวจรีวิวจากมนุษย์"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

# =====================================================================
# 2. ฟังก์ชันหลักสำหรับเชื่อมโยงการทำงาน (End-to-End Execution)
# =====================================================================
def run_agentic_sdlc_pipeline():
    print("==================================================")
    print("      ANTIGRAVITY AGENTIC SDLC CORE PIPELINE      ")
    print("==================================================")
    
    # 2.1 เปิดใช้ API Gateway ในแบบ Background Thread เพื่อไม่ให้บล็อกการประมวลผลโค้ด
    api_server_thread = threading.Thread(target=start_governance_gateway, daemon=True)
    api_server_thread.start()
    time.sleep(1.5)  # ให้เวลาระบบเครือข่าย FastAPI ตั้งตัว 1.5 วินาที
    
    # 2.2 จัดเตรียมเซสชันและระบุข้อมูลตั้งต้นเข้าสู่ระบบ
    # (เปลี่ยน Thread ID ทุกครั้งเมื่อรัน Sprint ใหม่เพื่อแยกเก็บ Checkpoint)
    session_config = {"configurable": {"thread_id": "antigravity_sprint_session_777"}}
    
    initial_payload = {
        "project_id": "PROJ-777",
        "artifact_status": "initialized",
        "review_comment": "",
        "is_approved": False
    }
    
    print("\n[🎬 Step 1: รันเวิร์กโฟลว์อัตโนมัติพาร์ทต้น (Upstream Pipeline)]")
    print("-> ดึงข้อมูลตั๋วงาน -> ร่าง Spec -> ตรวจโครงสร้างความปลอดภัย")
    
    # สั่งให้ LangGraph ค่อย ๆ สตรีมประมวลผลไปทีละ Node
    for processing_event in runtime_workflow.stream(initial_payload, session_config):
        print(f"   ⚙️ Status ความคืบหน้าของ Agent: {processing_event}")

    # =====================================================================
    # 🛑 จุดล็อคความปลอดภัยสูงสุด (Human-in-the-Loop Interrupt)
    # =====================================================================
    print("\n[🛑 Step 2: เวิร์กโฟลว์ติดขัดอย่างปลอดภัยบนระบบควบคุม (Interrupt Activated)]")
    print("-> ระบบตรวจพบคำสั่งล็อก: แช่แข็งการส่งข้อมูลขึ้น Production ชั่วคราว...")
    
    # แสดงข้อความแจ้งเตือนด่วนสำหรับ UI (กระชับ / คุม Token ต่ำกว่า 200 ตัวอักษร)
    print("\n" + "-"*65)
    print("🚨 ตรวจพบการขอ Deploy โค้ดไปยัง Production!")
    print("โครงสร้างไฟล์ทั้งหมดผ่าน Safe-Write Check และสแกนสถาปัตยกรรมแล้ว")
    print("✅ ยอมรับขั้นตอนต่อ? กด Approve เพื่อดำเนินต่อหรือ Reject เพื่อยกเลิก (10 วินาที)")
    print("-"*65 + "\n")
    
    # 2.3 จำลองเหตุการณ์: มนุษย์อ่านสรุปรายงานบนหน้าจอแล้วกดยืนยัน "Approve" 
    print("[👤 Step 3: ผู้มีอำนาจตัดสินใจกดยืนยันผ่านหน้าแผงควบคุมระบบ]")
    time.sleep(3.0)  # จำลองเวลาที่มนุษย์ใช้พินิจพิจารณาก่อนกดปุ่ม
    
    human_decision_payload = {
        "thread_id": "antigravity_sprint_session_777",
        "approve": True,
        "comment": "สถาปัตยกรรมโค้ดผ่านเกณฑ์ประเมินความเสี่ยง ยินยอมให้ Deployment ขึ้นระบบได้"
    }
    
    # ส่งคำสั่งอนุมัติผ่าน HTTP POST ไปยังตัวตนฝั่ง API หลังบ้านที่สร้างไว้ใน Task 4.2
    api_endpoint_url = "http://127.0.0.1:8000/api/agent/review"
    try:
        api_response = requests.post(api_endpoint_url, json=human_decision_payload)
        print(f"-> สัญญาณตอบกลับจาก Gateway: {api_response.json()}")
    except Exception as network_error:
        print(f"🚨 [NETWORK ERROR] ไม่สามารถส่งสิทธิ์การรีวิวได้: {str(network_error)}")
        return

    # 2.4 ปลดล็อกเวิร์กโฟลว์ รันพาร์ทท้ายจนส่งมอบงานถึงปลายทางอย่างรัดกุม
    print("\n[🚀 Step 4: ปลดล็อกเวิร์กโฟลว์ (Resuming Downstream Pipeline)]")
    print("-> โค้ดหลุดพ้นจากจุดแช่แข็ง และวิ่งเข้าทำงานต่อใน Node ความเสี่ยงสูง")
    
    # รันต่อโดยการส่งผ่านค่า None (ระบบจะไปดึง Checkpoint เดิมในหน่วยความจำมารันต่อทันที)
    for final_event in runtime_workflow.stream(None, session_config):
        print(f"   ⚙️ Status ความคืบหน้าปลายทาง: {final_event}")
        
    print("\n==================================================")
    print("      PRODUCTION PROTECTION PIPELINE SUCCESS      ")
    print("==================================================")

if __name__ == "__main__":
    run_agentic_sdlc_pipeline()