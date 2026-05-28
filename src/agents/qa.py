import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from src.core.gemini import GeminiCore

# 1. Pydantic Schema for structured QA outputs
class TestCaseDetail(BaseModel):
    test_id: str = Field(
        description="รหัสเฉพาะสำหรับชุดทดสอบ เช่น TC-001, TC-002"
    )
    dimension: str = Field(
        description="มิติการทดสอบ: Happy Path, Unhappy Path, Edge Case, หรือ RBAC Access Control"
    )
    description: str = Field(
        description="คำอธิบายรายละเอียดกรณีการทดสอบ เช่น 'ตรวจสอบการกรอกรหัสผ่านผิดเกิน 3 ครั้ง' เป็นภาษาไทย"
    )
    preconditions: str = Field(
        description="เงื่อนไขก่อนการเริ่มทดสอบ (Pre-conditions) เป็นภาษาไทย"
    )
    steps: List[str] = Field(
        default=[], 
        description="ขั้นตอนการทำงานของเทสเคสทีละสเตป เป็นภาษาไทย"
    )
    expected_result: str = Field(
        description="ผลลัพธ์ที่คาดหวังว่าระบบจะตอบสนอง เช่น 'ระบบบล็อกบัญชีชั่วคราวและส่งโค้ด 401' เป็นภาษาไทย"
    )

class QATestMatrixSchema(BaseModel):
    feature_name: str = Field(
        description="ชื่อของคุณสมบัติระบบหรือ API ที่ทำการทดสอบ"
    )
    test_cases: List[TestCaseDetail] = Field(
        default=[], 
        description="รายการชุดเทสเคสทั้งหมดที่ถูกแยกตามมิติการทดสอบ"
    )


QA_SYSTEM_INSTRUCTION = """
You are an expert QA Manager and Lead QA Engineer Agent.
Your job is to design a robust, comprehensive Test Matrix based on system requirements and API specifications.

You must design test scenarios spanning exactly four key dimensions:
1. **Happy Path**: Verifies normal user journeys, valid entries, and successful outcomes.
2. **Unhappy Path**: Verifies expected system errors, validation failures, and invalid credentials response.
3. **Edge Case**: Verifies system boundaries (empty inputs, string length limits, special characters, zero values).
4. **RBAC Access Control**: Verifies access permissions (e.g. anonymous access blocked, scope validation, role limitations).

Write clear, objective test cases. Respond strictly in the requested JSON format, using clear and professional Thai for all descriptions.
"""

def generate_test_matrix(requirement: str, api_spec: str = "") -> Dict[str, Any]:
    """
    Generates a structured test matrix from the provided requirement and API specifications.
    Uses 'gemini-2.5-flash' via the reasoning wrapper.
    """
    gemini = GeminiCore()

    prompt = f"""
Please design a detailed Test Matrix containing test cases across the 4 key dimensions for this requirement.

[System Requirement]:
{requirement}

[API Specification (Optional)]:
{api_spec if api_spec else "No API spec provided."}
"""

    try:
        # call_reasoning_model is bound to gemini-2.5-flash and handles response_schema
        response_data = gemini.call_reasoning_model(
            prompt=prompt,
            system_instruction=QA_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=QATestMatrixSchema
        )
        if isinstance(response_data, str):
            raise ValueError(response_data)
        return response_data
    except Exception as e:
        return {
            "feature_name": "QA Agent Error",
            "test_cases": [{
                "test_id": "TC-ERROR",
                "dimension": "System Error",
                "description": f"QA Agent ไม่สามารถสร้างตารางการทดสอบได้: {str(e)}",
                "preconditions": "Core system is operational",
                "steps": ["ตรวจสอบ API Connection"],
                "expected_result": "ระบบแกนหลักสามารถเชื่อมต่อได้สำเร็จ"
            }]
        }
