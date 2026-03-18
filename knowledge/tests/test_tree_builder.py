"""Tests for the knowledge tree builder."""

from unittest.mock import patch, MagicMock

import pytest

from isabl_knowledge.models import Document, TreeNode
from isabl_knowledge.tree_builder import build_tree


@pytest.fixture
def summarized_docs():
    return [
        Document(
            doc_id="cli/get_experiments",
            source_type="github_docstring",
            source_url="https://github.com/test",
            content="...",
            title="Query Experiments",
            summary="How to query experiments.",
            tags=["experiments", "querying"],
        ),
        Document(
            doc_id="apps/mutect2",
            source_type="github_apps",
            source_url="https://github.com/test",
            content="...",
            title="MuTect2 Variant Caller",
            summary="Somatic variant calling pipeline.",
            tags=["variant-calling", "pipelines"],
        ),
    ]


def test_build_tree_returns_tree_node(summarized_docs):
    """Test that build_tree returns a valid TreeNode."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="""{
        "id": "root",
        "title": "Isabl Genomics Platform",
        "summary": "Complete platform knowledge",
        "children": [
            {
                "id": "0001",
                "title": "Data Querying",
                "summary": "How to find and retrieve data",
                "documents": ["cli/get_experiments"]
            },
            {
                "id": "0002",
                "title": "Analysis Pipelines",
                "summary": "Available genomic analysis pipelines",
                "documents": ["apps/mutect2"]
            }
        ]
    }""")]

    with patch("isabl_knowledge.tree_builder.get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_response
        tree = build_tree(summarized_docs)

    assert isinstance(tree, TreeNode)
    assert tree.id == "root"
    assert len(tree.children) == 2
    assert tree.children[0].documents == ["cli/get_experiments"]
