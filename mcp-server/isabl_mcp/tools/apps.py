"""Application tools for Isabl MCP Server.

Tools:
- search_apps: Search installed applications via API
- explain_app: Get detailed app explanation
- get_app_template: Get boilerplate code
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from isabl_mcp.clients.isabl_api import IsablAPIClient


def register_app_tools(mcp: FastMCP, client: IsablAPIClient) -> None:
    """Register application tools with the MCP server."""

    @mcp.tool()
    async def search_apps(
        query: str,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for installed Isabl applications.

        Queries the Isabl API for applications matching the search term.
        Applications are user-specific based on INSTALLED_APPLICATIONS config.

        Args:
            query: Search term (e.g., "fusion", "copy number", "alignment", "MUTECT")
            category: Optional category filter. Options:
                     - variant_calling
                     - cnv (copy number)
                     - sv (structural variants)
                     - fusion
                     - alignment
                     - qc
                     - rna
                     - single_cell

        Returns:
            List of matching applications with name, version, and description

        Example:
            search_apps("fusion")
            search_apps("variant", category="variant_calling")
        """
        # Query applications from API
        result = await client.query(
            "applications",
            filters={"name__icontains": query} if query else {},
            limit=50,
        )

        apps = result.get("results", [])
        matches = []

        for app in apps:
            matches.append({
                "pk": app.get("pk"),
                "name": app.get("name"),
                "version": app.get("version"),
                "description": (app.get("description") or "")[:200],
                "assembly": app.get("assembly"),
                "species": app.get("species"),
            })

        # Apply category filter based on name/description keywords
        if category:
            category_keywords = {
                "variant_calling": ["variant", "mutect", "strelka", "gatk", "caller"],
                "cnv": ["cnv", "copy number", "battenberg", "ascat", "facets"],
                "sv": ["sv", "structural", "delly", "manta", "brass"],
                "fusion": ["fusion", "arriba", "starfusion", "fusioncatcher"],
                "alignment": ["align", "bwa", "star", "hisat", "mapping"],
                "qc": ["qc", "quality", "coverage", "fastqc", "metrics"],
                "rna": ["rna", "rsem", "salmon", "expression", "transcript"],
                "single_cell": ["single", "cell", "sc_", "scrnaseq", "scdna"],
            }

            keywords = category_keywords.get(category.lower(), [])
            if keywords:
                matches = [
                    m for m in matches
                    if any(kw in m.get("description", "").lower() or
                           kw in m.get("name", "").lower()
                           for kw in keywords)
                ]

        return matches[:20]  # Limit results

    @mcp.tool()
    async def explain_app(app_name: str) -> Dict[str, Any]:
        """
        Get detailed explanation of an Isabl application.

        Queries the API for application details including settings and results schema.

        Args:
            app_name: Application name (e.g., "MUTECT", "BATTENBERG", "BWA_MEM")

        Returns:
            Detailed application information including:
            - Name, version, assembly, species
            - Description
            - Application settings schema
            - Application results schema

        Example:
            explain_app("MUTECT")
        """
        # Query for the specific application
        result = await client.query(
            "applications",
            filters={"name__iexact": app_name},
            limit=1,
        )

        apps = result.get("results", [])
        if not apps:
            return {"error": f"Application '{app_name}' not found"}

        app = apps[0]
        return {
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
