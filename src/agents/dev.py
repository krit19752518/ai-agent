import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from src.core.gemini import GeminiCore

# 1. Pydantic Schema for structured code outputs
class GeneratedCodeFile(BaseModel):
    file_path: str = Field(
        description="Relative target directory path of the file (e.g., 'src/controllers/auth_controller.py')"
    )
    code_content: str = Field(
        description="Full, functional, production-ready Python source code. Absolutely NO placeholders or ellipsis (...)."
    )

class DevAgentOutputSchema(BaseModel):
    generated_files: List[GeneratedCodeFile] = Field(
        default=[], 
        description="A list of generated source code files (exactly 1 Controller, 1 Service, and 1 Unit Test file)."
    )


DEV_SYSTEM_INSTRUCTION = """
You are a Senior Software Developer Agent.
Your job is to generate clean, PEP8-compliant, and functional Python code based on a target feature requirement, API Spec, and codebase structure.

For the target feature, you must generate exactly three files:
1. **Controller File**: Handles HTTP routing, input validation, calls the Service layer, and returns standardized JSON responses.
2. **Service File**: Houses the core business logic.
3. **Unit Test File**: Tests the controller and service functionality using Python's `unittest` module, mocking external calls where necessary.

Coding Guidelines:
- Follow standard Python naming conventions.
- Implement comprehensive error handling (try-except blocks) and HTTP status codes.
- Do not use placeholders like '# TODO' or 'pass' or '...'. Write complete code.
- Respond strictly in the requested JSON format, using clear and professional Thai for code comments.
"""

def generate_code_files(api_spec: str, repo_structure: str, feature_desc: str) -> Dict[str, Any]:
    """
    Generates Controller, Service, and Unit Test files based on the specified feature description,
    API specifications, and repo directory layout.
    Uses 'gemini-2.5-flash' via the reasoning wrapper.
    """
    gemini = GeminiCore()

    prompt = f"""
Please generate the required boilerplate code files (Controller, Service, Unit Test) for the following feature.

[Feature Description]:
{feature_desc}

[Target API Specification]:
{api_spec if api_spec else "No API spec provided. Please design based on the feature requirements."}

[Current Repository Layout]:
{repo_structure if repo_structure else "No structure provided."}
"""

    try:
        # call_reasoning_model was configured by the user to use gemini-2.5-flash and supports JSON schemas
        response_data = gemini.call_reasoning_model(
            prompt=prompt,
            system_instruction=DEV_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=DevAgentOutputSchema
        )
        if isinstance(response_data, str):
            raise ValueError(response_data)
        return response_data
    except Exception as e:
        return {
            "generated_files": [{
                "file_path": "error.py",
                "code_content": f"# Dev Agent failed to generate code files: {str(e)}"
            }]
        }
