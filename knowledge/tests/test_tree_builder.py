"""Tests for the knowledge tree builder."""

from unittest.mock import patch, MagicMock

import pytest

from isabl_knowledge.models import Document, TreeNode
from isabl_knowledge.tree_builder import build_tree, MAX_LEAF_DOCS


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
    mock_response.choices = [MagicMock(message=MagicMock(content="""{
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
    }"""))]

    with patch("isabl_knowledge.tree_builder.get_client") as mock_client:
        mock_client.return_value.chat.completions.create.return_value = mock_response
        tree = build_tree(summarized_docs)

    assert isinstance(tree, TreeNode)
    assert tree.id == "root"
    assert len(tree.children) == 2
    assert tree.children[0].documents == ["cli/get_experiments"]


def test_build_tree_splits_oversized_leaf():
    """Test that leaves with > MAX_LEAF_DOCS are split into sub-topics."""
    import json as _json

    n_docs = MAX_LEAF_DOCS + 3
    docs = [
        Document(
            doc_id=f"doc/{i}",
            source_type="test",
            source_url="https://example.com",
            content=f"Content {i}",
            title=f"Doc {i}",
            summary=f"Summary {i}",
        )
        for i in range(n_docs)
    ]
    all_ids = [f"doc/{i}" for i in range(n_docs)]
    half = n_docs // 2

    # First LLM call: build tree with one oversized leaf
    tree_data = {
        "id": "root",
        "title": "Root",
        "summary": "Root node",
        "children": [{
            "id": "0001",
            "title": "Big Leaf",
            "summary": "An oversized leaf",
            "documents": all_ids,
        }],
    }
    tree_response = MagicMock()
    tree_response.choices = [MagicMock(
        message=MagicMock(content=_json.dumps(tree_data)),
    )]

    # Second LLM call: split the oversized leaf
    split_data = [
        {
            "id": "0001.0001",
            "title": "Sub A",
            "summary": "First half",
            "documents": all_ids[:half],
        },
        {
            "id": "0001.0002",
            "title": "Sub B",
            "summary": "Second half",
            "documents": all_ids[half:],
        },
    ]
    split_response = MagicMock()
    split_response.choices = [MagicMock(
        message=MagicMock(content=_json.dumps(split_data)),
    )]

    with patch("isabl_knowledge.tree_builder.get_client") as mock_client:
        mock_client.return_value.chat.completions.create.side_effect = [
            tree_response,
            split_response,
        ]
        tree = build_tree(docs)

    # The oversized leaf should have been split
    big_leaf = tree.children[0]
    assert big_leaf.documents == [], "Oversized leaf should have no direct documents after split"
    assert len(big_leaf.children) == 2, "Should have been split into 2 sub-topics"
    # All doc_ids should be preserved across the split
    child_docs = [did for child in big_leaf.children for did in child.documents]
    assert set(child_docs) == set(all_ids)
