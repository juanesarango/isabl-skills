"""Build a knowledge tree from summarized documents."""

from __future__ import annotations

import json
import logging

from isabl_knowledge.llm import get_client, get_default_model
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


def build_tree(docs: list[Document], model: str | None = None) -> TreeNode:
    """Build a knowledge tree from summarized documents."""
    client = get_client()
    model = model or get_default_model()

    doc_summaries = json.dumps([
        {"doc_id": d.doc_id, "title": d.title, "summary": d.summary, "tags": d.tags}
        for d in docs
    ], indent=2)

    prompt = TREE_PROMPT.format(count=len(docs), documents=doc_summaries)

    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=16384,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content
    data = json.loads(text)
    return TreeNode(**data)
