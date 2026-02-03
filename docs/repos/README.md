# Repository Inventory

This document catalogs all Isabl-related repositories and their purposes.

## Core Platform

| Repository | Location | Purpose |
|------------|----------|---------|
| **isabl_cli** | `papaemmelab/isabl_cli` | CLI and Python SDK for data management and pipeline execution |
| **isabl_web** | `~/isabl/isabl_web` | Vue.js frontend for browsing metadata and visualizing results |
| **isabl_api** | `papaemmelab/isabl_api` (private) | Django REST API backend |

## Application Framework

| Repository | Location | Purpose |
|------------|----------|---------|
| **register_apps** | `papaemmelab/register_apps` | CLI for registering versioned containerized applications |
| **cookiecutter-toil** | `papaemmelab/cookiecutter-toil` | Template for creating Toil-based pipelines |
| **toil_container** | `papaemmelab/toil_container` | Toil + Docker/Singularity base container |

## AI/LLM Integration (Existing)

| Repository | Location | Purpose |
|------------|----------|---------|
| **isaibl** | `juanesarango/isaibl` | Experimental RAG + MCP prototype (reference only, not production) |

## Example/Reference

| Repository | Location | Purpose |
|------------|----------|---------|
| **analyses-notebooks** | `juanesarango/analyses-notebooks` | Jupyter notebooks for NGS data analysis |

## Detailed Analyses

- [isabl_cli](./isabl_cli.md) - Full analysis of the CLI and SDK
- [isabl_web](./isabl_web.md) - Full analysis of the web frontend
- [register_apps](./register_apps.md) - Full analysis of the app registration tool
- [isaibl](./isaibl.md) - Full analysis of the existing LLM integration
