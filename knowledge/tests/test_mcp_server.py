"""Tests for the knowledge MCP server."""

import json
from pathlib import Path

import pytest

from isabl_knowledge.mcp_server import create_knowledge_server


@pytest.fixture
def tree_data(tmp_path):
    """Create sample tree.json and documents.json for testing."""
    tree = {
        "id": "root",
        "title": "Isabl Platform",
        "summary": "Root",
        "children": [
            {
                "id": "0001",
                "title": "Querying Data",
                "summary": "How to query",
                "documents": ["cli/get_experiments"],
            },
        ],
    }
    docs = [
        {
            "doc_id": "cli/get_experiments",
            "source_type": "docstring",
            "source_url": "https://github.com/test",
            "content": "# get_experiments\n\nQuery experiments.",
            "title": "Query Experiments",
            "summary": "How to query experiments.",
            "tags": ["querying"],
            "questions": ["How do I get experiments?"],
            "metadata": {},
        },
    ]

    (tmp_path / "tree.json").write_text(json.dumps(tree))
    (tmp_path / "documents.json").write_text(json.dumps(docs))
    return tmp_path


def test_create_server(tree_data):
    """Test that the MCP server loads tree and documents."""
    server = create_knowledge_server(
        tree_path=tree_data / "tree.json",
        docs_path=tree_data / "documents.json",
    )
    assert server is not None
