import os
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with Pydantic validation."""
    
    # API
    api_title: str = "Process Verifier"
    api_version: str = "1.0.0"
    api_description: str = "LLM-powered verification system for judicial process eligibility"
    environment: Literal["development", "production", "testing"] = "development"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Groq API (ChatGPT)
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_MODEL")
    max_tokens: int = 2000
    
    
    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project_name: str = "juscash-verifier"
    enable_langsmith: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Database (TODO: Implement)
    database_url: str = "sqlite:///./juscash.db"
    
    # Limits
    max_batch_size: int = 50
    max_request_timeout: int = 30
    
    # Policy (TODO: Implement)
    min_valor_condenacao: float = 1000.00
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global instance
settings = Settings()