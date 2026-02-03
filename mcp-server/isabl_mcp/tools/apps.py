"""Application tools for Isabl MCP Server.

Tools:
- search_apps: Search application repositories
- explain_app: Get detailed app explanation
- get_app_template: Get boilerplate code
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path
import ast
import re

from mcp.server.fastmcp import FastMCP

from isabl_mcp.config import settings


# Application metadata cache
_app_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None


def _parse_app_class(file_path: Path) -> List[Dict[str, Any]]:
    """Parse an application Python file to extract app metadata."""
    apps = []

    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from AbstractApplication or similar
                bases = [
                    b.id if isinstance(b, ast.Name) else
                    b.attr if isinstance(b, ast.Attribute) else ""
                    for b in node.bases
                ]

                if any("Application" in b for b in bases):
                    app_info: Dict[str, Any] = {
                        "class_name": node.name,
                        "file": str(file_path),
                    }

                    # Extract class attributes
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    name = target.id
                                    if name in ["NAME", "VERSION", "ASSEMBLY", "SPECIES"]:
                                        if isinstance(item.value, ast.Constant):
                                            app_info[name.lower()] = item.value.value

                                    if name == "cli_options":
                                        # Try to extract options
                                        if isinstance(item.value, ast.List):
                                            options = []
                                            for elt in item.value.elts:
                                                if isinstance(elt, ast.Attribute):
                                                    options.append(elt.attr)
                                            app_info["cli_options"] = options

                                    if name == "application_settings":
                                        if isinstance(item.value, ast.Dict):
                                            app_info["has_settings"] = True

                        # Extract docstring
                        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                            if isinstance(item.value.value, str):
                                app_info["docstring"] = item.value.value.strip()

                        # Check for methods
                        if isinstance(item, ast.FunctionDef):
                            if item.name == "get_dependencies":
                                app_info["has_dependencies"] = True
                            if item.name == "validate_experiments":
                                app_info["has_validation"] = True

                    if app_info.get("name"):
                        apps.append(app_info)

    except Exception:
        pass

    return apps


def _scan_app_repository(repo_path: Path, repo_name: str) -> List[Dict[str, Any]]:
    """Scan an application repository for apps."""
    apps = []

    if not repo_path.exists():
        return apps

    # Find Python files
    for py_file in repo_path.rglob("*.py"):
        # Skip test files
        if "test" in py_file.name.lower():
            continue

        parsed = _parse_app_class(py_file)
        for app in parsed:
            app["repo"] = repo_name
            apps.append(app)

    return apps


def _get_all_apps() -> List[Dict[str, Any]]:
    """Get all apps from configured repositories."""
    global _app_cache

    if _app_cache is not None:
        return _app_cache.get("all", [])

    apps = []

    if settings.isabl_apps_path:
        isabl_apps = _scan_app_repository(
            Path(settings.isabl_apps_path), "isabl_apps"
        )
        apps.extend(isabl_apps)

    if settings.shahlab_apps_path:
        shahlab_apps = _scan_app_repository(
            Path(settings.shahlab_apps_path), "shahlab_apps"
        )
        apps.extend(shahlab_apps)

    _app_cache = {"all": apps}
    return apps


def register_app_tools(mcp: FastMCP) -> None:
    """Register application tools with the MCP server."""

    @mcp.tool()
    async def search_apps(
        query: str,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for Isabl applications by name or purpose.

        Searches across isabl_apps (63 production apps) and shahlab_apps
        (111 research apps) to find relevant bioinformatics pipelines.

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
            List of matching applications with name, repo, purpose, and patterns

        Example:
            search_apps("fusion")
            search_apps("variant", category="variant_calling")
        """
        apps = _get_all_apps()
        query_lower = query.lower()

        matches = []
        for app in apps:
            # Search in name, docstring, class_name
            searchable = " ".join([
                str(app.get("name", "")),
                str(app.get("class_name", "")),
                str(app.get("docstring", "")),
            ]).lower()

            if query_lower in searchable:
                # Determine input pattern
                cli_options = app.get("cli_options", [])
                if "PAIRS" in cli_options:
                    input_pattern = "PAIRS"
                elif "REFERENCES" in cli_options:
                    input_pattern = "TARGETS + REFERENCES"
                else:
                    input_pattern = "TARGETS"

                matches.append({
                    "name": app.get("name"),
                    "repo": app.get("repo"),
                    "purpose": (app.get("docstring") or "")[:200],
                    "input_pattern": input_pattern,
                    "has_dependencies": app.get("has_dependencies", False),
                    "version": app.get("version"),
                })

        # Apply category filter
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
                    if any(kw in m.get("purpose", "").lower() or
                           kw in m.get("name", "").lower()
                           for kw in keywords)
                ]

        return matches[:20]  # Limit results

    @mcp.tool()
    async def explain_app(app_name: str) -> Dict[str, Any]:
        """
        Get detailed explanation of an Isabl application.

        Provides comprehensive information about an application including:
        - Purpose and description
        - Input pattern (TARGETS, PAIRS, etc.)
        - Settings and configuration
        - Dependencies on other apps
        - Output results

        Args:
            app_name: Application name (e.g., "MUTECT", "BATTENBERG", "BWA_MEM")

        Returns:
            Detailed application information

        Example:
            explain_app("MUTECT")
        """
        apps = _get_all_apps()
        app_name_lower = app_name.lower()

        for app in apps:
            if app.get("name", "").lower() == app_name_lower:
                # Determine input pattern
                cli_options = app.get("cli_options", [])
                if "PAIRS" in cli_options:
                    input_pattern = "PAIRS (tumor-normal)"
                elif "REFERENCES" in cli_options:
                    input_pattern = "TARGETS + REFERENCES"
                else:
                    input_pattern = "TARGETS (single sample)"

                return {
                    "name": app.get("name"),
                    "version": app.get("version"),
                    "assembly": app.get("assembly"),
                    "species": app.get("species"),
                    "repo": app.get("repo"),
                    "purpose": app.get("docstring"),
                    "input_pattern": input_pattern,
                    "has_settings": app.get("has_settings", False),
                    "has_dependencies": app.get("has_dependencies", False),
                    "has_validation": app.get("has_validation", False),
                    "file": app.get("file"),
                }

        return {"error": f"Application '{app_name}' not found"}

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
