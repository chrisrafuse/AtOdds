"""
API Configuration for AtOdds Web API
Phase 6: FastAPI REST API Layer - CR_ compliant configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class CR_Settings(BaseSettings):
    """CR_ compliant API settings"""

    # API Server Configuration
    CR_api_title: str = "AtOdds API"
    CR_api_version: str = "1.0"
    CR_api_description: str = "CR_ compliant odds analysis REST API"
    CR_api_host: str = "0.0.0.0"
    CR_api_port: int = 8000
    CR_api_workers: int = 4

    # CORS Configuration
    CR_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    CR_cors_allow_credentials: bool = True
    CR_cors_allow_methods: List[str] = ["*"]
    CR_cors_allow_headers: List[str] = ["*"]

    # Rate Limiting
    CR_rate_limit_default: str = "100/minute"
    CR_rate_limit_analyze: str = "10/minute"
    CR_rate_limit_upload: str = "5/minute"

    # File Upload Limits
    CR_max_upload_size_mb: int = 10
    CR_allowed_file_extensions: List[str] = [".json"]

    # Session Configuration
    CR_session_timeout_hours: int = 1
    CR_session_cleanup_interval_minutes: int = 15

    # Logging
    CR_log_level: str = "INFO"
    CR_log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "mock"           # openai | anthropic | gemini | mock
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Deployment
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = ""

    # Development Settings
    CR_debug_mode: bool = False
    CR_reload_on_change: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
CR_settings = CR_Settings()
