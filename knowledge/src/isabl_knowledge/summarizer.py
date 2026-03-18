"""LLM-based document summarizer."""

from __future__ import annotations

import json
import logging

from isabl_knowledge.llm import get_client, get_default_model
from isabl_knowledge.models import Document

logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT = """Analyze this document from the Isabl genomics platform and produce a JSON object with:
- "title": descriptive title (5-10 words)
- "summary": 2-3 sentence summary explaining what this document covers
- "tags": 3-5 topic tags
- "questions": 3-5 questions this document answers

The audience is researchers, bioinformaticians, and engineers learning about Isabl.

Document:
{content}

Respond with only the JSON object, no markdown fencing."""


def summarize_document(doc: Document, model: str | None = None) -> Document:
    """Summarize a single document using an LLM."""
    client = get_client()
    model = model or get_default_model()
    prompt = SUMMARIZE_PROMPT.format(content=doc.content[:4000])

    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse LLM response for {doc.doc_id}")
        return doc

    doc.title = data.get("title", "")
    doc.summary = data.get("summary", "")
    doc.tags = data.get("tags", [])
    doc.questions = data.get("questions", [])
    return doc


def summarize_documents(docs: list[Document], model: str | None = None) -> list[Document]:
    """Summarize all documents."""
    results = []
    for i, doc in enumerate(docs):
        logger.info(f"Summarizing {i + 1}/{len(docs)}: {doc.doc_id}")
        results.append(summarize_document(doc, model=model))
    return results
