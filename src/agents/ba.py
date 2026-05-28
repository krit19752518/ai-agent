import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from core.gemini import GeminiCore

# 1. กำหนด Pydantic Schema โครงสร้างที่ระบบส่วนกลางต้องการ
class ConflictDetail(BaseModel):
    location: str = Field(description="ระบุตำแหน่งของไฟล์, ตารางฐานข้อมูล, หรือตั๋วงานเก่าที่เกิดความขัดแย้ง")
    reason: str = Field(description="อธิบายเหตุผลความขัดแย้งทางตรรกะ หรือช่องโหว่ที่พบอย่างละเอียดเป็นภาษาไทย")

class ConflictReportSchema(BaseModel):
    has_conflict: bool = Field(description="เป็น True หากพบความขัดแย้ง ตรรกะบกพร่อง หรือช่องโหว่ในข้อกำหนด")
    conflicts: List[ConflictDetail] = Field(default=[], description="รายการความขัดแย้งที่ตรวจพบทั้งหมด")


BA_SYSTEM_INSTRUCTION = """
You are an expert Business Analyst (BA) Agent with outstanding critical thinking and logical reasoning skills.
Your primary role is to audit and analyze incoming software requirements to detect contradictions, logical fallacies, ambiguities, or incompatibilities when compared to existing features, history, and specifications.

Approach requirements with a critical eye:
1. **Identify Contradictions**: Check if the new requirement directly conflicts with previous system specs or tickets.
2. **Detect Gaps / Omissions**: Point out missing details necessary for execution.
3. **Expose Workflow/Logical Inconsistencies**: Highlight illogical state transitions or impossible conditional branches.

You MUST respond strictly in the requested JSON schema format. Keep descriptions objective and written in Thai.
"""

def check_conflicts(new_requirement: str, historical_context: List[str]) -> Dict[str, Any]:
    """
    Compares a new requirement against previous context/tickets using gemini-2.5-pro.
    Enforces a strict structured JSON output format.
    
    Args:
        new_requirement: The new feature specification text.
        historical_context: A list of previously compiled tickets, database schema maps, or PR diffs.
        
    Returns:
        A dictionary matching: { "has_conflict": bool, "conflicts": [ { "location": str, "reason": str } ] }
    """
    # Initialize the reasoning model wrapper
    gemini = GeminiCore()

    # Format history context
    if historical_context:
        history_str = "\n\n".join(
            [f"--- Historical Item {idx+1} ---\n{item}" for idx, item in enumerate(historical_context)]
        )
    else:
        history_str = "No historical context available."

    prompt = f"""
Please perform a rigorous conflict analysis between the following New Requirement and the Historical Context.
Analyze it item by item based on your system instructions.

[New Requirement]:
{new_requirement}

[Historical Context]:
{history_str}
"""
    
    try:
        # เรียกใช้โมเดลโดยส่งข้อมูลโครงสร้าง Schema เข้าไปด้วยแบบปลอดภัย
        response_data = gemini.call_reasoning_model(
            prompt=prompt, 
            system_instruction=BA_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ConflictReportSchema
        )
        
        # ป้องกันกรณีเกิด Error string หลุดมาจาก exception ในระดับคอร์
        if isinstance(response_data, str):
            raise ValueError(response_data)
            
        return response_data
        
    except Exception as e:
        # Fallback ปลอดภัยหากเกิดการขัดข้องทางเทคนิค
        return {
            "has_conflict": True,
            "conflicts": [
                {
                    "location": "BA Agent System Error",
                    "reason": f"เกิดข้อผิดพลาดภายในระบบในการประมวลผลข้อมูลโครงสร้าง: {str(e)}"
                }
            ]
        }