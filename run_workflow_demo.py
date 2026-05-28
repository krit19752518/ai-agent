import asyncio
from src.workflow import app, AgentState

async def main():
    # 1. ป้อนข้อมูลเพื่อทดสอบเริ่มต้นสายพานซอฟต์แวร์
    init_state = AgentState(
        jira_ticket_id="ANTG-777",
        raw_requirement="ต้องการเพิ่มระบบล็อกอินและระบบบันทึก Log สำหรับผู้ดูแลระบบ",
        raw_logs="ERROR: localhost port 5432 connection refused error trace in database.py line 42"
    )
    
    config = {"configurable": {"thread_id": "sprint-demo-thread"}}
    
    print("🚀 [1/3] เริ่มรันระบบจำลองการทำงาน Multi-Agent...")
    async for event in app.astream(init_state, config=config, stream_mode="values"):
        current_node = event
        
    # 2. ตรวจสอบสถานะการตกค้าง (หยุดรอการอนุมัติจากมนุษย์ที่ Governance Gateway)
    snapshot = await app.aget_state(config)
    if snapshot.next:
        print("\n🚨 [🚨 SYSTEM INTERRUPTED BY GOVERNANCE GATEWAY]")
        print(f"-> สายพานจอดสนิทหน้าโหนด: {snapshot.next}")
        print("-> ผลลัพธ์ Downstream ล่าสุดที่รวบรวมมาได้:")
        print(snapshot.values.get("downstream_report"))
        
        print("\n⌨️ [Human Reaction] มนุษย์ตรวจสอบแล้วพิมพ์ 'y' เพื่อกดอนุมัติ (Approve) ขึ้นโปรดักชัน: ")
        # จำลองการตรวจสอบแบบ Interactive
        user_input = "y" # บังคับกดตกลงอัตโนมัติสำหรับการสคริปต์ Demo
        print(f"(Auto-Selected: {user_input})")
        
        if user_input.lower() == 'y':
            print("\n🏁 [3/3] สั่งงานให้ระบบรับผลการตัดสินใจ และทำงานสเต็ปสุดท้าย...")
            
            # 💡 แก้ไขจุดนี้: กำหนดค่าเริ่มต้นเป็น Dictionary ว่างนอกลูป 
            # เพื่อการันตีความปลอดภัยและเคลียร์เออร์เรอร์ "final_output may be uninitialized"
            final_output = {}
            
            # ส่งค่า None เข้าไปเพื่อปล่อยตัวเบรกเกอร์ (Interrupt) ให้กราฟวิ่งไปทำงานต่อ
            async for event in app.astream(None, config=config, stream_mode="values"):
                final_output = event
            
            print("\n🏆 == สรุปผลรายงานความเสี่ยง (Final Risk Radar Report) == 🏆")
            print(final_output.get("risk_radar_report", "ไม่สามารถดึงรายงานความเสี่ยงได้"))
        else:
            print("❌ ยกเลิกและสั่งตีกลับงาน (Rejected!)")

if __name__ == "__main__":
    asyncio.run(main())