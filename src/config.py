import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Linear
    LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
    
    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    
    # PostgreSQL Read-only Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    @classmethod
    def validate_keys(cls) -> dict:
        """Helper function to validate which keys are missing."""
        missing = {}
        if not cls.GEMINI_API_KEY:
            missing["GEMINI_API_KEY"] = "Missing Gemini API Key"
        if not cls.LINEAR_API_KEY:
            missing["LINEAR_API_KEY"] = "Missing Linear API Key (Linear MCP tool might fail)"
        if not cls.GITHUB_TOKEN:
            missing["GITHUB_TOKEN"] = "Missing GitHub Token (GitHub MCP tool might fail)"
        return missing
