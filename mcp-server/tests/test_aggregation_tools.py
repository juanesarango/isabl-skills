"""Tests for aggregation tools.

Tools tested:
- merge_results
- project_summary
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile


class TestMergeResults:
    """Tests for the merge_results tool."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return AsyncMock()

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock MCP server."""
        return MagicMock()

    @pytest.fixture
    def merge_results(self, mock_mcp, mock_client):
        """Get the merge_results tool function."""
        from isabl_mcp.tools.aggregation import register_aggregation_tools

        tool_func = None

        def capture_tool():
            def decorator(func):
                nonlocal tool_func
                if func.__name__ == "merge_results":
                    tool_func = func
                return func
            return decorator

        mock_mcp.tool = capture_tool
        register_aggregation_tools(mock_mcp, mock_client)
        return tool_func

    @pytest.mark.asyncio
    async def test_merge_results_paths_mode(self, mock_client, merge_results):
        """Test merging results returns file paths."""
        mock_client.get_analysis_results.side_effect = [
            {
                "storage_url": "/data/analyses/1",
                "status": "SUCCEEDED",
                "results": {"vcf": "/data/analyses/1/output.vcf"},
            },
            {
                "storage_url": "/data/analyses/2",
                "status": "SUCCEEDED",
                "results": {"vcf": "/data/analyses/2/output.vcf"},
            },
            {
                "storage_url": "/data/analyses/3",
                "status": "SUCCEEDED",
                "results": {"vcf": "/data/analyses/3/output.vcf"},
            },
        ]

        result = await merge_results([1, 2, 3], "vcf", output_format="paths")

        assert result["result_key"] == "vcf"
        assert result["total_requested"] == 3
        assert result["files_found"] == 3
        assert len(result["files"]) == 3
        assert result["files"][0]["path"] == "/data/analyses/1/output.vcf"
        assert result["files"][0]["analysis_id"] == 1
        assert result["errors"] is None

    @pytest.mark.asyncio
    async def test_merge_results_preview_mode(self, mock_client, merge_results):
        """Test merging results with file preview."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "output.tsv"
            test_content = "col1\tcol2\n1\t2\n3\t4\n5\t6\n7\t8\n9\t10\n"
            test_file.write_text(test_content)

            mock_client.get_analysis_results.return_value = {
                "storage_url": tmpdir,
                "status": "SUCCEEDED",
                "results": {"tsv": str(test_file)},
            }

            result = await merge_results([1], "tsv", output_format="preview")

            assert result["files_found"] == 1
            assert "preview" in result["files"][0]
            assert "col1\tcol2\n" in result["files"][0]["preview"]

    @pytest.mark.asyncio
    async def test_merge_results_preview_file_not_found(self, mock_client, merge_results):
        """Test preview mode handles missing files."""
        mock_client.get_analysis_results.return_value = {
            "storage_url": "/nonexistent",
            "status": "SUCCEEDED",
            "results": {"tsv": "/nonexistent/file.tsv"},
        }

        result = await merge_results([1], "tsv", output_format="preview")

        assert result["files_found"] == 1
        assert "preview_error" in result["files"][0]
        assert "not found" in result["files"][0]["preview_error"].lower()

    @pytest.mark.asyncio
    async def test_merge_results_missing_result_key(self, mock_client, merge_results):
        """Test handling missing result key."""
        mock_client.get_analysis_results.return_value = {
            "storage_url": "/data/analyses/1",
            "status": "SUCCEEDED",
            "results": {"bam": "/data/analyses/1/output.bam"},
        }

        result = await merge_results([1], "vcf")

        assert result["files_found"] == 0
        assert len(result["errors"]) == 1
        assert "vcf" in result["errors"][0]
        assert "not found" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_merge_results_dict_result_format(self, mock_client, merge_results):
        """Test handling result as dict with path key."""
        mock_client.get_analysis_results.return_value = {
            "storage_url": "/data/analyses/1",
            "status": "SUCCEEDED",
            "results": {
                "vcf": {
                    "path": "/data/analyses/1/output.vcf",
                    "size": 1024,
                }
            },
        }

        result = await merge_results([1], "vcf")

        assert result["files_found"] == 1
        assert result["files"][0]["path"] == "/data/analyses/1/output.vcf"

    @pytest.mark.asyncio
    async def test_merge_results_dict_result_with_url(self, mock_client, merge_results):
        """Test handling result as dict with url key."""
        mock_client.get_analysis_results.return_value = {
            "storage_url": "/data/analyses/1",
            "status": "SUCCEEDED",
            "results": {
                "vcf": {
                    "url": "/data/analyses/1/output.vcf",
                }
            },
        }

        result = await merge_results([1], "vcf")

        assert result["files_found"] == 1
        assert result["files"][0]["path"] == "/data/analyses/1/output.vcf"

    @pytest.mark.asyncio
    async def test_merge_results_fallback_to_storage_url(self, mock_client, merge_results):
        """Test falling back to constructing path from storage_url."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "metrics.tsv"
            test_file.write_text("data")

            mock_client.get_analysis_results.return_value = {
                "storage_url": tmpdir,
                "status": "SUCCEEDED",
                "results": {},  # Result key not in results
            }

            result = await merge_results([1], "metrics")

            assert result["files_found"] == 1
            assert result["files"][0]["path"] == str(test_file)

    @pytest.mark.asyncio
    async def test_merge_results_fallback_tries_extensions(self, mock_client, merge_results):
        """Test fallback tries common file extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file with extension
            test_file = Path(tmpdir) / "output.vcf.gz"
            test_file.write_text("compressed")

            mock_client.get_analysis_results.return_value = {
                "storage_url": tmpdir,
                "status": "SUCCEEDED",
                "results": {},
            }

            result = await merge_results([1], "output")

            assert result["files_found"] == 1
            assert result["files"][0]["path"].endswith(".vcf.gz")

    @pytest.mark.asyncio
    async def test_merge_results_no_storage_url(self, mock_client, merge_results):
        """Test handling analysis with no storage_url."""
        mock_client.get_analysis_results.return_value = {
            "storage_url": None,
            "status": "CREATED",
            "results": {},
        }

        result = await merge_results([1], "vcf")

        assert result["files_found"] == 0
        assert len(result["errors"]) == 1
        assert "No storage_url" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_merge_results_handles_exception(self, mock_client, merge_results):
        """Test handling exceptions during result fetching."""
        mock_client.get_analysis_results.side_effect = Exception("API error")

        result = await merge_results([1], "vcf")

        assert result["files_found"] == 0
        assert len(result["errors"]) == 1
        assert "API error" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_merge_results_mixed_success_failure(self, mock_client, merge_results):
        """Test handling mix of successful and failed results."""
        mock_client.get_analysis_results.side_effect = [
            {
                "storage_url": "/data/1",
                "status": "SUCCEEDED",
                "results": {"vcf": "/data/1/output.vcf"},
            },
            Exception("Not found"),
            {
                "storage_url": "/data/3",
                "status": "SUCCEEDED",
                "results": {},  # Missing result key
            },
        ]

        result = await merge_results([1, 2, 3], "vcf")

        assert result["total_requested"] == 3
        assert result["files_found"] == 1
        assert len(result["errors"]) == 2

    @pytest.mark.asyncio
    async def test_merge_results_empty_list(self, mock_client, merge_results):
        """Test handling empty analysis list."""
        result = await merge_results([], "vcf")

        assert result["total_requested"] == 0
        assert result["files_found"] == 0
        assert result["files"] == []
        assert result["errors"] is None

    @pytest.mark.asyncio
    async def test_merge_results_includes_status(self, mock_client, merge_results):
        """Test that result includes analysis status."""
        mock_client.get_analysis_results.return_value = {
            "storage_url": "/data/1",
            "status": "SUCCEEDED",
            "results": {"vcf": "/data/1/output.vcf"},
        }

        result = await merge_results([1], "vcf")

        assert result["files"][0]["status"] == "SUCCEEDED"


class TestProjectSummary:
    """Tests for the project_summary tool."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return AsyncMock()

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock MCP server."""
        return MagicMock()

    @pytest.fixture
    def project_summary(self, mock_mcp, mock_client):
        """Get the project_summary tool function."""
        from isabl_mcp.tools.aggregation import register_aggregation_tools

        tool_func = None

        def capture_tool():
            def decorator(func):
                nonlocal tool_func
                if func.__name__ == "project_summary":
                    tool_func = func
                return func
            return decorator

        mock_mcp.tool = capture_tool
        register_aggregation_tools(mock_mcp, mock_client)
        return tool_func

    @pytest.mark.asyncio
    async def test_project_summary_basic(self, mock_client, project_summary):
        """Test getting basic project summary."""
        mock_client.get_project_summary.return_value = {
            "project": {
                "pk": 102,
                "title": "Test Project",
                "short_title": "TEST",
            },
            "counts": {
                "experiments": 100,
                "analyses": {
                    "total": 500,
                    "by_status": {
                        "SUCCEEDED": 450,
                        "FAILED": 30,
                        "STARTED": 20,
                    },
                    "by_application": {
                        "MUTECT": 200,
                        "STAR": 150,
                        "BWA": 150,
                    },
                },
            },
            "storage_usage_gb": 1500.5,
        }

        result = await project_summary(102)

        mock_client.get_project_summary.assert_called_once_with(102)
        assert result["project"]["pk"] == 102
        assert result["project"]["title"] == "Test Project"
        assert result["counts"]["experiments"] == 100
        assert result["counts"]["analyses"]["total"] == 500
        assert result["counts"]["analyses"]["by_status"]["SUCCEEDED"] == 450
        assert result["storage_usage_gb"] == 1500.5

    @pytest.mark.asyncio
    async def test_project_summary_empty_project(self, mock_client, project_summary):
        """Test getting summary for empty project."""
        mock_client.get_project_summary.return_value = {
            "project": {
                "pk": 999,
                "title": "Empty Project",
                "short_title": "EMPTY",
            },
            "counts": {
                "experiments": 0,
                "analyses": {
                    "total": 0,
                    "by_status": {},
                    "by_application": {},
                },
            },
            "storage_usage_gb": 0.0,
        }

        result = await project_summary(999)

        assert result["counts"]["experiments"] == 0
        assert result["counts"]["analyses"]["total"] == 0
        assert result["counts"]["analyses"]["by_status"] == {}
        assert result["storage_usage_gb"] == 0.0

    @pytest.mark.asyncio
    async def test_project_summary_calls_client(self, mock_client, project_summary):
        """Test that project_summary delegates to client."""
        mock_client.get_project_summary.return_value = {"project": {"pk": 1}}

        await project_summary(123)

        mock_client.get_project_summary.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_project_summary_propagates_errors(self, mock_client, project_summary):
        """Test that errors from client are propagated."""
        mock_client.get_project_summary.side_effect = Exception("Project not found")

        with pytest.raises(Exception) as exc_info:
            await project_summary(99999)

        assert "Project not found" in str(exc_info.value)
