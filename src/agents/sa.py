import json
import os
from typing import Dict, Any
from pydantic import BaseModel, Field
from src.core.gemini import GeminiCore

# 1. กำหนดโครงสร้างรายงานตรวจสถาปัตยกรรมสำหรับส่งต่อในระบบ Pipeline
class ArchitectureComplianceDetail(BaseModel):
    rule_category: str = Field(description="หมวดหมู่ของกฎที่ละเมิด เช่น folder_structure, naming_conventions, api_standards")
    violation_detected: str = Field(description="อธิบายจุดที่ข้อกำหนดใหม่ละเมิดกฎสถาปัตยกรรมระบบเป็นภาษาไทย")
    suggested_fix: str = Field(description="คำแนะนำในการแก้ไขให้ถูกต้องตามมาตรฐานของทีมเป็นภาษาไทย")

class ArchitectureReportSchema(BaseModel):
    is_compliant: bool = Field(description="เป็น True ถ้าข้อกำหนดนั้นทำตามกฎสถาปัตยกรรมทุกประการ, เป็น False ถ้ามีจุดที่ละเมิดกฎ")
    violations: list[ArchitectureComplianceDetail] = Field(default=[], description="รายการจุดที่ละเมิดกฎสถาปัตยกรรม")


SA_SYSTEM_INSTRUCTION = """
You are an expert System Architect (SA) Agent. Your role is to enforce code and architectural guidelines.
You will receive a New Requirement and a set of strict Architecture Rules.
Your job is to cross-reference them and find any design violations, wrong naming conventions, or illegal API designs.

Respond strictly in the requested JSON format, using clear and precise Thai for explanations.
"""

def review_architecture_compliance(new_requirement: str) -> Dict[str, Any]:
    """
    SA Agent โลดยกฎสถาปัตยกรรมจาก JSON มาตรวจจับข้อกำหนดใหม่แบบ Dynamic Context (ประหยัด Token)
    """
    gemini = GeminiCore()
    
    # ดึง Context จากไฟล์ที่เราสร้างผ่าน PowerShell
    rules_path = "d:/AI-AgentProject/architecture_rules.json"
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8-sig") as f:
            arch_rules = json.load(f)
            arch_rules_str = json.dumps(arch_rules, ensure_ascii=False)
    else:
        arch_rules_str = "No specific architecture rules defined."

    prompt = f"""
Please audit the following New Requirement against our strict Architecture Rules.
Identify if there are any naming mismatches, improper layer placements, or invalid API responses.

[Strict Architecture Rules]:
{arch_rules_str}

[New Requirement to Audit]:
{new_requirement}
"""

    try:
        response_data = gemini.call_reasoning_model(
            prompt=prompt,
            system_instruction=SA_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ArchitectureReportSchema
        )
        if isinstance(response_data, str):
            raise ValueError(response_data)
        return response_data
    except Exception as e:
        return {
            "is_compliant": False,
            "violations": [{
                "rule_category": "System Error",
                "violation_detected": f"SA Agent ไม่สามารถรันการตรวจเช็กได้: {str(e)}",
                "suggested_fix": "ตรวจสอบการเชื่อมต่อระบบคอร์"
            }]
        }