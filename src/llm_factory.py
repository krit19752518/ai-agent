import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# โหลดค่าจากไฟล์ .env
load_dotenv()

def get_agent_llm(provider: str = "groq"):
    """
    Factory function สำหรับเลือกค่าย AI 
    รองรับ: 'gemini', 'groq', 'openrouter', 'cohere'
    """
    print(f"[LLM Factory] กำลังเรียกใช้โมเดลจากค่าย: {provider.upper()}")
    
    if provider == "gemini":
        try:
            # ทดสอบเรียกใช้ Gemini (ถ้าโควตาเต็ม จะเด้งไปตกลงที่ Exception)
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.2
            )
        except Exception as e:
            print(f"⚠️ [WARNING] Gemini ของคุณโควตาเต็มหรือเกิดข้อผิดพลาด: {e}")
            print("🔄 [FAILOVER] ระบบกำลังสลับไปใช้ Groq อัตโนมัติ...")
            provider = "groq" # สลับค่ายอัตโนมัติ
            
    if provider == "groq":
        return ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_DEFAULT_MODEL", "llama3-8b-8192"),
            temperature=0.2
        )
        
    if provider == "openrouter":
        return ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            model=os.getenv("OPENROUTER_DEFAULT_MODEL", "meta-llama/llama-3-8b-instruct:free"),
            temperature=0.2
        )
        
    if provider == "cohere":
        # สำหรับ Cohere สามารถใช้ OpenAI-compatible หรือฐานของตัวมันเองได้
        return ChatOpenAI(
            openai_api_base="https://api.cohere.ai/v1",
            openai_api_key=os.getenv("COHERE_API_KEY"),
            model=os.getenv("COHERE_DEFAULT_MODEL", "command-light"),
            temperature=0.2
        )
        
    raise ValueError(f"ไม่รู้จักค่าย AI ที่ระบุ: {provider}")