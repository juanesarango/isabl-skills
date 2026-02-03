"""Data access tools for Isabl MCP Server.

Tools:
- isabl_query: Query any endpoint with filters
- isabl_get_tree: Get individual hierarchy
- isabl_get_results: Get analysis results
- isabl_get_logs: Get analysis logs
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from isabl_mcp.clients.isabl_api import IsablAPIClient


def register_data_tools(mcp: FastMCP, client: IsablAPIClient) -> None:
    """Register data access tools with the MCP server."""

    @mcp.tool()
    async def isabl_query(
        endpoint: str,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Query any Isabl API endpoint with filters.

        Args:
            endpoint: API endpoint to query. Options: experiments, analyses, projects,
                     individuals, samples, applications, techniques, centers, diseases
            filters: Django-style query filters. Examples:
                     - {"projects": 102} - filter by project
                     - {"status": "FAILED"} - filter by status
                     - {"application__name": "MUTECT"} - filter by related field
                     - {"created__gte": "2024-01-01"} - date comparisons
            fields: List of fields to return (optional, returns all if not specified)
            limit: Maximum number of results (default 100)

        Returns:
            API response with count and results list

        Examples:
            # Get failed analyses for a project
            isabl_query("analyses", {"projects": 102, "status": "FAILED"})

            # Get WGS experiments
            isabl_query("experiments", {"technique__method": "WGS"}, limit=50)

            # Get specific fields only
            isabl_query("analyses", {"status": "SUCCEEDED"}, fields=["pk", "results"])
        """
        result = await client.query(
            endpoint=endpoint,
            filters=filters or {},
            fields=fields,
            limit=limit,
        )
        return {
            "count": result.get("count", 0),
            "results": result.get("results", []),
            "has_more": result.get("next") is not None,
        }

    @mcp.tool()
    async def isabl_get_tree(identifier: str) -> Dict[str, Any]:
        """
        Get the complete hierarchy for an individual.

        Returns the full tree: individual → samples → experiments → analyses.
        Useful for understanding all data related to a patient/subject.

        Args:
            identifier: Individual primary key (int) or system_id (string)

        Returns:
            Nested structure with individual, samples, experiments, and their analyses

        Example:
            isabl_get_tree("ISB_H000001")  # by system_id
            isabl_get_tree("123")          # by pk
        """
        return await client.get_tree(identifier)

    @mcp.tool()
    async def isabl_get_results(
        analysis_id: int,
        result_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get result files from an analysis.

        Args:
            analysis_id: Analysis primary key
            result_key: Optional specific result key (e.g., "vcf", "bam", "tsv").
                       If not provided, returns all results.

        Returns:
            Dict with storage_url, status, and results.
            Results contains file paths for each result key.

        Example:
            # Get all results
            isabl_get_results(12345)

            # Get specific result
            isabl_get_results(12345, result_key="vcf")
        """
        data = await client.get_analysis_results(analysis_id)

        if result_key and data.get("results"):
            results = data.get("results", {})
            if result_key in results:
                data["results"] = {result_key: results[result_key]}
            else:
                data["results"] = {
                    "error": f"Result key '{result_key}' not found. "
                    f"Available keys: {list(results.keys())}"
                }

        return data

    @mcp.tool()
    async def isabl_get_logs(
        analysis_id: int,
        log_type: str = "all",
        tail_lines: Optional[int] = None,
    ) -> Dict[str, str]:
        """
        Get execution logs from an analysis.

        Reads log files from the analysis storage directory:
        - head_job.log: Standard output (stdout)
        - head_job.err: Standard error (stderr) - most useful for debugging
        - head_job.sh: The command script that was executed

        Args:
            analysis_id: Analysis primary key
            log_type: Which log to get: "stdout", "stderr", "script", or "all"
            tail_lines: Only return last N lines (optional, useful for large logs)

        Returns:
            Dict with log file contents

        Example:
            # Get all logs
            isabl_get_logs(12345)

            # Get only stderr (most useful for debugging)
            isabl_get_logs(12345, log_type="stderr")

            # Get last 50 lines of stderr
            isabl_get_logs(12345, log_type="stderr", tail_lines=50)
        """
        return await client.get_analysis_logs(
            analysis_pk=analysis_id,
            log_type=log_type,
            tail_lines=tail_lines,
        )
