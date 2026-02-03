# Repository Inventory

This document catalogs all Isabl-related repositories analyzed for AI integration.

## Core Platform

| Repository | Source | Purpose |
|------------|--------|---------|
| **isabl_api** | `papaemmelab/isabl_api` (private) | Django REST API |
| **isabl_cli** | `papaemmelab/isabl_cli` (public)  | CLI and Python SDK |
| **isabl_web** | `papaemmelab/isabl_web` (private) | Vue.js frontend |

## Application Repositories

| Repository | Source | Apps | Purpose |
|------------|--------|------|---------|
| **isabl_apps** | `papaemmelab/isabl_apps` (private) | 63 | Production bioinformatics apps |
| **shahlab_apps** | `shahcompbio/shahlab_apps` (private) | 111 | Research apps (scDNA, scRNA, ONT) |

## Examples

| Repository | Source | Purpose |
|------------|--------|---------|
| **notebooks** | local (private) | 31 Jupyter notebooks with usage patterns |

## Experimental

| Repository | Source | Purpose |
|------------|--------|---------|
| **isaibl** | `juanesarango/isaibl` | Experimental RAG + MCP prototype (reference only) |

## Detailed Analyses

- [isabl_api](./isabl_api.md) - **Django REST API (single source of truth for data model)**
- [isabl_cli](./isabl_cli.md) - CLI and Python SDK
- [isabl_web](./isabl_web.md) - Vue.js frontend
- [isabl_apps](./isabl_apps.md) - 63 production apps
- [shahlab_apps](./shahlab_apps.md) - 111 research apps
- [notebooks](./notebooks.md) - Usage patterns from Jupyter notebooks
- [isaibl](./isaibl.md) - Experimental LLM integration

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total apps | 174 |
| Production apps (isabl_apps) | 63 |
| Research apps (shahlab_apps) | 111 |
| Example notebooks | 31 |
| Claude Code skills | 8 |
| MCP tools (designed) | 10 |
| App categories | Alignment, Variant Calling, CNV, SV, Fusion, QC, scDNA, scRNA, ONT |
