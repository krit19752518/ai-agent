from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from src.agents.devops_agent import devops_log_analyzer_node

# =====================================================================
# 1. นิยามโครงสร้างข้อมูลกลาง (State) ครอบคลุมตั้งแต่ต้นน้ำยันปลายน้ำ
# =====================================================================
class AgentState(BaseModel):
    # ─── INPUT / JIRA CONTEXT ───
    jira_ticket_id: str = Field(default="", description="ID ของตั๋วงาน Jira เช่น ANTG-101")
    raw_requirement: str = Field(default="", description="ข้อกำหนดหรือคำอธิบายงานดิบจากตั๋ว")

    # ─── UPSTREAM AGENTS (BA / SA / UX / DEV) ───
    brd_analysis: str = Field(default="", description="ผลวิเคราะห์และจุดขัดแย้งทางตรรกะใน Requirement จาก BA Agent")
    api_specification: dict = Field(default_factory=dict, description="OpenAPI / Swagger Specification ที่ SA Agent ออกแบบ")
    ui_component_mapping: str = Field(default="", description="โครงสร้างหน้าจอและลิสต์ Component จาก Storybook โดย UX Agent")
    generated_code_paths: list[str] = Field(default_factory=list, description="รายชื่อไฟล์โค้ด Boilerplate ที่ Dev Agent เสกขึ้นมา")

    # ─── DOWNSTREAM AGENTS (QA / DEVOPS / PM) ───
    test_matrix_markdown: str = Field(default="", description="ตาราง QA Test Matrix (Happy/Edge Cases) จาก QA Agent")
    raw_logs: str = Field(default="", description="Log ดิบยาวๆ จากระบบ CI (สำหรับกรณี Build/Test พัง)")
    devops_analysis: str = Field(default="", description="ผลวิเคราะห์สาเหตุและวิธีแก้ Log พังภาษาไทยจาก DevOps Agent")
    sprint_risk_score: int = Field(default=0, description="คะแนนความเสี่ยงของชิ้นงาน (0-100) ประเมินโดย PM Agent")
    risk_radar_report: str = Field(default="", description="รายงาน Sprint Risk Radar ฉบับย่อภาษาไทยสำหรับสรุปให้มนุษย์อนุมัติ")

# =====================================================================
# 2. นิยามฟังก์ชันจำลอง (Mock Nodes) ของ BA, SA, UX, และ Dev Agent
# =====================================================================
def ba_requirement_node(state: AgentState) -> dict:
    """
    Mock Node สำหรับ BA Agent (Requirement Conflict Checker)
    """
    jira_id = state.jira_ticket_id or "UNKNOWN"
    req = state.raw_requirement or "No requirement provided"
    
    brd_analysis = (
        f"## 📋 ผลวิเคราะห์ Requirement สำหรับ {jira_id}\n"
        f"- **ข้อกำหนดดิบ**: {req}\n"
        f"- **สถานะการตรวจสอบ**: ผ่านการสแกนความขัดแย้งเชิงตรรกะแบบวิพากษ์ (Critical Thinking)\n"
        f"- **ผลการวิเคราะห์**: ไม่พบจุดขัดแย้งทางตรรกะ (Logical Inconsistency) "
        f"เมื่อเทียบกับประวัติระบบเดิม โครงสร้างข้อมูลมีความสอดคล้องกัน"
    )
    return {"brd_analysis": brd_analysis}

def sa_architecture_node(state: AgentState) -> dict:
    """
    Mock Node สำหรับ SA Agent (Architecture Review Bot)
    """
    jira_id = state.jira_ticket_id or "UNKNOWN"
    mock_api_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": f"API for {jira_id}",
            "description": "Generated API specification by SA Agent Mock Node",
            "version": "1.0.0"
        },
        "paths": {
            "/api/v1/auth/login": {
                "post": {
                    "summary": "Authenticate User",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    },
                                    "required": ["username", "password"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login Successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "token": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return {"api_specification": mock_api_spec}

def ux_component_node(state: AgentState) -> dict:
    """
    Mock Node สำหรับ UX Agent (State & Component Mapper)
    """
    jira_id = state.jira_ticket_id or "UNKNOWN"
    ui_mapping = (
        f"## 🎨 UI Spec & Storybook Mapping: {jira_id}\n"
        f"### 1. Happy Path\n"
        f"- **พฤติกรรม**: แสดงหน้าจอเข้าสู่ระบบสมบูรณ์\n"
        f"- **Components**: `AuthCard`, `InputField`, `Button`\n\n"
        f"### 2. Loading State\n"
        f"- **พฤติกรรม**: แสดงวงล้อโหลดระหว่างตรวจสอบข้อมูลการเข้าสู่ระบบ\n"
        f"- **Components**: `LoadingSpinner`\n\n"
        f"### 3. Empty State\n"
        f"- **พฤติกรรม**: ไม่พบข้อมูลหรือฟิลด์ข้อมูลว่างเปล่าตอนโหลดครั้งแรก\n"
        f"- **Components**: `EmptyStatePlaceholder`\n\n"
        f"### 4. Error State\n"
        f"- **พฤติกรรม**: แสดงข้อความแจ้งเตือนสีแดงเมื่อตรวจสอบข้อมูลไม่ผ่าน/รหัสผ่านผิด\n"
        f"- **Components**: `AlertCallout`"
    )
    return {"ui_component_mapping": ui_mapping}

def dev_boilerplate_node(state: AgentState) -> dict:
    """
    Mock Node สำหรับ Dev Agent (Boilerplate Generator)
    """
    mock_paths = [
        "src/controllers/auth_controller.py",
        "src/services/auth_service.py",
        "src/tests/test_auth.py"
    ]
    return {"generated_code_paths": mock_paths}

# =====================================================================
# 3. เริ่มต้นสร้างและกำหนดโครงสร้าง Graph
# =====================================================================
workflow = StateGraph(AgentState)

# ติดตั้ง Node การทำงาน (รวมทั้งจำลองและจริง)
workflow.add_node("ba_checker", ba_requirement_node)
workflow.add_node("sa_reviewer", sa_architecture_node)
workflow.add_node("ux_mapper", ux_component_node)
workflow.add_node("dev_generator", dev_boilerplate_node)
workflow.add_node("devops_analyzer", devops_log_analyzer_node)

# =====================================================================
# 4. กำหนดเส้นทางการเดินรถ (Routing Control)
# =====================================================================
# เริ่มต้นจาก BA Agent วิ่งยาวไปจนถึงจุดสิ้นสุดของฝั่ง Dev
workflow.set_entry_point("ba_checker")
workflow.add_edge("ba_checker", "sa_reviewer")
workflow.add_edge("sa_reviewer", "ux_mapper")
workflow.add_edge("ux_mapper", "dev_generator")
workflow.add_edge("dev_generator", END)

# 5. ประกอบร่างคอมไพล์โครงสร้างทั้งหมดให้กลายเป็นแอปพลิเคชันพร้อมใช้
app = workflow.compile()