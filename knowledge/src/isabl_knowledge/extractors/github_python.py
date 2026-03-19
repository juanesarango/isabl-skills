"""Extractor for Python source files (docstrings, function signatures)."""

from __future__ import annotations

import ast
import subprocess
import tempfile
from pathlib import Path

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.extractors.base import BaseExtractor
from isabl_knowledge.models import Document


class PythonExtractor(BaseExtractor):
    """Extract docstrings and signatures from Python source files."""

    def extract(self) -> list[Document]:
        """Clone the repo and extract from all .py files."""
        repo = self.source.repo
        if not repo:
            return []

        with tempfile.TemporaryDirectory() as tmp:
            clone_dir = Path(tmp) / "repo"
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    f"https://github.com/{repo}.git",
                    str(clone_dir),
                ],
                capture_output=True,
                check=True,
            )

            documents = []
            for py_file in sorted(clone_dir.rglob("*.py")):
                rel_path = str(py_file.relative_to(clone_dir))
                if any(
                    skip in rel_path
                    for skip in ["test", "migration", "setup.py", "conftest"]
                ):
                    continue
                docs = self._extract_file(py_file, rel_path)
                documents.extend(docs)

            return documents

    def _extract_file(self, file_path: Path, rel_path: str) -> list[Document]:
        """Extract documented functions, classes, and module docstrings from a file."""
        try:
            source = file_path.read_text()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            return []

        documents = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if not docstring:
                    continue

                sig = self.get_signature(node)
                content = f"# {node.name}\n\n```python\n{sig}\n```\n\n{docstring}"

                documents.append(
                    Document(
                        doc_id=f"{self.source.name}/{rel_path}:{node.name}",
                        source_type="github_docstring",
                        source_url=f"https://github.com/{self.source.repo}/blob/main/{rel_path}",
                        content=content,
                        metadata={
                            "kind": "function",
                            "name": node.name,
                            "file": rel_path,
                        },
                    )
                )

            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                if not docstring:
                    continue

                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_doc = ast.get_docstring(item)
                        if method_doc:
                            sig = self.get_signature(item)
                            methods.append(
                                f"### {item.name}\n\n```python\n{sig}\n```\n\n{method_doc}"
                            )

                content = f"# class {node.name}\n\n{docstring}"
                if methods:
                    content += "\n\n## Methods\n\n" + "\n\n".join(methods)

                documents.append(
                    Document(
                        doc_id=f"{self.source.name}/{rel_path}:{node.name}",
                        source_type="github_docstring",
                        source_url=f"https://github.com/{self.source.repo}/blob/main/{rel_path}",
                        content=content,
                        metadata={
                            "kind": "class",
                            "name": node.name,
                            "file": rel_path,
                        },
                    )
                )

        return documents

