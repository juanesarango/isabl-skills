"""Build a knowledge tree from summarized documents."""

from __future__ import annotations

import json
import logging

from isabl_knowledge.llm import get_client, get_default_model, parse_json_response
from isabl_knowledge.models import Document, TreeNode

logger = logging.getLogger(__name__)

MAX_LEAF_DOCS = 7

TREE_PROMPT = """You are organizing documentation for the Isabl genomics platform into a navigable knowledge tree.

Given these {count} documents (each with doc_id, title, summary, tags), create a DEEP hierarchical tree:

STRUCTURE REQUIREMENTS:
- Use 3-4 levels of depth (root → domain → area → topic → documents)
- Root should have 5-8 top-level domains
- Each domain should have 2-5 areas
- Areas with 8+ documents MUST be split into sub-topics
- Only leaf nodes list doc_ids — intermediate nodes have children only
- Max 100 total nodes
- Each node needs: id (dotted notation like "0001.0002.0003"), title, summary, and either children or documents (never both)

GROUPING GUIDELINES:
- Group by user intent and capabilities, not code structure
- Think: "What would a researcher/engineer search for?"
- Example levels: "Data Management" → "Importing Data" → "File Formats & Validation" → [doc_ids]

Documents:
{documents}

Return a JSON object representing the root TreeNode. No markdown fencing."""


SPLIT_LEAF_PROMPT = """This leaf node in a knowledge tree has too many documents ({count}).
Split them into 2-4 sub-topics for better navigation.

Node: {title}
Node ID prefix: {node_id}

Documents:
{documents}

Return a JSON array of sub-topic objects. Each object has:
- "id": "{node_id}.NNNN" (4-digit suffix)
- "title": descriptive sub-topic title
- "summary": 1-sentence description
- "documents": list of doc_ids belonging to this sub-topic

Every doc_id must appear in exactly one sub-topic. No markdown fencing."""


def build_tree(
    docs: list[Document],
    model: str | None = None,
    split_large_leaves: bool = True,
) -> TreeNode:
    """Build a knowledge tree from summarized documents.

    If split_large_leaves is True (default), leaf nodes with more than
    MAX_LEAF_DOCS documents are automatically split into sub-topics.
    """
    client = get_client()
    model = model or get_default_model()

    doc_summaries = json.dumps([
        {"doc_id": d.doc_id, "title": d.title, "summary": d.summary, "tags": d.tags}
        for d in docs
    ], indent=2)

    prompt = TREE_PROMPT.format(count=len(docs), documents=doc_summaries)

    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=32768,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content or ""
    if not text.strip():
        raise ValueError(
            f"LLM returned empty response. "
            f"Finish reason: {response.choices[0].finish_reason}, "
            f"Usage: {response.usage}"
        )

    data = parse_json_response(text)
    tree = TreeNode(**data)

    # Validate that all doc_ids in the tree actually exist
    valid_ids = {d.doc_id for d in docs}
    _warn_invalid_doc_ids(tree, valid_ids)

    if split_large_leaves:
        docs_by_id = {d.doc_id: d for d in docs}
        _split_oversized_leaves(tree, docs_by_id, client, model)

    return tree


def _warn_invalid_doc_ids(node: TreeNode, valid_ids: set[str]) -> None:
    """Log warnings for doc_ids not present in the input documents."""
    for doc_id in node.documents:
        if doc_id not in valid_ids:
            logger.warning("Tree contains unknown doc_id: %s (node: %s)", doc_id, node.id)
    for child in node.children:
        _warn_invalid_doc_ids(child, valid_ids)


def _split_oversized_leaves(
    node: TreeNode,
    docs_by_id: dict[str, Document],
    client,
    model: str,
) -> None:
    """Recursively find leaf nodes with too many docs and split them."""
    # Recurse into children first
    for child in node.children:
        _split_oversized_leaves(child, docs_by_id, client, model)

    # Check if this node is an oversized leaf
    if node.documents and len(node.documents) > MAX_LEAF_DOCS:
        logger.info(
            "Splitting leaf '%s' (%d docs) into sub-topics",
            node.title, len(node.documents),
        )
        sub_nodes = _split_leaf(node, docs_by_id, client, model)
        if sub_nodes:
            node.children = sub_nodes
            node.documents = []


def _split_leaf(
    node: TreeNode,
    docs_by_id: dict[str, Document],
    client,
    model: str,
) -> list[TreeNode]:
    """Use LLM to split a large leaf into sub-topic children."""
    doc_infos = json.dumps([
        {"doc_id": did, "title": docs_by_id[did].title, "summary": docs_by_id[did].summary}
        for did in node.documents if did in docs_by_id
    ], indent=2)

    prompt = SPLIT_LEAF_PROMPT.format(
        count=len(node.documents),
        title=node.title,
        node_id=node.id,
        documents=doc_infos,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            max_completion_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        data = parse_json_response(response.choices[0].message.content or "")
        if not isinstance(data, list) or len(data) < 2:
            return []
        sub_nodes = [TreeNode(**item) for item in data]

        # Validate: all original doc_ids must appear exactly once across sub-nodes
        original = set(node.documents)
        split_ids = [did for sn in sub_nodes for did in sn.documents]
        if set(split_ids) != original or len(split_ids) != len(original):
            logger.warning(
                "Split of '%s' produced invalid doc_id distribution "
                "(expected %d, got %d unique / %d total); keeping original leaf",
                node.title, len(original), len(set(split_ids)), len(split_ids),
            )
            return []

        return sub_nodes
    except Exception as e:
        logger.warning("Failed to split leaf '%s': %s", node.title, e)
        return []
