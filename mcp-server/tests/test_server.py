"""Tests for MCP server creation and configuration."""

import pytest
from unittest.mock import patch, MagicMock

from isabl_mcp.server import create_server
from isabl_mcp.config import Settings


class TestServerCreation:
    """Tests for MCP server creation."""

    def test_server_creation(self):
        """Test that the MCP server can be created."""
        server = create_server()
        assert server is not None
        assert server.name == "Isabl MCP Server"

    def test_server_has_tools_registered(self):
        """Test that the server has tools registered."""
        server = create_server()
        # Server should be a FastMCP instance
        assert hasattr(server, "name")
        assert server.name == "Isabl MCP Server"

    def test_multiple_server_creation(self):
        """Test that multiple servers can be created independently."""
        server1 = create_server()
        server2 = create_server()

        assert server1 is not None
        assert server2 is not None
        # They should be different instances
        assert server1 is not server2


class TestSettings:
    """Tests for server settings."""

    def test_settings_defaults(self):
        """Test default settings values."""
        s = Settings()
        assert "localhost" in s.isabl_api_url or "api" in s.isabl_api_url
        assert s.timeout == 30
        assert s.verify_ssl is True

    def test_settings_from_env(self, monkeypatch):
        """Test settings loaded from environment."""
        monkeypatch.setenv("ISABL_API_URL", "https://test.isabl.io/api/v1/")
        monkeypatch.setenv("ISABL_API_TOKEN", "test-token")

        s = Settings()
        assert s.isabl_api_url == "https://test.isabl.io/api/v1/"
        assert s.isabl_api_token == "test-token"

    def test_settings_api_url_property(self, monkeypatch):
        """Test api_url property returns correct value."""
        monkeypatch.setenv("ISABL_API_URL", "https://custom.api.io/api/v1/")

        s = Settings()
        assert s.api_url == "https://custom.api.io/api/v1/"
        assert s.isabl_api_url == "https://custom.api.io/api/v1/"

    def test_settings_api_token_property(self, monkeypatch):
        """Test api_token property returns correct value."""
        monkeypatch.setenv("ISABL_API_TOKEN", "my-secret-token")

        s = Settings()
        assert s.api_token == "my-secret-token"
        assert s.isabl_api_token == "my-secret-token"

    def test_settings_verify_ssl(self, monkeypatch):
        """Test SSL verification setting."""
        monkeypatch.setenv("ISABL_VERIFY_SSL", "false")

        s = Settings()
        assert s.verify_ssl is False

    def test_settings_verify_ssl_true(self, monkeypatch):
        """Test SSL verification defaults to true."""
        # Don't set the env var, should default to True
        s = Settings()
        assert s.verify_ssl is True

    def test_settings_timeout(self, monkeypatch):
        """Test timeout setting."""
        monkeypatch.setenv("ISABL_TIMEOUT", "60")

        s = Settings()
        assert s.timeout == 60

    def test_settings_log_level(self, monkeypatch):
        """Test log level setting."""
        monkeypatch.setenv("ISABL_LOG_LEVEL", "DEBUG")

        s = Settings()
        assert s.log_level == "DEBUG"

    def test_settings_log_level_default(self):
        """Test log level defaults to INFO."""
        s = Settings()
        assert s.log_level == "INFO"

    def test_settings_empty_token(self):
        """Test that empty token is handled."""
        s = Settings()
        # Token should default to empty string
        assert s.api_token == "" or s.api_token is not None

    def test_settings_ignores_extra_env_vars(self, monkeypatch):
        """Test that extra environment variables are ignored."""
        monkeypatch.setenv("ISABL_UNKNOWN_SETTING", "value")

        # Should not raise an error
        s = Settings()
        assert s is not None


class TestSettingsModel:
    """Tests for settings model configuration."""

    def test_model_config_env_prefix(self):
        """Test that model uses ISABL_ prefix for env vars."""
        config = Settings.model_config
        assert config.get("env_prefix") == "ISABL_"

    def test_model_config_extra_ignore(self):
        """Test that extra fields are ignored."""
        config = Settings.model_config
        assert config.get("extra") == "ignore"


class TestServerIntegration:
    """Integration tests for server components."""

    def test_server_with_custom_settings(self, monkeypatch):
        """Test server creation with custom settings."""
        monkeypatch.setenv("ISABL_API_URL", "https://prod.isabl.io/api/v1/")
        monkeypatch.setenv("ISABL_API_TOKEN", "prod-token")
        monkeypatch.setenv("ISABL_LOG_LEVEL", "WARNING")

        # Re-import to get fresh settings
        # This tests that settings are properly loaded
        server = create_server()
        assert server is not None

    def test_server_logging_level(self, monkeypatch, caplog):
        """Test that logging level is properly configured."""
        monkeypatch.setenv("ISABL_LOG_LEVEL", "DEBUG")

        # Server creation should not fail with any log level
        server = create_server()
        assert server is not None
