from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AgentState(BaseModel):
    """
    State definition for the Antigravity Agentic SDLC LangGraph orchestrator.
    Manages central state variables, tool responses, and approval flags.
    Supports token optimization and is strictly typed with Pydantic.
    """
    # Core State Variables (from workflow.py)
    jira_ticket_id: str = Field(default="", description="ID ของตั๋วงาน Jira เช่น ANTG-101")
    raw_requirement: str = Field(default="", description="ข้อกำหนดหรือคำอธิบายงานดิบจากตั๋ว")
    brd_analysis: str = Field(default="", description="ผลวิเคราะห์จาก BA")
    api_specification: dict = Field(default_factory=dict, description="API Spec จาก SA")
    ui_component_mapping: str = Field(default="", description="Component จาก UX")
    generated_code_paths: List[str] = Field(default_factory=list, description="รายชื่อไฟล์โค้ด Boilerplate")
    architecture_compliance_report: str = Field(default="", description="ผลวิเคราะห์จาก SA Code Review")
    test_matrix_markdown: str = Field(default="", description="ตาราง QA Test Matrix")
    raw_logs: str = Field(default="", description="Log ดิบยาวๆ จากระบบ CI")
    devops_analysis: str = Field(default="", description="ผลวิเคราะห์จาก DevOps Agent")
    sprint_risk_score: int = Field(default=0, description="คะแนนความเสี่ยงประเมินโดย PM")
    risk_radar_report: str = Field(default="", description="รายงาน Sprint Risk Radar")
    downstream_report: str = Field(default="", description="รายงานสรุปรวมผลลัพธ์ปลายน้ำ")

    # Core State Variables (from original state.py)
    linear_issue_id: str = Field(default="", description="The active ticket ID from Linear")
    current_api_spec: Optional[str] = Field(default=None, description="OpenAPI or API specification YAML/JSON")
    risk_score: float = Field(default=0.0, description="Overall risk calculation score (0.0 to 100.0)")
    approval_status: str = Field(default="PENDING", description="Decision gate status: 'PENDING', 'APPROVED', 'REJECTED'")
    
    # Read-Only Fetched Contexts
    issue_details: Optional[str] = Field(default=None, description="Clean Markdown format of issue contents")
    repo_structure: Optional[str] = Field(default=None, description="Codebase directory layout")
    pr_diff: Optional[str] = Field(default=None, description="Unified diff from GitHub PR")
    db_schema: Optional[str] = Field(default=None, description="Postgres Database Schema metadata map")
    
    # Shared Context / Execution Log
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Audit trail of agent decisions and state changes")

    # AI Web Record & Replay with Playwright fields (Phase 6)
    recorded_steps: List[Dict[str, Any]] = Field(default_factory=list, description="ลำดับขั้นตอนการบันทึก DOM Events หน้าจอ")
    dom_snapshots: List[str] = Field(default_factory=list, description="Snapshots ของ DOM ในแต่ละขั้นตอน")
    playwright_script: str = Field(default="", description="สคริปต์ Playwright Python ที่ QA Agent เจนเนอเรต")
    playwright_logs: str = Field(default="", description="Logs การรัน Playwright จากตัวทดสอบ")
    playwright_retry_count: int = Field(default=0, description="จำนวนครั้งที่รัน Playwright ใหม่เมื่อเจอปัญหา")

