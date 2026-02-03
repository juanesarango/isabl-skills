"""Application tools for Isabl MCP Server.

Tools:
- get_apps: Search and get details for installed applications
- get_app_template: Get boilerplate code for new apps
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from isabl_mcp.clients.isabl_api import IsablAPIClient


def register_app_tools(mcp: FastMCP, client: IsablAPIClient) -> None:
    """Register application tools with the MCP server."""

    @mcp.tool()
    async def get_apps(
        query: str,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """
        Search for installed Isabl applications and get their details.

        Queries the Isabl API for applications matching the search term.
        Applications are user-specific based on INSTALLED_APPLICATIONS config.

        Args:
            query: Search term or exact app name (e.g., "fusion", "MUTECT")
            detailed: If True, returns full details including settings/results schema.
                     If False (default), returns summary list of matches.

        Returns:
            If detailed=False: List of matching apps with name, version, description
            If detailed=True: Full app info including settings and results schema

        Examples:
            get_apps("fusion")                    # Search for fusion-related apps
            get_apps("MUTECT", detailed=True)     # Get full details for MUTECT
        """
        # First try exact match
        exact_result = await client.query(
            "applications",
            filters={"name__iexact": query},
            limit=1,
        )

        exact_matches = exact_result.get("results", [])

        # If exact match found and detailed requested, return full info
        if exact_matches and detailed:
            app = exact_matches[0]
            return {
                "match_type": "exact",
                "app": {
                    "pk": app.get("pk"),
                    "name": app.get("name"),
                    "version": app.get("version"),
                    "assembly": app.get("assembly"),
                    "species": app.get("species"),
                    "description": app.get("description"),
                    "application_class": app.get("application_class"),
                    "application_settings": app.get("application_settings", {}),
                    "application_results": app.get("application_results", {}),
                }
            }

        # Otherwise, do a broader search
        search_result = await client.query(
            "applications",
            filters={"name__icontains": query},
            limit=20,
        )

        apps = search_result.get("results", [])

        if not apps:
            return {
                "match_type": "none",
                "message": f"No applications found matching '{query}'",
                "apps": []
            }

        # Return summary list
        return {
            "match_type": "search",
            "count": len(apps),
            "apps": [
                {
                    "pk": app.get("pk"),
                    "name": app.get("name"),
                    "version": app.get("version"),
                    "description": (app.get("description") or "")[:200],
                    "assembly": app.get("assembly"),
                }
                for app in apps
            ]
        }

    @mcp.tool()
    async def get_app_template(
        app_type: str = "single",
        include_dependencies: bool = False,
    ) -> str:
        """
        Get boilerplate code for creating a new Isabl application.

        Generates a complete Python class template with all required methods
        for a new Isabl bioinformatics application.

        Args:
            app_type: Type of application:
                     - "single": Single sample analysis (TARGETS)
                     - "paired": Tumor-normal pair analysis (PAIRS)
                     - "cohort": Multi-sample cohort analysis
            include_dependencies: Whether to include get_dependencies() example

        Returns:
            Python code template as a string

        Example:
            get_app_template("paired", include_dependencies=True)
        """
        # Base template
        template = '''from isabl_cli import AbstractApplication, options


class MyApplication(AbstractApplication):
    """
    Brief description of what this application does.

    This app runs [TOOL_NAME] on [input type] to produce [output type].
    """

    # Required metadata
    NAME = "my_application"
    VERSION = "1.0.0"

    # Optional: restrict to specific assembly/species
    ASSEMBLY = "GRCh38"  # or None for any
    SPECIES = "HUMAN"    # or None for any

    # CLI configuration
    cli_help = "Run my application"
'''

        # Add CLI options based on type
        if app_type == "single":
            template += '    cli_options = [options.TARGETS]\n'
        elif app_type == "paired":
            template += '    cli_options = [options.PAIRS]\n'
        else:
            template += '''    cli_options = [options.TARGETS]
    unique_analysis_per_individual = False  # Allow multiple targets
'''

        # Add settings
        template += '''
    # Configurable settings
    application_settings = {
        "tool_path": "/usr/bin/mytool",
        "threads": 4,
        "memory_gb": 16,
    }

    # Define expected results
    application_results = {
        "output_file": {
            "frontend_type": "text-file",
            "description": "Main output file",
            "verbose_name": "Output",
        }
    }
'''

        # Add validation
        if app_type == "paired":
            template += '''
    def validate_experiments(self, targets, references):
        """Validate input experiments."""
        assert len(targets) == 1, "Requires exactly one tumor"
        assert len(references) == 1, "Requires exactly one normal"
        assert targets[0].sample.category == "TUMOR"
        assert references[0].sample.category == "NORMAL"
'''
        else:
            template += '''
    def validate_experiments(self, targets, references):
        """Validate input experiments."""
        assert len(targets) == 1, "Requires exactly one target"
        assert targets[0].technique.method == "WGS", "Only WGS supported"
'''

        # Add dependencies if requested
        if include_dependencies:
            template += '''
    def get_dependencies(self, targets, references, settings):
        """Get results from upstream applications."""
        from isabl_cli import utils

        # Get BAM from alignment app
        bam, bam_analysis = utils.get_result(
            experiment=targets[0],
            application_key=settings.alignment_app_pk,
            result_key="bam"
        )

        return [bam_analysis], {"input_bam": bam}
'''
        else:
            template += '''
    def get_dependencies(self, targets, references, settings):
        """Return dependencies if needed, otherwise empty."""
        return [], {}
'''

        # Add get_command
        if app_type == "paired":
            template += '''
    def get_command(self, analysis, inputs, settings):
        """Generate the shell command to execute."""
        tumor = analysis.targets[0]
        normal = analysis.references[0]
        output_dir = analysis.storage_url

        return f"""
        {settings.tool_path} \\\\
            --tumor {tumor.bam_files["GRCh38"]["url"]} \\\\
            --normal {normal.bam_files["GRCh38"]["url"]} \\\\
            --output {output_dir}/result.vcf \\\\
            --threads {settings.threads}
        """
'''
        else:
            template += '''
    def get_command(self, analysis, inputs, settings):
        """Generate the shell command to execute."""
        target = analysis.targets[0]
        output_dir = analysis.storage_url

        return f"""
        {settings.tool_path} \\\\
            --input {target.bam_files["GRCh38"]["url"]} \\\\
            --output {output_dir}/result.txt \\\\
            --threads {settings.threads}
        """
'''

        # Add get_analysis_results
        template += '''
    def get_analysis_results(self, analysis):
        """Return dict of result paths after completion."""
        return {
            "output_file": f"{analysis.storage_url}/result.txt"
        }
'''

        return template
