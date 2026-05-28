from typing import Dict, Any
# 1. นำเข้า BaseModel จาก pydantic มาแทน TypedDict
from pydantic import BaseModel 
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver 

# =====================================================================
# 1. นิยามโครงสร้างข้อมูลกลาง (AgentState) ด้วย Pydantic BaseModel
# =====================================================================
# การใช้ BaseModel จะช่วยให้ Pyrefly ตรวจผ่านฉลุย เพราะตรงตามข้อตกลงของ StateT 100%
class AgentState(BaseModel):
    project_id: str = ""
    artifact_status: str = ""
    review_comment: str = ""
    is_approved: bool = False

# =====================================================================
# 2. นิยาม Nodes การทำงานของระบบ (ปรับการเรียกใช้คุณสมบัติของ Object)
# =====================================================================
def dev_boilerplate_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent] กำลังสร้างโครงสร้างไฟล์พื้นฐาน (Boilerplate)...")
    # สั่งอัปเดตค่ากลับไปที่ StateGraph
    return {"artifact_status": "ready_for_production"}

def prod_deploy_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent] ตรวจสอบสถานะการอนุมัติก่อนขึ้น Production...")
    
    # เปลี่ยนจากการใช้ .get() ใน dict มาเป็นการอ่าน attribute ของวัตถุ (.is_approved)
    if not state.is_approved:
        print("[Governance] 🚨 ปฏิเสธการทำงาน: ไม่ผ่านการอนุมัติ")
        return {"artifact_status": "rejected_by_governance"}
    
    print("[DevOps] 🚀 ดำเนินการ Deploy โค้ดไปยัง Production สำเร็จ!")
    return {"artifact_status": "deployed_to_production"}

# =====================================================================
# 3. ประกอบผังการทำงาน (StateGraph)
# =====================================================================
# เคลียร์คัตแน่นอน! Pyrefly จะเห็นว่า AgentState เป็นลูกหลานของ BaseModel โดยตรง
builder = StateGraph(AgentState)

builder.add_node("dev_boilerplate", dev_boilerplate_node)
builder.add_node("prod_deploy", prod_deploy_node)

builder.add_edge(START, "dev_boilerplate")
builder.add_edge("dev_boilerplate", "prod_deploy")
builder.add_edge("prod_deploy", END)

# =====================================================================
# 4. ติดตั้งจุดจัดเก็บสถานะระบบชั่วคราว
# =====================================================================
memory_saver = MemorySaver()

# =====================================================================
# 5. คอมไพล์ระบบพร้อมระบุจุดหยุดพินิจ (Interrupt)
# =====================================================================
runtime_workflow = builder.compile(
    checkpointer=memory_saver,
    interrupt_before=["prod_deploy"]
)

print("[System] สถาปัตยกรรม Governance ผ่านการเคลียร์ Type ด้วย BaseModel สำเร็จ!")