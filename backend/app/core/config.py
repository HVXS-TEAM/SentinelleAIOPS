import os
from pydantic_settings import BaseSettings
from typing import Optional

# Fixed absolute path to database file inside backend/ directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_FILE = os.path.join(BASE_DIR, "sentinelle_aiops.db").replace("\\", "/")


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinelle AIOps"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database URL
    DATABASE_URL: str = f"sqlite:///{DB_FILE}"
    
    # Security
    SECRET_KEY: str = "sentinelle_aiops_super_secret_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Ollama LLM Config
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
