from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# นำเข้าโครงสร้างเวิร์กโฟลว์และ State จากโมดูลในโปรเจกต์ (ปรับวิถี Import Root ตามมาตรฐานทีม)
from workflows.governance_graph import runtime_workflow

app = FastAPI(title="Antigravity Governance Gateway")

# =====================================================================
# ตั้งค่าระบบควบคุมสิทธิ์ CORS (Cross-Origin Resource Sharing)
# เพื่อรองรับหน้าจอแผงควบคุมภายนอกที่อาจรันอยู่ที่พอร์ต 8080 (ไม่ให้เกิดการบล็อกสิทธิ์)
# =====================================================================
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 1. นิยามโครงสร้างข้อมูลรับเข้า (Payload) จาก UI หน้าแผงควบคุม
# =====================================================================
class ReviewPayload(BaseModel):
    thread_id: str
    approve: bool
    comment: str = ""

# =====================================================================
# 2. API Endpoint รับสัญญาณการตัดสินใจจากมนุษย์ (Task 4.2)
# =====================================================================
@app.post("/api/agent/review")
async def review_agent_workflow(payload: ReviewPayload):
    try:
        # ระบุโครงสร้าง Config เพื่อเข้าถึง Thread ที่ติด Interrupt อยู่ใน MemorySaver
        config = {"configurable": {"thread_id": payload.thread_id}}
        
        # 1. ตรวจสอบสถานะปัจจุบันของ Workflow ใน Thread นั้น ๆ
        current_state = runtime_workflow.get_state(config)
        if not current_state.next:
            raise HTTPException(
                status_code=400, 
                detail="ไม่พบสถานะที่รอการอนุมัติ (Interrupt) ใน Thread นี้ หรือระบบทำงานสิ้นสุดแล้ว"
            )
        
        # 2. ทำการอัปเดตค่า (Update State) สิทธิ์การตัดสินใจของมนุษย์กลับเข้าไปที่วัตถุกลาง
        # เนื่องจากเปลี่ยนไปใช้ Pydantic BaseModel ในโมดูลหลัก จึงสามารถส่งค่าดิกชันนารีอัปเดตตรง ๆ ได้
        runtime_workflow.update_state(
            config, 
            {
                "is_approved": payload.approve, 
                "review_comment": payload.comment
            },
            as_node="dev_boilerplate"
        )
        
        # 3. สั่งให้ระบบ LangGraph ปลดล็อกและเดินหน้าทำงานต่อไปยังขั้นตอนถัดไปทันที
        # (ส่งผ่าน None เพื่อบอกให้ดึงข้อมูลจากจุด Checkpoint ล่าสุดขึ้นมาวิ่งต่อเข้า Node ถัดไป)
        runtime_workflow.stream(None, config)
        
        return {
            "status": "success", 
            "action_taken": "APPROVED" if payload.approve else "REJECTED",
            "thread_id": payload.thread_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))