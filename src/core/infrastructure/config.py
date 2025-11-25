"""
Configuration and environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "Judicial Process Verification Engine"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "LLM-powered verification system for judicial process eligibility"
    DEBUG: bool = False
    
    # LLM Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    
    # LangSmith Configuration
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "judicial-process-verification"
    LANGSMITH_ENABLED: bool = False
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

