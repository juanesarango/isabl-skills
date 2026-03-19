"""Tests for the CLI."""

import json
from unittest.mock import patch

from click.testing import CliRunner

from isabl_knowledge.cli import cli
from isabl_knowledge.models import Document


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "extract" in result.output
    assert "build" in result.output


def test_extract_command(config_yaml_path, tmp_path):
    mock_doc = Document(
        doc_id="test/doc1",
        source_type="github_docstring",
        source_url="https://github.com/test",
        content="Test content",
        title="Test Doc",
    )
    output_dir = tmp_path / "extract_output"

    with patch("isabl_knowledge.extractors.registry.get_extractor") as mock_get:
        mock_extractor = mock_get.return_value
        mock_extractor.extract.return_value = [mock_doc]

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--config", str(config_yaml_path), "extract", "-o", str(output_dir)],
        )

    assert result.exit_code == 0
    assert "Extracting" in result.output

    # Verify documents.json was created with valid data
    docs_file = output_dir / "documents.json"
    assert docs_file.exists(), "documents.json should be created"
    docs_data = json.loads(docs_file.read_text())
    assert isinstance(docs_data, list)
    assert len(docs_data) > 0
