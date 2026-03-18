"""Tests for the Gitbook docs extractor."""

import pytest
from unittest.mock import patch

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.extractors.gitbook import GitbookExtractor

# Content long enough to pass MIN_CONTENT_LENGTH (100 chars)
LONG_CONTENT = "This is documentation content that needs to be long enough to pass the minimum content length threshold for the extractor."


@pytest.fixture
def gitbook_source():
    return SourceConfig(
        name="docs",
        type="gitbook",
        url="https://docs.isabl.io",
    )


def test_gitbook_extractor_creates_documents(gitbook_source):
    """Test that the extractor produces Document objects from discovered pages."""
    fake_markdown = {
        "https://docs.isabl.io/": f"# Isabl\n\n{LONG_CONTENT}",
        "https://docs.isabl.io/quick-start": f"# Quick Start\n\n{LONG_CONTENT}",
    }

    def mock_fetch(client, url):
        return fake_markdown.get(url, "")

    extractor = GitbookExtractor(gitbook_source)
    with patch.object(extractor, "_discover_pages", return_value=["/", "/quick-start"]), \
         patch.object(extractor, "_fetch_markdown", side_effect=mock_fetch):
        docs = extractor.extract()

    assert len(docs) == 2
    assert all(d.source_type == "gitbook" for d in docs)
    assert any("Quick Start" in d.content for d in docs)
    assert all(d.doc_id.startswith("docs/") for d in docs)


def test_gitbook_extractor_skips_empty_pages(gitbook_source):
    """Test that empty or trivial pages are skipped."""
    fake_markdown = {
        "https://docs.isabl.io/": f"# Isabl\n\n{LONG_CONTENT}",
        "https://docs.isabl.io/empty": "",
        "https://docs.isabl.io/tiny": "x",
    }

    def mock_fetch(client, url):
        return fake_markdown.get(url, "")

    extractor = GitbookExtractor(gitbook_source)
    with patch.object(extractor, "_discover_pages", return_value=["/", "/empty", "/tiny"]), \
         patch.object(extractor, "_fetch_markdown", side_effect=mock_fetch):
        docs = extractor.extract()

    assert len(docs) == 1
