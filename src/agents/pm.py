import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.core.gemini import GeminiCore

def calculate_base_risk_score(priority: str, conflict_count: int, comment_count: int) -> float:
    """
    [Human Task] Basic mathematical formula to calculate baseline risk score (0-100%).
    This runs locally to save LLM tokens.
    Developers (Human) can edit and customize this formula as needed.
    """
    score = 0.0
    
    # Priority weight
    priority_lower = priority.lower()
    if "critical" in priority_lower:
        score += 50.0
    elif "high" in priority_lower:
        score += 30.0
    elif "medium" in priority_lower:
        score += 15.0
    else:  # low or default
        score += 5.0
        
    # Conflict weight
    score += conflict_count * 15.0
    
    # Comment weight
    score += comment_count * 5.0
    
    # Clamp to 0.0 - 100.0 (แก้ไขเพื่อลบคำเตือน unnecessary-type-conversion ของ Linter)
    return max(0.0, min(100.0, score))


class PMSprintRiskSchema(BaseModel):
    is_blocked: bool = Field(description="สถานะบล็อกหรือข้อพิพาทรุนแรง (True/False)")
    risk_level: str = Field(description="ระดับความเสี่ยง: Low, Medium, High, Critical")
    impact_analysis: str = Field(description="ผลกระทบต่อ Sprint / แผนงานหลัก (ภาษาไทย)")
    mitigation_plan: List[str] = Field(description="ข้อเสนอแนะในการแก้ไขปัญหาเพื่อลดความเสี่ยงเป็นหัวข้อย่อย (ภาษาไทย)")


PM_SYSTEM_INSTRUCTION = """
You are an expert Project Manager (PM) Agent specializing in Agile Sprint Risk Assessment (Sprint Risk Radar).
Your primary role is to analyze active project comments, developer logs, and conflict status to assess timeline risks and blockages.

Audit the comments for:
1. **Developer Disagreements / Deadlocks**: Developers debating implementation paths, causing delays.
2. **External Blockers**: Dependency delays, missing API credentials, unclarified specs.
3. **Scope Creep / Over-complexity**: Discussions that suggest the task is much larger than estimated.
4. **Severity**: Determine if the risk is Low, Medium, High, or Critical.

You MUST respond strictly in the requested JSON schema format. Keep descriptions objective and written in Thai.
"""


def analyze_sprint_risk(requirement: str, comment_logs: List[str], base_score: float) -> Dict[str, Any]:
    """
    Analyzes sprint risk using Gemini 2.5 and outputs a structured JSON report.
    Integrates the baseline mathematical score (base_score) with the AI analysis.
    
    Args:
        requirement: The current requirement description.
        comment_logs: List of developer comments/logs discussing the task.
        base_score: The mathematical risk score calculated by the human formula.
        
    Returns:
        A dictionary matching: {
            "is_blocked": bool,
            "risk_level": str,
            "impact_analysis": str,
            "mitigation_plan": list[str]
        }
    """
    gemini = GeminiCore()
    
    if comment_logs:
        comments_str = "\n".join([f"- {comment}" for comment in comment_logs])
    else:
        comments_str = "No developer comments available."
        
    prompt = f"""
Analyze the potential sprint risks and blockages based on the following requirement and developer discussion.

[Requirement]:
{requirement}

[Developer Discussions / Comments]:
{comments_str}

[Current Base Risk Score (Calculated Mathematically)]:
{base_score}%

Please perform a deep risk assessment and propose a mitigation plan.
"""
    
    try:
        response_data = gemini.call_reasoning_model(
            prompt=prompt,
            system_instruction=PM_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=PMSprintRiskSchema
        )
        
        if isinstance(response_data, str):
            raise ValueError(response_data)
            
        return response_data
        
    except Exception as e:
        # Safe fallback in case of Gemini issues or schema mismatch
        return {
            "is_blocked": base_score >= 50.0,
            "risk_level": "High" if base_score >= 50.0 else "Medium",
            "impact_analysis": f"การจำลองวิเคราะห์ความเสี่ยงล้มเหลวเนื่องจาก: {str(e)}",
            "mitigation_plan": [
                "ตรวจสอบการเชื่อมต่อกับ Gemini API หรือตรวจสอบความครบถ้วนของพารามิเตอร์",
                "ทีมควรเข้าตรวจสอบการประสานงานและสถานะตัวช่วยวิเคราะห์ความเสี่ยงด้วยตนเอง"
            ]
        }