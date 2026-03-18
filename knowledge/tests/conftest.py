"""Shared fixtures for knowledge tree tests."""

from pathlib import Path

import pytest

from isabl_knowledge.config import KnowledgeConfig, SourceConfig, TreeConfig


@pytest.fixture
def sample_config():
    """Minimal pipeline config for testing."""
    return KnowledgeConfig(
        name="test-knowledge",
        sources=[
            SourceConfig(
                name="test_source",
                type="github_python",
                repo="test/repo",
                extract=["docstrings"],
            ),
        ],
        tree=TreeConfig(),
    )


@pytest.fixture
def config_yaml_path(tmp_path):
    """Create a temporary knowledge.yaml for testing."""
    config_file = tmp_path / "knowledge.yaml"
    config_file.write_text(
        """
name: test-knowledge
sources:
  - name: test_source
    type: github_python
    repo: test/repo
    extract: [docstrings]
tree:
  max_depth: 3
  max_nodes: 50
"""
    )
    return config_file
