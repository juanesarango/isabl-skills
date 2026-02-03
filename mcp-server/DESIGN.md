# Isabl MCP Server Design

> MCP server providing AI agents access to Isabl data and operations

## Overview

This MCP server provides 10 tools for AI agents to interact with the Isabl genomics platform. It works with any MCP-compatible client (Claude, Cursor, Zed, etc.).

## Tools (10 total)

### Core Data Tools (4)

#### `isabl_query`

Query any Isabl endpoint with filters.

```python
# Parameters
endpoint: str      # experiments, analyses, projects, individuals, samples, etc.
filters: dict      # Django-style filters (project=102, status="FAILED", etc.)
fields: list[str]  # Optional: limit returned fields
limit: int         # Optional: max results (default 100)

# Example
isabl_query(
    endpoint="analyses",
    filters={"projects": 102, "status": "FAILED", "application__name": "MUTECT"},
    fields=["pk", "status", "targets"],
    limit=50
)
```

#### `isabl_get_tree`

Get complete hierarchy for an individual: individual → samples → experiments → analyses.

```python
# Parameters
identifier: str | int  # Individual pk or system_id

# Returns
{
    "individual": {...},
    "samples": [
        {
            "sample": {...},
            "experiments": [
                {
                    "experiment": {...},
                    "analyses": [...]
                }
            ]
        }
    ]
}
```

#### `isabl_get_results`

Get result files from an analysis.

```python
# Parameters
analysis_id: int           # Analysis pk
result_key: str | None     # Optional: specific result key (e.g., "vcf", "bam")

# Returns
{
    "storage_url": "/path/to/analysis/",
    "results": {
        "vcf": "/path/to/output.vcf.gz",
        "bam": "/path/to/output.bam",
        ...
    }
}
```

#### `isabl_get_logs`

Get execution logs from an analysis.

```python
# Parameters
analysis_id: int           # Analysis pk
log_type: str              # "stdout", "stderr", "script", or "all"
tail_lines: int | None     # Optional: only return last N lines

# Returns
{
    "head_job.log": "...",   # stdout
    "head_job.err": "...",   # stderr
    "head_job.sh": "..."     # command script
}
```

### Application Tools (3)

#### `search_apps`

Search across isabl_apps (63) and shahlab_apps (111) by name or purpose.

```python
# Parameters
query: str           # Search term (e.g., "fusion", "copy number", "alignment")
category: str | None # Optional: filter by category (variant_calling, cnv, fusion, etc.)

# Returns
[
    {
        "name": "STARFUSION",
        "repo": "isabl_apps",
        "purpose": "Find fusions in RNA with STAR-Fusion",
        "input_pattern": "TARGETS",
        "has_dependencies": false
    },
    ...
]
```

#### `explain_app`

Get detailed explanation of an application.

```python
# Parameters
app_name: str        # Application name (e.g., "MUTECT", "BATTENBERG")

# Returns
{
    "name": "MUTECT",
    "version": "1.0.0",
    "purpose": "Somatic variant calling for WGS/WES",
    "input_pattern": "PAIRS",  # or TARGETS
    "settings": {
        "tool_path": "/usr/bin/mutect",
        "threads": 4,
        ...
    },
    "dependencies": ["BWA_MEM"],
    "results": {
        "vcf": "Variant calls in VCF format",
        "maf": "Annotated variants in MAF format"
    }
}
```

#### `get_app_template`

Get boilerplate code for creating a new application.

```python
# Parameters
app_type: str        # "single" (TARGETS), "paired" (PAIRS), or "cohort"
include_dependencies: bool  # Whether to include get_dependencies() example

# Returns
# Complete Python class template with all required methods
```

### Aggregation Tools (2)

#### `merge_results`

Combine result files from multiple analyses into a single dataset.

```python
# Parameters
analysis_ids: list[int]    # List of analysis pks
result_key: str            # Which result to merge (e.g., "pass_tsv", "vcf")
output_format: str         # "dataframe" or "paths"

# Returns (if dataframe)
{
    "columns": ["chrom", "pos", "ref", "alt", "sample", ...],
    "data": [...],
    "row_count": 1500
}

# Returns (if paths)
{
    "files": [
        {"analysis_id": 123, "path": "/path/to/result.tsv"},
        ...
    ]
}
```

#### `project_summary`

Get summary statistics for a project.

```python
# Parameters
project_id: int            # Project pk

# Returns
{
    "project": {"pk": 102, "title": "My Project"},
    "counts": {
        "individuals": 50,
        "samples": 120,
        "experiments": 200,
        "analyses": {
            "total": 1500,
            "by_status": {
                "SUCCEEDED": 1200,
                "FAILED": 50,
                "STARTED": 100,
                "STAGED": 150
            },
            "by_application": {
                "MUTECT": 200,
                "BATTENBERG": 200,
                ...
            }
        }
    },
    "storage_usage_gb": 1500.5
}
```

### Documentation Tool (1)

#### `search_docs`

RAG search across Isabl documentation.

```python
# Parameters
query: str           # Natural language question
source: str | None   # Optional: "docs" (docs.isabl.io), "sdk" (docstrings), or "all"

# Returns
{
    "answer": "To query experiments, use ii.get_experiments(...)...",
    "sources": [
        {"title": "CLI Quickstart", "url": "https://docs.isabl.io/cli"},
        ...
    ]
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MCP Server                               │
│                      (isabl_mcp/server.py)                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Data Tools   │  │ App Tools    │  │ Aggregation + Docs     │ │
│  │              │  │              │  │                        │ │
│  │ • query      │  │ • search     │  │ • merge_results        │ │
│  │ • get_tree   │  │ • explain    │  │ • project_summary      │ │
│  │ • get_results│  │ • template   │  │ • search_docs          │ │
│  │ • get_logs   │  │              │  │                        │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
└─────────┼─────────────────┼──────────────────────┼──────────────┘
          │                 │                      │
          ▼                 ▼                      ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
│ Isabl API       │ │ App Repos       │ │ Knowledge Base          │
│ Client          │ │ (indexed)       │ │ (RAG)                   │
│                 │ │                 │ │                         │
│ • REST calls    │ │ • isabl_apps    │ │ • docs.isabl.io         │
│ • Auth handling │ │ • shahlab_apps  │ │ • SDK docstrings        │
└─────────────────┘ └─────────────────┘ └─────────────────────────┘
```

## Configuration

```python
# Environment variables
ISABL_API_URL=https://api.isabl.io/api/v1/
ISABL_API_TOKEN=your-token
ISABL_APPS_PATH=/path/to/isabl_apps
SHAHLAB_APPS_PATH=/path/to/shahlab_apps

# Optional
ISABL_VERIFY_SSL=true
ISABL_TIMEOUT=30
LOG_LEVEL=INFO
```

## Project Structure

```
mcp-server/
├── DESIGN.md                # This file
├── pyproject.toml
├── isabl_mcp/
│   ├── __init__.py
│   ├── server.py            # MCP server entry point
│   ├── config.py            # Configuration
│   ├── tools/
│   │   ├── data.py          # isabl_query, get_tree, get_results, get_logs
│   │   ├── apps.py          # search_apps, explain_app, get_app_template
│   │   ├── aggregation.py   # merge_results, project_summary
│   │   └── docs.py          # search_docs (RAG)
│   ├── clients/
│   │   ├── isabl_api.py     # Isabl REST client
│   │   └── app_index.py     # App repository indexer
│   └── rag/
│       ├── knowledge_base.py
│       └── ingestion.py
└── tests/
```

## Usage

### Claude Code Integration

```json
{
  "mcpServers": {
    "isabl": {
      "command": "python",
      "args": ["-m", "isabl_mcp.server"],
      "env": {
        "ISABL_API_URL": "https://api.isabl.io/api/v1/",
        "ISABL_API_TOKEN": "${ISABL_TOKEN}"
      }
    }
  }
}
```

### Cursor Integration

```json
{
  "mcp": {
    "servers": {
      "isabl": {
        "command": "python",
        "args": ["-m", "isabl_mcp.server"]
      }
    }
  }
}
```

## Implementation Priority

1. **Phase 1**: Core data tools (`isabl_query`, `get_results`, `get_logs`)
2. **Phase 2**: App tools (`search_apps`, `explain_app`)
3. **Phase 3**: Aggregation (`merge_results`, `project_summary`)
4. **Phase 4**: RAG (`search_docs`)
5. **Phase 5**: Polish (`get_tree`, `get_app_template`)
