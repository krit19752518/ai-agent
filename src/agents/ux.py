import json
import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from src.core.gemini import GeminiCore

# 1. Pydantic schema for UI State Spec
class UIStateDetail(BaseModel):
    state_name: str = Field(description="ชื่อสถานะการทำงาน: Happy Path, Empty State, Loading State, หรือ Error State")
    behavior_description: str = Field(description="อธิบายรูปแบบการทำงานและพฤติกรรมของหน้าจอในสถานะนี้เป็นภาษาไทย")
    suggested_components: List[str] = Field(default=[], description="รายชื่อ UI Components ที่สามารถนำกลับมาใช้ซ้ำได้จาก Storybook")
    components_to_create: List[str] = Field(default=[], description="รายชื่อ UI Components ย่อยใหม่ที่ต้องพัฒนาเพิ่มเติม")

class UISpecReportSchema(BaseModel):
    page_name: str = Field(description="ชื่อหน้าจอ หรือฟังก์ชันการทำงานระบบ")
    states: List[UIStateDetail] = Field(default=[], description="รายการวิเคราะห์พฤติกรรมแยกออกเป็น 4 มิติสถานะ")


UX_SYSTEM_INSTRUCTION = """
You are a Senior UX/UI Engineer Agent.
Your job is to analyze functional software requirements and translate them into a clear UI State Specification.

Specifically:
1. Map the screen behavior into 4 core UI States:
   - Happy Path (Normal execution and success screen)
   - Empty State (Screen behavior when no data is returned or initial state)
   - Loading State (Screen behavior during network requests or data loading)
   - Error State (Screen behavior when validation fails, permissions are denied, or network fails)
2. Match the needed elements to existing UI components in our Storybook catalog. Suggest reuse where possible.
3. If no matching component exists, list it in 'components_to_create'.

Respond strictly in the requested JSON format, using clear and professional Thai for all descriptions.
"""

def read_storybook_metadata() -> str:
    """
    Parses and returns Storybook components metadata JSON, or fallback defaults if not found.
    """
    rules_path = "d:/AI-AgentProject/storybook_metadata.json"
    if os.path.exists(rules_path):
        try:
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False)
        except Exception:
            pass

    # Default mock components representation to guide reuse
    mock_components = [
        {"name": "Button", "type": "Atom", "description": "Standard action button"},
        {"name": "InputField", "type": "Atom", "description": "Form text input with validation support"},
        {"name": "LoadingSpinner", "type": "Atom", "description": "Animated loading spinner indicator"},
        {"name": "AlertCallout", "type": "Molecule", "description": "Alert notification banner for success/warning/error states"},
        {"name": "EmptyStatePlaceholder", "type": "Molecule", "description": "Default placeholder graphic and text for empty lists"},
        {"name": "AuthCard", "type": "Organism", "description": "Structured card wrapper for credentials entry forms"}
    ]
    return json.dumps(mock_components, ensure_ascii=False)

def review_ui_spec(new_requirement: str) -> Dict[str, Any]:
    """
    UX Agent analyzes requirements and maps them to UI states and Storybook components.
    Uses 'gemini-2.5-flash' via the reasoning wrapper.
    """
    gemini = GeminiCore()
    storybook_components = read_storybook_metadata()

    prompt = f"""
Please analyze the following requirement and map its UI behaviors into 4 states.
Cross-reference the needed UI elements with our available Storybook Components to suggest reuse.

[Available Storybook Components]:
{storybook_components}

[New Requirement to Analyze]:
{new_requirement}
"""

    try:
        response_data = gemini.call_reasoning_model(
            prompt=prompt,
            system_instruction=UX_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=UISpecReportSchema
        )
        if isinstance(response_data, str):
            raise ValueError(response_data)
        return response_data
    except Exception as e:
        return {
            "page_name": "UX Agent Error",
            "states": [{
                "state_name": "System Error",
                "behavior_description": f"UX Agent ไม่สามารถวิเคราะห์ได้เนื่องจากระบบคอร์เกิดข้อขัดข้อง: {str(e)}",
                "suggested_components": [],
                "components_to_create": []
            }]
        }
