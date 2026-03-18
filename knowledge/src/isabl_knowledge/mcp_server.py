"""Knowledge tree MCP server."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from isabl_knowledge.models import Document, TreeNode

logger = logging.getLogger(__name__)


def create_knowledge_server(tree_path: Path, docs_path: Path) -> FastMCP:
    """Create an MCP server that serves the knowledge tree.

    Args:
        tree_path: Path to tree.json file.
        docs_path: Path to documents.json file.
    """
    mcp = FastMCP("Isabl Knowledge")

    tree_data = json.loads(tree_path.read_text())
    tree = TreeNode(**tree_data)

    docs_list = json.loads(docs_path.read_text())
    docs = {d["doc_id"]: Document(**d) for d in docs_list}

    node_index: dict[str, TreeNode] = {}
    _index_nodes(tree, node_index)

    @mcp.tool()
    async def get_tree() -> dict:
        """Get the top-level knowledge tree with node summaries.

        Returns the root node with its immediate children.
        Use get_node() to drill into a specific branch.
        """
        return {
            "id": tree.id,
            "title": tree.title,
            "summary": tree.summary,
            "children": [
                {"id": c.id, "title": c.title, "summary": c.summary}
                for c in tree.children
            ],
        }

    @mcp.tool()
    async def get_node(node_id: str) -> dict:
        """Get a specific node's details, children, and linked documents.

        Args:
            node_id: The node ID (e.g., "0001", "0001.0002")
        """
        node = node_index.get(node_id)
        if not node:
            return {"error": f"Node {node_id} not found"}

        result = {
            "id": node.id,
            "title": node.title,
            "summary": node.summary,
        }

        if node.children:
            result["children"] = [
                {"id": c.id, "title": c.title, "summary": c.summary}
                for c in node.children
            ]

        if node.documents:
            result["documents"] = []
            for doc_id in node.documents:
                doc = docs.get(doc_id)
                if doc:
                    result["documents"].append({
                        "doc_id": doc.doc_id,
                        "title": doc.title,
                        "summary": doc.summary,
                        "tags": doc.tags,
                        "questions": doc.questions,
                    })

        return result

    @mcp.tool()
    async def get_document(doc_id: str) -> dict:
        """Get the full content of a source document.

        Args:
            doc_id: The document ID (e.g., "cli/get_experiments")
        """
        doc = docs.get(doc_id)
        if not doc:
            return {"error": f"Document {doc_id} not found"}
        return doc.model_dump()

    return mcp


def _index_nodes(node: TreeNode, index: dict[str, TreeNode]) -> None:
    """Recursively index all nodes by ID."""
    index[node.id] = node
    for child in node.children:
        _index_nodes(child, index)
