"""Configuration for Isabl MCP Server."""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """MCP Server settings loaded from environment variables."""

    # Isabl API configuration
    isabl_api_url: str = "http://localhost:8000/api/v1/"
    isabl_api_token: str = ""

    # Optional paths to app repositories (for search_apps, explain_app)
    isabl_apps_path: Optional[str] = None
    shahlab_apps_path: Optional[str] = None

    # HTTP client settings
    verify_ssl: bool = True
    timeout: int = 30

    # Logging
    log_level: str = "INFO"

    model_config = {
        "env_prefix": "ISABL_",
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
