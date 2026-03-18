"""Tests for the Gitbook docs extractor."""

import pytest
from unittest.mock import patch

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.extractors.gitbook import GitbookExtractor


@pytest.fixture
def gitbook_source():
    return SourceConfig(
        name="docs",
        type="gitbook",
        url="https://docs.isabl.io",
    )


def test_gitbook_extractor_creates_documents(gitbook_source):
    """Test that the extractor produces Document objects from fetched pages."""
    fake_pages = {
        "/": "<h1>Isabl Platform</h1><p>Welcome to the Isabl documentation site with detailed guides and references.</p>",
        "/quick-start": "<h1>Quick Start Guide</h1><p>Get started with Isabl by following these step-by-step instructions for setup.</p>",
    }

    with patch.object(GitbookExtractor, "_fetch_pages", return_value=fake_pages):
        extractor = GitbookExtractor(gitbook_source)
        docs = extractor.extract()

    assert len(docs) == 2
    assert all(d.source_type == "gitbook" for d in docs)
    assert any("Quick Start" in d.content for d in docs)
    assert all(d.doc_id.startswith("docs/") for d in docs)


def test_gitbook_extractor_skips_empty_pages(gitbook_source):
    """Test that empty or trivial pages are skipped."""
    fake_pages = {
        "/": "<h1>Isabl Platform</h1><p>This page has enough content to pass the minimum length threshold for extraction.</p>",
        "/empty": "",
        "/tiny": "<p>x</p>",
    }

    with patch.object(GitbookExtractor, "_fetch_pages", return_value=fake_pages):
        extractor = GitbookExtractor(gitbook_source)
        docs = extractor.extract()

    # Should skip empty and very short pages
    assert len(docs) == 1
