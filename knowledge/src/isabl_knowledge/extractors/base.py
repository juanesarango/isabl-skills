"""Base class for source extractors."""

from __future__ import annotations

import abc
import ast

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.models import Document


class BaseExtractor(abc.ABC):
    """Base class for extracting documents from a source."""

    def __init__(self, source: SourceConfig):
        self.source = source

    @abc.abstractmethod
    def extract(self) -> list[Document]:
        """Extract documents from the source. Returns a list of Documents."""
        ...

    @staticmethod
    def get_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Reconstruct a function signature string from AST."""
        args = []
        defaults_offset = len(node.args.args) - len(node.args.defaults)

        for i, arg in enumerate(node.args.args):
            name = arg.arg
            annotation = ""
            if arg.annotation:
                annotation = f": {ast.unparse(arg.annotation)}"
            default_idx = i - defaults_offset
            default = ""
            if default_idx >= 0:
                default = f"={ast.unparse(node.args.defaults[default_idx])}"
            args.append(f"{name}{annotation}{default}")

        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwonlyargs:
            if not node.args.vararg:
                args.append("*")
            for j, kw in enumerate(node.args.kwonlyargs):
                kw_default = ""
                if j < len(node.args.kw_defaults) and node.args.kw_defaults[j]:
                    kw_default = f"={ast.unparse(node.args.kw_defaults[j])}"
                args.append(f"{kw.arg}{kw_default}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        ret = ""
        if node.returns:
            ret = f" -> {ast.unparse(node.returns)}"

        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({', '.join(args)}){ret}"
