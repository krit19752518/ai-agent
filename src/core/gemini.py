import os
import json
from typing import Optional, Any, Union
from google import genai
from google.genai import types
from src.config import Config

class GeminiCore:
    """
    Wrapper class for Google Gemini 2.5 APIs.
    Configured specifically for Agent operations using a low temperature (default 0.1) to enforce deterministic logic.
    """
    def __init__(self):
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            # Fallback to look directly at env if Config not initialized
            api_key = os.getenv("GEMINI_API_KEY")
            
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set it in your environment variables or .env file."
            )
        # Initialize GenAI Client
        self.client = genai.Client(api_key=api_key)

    def call_reasoning_model(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None, 
        temperature: float = 0.1,
        response_mime_type: Optional[str] = None,
        response_schema: Optional[Any] = None
    ) -> Any:  # 👈 เปลี่ยนจาก str เป็น Any เพราะฟังก์ชันนี้คืนค่าได้ทั้ง dict, list, และ str
        """
        Uses 'gemini-2.5-pro' for tasks requiring high reasoning capabilities,
        such as logical conflict checking (BA Agent) or architecture review (SA Agent).
        """
        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
            response_mime_type=response_mime_type,
            response_schema=response_schema
        )
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            
            # ดึง Text ออกมาอย่างปลอดภัย และเซ็ตเป็น String เปล่าถ้ากรณีหลุดเป็น None
            raw_text = response.text if response.text is not None else ""
            
            # ถ้าผู้ใช้งานระบุว่าต้องการ JSON ให้แปลงจาก String เป็น Python Dict ทันที
            if response_mime_type == "application/json":
                return json.loads(raw_text)
                
            return raw_text
        except Exception as e:
            return f"Error executing Gemini 2.5 Pro: {str(e)}"

    def call_fast_model(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None, 
        temperature: float = 0.1
    ) -> str:  # 👈 ตัวนี้ยังคงเป็น str ปลอดภัย
        """
        Uses 'gemini-2.5-flash' for high-throughput, latency-sensitive tasks
        such as code boilerplates generation (Dev Agent) or log analysis (DevOps Agent).
        """
        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction
        )
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            
            # ป้องกันปัญหา 'str | None' ไม่ตรงกับ Return Type 'str' ด้วยการ fallback ใส่ ""
            return response.text if response.text is not None else ""
        except Exception as e:
            return f"Error executing Gemini 2.5 Flash: {str(e)}"