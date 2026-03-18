"""Extractor for Gitbook documentation sites."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.extractors.base import BaseExtractor
from isabl_knowledge.models import Document

MIN_CONTENT_LENGTH = 50


class _HTMLToMarkdown(HTMLParser):
    """Minimal HTML to markdown converter."""

    def __init__(self):
        super().__init__()
        self.result = []
        self._tag_stack = []

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        if tag in ("h1", "h2", "h3", "h4"):
            level = int(tag[1])
            self.result.append("\n" + "#" * level + " ")
        elif tag == "li":
            self.result.append("\n- ")
        elif tag == "p":
            self.result.append("\n\n")
        elif tag == "code":
            self.result.append("`")
        elif tag == "pre":
            self.result.append("\n```\n")
        elif tag == "a":
            href = dict(attrs).get("href", "")
            self.result.append("[")
            self._tag_stack.append(("a_href", href))

    def handle_endtag(self, tag):
        if tag == "code":
            self.result.append("`")
        elif tag == "pre":
            self.result.append("\n```\n")
        elif tag == "a":
            href = ""
            while self._tag_stack:
                item = self._tag_stack.pop()
                if isinstance(item, tuple) and item[0] == "a_href":
                    href = item[1]
                    break
            self.result.append(f"]({href})")
        elif self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data):
        self.result.append(data)

    def get_markdown(self) -> str:
        text = "".join(self.result).strip()
        return re.sub(r"\n{3,}", "\n\n", text)


def html_to_markdown(html: str) -> str:
    """Convert HTML to simple markdown."""
    parser = _HTMLToMarkdown()
    parser.feed(html)
    return parser.get_markdown()


class GitbookExtractor(BaseExtractor):
    """Extract documentation pages from a Gitbook site."""

    def __init__(self, source: SourceConfig):
        super().__init__(source)
        self.base_url = source.url.rstrip("/") if source.url else ""

    def extract(self) -> list[Document]:
        """Fetch all pages and convert to Documents."""
        pages = self._fetch_pages()
        documents = []

        for path, html in pages.items():
            markdown = html_to_markdown(html)
            if len(markdown) < MIN_CONTENT_LENGTH:
                continue

            slug = path.strip("/") or "index"
            doc = Document(
                doc_id=f"{self.source.name}/{slug}",
                source_type="gitbook",
                source_url=f"{self.base_url}{path}",
                content=markdown,
                metadata={"path": path},
            )
            documents.append(doc)

        return documents

    def _fetch_pages(self) -> dict[str, str]:
        """Fetch pages from the Gitbook site. Returns {path: html_content}."""
        pages = {}
        visited: set[str] = set()
        to_visit = ["/"]

        with httpx.Client(follow_redirects=True, timeout=30) as client:
            while to_visit:
                path = to_visit.pop(0)
                if path in visited:
                    continue
                visited.add(path)

                url = urljoin(self.base_url, path)
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                pages[path] = resp.text

                for match in re.finditer(r'href="(/[^"]*)"', resp.text):
                    link = match.group(1).split("#")[0].split("?")[0]
                    if link not in visited and not link.startswith("/api"):
                        to_visit.append(link)

        return pages
