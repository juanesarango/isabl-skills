"""Aggregation tools for Isabl MCP Server.

Tools:
- merge_results: Combine results from multiple analyses
- project_summary: Get project statistics
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from isabl_mcp.clients.isabl_api import IsablAPIClient


def register_aggregation_tools(mcp: FastMCP, client: IsablAPIClient) -> None:
    """Register aggregation tools with the MCP server."""

    @mcp.tool()
    async def merge_results(
        analysis_ids: List[int],
        result_key: str,
        output_format: str = "paths",
    ) -> Dict[str, Any]:
        """
        Combine result files from multiple analyses.

        Collects results from multiple analyses, either returning file paths
        or attempting to merge tabular data into a combined dataset.

        Args:
            analysis_ids: List of analysis primary keys to merge
            result_key: Which result to merge (e.g., "tsv", "vcf", "summary")
            output_format: "paths" returns file paths, "preview" reads first few lines

        Returns:
            If output_format="paths": Dict with list of file paths
            If output_format="preview": Dict with file previews

        Example:
            # Get paths to all VCF files
            merge_results([123, 456, 789], "vcf", output_format="paths")

            # Preview TSV files
            merge_results([123, 456], "tsv", output_format="preview")
        """
        files: List[Dict[str, Any]] = []
        errors: List[str] = []

        for analysis_id in analysis_ids:
            try:
                data = await client.get_analysis_results(analysis_id)
                results = data.get("results", {})
                storage_url = data.get("storage_url")

                # Try to find the result
                if result_key in results:
                    result_value = results[result_key]
                    # Handle different result formats
                    if isinstance(result_value, str):
                        path = result_value
                    elif isinstance(result_value, dict):
                        path = result_value.get("path") or result_value.get("url")
                    else:
                        path = None

                    if path:
                        file_info: Dict[str, Any] = {
                            "analysis_id": analysis_id,
                            "path": path,
                            "status": data.get("status"),
                        }

                        # Add preview if requested
                        if output_format == "preview":
                            file_path = Path(path)
                            if file_path.exists():
                                try:
                                    with open(file_path) as f:
                                        lines = [next(f) for _ in range(5)]
                                    file_info["preview"] = "".join(lines)
                                except Exception as e:
                                    file_info["preview_error"] = str(e)
                            else:
                                file_info["preview_error"] = "File not found"

                        files.append(file_info)
                    else:
                        errors.append(
                            f"Analysis {analysis_id}: Could not extract path from result"
                        )
                elif storage_url:
                    # Try constructing path from storage_url
                    possible_path = Path(storage_url) / f"{result_key}"
                    extensions = ["", ".tsv", ".csv", ".vcf", ".vcf.gz", ".txt"]
                    found = False

                    for ext in extensions:
                        test_path = Path(str(possible_path) + ext)
                        if test_path.exists():
                            file_info = {
                                "analysis_id": analysis_id,
                                "path": str(test_path),
                                "status": data.get("status"),
                            }
                            files.append(file_info)
                            found = True
                            break

                    if not found:
                        errors.append(
                            f"Analysis {analysis_id}: Result key '{result_key}' not found"
                        )
                else:
                    errors.append(f"Analysis {analysis_id}: No storage_url")

            except Exception as e:
                errors.append(f"Analysis {analysis_id}: {str(e)}")

        return {
            "result_key": result_key,
            "total_requested": len(analysis_ids),
            "files_found": len(files),
            "files": files,
            "errors": errors if errors else None,
        }

    @mcp.tool()
    async def project_summary(project_id: int) -> Dict[str, Any]:
        """
        Get summary statistics for a project.

        Provides an overview of a project including:
        - Basic project info (title, description)
        - Counts of experiments and analyses
        - Analysis status breakdown (succeeded, failed, running, etc.)
        - Analysis counts by application
        - Storage usage

        Args:
            project_id: Project primary key

        Returns:
            Comprehensive project summary with counts and statistics

        Example:
            project_summary(102)
        """
        return await client.get_project_summary(project_id)
