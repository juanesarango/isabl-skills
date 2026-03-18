"""Shared LLM client configuration.

Supports direct Anthropic API or Portkey gateway via environment variables:

    # Direct Anthropic (default):
    export ANTHROPIC_API_KEY=sk-ant-...

    # Via Portkey gateway:
    export LLM_API_KEY=your-portkey-api-key
    export LLM_BASE_URL=https://api.portkey.ai
    export LLM_MODEL=@your-provider-slug/claude-sonnet-4-5-20250929

    # Or any OpenAI-compatible gateway:
    export LLM_BASE_URL=https://your-gateway.com
    export LLM_API_KEY=your-key
"""

from __future__ import annotations

import os

from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-20250514"


def get_client() -> Anthropic:
    """Get an Anthropic-compatible client.

    If LLM_BASE_URL is set, uses it as the gateway (e.g. Portkey).
    Otherwise falls back to direct Anthropic API.
    """
    base_url = os.environ.get("LLM_BASE_URL")
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    return Anthropic(**kwargs)


def get_default_model() -> str:
    """Get the default model, overridable via LLM_MODEL env var."""
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)
