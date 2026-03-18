"""Shared LLM client configuration (OpenAI-compatible).

Configure via environment variables:

    export LLM_BASE_URL=https://your-gateway.com/v1
    export LLM_API_KEY=your-api-key
    export LLM_MODEL=@provider/model-name

    # Or direct OpenAI:
    export OPENAI_API_KEY=sk-...
"""

from __future__ import annotations

import os

from openai import OpenAI

DEFAULT_MODEL = "claude-sonnet-4-20250514"


def get_client() -> OpenAI:
    """Get an OpenAI-compatible client."""
    base_url = os.environ.get("LLM_BASE_URL")
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    return OpenAI(**kwargs)


def get_default_model() -> str:
    """Get the default model, overridable via LLM_MODEL env var."""
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)
