"""Configuration for Isabl MCP Server."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """MCP Server settings loaded from environment variables.

    Environment variables:
        ISABL_API_URL: Isabl API base URL
        ISABL_API_TOKEN: Authentication token
        ISABL_VERIFY_SSL: Whether to verify SSL certificates
        ISABL_TIMEOUT: HTTP request timeout in seconds
        ISABL_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    # Isabl API configuration
    api_url: str = "http://localhost:8000/api/v1/"
    api_token: str = ""

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

    # Convenience properties for backwards compatibility
    @property
    def isabl_api_url(self) -> str:
        return self.api_url

    @property
    def isabl_api_token(self) -> str:
        return self.api_token


settings = Settings()
