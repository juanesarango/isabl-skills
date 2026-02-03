"""Tests for MCP server creation and configuration."""

import pytest

from isabl_mcp.server import create_server
from isabl_mcp.config import Settings


def test_server_creation():
    """Test that the MCP server can be created."""
    server = create_server()
    assert server is not None
    assert server.name == "Isabl MCP Server"


def test_settings_defaults():
    """Test default settings values."""
    s = Settings()
    assert "localhost" in s.isabl_api_url or "api" in s.isabl_api_url
    assert s.timeout == 30
    assert s.verify_ssl is True


def test_settings_from_env(monkeypatch):
    """Test settings loaded from environment."""
    monkeypatch.setenv("ISABL_API_URL", "https://test.isabl.io/api/v1/")
    monkeypatch.setenv("ISABL_API_TOKEN", "test-token")

    s = Settings()
    assert s.isabl_api_url == "https://test.isabl.io/api/v1/"
    assert s.isabl_api_token == "test-token"
