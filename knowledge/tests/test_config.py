"""Tests for configuration loading."""

from isabl_knowledge.config import load_config, KnowledgeConfig


def test_load_config(config_yaml_path):
    config = load_config(config_yaml_path)
    assert isinstance(config, KnowledgeConfig)
    assert config.name == "test-knowledge"
    assert len(config.sources) == 1
    assert config.sources[0].name == "test_source"
    assert config.tree.max_depth == 3
    assert config.tree.max_nodes == 50


def test_config_defaults(sample_config):
    assert sample_config.tree.max_depth == 4
    assert sample_config.tree.max_nodes == 100
    assert sample_config.output.github_repo is None
