"""Evaluate knowledge tree retrieval and answer quality.

Workflow:
  1. Generate test questions from the indexed documents (or provide your own)
  2. For each question, use the LLM to navigate the tree and retrieve documents
  3. Use the LLM to answer the question using only retrieved context
  4. Use a judge LLM to score the answer against the expected answer

Usage:
  isabl-knowledge eval --data-dir data --output-dir output
  isabl-knowledge eval --questions eval_questions.json  # custom questions
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from isabl_knowledge.llm import get_async_client, get_default_model, parse_json_response
from isabl_knowledge.models import Document, TreeNode

logger = logging.getLogger(__name__)


@dataclass
class EvalQuestion:
    """A test question for evaluating the knowledge tree."""
    question: str
    expected_doc_ids: list[str] = field(default_factory=list)
    expected_answer: str = ""
    category: str = ""


@dataclass
class EvalResult:
    """Result of evaluating a single question."""
    question: str
    category: str
    # Retrieval
    retrieved_node_ids: list[str] = field(default_factory=list)
    retrieved_doc_ids: list[str] = field(default_factory=list)
    expected_doc_ids: list[str] = field(default_factory=list)
    retrieval_recall: float = 0.0
    # Generation
    generated_answer: str = ""
    expected_answer: str = ""
    correctness_score: float = 0.0
    judge_reasoning: str = ""


GENERATE_QUESTIONS_PROMPT = """You are evaluating a knowledge base for the Isabl genomics platform.

Given these document summaries, generate {count} diverse test questions that a researcher or engineer would ask.

Requirements:
- Mix of simple lookup questions and complex multi-doc questions
- Cover different areas: CLI usage, API, data management, applications, configuration
- Include questions that require understanding relationships between concepts
- For each question, list the doc_ids that contain the answer
- Include an expected answer (concise, 1-3 sentences)

Documents:
{documents}

Return a JSON array of objects with:
- "question": the test question
- "expected_doc_ids": list of doc_ids needed to answer
- "expected_answer": concise expected answer
- "category": one of "lookup", "how-to", "conceptual", "multi-doc", "troubleshooting"

Return only the JSON array, no markdown fencing."""


NAVIGATE_TREE_PROMPT = """You are navigating a knowledge tree to find documents relevant to a user question.

Question: {question}

Here is the tree structure. Each node has an id, title, summary, and either children (branches) or documents (leaf doc_ids).

Tree:
{tree}

Which leaf nodes likely contain the answer? Return a JSON object:
{{
  "reasoning": "brief explanation of your navigation path",
  "node_ids": ["id1", "id2"]
}}

Pick 1-3 most relevant leaf nodes. Return only JSON, no markdown fencing."""


ANSWER_PROMPT = """Answer this question using ONLY the provided context. If the context doesn't contain enough information, say so.

Question: {question}

Context:
{context}

Provide a concise answer (1-5 sentences)."""


JUDGE_PROMPT = """You are judging the quality of an AI-generated answer.

Question: {question}

Expected Answer: {expected}

Generated Answer: {generated}

Rate the generated answer on a scale of 0.0 to 1.0:
- 1.0: Fully correct and complete
- 0.75: Mostly correct, minor gaps
- 0.5: Partially correct
- 0.25: Has some relevant info but mostly wrong
- 0.0: Completely wrong or "I don't know"

Return a JSON object:
{{
  "score": 0.0,
  "reasoning": "brief explanation"
}}

Return only JSON, no markdown fencing."""


def _tree_to_nav_text(node: TreeNode, depth: int = 0) -> str:
    """Convert tree to a compact text representation for LLM navigation."""
    indent = "  " * depth
    parts = [f"{indent}[{node.id}] {node.title}"]
    if node.summary:
        parts[0] += f" — {node.summary}"
    if node.documents:
        parts[0] += f" (docs: {len(node.documents)})"
    for child in node.children:
        parts.append(_tree_to_nav_text(child, depth + 1))
    return "\n".join(parts)


def _collect_leaf_nodes(node: TreeNode) -> dict[str, TreeNode]:
    """Collect all leaf nodes (nodes with documents) indexed by ID."""
    result = {}
    if node.documents:
        result[node.id] = node
    for child in node.children:
        result.update(_collect_leaf_nodes(child))
    return result


async def generate_questions(
    docs: list[Document],
    count: int = 20,
    model: str | None = None,
) -> list[EvalQuestion]:
    """Generate test questions from documents using an LLM."""
    client = get_async_client()
    model = model or get_default_model()

    # Send doc summaries (not full content) to keep within context
    doc_summaries = json.dumps([
        {"doc_id": d.doc_id, "title": d.title, "summary": d.summary, "tags": d.tags}
        for d in docs if d.summary
    ], indent=2)

    prompt = GENERATE_QUESTIONS_PROMPT.format(count=count, documents=doc_summaries)

    response = await client.chat.completions.create(
        model=model,
        max_completion_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    questions_data = parse_json_response(response.choices[0].message.content or "")

    return [
        EvalQuestion(
            question=q["question"],
            expected_doc_ids=q.get("expected_doc_ids", []),
            expected_answer=q.get("expected_answer", ""),
            category=q.get("category", ""),
        )
        for q in questions_data
    ]


async def _navigate_tree(
    question: str,
    tree: TreeNode,
    client,
    model: str,
) -> list[str]:
    """Use LLM to navigate the tree and find relevant node IDs."""
    tree_text = _tree_to_nav_text(tree)

    prompt = NAVIGATE_TREE_PROMPT.format(question=question, tree=tree_text)

    response = await client.chat.completions.create(
        model=model,
        max_completion_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    result = parse_json_response(response.choices[0].message.content or "")
    return result.get("node_ids", [])


async def _generate_answer(
    question: str,
    context_docs: list[Document],
    client,
    model: str,
) -> str:
    """Generate an answer using retrieved documents as context."""
    context = "\n\n---\n\n".join(
        f"## {doc.title}\n\n{doc.content[:4000]}"
        for doc in context_docs
    )

    prompt = ANSWER_PROMPT.format(question=question, context=context)

    response = await client.chat.completions.create(
        model=model,
        max_completion_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return (response.choices[0].message.content or "").strip()


async def _judge_answer(
    question: str,
    expected: str,
    generated: str,
    client,
    model: str,
) -> tuple[float, str]:
    """Use LLM as judge to score answer correctness."""
    prompt = JUDGE_PROMPT.format(
        question=question, expected=expected, generated=generated,
    )

    response = await client.chat.completions.create(
        model=model,
        max_completion_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    result = parse_json_response(response.choices[0].message.content or "")
    return result.get("score", 0.0), result.get("reasoning", "")


async def evaluate(
    questions: list[EvalQuestion],
    tree: TreeNode,
    docs: dict[str, Document],
    model: str | None = None,
    on_progress: Callable | None = None,
) -> list[EvalResult]:
    """Run the full eval pipeline on a set of questions."""
    client = get_async_client()
    model = model or get_default_model()
    leaf_nodes = _collect_leaf_nodes(tree)

    results = []
    for i, q in enumerate(questions):
        if on_progress:
            on_progress(i + 1, len(questions), q.question)

        result = EvalResult(
            question=q.question,
            category=q.category,
            expected_doc_ids=q.expected_doc_ids,
            expected_answer=q.expected_answer,
        )

        # Step 1: Navigate tree to find relevant nodes
        try:
            node_ids = await _navigate_tree(q.question, tree, client, model)
            result.retrieved_node_ids = node_ids
        except Exception as e:
            logger.warning(f"Navigation failed for '{q.question}': {e}")
            node_ids = []

        # Step 2: Collect documents from retrieved nodes
        retrieved_docs = []
        for nid in node_ids:
            node = leaf_nodes.get(nid)
            if node:
                for doc_id in node.documents:
                    if doc_id in docs:
                        retrieved_docs.append(docs[doc_id])
                        result.retrieved_doc_ids.append(doc_id)

        # Step 3: Calculate retrieval recall
        if q.expected_doc_ids:
            hits = len(set(result.retrieved_doc_ids) & set(q.expected_doc_ids))
            result.retrieval_recall = hits / len(q.expected_doc_ids)

        # Step 4: Generate answer from retrieved docs
        if retrieved_docs:
            try:
                result.generated_answer = await _generate_answer(
                    q.question, retrieved_docs, client, model,
                )
            except Exception as e:
                logger.warning(f"Answer generation failed: {e}")
                result.generated_answer = f"Error: {e}"

        # Step 5: Judge answer if we have an expected answer
        if q.expected_answer and result.generated_answer:
            try:
                score, reasoning = await _judge_answer(
                    q.question, q.expected_answer,
                    result.generated_answer, client, model,
                )
                result.correctness_score = score
                result.judge_reasoning = reasoning
            except Exception as e:
                logger.warning(f"Judging failed: {e}")

        results.append(result)

    return results


def print_report(results: list[EvalResult]) -> str:
    """Generate a readable eval report."""
    lines = ["# Knowledge Tree Evaluation Report", ""]

    # Summary stats
    total = len(results)
    avg_recall = sum(r.retrieval_recall for r in results) / total if total else 0
    avg_correctness = sum(r.correctness_score for r in results) / total if total else 0
    answered = sum(1 for r in results if r.generated_answer)
    no_docs = sum(1 for r in results if not r.retrieved_doc_ids)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total questions | {total} |")
    lines.append(f"| Avg retrieval recall | {avg_recall:.0%} |")
    lines.append(f"| Avg answer correctness | {avg_correctness:.2f}/1.0 |")
    lines.append(f"| Questions answered | {answered}/{total} |")
    lines.append(f"| No docs retrieved | {no_docs}/{total} |")
    lines.append("")

    # By category
    categories = {}
    for r in results:
        cat = r.category or "uncategorized"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    if len(categories) > 1:
        lines.append("## By Category")
        lines.append("")
        lines.append(f"| Category | Count | Recall | Correctness |")
        lines.append(f"|----------|-------|--------|-------------|")
        for cat, cat_results in sorted(categories.items()):
            n = len(cat_results)
            recall = sum(r.retrieval_recall for r in cat_results) / n
            correct = sum(r.correctness_score for r in cat_results) / n
            lines.append(f"| {cat} | {n} | {recall:.0%} | {correct:.2f} |")
        lines.append("")

    # Detail per question
    lines.append("## Results Detail")
    lines.append("")

    for i, r in enumerate(results, 1):
        emoji = "pass" if r.correctness_score >= 0.75 else "FAIL" if r.correctness_score < 0.5 else "partial"
        lines.append(f"### Q{i}: {r.question}")
        lines.append(f"**Category:** {r.category} | **Score:** {r.correctness_score:.2f} | **Recall:** {r.retrieval_recall:.0%} | **Verdict:** {emoji}")
        lines.append("")
        if r.expected_answer:
            lines.append(f"**Expected:** {r.expected_answer}")
        lines.append(f"**Generated:** {r.generated_answer or '(no answer — no docs retrieved)'}")
        lines.append("")
        if r.judge_reasoning:
            lines.append(f"**Judge:** {r.judge_reasoning}")
            lines.append("")
        lines.append(f"**Retrieved nodes:** {r.retrieved_node_ids}")
        lines.append(f"**Retrieved docs:** {len(r.retrieved_doc_ids)} | **Expected docs:** {len(r.expected_doc_ids)}")
        if r.expected_doc_ids and not set(r.expected_doc_ids) <= set(r.retrieved_doc_ids):
            missed = set(r.expected_doc_ids) - set(r.retrieved_doc_ids)
            lines.append(f"**Missed docs:** {list(missed)}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
