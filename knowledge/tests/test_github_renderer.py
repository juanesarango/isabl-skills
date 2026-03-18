"""Tests for the GitHub repo renderer."""

from pathlib import Path

from isabl_knowledge.models import Document, TreeNode
from isabl_knowledge.renderers.github_repo import render_tree_to_repo


def test_render_creates_folder_hierarchy(tmp_path):
    """Test that render creates folders with README.md files."""
    tree = TreeNode(
        id="root",
        title="Isabl Platform",
        summary="Root node",
        children=[
            TreeNode(
                id="0001",
                title="Data Querying",
                summary="How to query data",
                documents=["cli/get_experiments"],
            ),
            TreeNode(
                id="0002",
                title="Pipelines",
                summary="Analysis pipelines",
                children=[
                    TreeNode(
                        id="0002.0001",
                        title="Variant Calling",
                        summary="Somatic variants",
                        documents=["apps/mutect2"],
                    ),
                ],
            ),
        ],
    )

    docs = {
        "cli/get_experiments": Document(
            doc_id="cli/get_experiments",
            source_type="docstring",
            source_url="https://github.com/test",
            content="# get_experiments\n\nQuery experiments.",
            title="Query Experiments",
            summary="How to query experiments.",
        ),
    }

    render_tree_to_repo(tree, docs, tmp_path)

    # Root README
    assert (tmp_path / "README.md").exists()
    root_content = (tmp_path / "README.md").read_text()
    assert "Isabl Platform" in root_content

    # Child folders
    assert (tmp_path / "data-querying" / "README.md").exists()
    assert (tmp_path / "pipelines" / "variant-calling" / "README.md").exists()

    # Document references in leaf READMEs
    leaf = (tmp_path / "data-querying" / "README.md").read_text()
    assert "cli/get_experiments" in leaf or "Query Experiments" in leaf
