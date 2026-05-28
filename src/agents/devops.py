import re
from typing import Dict, Any
from pydantic import BaseModel, Field
from src.core.gemini import GeminiCore

# 1. กำหนดรูปแบบรายงานการวิเคราะห์ Log ที่คืนกลับมาจาก Gemini
class DevOpsLogAnalysisSchema(BaseModel):
    is_build_fixed: bool = Field(description="ระบุว่าเป็น True หากมีแนวทางแก้ไขที่ชัดเจน, False หากข้อมูลไม่เพียงพอ")
    root_cause: str = Field(description="สาเหตุหลักที่ทำให้ Build หรือระบบพัง (ภาษาไทย)")
    suggested_fix: str = Field(description="คำแนะนำและขั้นตอนการแก้ไขโค้ดฉบับภาษาไทยเข้าใจง่าย (ภาษาไทย)")


DEVOPS_SYSTEM_INSTRUCTION = """
You are an expert DevOps and Site Reliability Engineer (SRE) Agent. 
Your role is to analyze compressed application logs, stack traces, and CI/CD build failures.

You will receive a stripped log containing only the failure context. 
Your job is to identify the exact line of failure, explain the root cause clearly, and provide actionable, easy-to-understand step-by-step remediation commands or code fixes in Thai.
"""

def strip_raw_log(raw_log: str, max_lines_around_error: int = 5) -> str:
    """
    [Human Task] Log Stripper Function
    สแกนหากลุ่มคำวิกฤต (Error/Exception/Failure) และดักจับ Stack Trace 
    ช่วยลดสัญญาณรบกวน (Noise) และประหยัด Token ได้มากกว่า 80%
    """
    if not raw_log:
        return "No log content provided."

    lines = raw_log.splitlines()
    important_lines = []
    
    # มองหารูปแบบข้อความผิดพลาดที่พบบ่อยใน Software Development
    error_patterns = [
        re.compile(r"error", re.IGNORECASE),
        re.compile(r"exception", re.IGNORECASE),
        re.compile(r"failed", re.IGNORECASE),
        re.compile(r"traceback", re.IGNORECASE),
        re.compile(r"caused by", re.IGNORECASE),
        re.compile(r"at \S+\.\S+\(.*:\d+\)") # Pattern สไตล์ Java/Node Stack Trace
    ]
    
    matched_indices = set()
    for idx, line in enumerate(lines):
        if any(pattern.search(line) for pattern in error_patterns):
            # เก็บดัชนีบรรทัดรอบ ๆ ข้อความที่พังเพื่อไม่ให้เสียบริบท (Context Window)
            start = max(0, idx - 2)
            end = min(len(lines), idx + max_lines_around_error)
            for i in range(start, end):
                matched_indices.add(i)
                
    if not matched_indices:
        # หากไม่เจอ Pattern เลย ให้ดึง 15 บรรทัดสุดท้ายมาวิเคราะห์ (มักเป็นจุดที่ CI ตัดจบ)
        return "\n".join(lines[-15:])
        
    # จัดเรียงบรรทัดกลับคืนมา
    for idx in sorted(matched_indices):
        important_lines.append(lines[idx])
        
    return "\n".join(important_lines)


def analyze_ci_build_log(raw_build_log: str) -> Dict[str, Any]:
    """
    ฟังก์ชันเรียกใช้งาน DevOps Agent: ทำความสะอาด Log ก่อนแล้วค่อยส่งให้ Gemini ประมวลผล
    """
    # 1. ทำความสะอาด Log ผ่านระบบคัดกรองของมนุษย์ล่วงหน้าเพื่อเซฟ Token
    stripped_context = strip_raw_log(raw_build_log)
    
    gemini = GeminiCore()
    prompt = f"""
Please review this stripped CI/CD build failure log and provide a root cause analysis with a fix strategy.

[Stripped Failure Log]:
{stripped_context}
"""
    try:
        return gemini.call_reasoning_model(
            prompt=prompt,
            system_instruction=DEVOPS_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=DevOpsLogAnalysisSchema
        )
    except Exception as e:
        return {
            "is_build_fixed": False,
            "root_cause": f"DevOps Agent ไม่สามารถวิเคราะห์ Log ได้เนื่องจาก: {str(e)}",
            "suggested_fix": "กรุณาตรวจสอบสถานะเครือข่ายหรือตรวจสอบโค้ด Log ด้วยตนเอง"
        }