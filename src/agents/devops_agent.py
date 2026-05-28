import os
from google import genai
from google.genai import types
from src.utils.log_extractor import extract_critical_logs

# เริ่มต้นใช้งาน Gemini Client
client = genai.Client()

DEVOPS_SYSTEM_INSTRUCTION = """
คุณคือ DevOps Agent ผู้เชี่ยวชาญด้าน CI/CD และ Log Analysis
หน้าที่ของคุณคือรับ Stack Trace ที่พังมาจากระบบ CI จากนั้นวิเคราะห์หา "สาเหตุที่แท้จริง (Root Cause)"

ให้ตอบกลับเป็นภาษาไทยที่เข้าใจง่าย กระชับสั้นที่สุด โดยใช้รูปแบบโครงสร้างต่อไปนี้:
## ❌ สาเหตุที่พัง
(สรุปสั้นๆ 1-2 บรรทัดว่าอะไรพัง และเกิดที่ไฟล์ไหน/บรรทัดไหน)

## 🛠️ วิธีแก้ไขที่แนะนำ
* (ข้อเสนอแนะในการแก้โค้ดหรือคอนฟิกที่ทีมนำไปกดทำตามได้ทันที เป็นข้อๆ)

ข้อกำหนดเคร่งครัด: ห้ามเกริ่นนำ ห้ามพูดทฤษฎียาวๆ เน้น Actionable Insight เท่านั้น
"""

def devops_log_analyzer_node(state) -> dict:
    """
    LangGraph Node สำหรับวิเคราะห์ Log ที่พัง
    ดึงข้อมูลดิบผ่านแอตทริบิวต์ของ Pydantic State ตัวกลาง
    """
    # ดึงค่าจาก Pydantic Object
    raw_logs = getattr(state, "raw_logs", "")

    # รันสคริปต์สกัด Log เพื่อลด Token และตัด Noise ออกไป 80%
    optimized_logs = extract_critical_logs(raw_logs)

    # ส่งให้ Gemini 2.5 Flash ประมวลผลอย่างรวดเร็ว
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"โปรดวิเคราะห์สแต็กเทรซนี้:\n\n{optimized_logs}",
        config=types.GenerateContentConfig(
            system_instruction=DEVOPS_SYSTEM_INSTRUCTION,
            temperature=0.2
        )
    )

    # ส่งผลลัพธ์กลับคืนไปอัปเดตค่าใน LangGraph State ตามคีย์ที่กำหนดไว้
    return {
        "devops_analysis": response.text
    }