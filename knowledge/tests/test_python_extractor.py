"""Tests for the Python/GitHub extractor."""

import textwrap
from pathlib import Path

import pytest

from isabl_knowledge.config import SourceConfig
from isabl_knowledge.extractors.github_python import PythonExtractor


@pytest.fixture
def python_source():
    return SourceConfig(
        name="isabl_cli",
        type="github_python",
        repo="isabl-io/isabl_cli",
        extract=["docstrings"],
    )


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file with docstrings."""
    code = textwrap.dedent('''
        """Module for querying experiments."""

        def get_experiments(projects=None, technique__method=None):
            """Get experiments from Isabl.

            Args:
                projects: Project PK or list of PKs.
                technique__method: Filter by sequencing method (WGS, RNA-Seq).

            Returns:
                List of experiment dictionaries.
            """
            pass


        class ExperimentManager:
            """Manages experiment queries and caching."""

            def count(self):
                """Return the number of experiments."""
                pass
    ''')
    f = tmp_path / "experiments.py"
    f.write_text(code)
    return f


def test_extract_from_file(python_source, sample_python_file):
    """Test extracting docstrings from a single Python file."""
    extractor = PythonExtractor(python_source)
    docs = extractor._extract_file(sample_python_file, "experiments.py")

    assert len(docs) >= 2
    assert any("get_experiments" in d.doc_id for d in docs)
    assert any("projects" in d.content for d in docs)


def test_skip_undocumented(python_source, tmp_path):
    """Functions without docstrings should be skipped."""
    code = "def no_docs():\n    pass\n"
    f = tmp_path / "empty.py"
    f.write_text(code)

    extractor = PythonExtractor(python_source)
    docs = extractor._extract_file(f, "empty.py")
    assert len(docs) == 0
