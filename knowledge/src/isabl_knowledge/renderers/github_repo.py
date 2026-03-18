"""Render a knowledge tree as a GitHub-browsable folder hierarchy."""

from __future__ import annotations

import re
from pathlib import Path

from isabl_knowledge.models import Document, TreeNode


def slugify(title: str) -> str:
    """Convert a title to a folder-safe slug."""
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug.strip("-")


def render_tree_to_repo(
    tree: TreeNode,
    documents: dict[str, Document],
    output_dir: Path,
) -> None:
    """Render a tree as folders with README.md files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _render_node(tree, documents, output_dir, is_root=True)


def _render_node(
    node: TreeNode,
    documents: dict[str, Document],
    parent_dir: Path,
    is_root: bool = False,
) -> None:
    """Recursively render a tree node."""
    if is_root:
        node_dir = parent_dir
    else:
        node_dir = parent_dir / slugify(node.title)
        node_dir.mkdir(parents=True, exist_ok=True)

    lines = [f"# {node.title}\n"]
    if node.summary:
        lines.append(f"{node.summary}\n")

    if node.children:
        lines.append("## Contents\n")
        for child in node.children:
            child_slug = slugify(child.title)
            lines.append(f"- [{child.title}](./{child_slug}/) — {child.summary}")
        lines.append("")

    if node.documents:
        lines.append("## Source Documents\n")
        for doc_id in node.documents:
            doc = documents.get(doc_id)
            if doc:
                lines.append(f"- **{doc.title or doc.doc_id}** — {doc.summary}")
                if doc.source_url:
                    lines.append(f"  [Source]({doc.source_url})")
            else:
                lines.append(f"- {doc_id}")
        lines.append("")

    readme = node_dir / "README.md"
    readme.write_text("\n".join(lines))

    for child in node.children:
        _render_node(child, documents, node_dir)
