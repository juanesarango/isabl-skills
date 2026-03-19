"""Shared LLM client configuration (OpenAI-compatible).

Configure via environment variables:

    export LLM_BASE_URL=https://your-gateway.com/v1
    export LLM_API_KEY=your-api-key
    export LLM_MODEL=@provider/model-name

    # Or direct OpenAI:
    export OPENAI_API_KEY=sk-...
"""

from __future__ import annotations

import json
import logging
import os
import re

from openai import AsyncOpenAI, OpenAI

DEFAULT_MODEL = "gpt-4.1-mini"

logger = logging.getLogger(__name__)

_client: OpenAI | None = None
_async_client: AsyncOpenAI | None = None


def _client_kwargs() -> dict:
    """Build shared client kwargs from environment."""
    base_url = os.environ.get("LLM_BASE_URL")
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return kwargs


def get_client() -> OpenAI:
    """Get a cached OpenAI-compatible client."""
    global _client
    if _client is None:
        _client = OpenAI(**_client_kwargs())
    return _client


def get_async_client() -> AsyncOpenAI:
    """Get a cached async OpenAI-compatible client."""
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI(**_client_kwargs())
    return _async_client


def get_default_model() -> str:
    """Get the default model, overridable via LLM_MODEL env var."""
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)


def strip_fencing(text: str) -> str:
    """Strip markdown code fencing from LLM output."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def parse_json_response(text: str) -> dict | list:
    """Strip fencing and parse JSON, with error logging."""
    text = strip_fencing(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response as JSON: %s...", text[:200])
        raise
