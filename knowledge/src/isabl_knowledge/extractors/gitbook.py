"""Extractor for Gitbook documentation sites using Jina Reader for clean markdown."""

from __future__ import annotations

import re
from urllib.parse import urljoin

import httpx

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.extractors.base import BaseExtractor
from isabl_knowledge.models import Document

MIN_CONTENT_LENGTH = 100

JINA_READER_PREFIX = "https://r.jina.ai/"

# URL paths to skip when crawling
SKIP_PATHS = {"/cdn-cgi", "/api", "/.gitbook"}


class GitbookExtractor(BaseExtractor):
    """Extract documentation pages from a Gitbook site via Jina Reader."""

    def __init__(self, source: SourceConfig):
        super().__init__(source)
        self.base_url = source.url.rstrip("/") if source.url else ""

    def extract(self) -> list[Document]:
        """Discover pages by crawling, then fetch clean markdown via Jina Reader."""
        paths = self._discover_pages()
        documents = []

        with httpx.Client(timeout=60, verify=False) as client:
            for path in paths:
                url = f"{self.base_url}{path}"
                markdown = self._fetch_markdown(client, url)
                if not markdown or len(markdown) < MIN_CONTENT_LENGTH:
                    continue

                slug = path.strip("/") or "index"
                doc = Document(
                    doc_id=f"{self.source.name}/{slug}",
                    source_type="gitbook",
                    source_url=url,
                    content=markdown,
                    metadata={"path": path},
                )
                documents.append(doc)

        return documents

    def _fetch_markdown(self, client: httpx.Client, url: str) -> str:
        """Fetch a URL via Jina Reader and return clean markdown."""
        jina_url = f"{JINA_READER_PREFIX}{url}"
        try:
            resp = client.get(jina_url, headers={"Accept": "text/markdown"})
            resp.raise_for_status()
            text = resp.text

            # Jina returns a header block then "Markdown Content:\n"
            marker = "Markdown Content:\n"
            idx = text.find(marker)
            if idx >= 0:
                text = text[idx + len(marker):]

            return text.strip()
        except httpx.HTTPError:
            return ""

    def _discover_pages(self) -> list[str]:
        """Crawl the site to discover page paths (without fetching full content)."""
        visited: set[str] = set()
        to_visit = ["/"]

        with httpx.Client(follow_redirects=True, timeout=30) as client:
            while to_visit:
                path = to_visit.pop(0)
                if path in visited:
                    continue
                visited.add(path)

                if any(path.startswith(skip) for skip in SKIP_PATHS):
                    continue

                url = urljoin(self.base_url, path)
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for match in re.finditer(r'href="(/[^"]*)"', resp.text):
                    link = match.group(1).split("#")[0].split("?")[0]
                    if link not in visited and not any(link.startswith(skip) for skip in SKIP_PATHS):
                        to_visit.append(link)

        return sorted(visited)
