"""Build a knowledge tree from summarized documents."""

from __future__ import annotations

import json
import logging

from anthropic import Anthropic

from isabl_knowledge.models import Document, TreeNode

logger = logging.getLogger(__name__)

TREE_PROMPT = """You are organizing documentation for the Isabl genomics platform into a navigable knowledge tree.

Given these {count} documents (each with doc_id, title, summary, tags), create a hierarchical tree structure:

- Max 4 levels deep
- Max 100 nodes
- Group by capabilities and use cases, not code structure
- Each leaf node should list the doc_ids of relevant documents
- Each node needs: id (dotted notation like "0001.0002"), title, summary, and optionally children or documents

Documents:
{documents}

Return a JSON object representing the root TreeNode. No markdown fencing."""


def get_client() -> Anthropic:
    """Get an Anthropic client."""
    return Anthropic()


def build_tree(docs: list[Document], model: str = "claude-sonnet-4-20250514") -> TreeNode:
    """Build a knowledge tree from summarized documents."""
    client = get_client()

    doc_summaries = json.dumps([
        {"doc_id": d.doc_id, "title": d.title, "summary": d.summary, "tags": d.tags}
        for d in docs
    ], indent=2)

    prompt = TREE_PROMPT.format(count=len(docs), documents=doc_summaries)

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    data = json.loads(text)
    return TreeNode(**data)
