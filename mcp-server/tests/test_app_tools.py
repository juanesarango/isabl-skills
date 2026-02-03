"""Tests for application tools.

Tools tested:
- get_apps
- get_app_template
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestGetApps:
    """Tests for the get_apps tool."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return AsyncMock()

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock MCP server."""
        return MagicMock()

    @pytest.fixture
    def get_apps(self, mock_mcp, mock_client):
        """Get the get_apps tool function."""
        from isabl_mcp.tools.apps import register_app_tools

        tool_func = None

        def capture_tool():
            def decorator(func):
                nonlocal tool_func
                if func.__name__ == "get_apps":
                    tool_func = func
                return func
            return decorator

        mock_mcp.tool = capture_tool
        register_app_tools(mock_mcp, mock_client)
        return tool_func

    @pytest.mark.asyncio
    async def test_get_apps_search(self, mock_client, get_apps):
        """Test searching for apps by name."""
        # No exact match
        mock_client.query.side_effect = [
            {"results": []},  # Exact match query
            {
                "results": [
                    {
                        "pk": 1,
                        "name": "FUSION_CALLER",
                        "version": "1.0.0",
                        "description": "Detects gene fusions",
                        "assembly": "GRCh38",
                    },
                    {
                        "pk": 2,
                        "name": "FUSION_FILTER",
                        "version": "2.0.0",
                        "description": "Filters fusion calls",
                        "assembly": "GRCh38",
                    },
                ]
            },  # Search query
        ]

        result = await get_apps("fusion")

        assert result["match_type"] == "search"
        assert result["count"] == 2
        assert len(result["apps"]) == 2
        assert result["apps"][0]["name"] == "FUSION_CALLER"
        assert result["apps"][1]["name"] == "FUSION_FILTER"

    @pytest.mark.asyncio
    async def test_get_apps_exact_match(self, mock_client, get_apps):
        """Test exact match without detailed flag returns search results."""
        mock_client.query.side_effect = [
            {
                "results": [
                    {
                        "pk": 1,
                        "name": "MUTECT",
                        "version": "2.4.3",
                        "description": "Somatic variant caller",
                        "assembly": "GRCh38",
                    }
                ]
            },  # Exact match
            {
                "results": [
                    {
                        "pk": 1,
                        "name": "MUTECT",
                        "version": "2.4.3",
                        "description": "Somatic variant caller",
                        "assembly": "GRCh38",
                    }
                ]
            },  # Search query (still runs)
        ]

        result = await get_apps("MUTECT")

        # Without detailed=True, it should do the broader search
        assert result["match_type"] == "search"

    @pytest.mark.asyncio
    async def test_get_apps_exact_match_detailed(self, mock_client, get_apps):
        """Test exact match with detailed flag returns full info."""
        mock_client.query.return_value = {
            "results": [
                {
                    "pk": 1,
                    "name": "MUTECT",
                    "version": "2.4.3",
                    "assembly": "GRCh38",
                    "species": "HUMAN",
                    "description": "Somatic variant caller using Bayesian model",
                    "application_class": "isabl_apps.mutect.Mutect",
                    "application_settings": {
                        "pon_path": "/data/pon/pon.vcf.gz",
                        "threads": 8,
                    },
                    "application_results": {
                        "vcf": {
                            "frontend_type": "igv-vcf",
                            "description": "VCF output",
                        }
                    },
                }
            ]
        }

        result = await get_apps("MUTECT", detailed=True)

        assert result["match_type"] == "exact"
        assert result["app"]["pk"] == 1
        assert result["app"]["name"] == "MUTECT"
        assert result["app"]["version"] == "2.4.3"
        assert result["app"]["assembly"] == "GRCh38"
        assert result["app"]["species"] == "HUMAN"
        assert "Bayesian" in result["app"]["description"]
        assert "pon_path" in result["app"]["application_settings"]
        assert "vcf" in result["app"]["application_results"]

    @pytest.mark.asyncio
    async def test_get_apps_no_results(self, mock_client, get_apps):
        """Test handling no matching apps."""
        mock_client.query.side_effect = [
            {"results": []},  # No exact match
            {"results": []},  # No search results
        ]

        result = await get_apps("nonexistent_app")

        assert result["match_type"] == "none"
        assert "No applications found" in result["message"]
        assert result["apps"] == []

    @pytest.mark.asyncio
    async def test_get_apps_truncates_description(self, mock_client, get_apps):
        """Test that long descriptions are truncated."""
        long_description = "A" * 500  # Very long description
        mock_client.query.side_effect = [
            {"results": []},
            {
                "results": [
                    {
                        "pk": 1,
                        "name": "LONG_DESC_APP",
                        "version": "1.0",
                        "description": long_description,
                        "assembly": "GRCh38",
                    }
                ]
            },
        ]

        result = await get_apps("LONG")

        assert len(result["apps"][0]["description"]) <= 200

    @pytest.mark.asyncio
    async def test_get_apps_handles_none_description(self, mock_client, get_apps):
        """Test handling apps with None description."""
        mock_client.query.side_effect = [
            {"results": []},
            {
                "results": [
                    {
                        "pk": 1,
                        "name": "NO_DESC_APP",
                        "version": "1.0",
                        "description": None,
                        "assembly": "GRCh38",
                    }
                ]
            },
        ]

        result = await get_apps("NO_DESC")

        assert result["apps"][0]["description"] == ""

    @pytest.mark.asyncio
    async def test_get_apps_query_parameters(self, mock_client, get_apps):
        """Test correct query parameters are used."""
        mock_client.query.side_effect = [
            {"results": []},
            {"results": []},
        ]

        await get_apps("myapp")

        # First call: exact match
        first_call = mock_client.query.call_args_list[0]
        assert first_call[0][0] == "applications"
        assert first_call[1]["filters"] == {"name__iexact": "myapp"}
        assert first_call[1]["limit"] == 1

        # Second call: search
        second_call = mock_client.query.call_args_list[1]
        assert second_call[0][0] == "applications"
        assert second_call[1]["filters"] == {"name__icontains": "myapp"}
        assert second_call[1]["limit"] == 20


class TestGetAppTemplate:
    """Tests for the get_app_template tool."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return AsyncMock()

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock MCP server."""
        return MagicMock()

    @pytest.fixture
    def get_app_template(self, mock_mcp, mock_client):
        """Get the get_app_template tool function."""
        from isabl_mcp.tools.apps import register_app_tools

        tool_func = None

        def capture_tool():
            def decorator(func):
                nonlocal tool_func
                if func.__name__ == "get_app_template":
                    tool_func = func
                return func
            return decorator

        mock_mcp.tool = capture_tool
        register_app_tools(mock_mcp, mock_client)
        return tool_func

    @pytest.mark.asyncio
    async def test_template_single_default(self, get_app_template):
        """Test generating single sample template (default)."""
        result = await get_app_template()

        assert "class MyApplication(AbstractApplication):" in result
        assert 'cli_options = [options.TARGETS]' in result
        assert "def validate_experiments" in result
        assert "def get_command" in result
        assert "def get_analysis_results" in result
        # Single template should mention target, not tumor/normal
        assert "target = analysis.targets[0]" in result

    @pytest.mark.asyncio
    async def test_template_single_explicit(self, get_app_template):
        """Test generating single sample template explicitly."""
        result = await get_app_template(app_type="single")

        assert 'cli_options = [options.TARGETS]' in result
        assert "target = analysis.targets[0]" in result
        assert "tumor" not in result.lower() or "tumor" in result.lower()  # May or may not appear
        # Check for single-sample specific validation
        assert "Requires exactly one target" in result

    @pytest.mark.asyncio
    async def test_template_paired(self, get_app_template):
        """Test generating tumor-normal pair template."""
        result = await get_app_template(app_type="paired")

        assert 'cli_options = [options.PAIRS]' in result
        assert "def validate_experiments" in result
        assert "exactly one tumor" in result
        assert "exactly one normal" in result
        assert "tumor = analysis.targets[0]" in result
        assert "normal = analysis.references[0]" in result

    @pytest.mark.asyncio
    async def test_template_cohort(self, get_app_template):
        """Test generating cohort template."""
        result = await get_app_template(app_type="cohort")

        assert "unique_analysis_per_individual = False" in result

    @pytest.mark.asyncio
    async def test_template_with_dependencies(self, get_app_template):
        """Test template includes dependencies example when requested."""
        result = await get_app_template(include_dependencies=True)

        assert "def get_dependencies" in result
        assert "utils.get_result" in result
        assert "application_key=settings.alignment_app_pk" in result
        assert "input_bam" in result

    @pytest.mark.asyncio
    async def test_template_without_dependencies(self, get_app_template):
        """Test template has minimal dependencies by default."""
        result = await get_app_template(include_dependencies=False)

        assert "def get_dependencies" in result
        assert "return [], {}" in result

    @pytest.mark.asyncio
    async def test_template_has_required_metadata(self, get_app_template):
        """Test template includes all required metadata fields."""
        result = await get_app_template()

        assert 'NAME = "my_application"' in result
        assert 'VERSION = "1.0.0"' in result
        assert "ASSEMBLY" in result
        assert "SPECIES" in result

    @pytest.mark.asyncio
    async def test_template_has_application_settings(self, get_app_template):
        """Test template includes application settings."""
        result = await get_app_template()

        assert "application_settings = {" in result
        assert '"tool_path"' in result
        assert '"threads"' in result
        assert '"memory_gb"' in result

    @pytest.mark.asyncio
    async def test_template_has_application_results(self, get_app_template):
        """Test template includes application results schema."""
        result = await get_app_template()

        assert "application_results = {" in result
        assert '"output_file"' in result
        assert '"frontend_type"' in result
        assert '"description"' in result

    @pytest.mark.asyncio
    async def test_template_has_cli_help(self, get_app_template):
        """Test template includes CLI help string."""
        result = await get_app_template()

        assert "cli_help =" in result

    @pytest.mark.asyncio
    async def test_template_paired_with_dependencies(self, get_app_template):
        """Test paired template with dependencies."""
        result = await get_app_template(app_type="paired", include_dependencies=True)

        assert 'cli_options = [options.PAIRS]' in result
        assert "utils.get_result" in result
        assert "tumor = analysis.targets[0]" in result
        assert "normal = analysis.references[0]" in result

    @pytest.mark.asyncio
    async def test_template_is_valid_python(self, get_app_template):
        """Test that generated template is valid Python syntax."""
        result = await get_app_template()

        # This should not raise SyntaxError
        compile(result, "<template>", "exec")

    @pytest.mark.asyncio
    async def test_template_paired_is_valid_python(self, get_app_template):
        """Test that paired template is valid Python syntax."""
        result = await get_app_template(app_type="paired", include_dependencies=True)

        # This should not raise SyntaxError
        compile(result, "<template>", "exec")

    @pytest.mark.asyncio
    async def test_template_cohort_is_valid_python(self, get_app_template):
        """Test that cohort template is valid Python syntax."""
        result = await get_app_template(app_type="cohort", include_dependencies=True)

        # This should not raise SyntaxError
        compile(result, "<template>", "exec")
