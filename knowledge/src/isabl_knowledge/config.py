"""Configuration for the knowledge tree pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


class SourceConfig(BaseModel):
    """A source to extract knowledge from."""
    name: str
    type: str
    repo: Optional[str] = None
    url: Optional[str] = None
    paths: Optional[list[str]] = None
    extract: Optional[list[str]] = None
    base_class: Optional[str] = None


class TreeConfig(BaseModel):
    """Tree generation settings."""
    max_depth: int = 4
    max_nodes: int = 100
    orientation: str = "capabilities and use cases, not code internals"


class OutputConfig(BaseModel):
    """Output settings."""
    github_repo: Optional[str] = None
    site: Optional[str] = None


class KnowledgeConfig(BaseModel):
    """Top-level pipeline configuration."""
    name: str
    sources: list[SourceConfig]
    tree: TreeConfig = TreeConfig()
    output: OutputConfig = OutputConfig()


def load_config(path: Path) -> KnowledgeConfig:
    """Load pipeline configuration from a YAML file."""
    with open(path) as f:
        raw = yaml.safe_load(f)
    return KnowledgeConfig(**raw)
