"""Render a knowledge tree as a Mermaid mindmap."""

from __future__ import annotations

from isabl_knowledge.models import TreeNode


def _escape(text: str) -> str:
    """Escape text for mermaid mindmap nodes."""
    # Replace characters that conflict with mermaid syntax
    return (text
        .replace("(", "").replace(")", "")
        .replace("[", "").replace("]", "")
        .replace("&", "and")
        .replace("/", " ")
        .replace(",", "")
    )


def render_tree_to_mermaid(tree: TreeNode) -> str:
    """Render tree as a Mermaid mindmap diagram."""
    root_label = _escape(tree.title)
    lines = ["```mermaid", "mindmap", f"  root(({root_label}))"]
    for child in tree.children:
        _render_node(child, lines, depth=2)
    lines.append("```")
    return "\n".join(lines)


def _render_node(node: TreeNode, lines: list[str], depth: int) -> None:
    """Recursively render tree nodes as mindmap entries."""
    indent = "  " * depth
    label = _escape(node.title)
    doc_count = len(node.documents)
    if doc_count:
        label = f"{label} - {doc_count} docs"
    lines.append(f"{indent}{label}")
    for child in node.children:
        _render_node(child, lines, depth + 1)
