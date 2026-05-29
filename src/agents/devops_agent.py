import os
from google import genai
from google.genai import types
from src.utils.log_extractor import extract_critical_logs
from src.config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)

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
    raw_logs = state.raw_logs if hasattr(state, "raw_logs") else ""
    optimized_logs = extract_critical_logs(raw_logs)

    # ดึงค่า Max Token สำรองไว้ ถ้าไม่มีให้สติ๊กที่ 200 (ปรับปรุงสำหรับ Task 5.2)
    max_tokens = int(os.getenv("MAX_OUTPUT_TOKENS", 200))


    if not Config.GEMINI_API_KEY or os.getenv("DATABASE_MODE") == "mock":
        return {"devops_analysis": get_placeholder_analysis(), "optimized_logs": optimized_logs}

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"โปรดวิเคราะห์สแต็กเทรซนี้:\n\n{optimized_logs}",
            config=types.GenerateContentConfig(
                system_instruction=DEVOPS_SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=max_tokens # บีบ Token ขาออกตามกฎกติกาประหยัดพลังงาน
            )
        )
        if not response.text:
            return {"devops_analysis": get_placeholder_analysis(), "optimized_logs": optimized_logs}
        return {"devops_analysis": response.text, "optimized_logs": optimized_logs}
        
    except Exception as e:
        return {"devops_analysis": get_placeholder_analysis(), "optimized_logs": optimized_logs}

def get_placeholder_analysis() -> str:
    return """## ❌ สาเหตุที่พัง
- CI ล้มเหลวเนื่องจากการเชื่อมต่อฐานข้อมูล (Port 5432, localhost) ไม่สำเร็จในโหมดจำลอง

## 🛠️ วิธีแก้ไขที่แนะนำ
- ตรวจสอบการตั้งค่าฐานข้อมูลในระบบ หรือสลับขั้วไปใช้งานแบบ Mock DB (In-memory) แทน"""