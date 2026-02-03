# Isabl AI Integration Plan

> Teaching AI agents to work with the Isabl genomics platform

## Goal

Enable AI coding assistants (Claude, Cursor, Copilot) to effectively work with Isabl by providing:

1. **MCP Tools** - Building blocks for data access (works in all AI clients)
2. **Skills** - Guided workflows for complex tasks (Claude Code)

## Progress

| Phase | Status | What |
|-------|--------|------|
| 1. Repo Analysis | ✓ Complete | Analyzed isabl_api, isabl_cli, isabl_web, register_apps, isabl_apps, shahlab_apps |
| 2. Skills (v4) | ✓ Complete | 8 skills: write-app, debug-analysis, query-data, project-report, merge-results, submit-data, monitor-analyses, run-pipeline |
| 3. Local Testing | ✓ Complete | Docker setup, isabl-cli configured |
| 4. Resource Analysis | ✓ Complete | Analyzed 174 apps, 31 notebooks, docs.isabl.io |
| 5. MCP Design (v2) | ✓ Complete | 10 tools designed based on real usage patterns |
| 6. MCP Implementation | ✓ Complete | 9 tools implemented (search_docs pending) |
| 7. Testing | **Next** | Test with local API and cross-tool validation |

## Architecture: Hybrid Approach

```
┌─────────────────────────────────────────────────────────┐
│                    Skills (Claude Code)                  │
│  Complex guided workflows that use MCP tools internally  │
└────────────────────────┬────────────────────────────────┘
                         │ uses
┌────────────────────────▼────────────────────────────────┐
│                    MCP Tools (All Clients)               │
│  Building blocks for data access and operations          │
└─────────────────────────────────────────────────────────┘
```

## MCP Tools (10 total)

### Core Data Tools

| Tool | Purpose |
|------|---------|
| `isabl_query` | Query any endpoint (experiments, analyses, projects, etc.) with filters |
| `isabl_get_tree` | Get individual → samples → experiments → analyses hierarchy |
| `isabl_get_results` | Get result files (VCF, TSV, etc.) from an analysis |
| `isabl_get_logs` | Get head_job.log/err/sh from analysis storage |

### Application Tools

| Tool | Purpose |
|------|---------|
| `search_apps` | Search 174 apps in isabl_apps + shahlab_apps by name/purpose |
| `explain_app` | Describe app: settings, inputs, outputs, dependencies |
| `get_app_template` | Return boilerplate code for writing a new app |

### Aggregation Tools

| Tool | Purpose |
|------|---------|
| `merge_results` | Combine result files from multiple analyses into DataFrame |
| `project_summary` | Get project stats: experiments, analyses by status, storage |

### Documentation Tool

| Tool | Purpose |
|------|---------|
| `search_docs` | RAG search across docs.isabl.io + SDK docstrings |

## Skills (8 total)

| Skill | Audience | Purpose |
|-------|----------|---------|
| `isabl-write-app` | Bioinformaticians | 9-step guide to create AbstractApplication |
| `isabl-debug-analysis` | Both | 8-step systematic debugging of failed analyses |
| `isabl-query-data` | Analysts | Query patterns and filter syntax reference |
| `isabl-project-report` | Analysts | 7-step workflow for project status reports |
| `isabl-merge-results` | Analysts | 7-step guide to aggregate results across analyses |
| `isabl-submit-data` | Both | 8-step workflow to submit new sequencing data |
| `isabl-monitor-analyses` | Both | 7-step guide to track analysis status and find issues |
| `isabl-run-pipeline` | Both | 7-step workflow to run multiple apps as a pipeline |

## Resources Analyzed

### Application Repositories

| Repo | Apps | Categories |
|------|------|------------|
| isabl_apps | 63 | Alignment, variant calling, CNV, fusions, QC |
| shahlab_apps | 111 | WGS, scDNA, scRNA, ONT, spatial, HMFTools |

### Common App Patterns

- **TARGETS**: Single sample input (33 apps)
- **PAIRS**: Tumor-normal pairs (22 apps)
- **Dependencies**: Apps that chain results from other apps (28 apps)

### Notebooks (31 total)

| Category | Count | Common Patterns |
|----------|-------|-----------------|
| Data fetching | 7 | `ii.get_analyses(filters...)` |
| Visualization | 8 | HPC benchmarks, caller agreement |
| Result merging | 3 | Combine TSVs from multiple analyses |
| Job management | 6 | Status tracking, restart commands |
| Project analysis | 3 | Storage footprint, metrics |

## Repository Structure

```
isabl-ai-integration/
├── PLAN.md                    # This file
├── SUMMARY.md                 # What we built and why
├── README.md                  # User-facing docs
├── docs/
│   ├── repos/                 # Analysis of Isabl repositories
│   └── local-testing.md       # Docker setup
├── skills/                    # Isabl user skills (installed globally)
├── .claude/skills/            # Project dev skills (local only)
├── scripts/
│   └── install-skills.sh      # Install skills to ~/.claude/skills/
└── mcp-server/
    └── DESIGN.md              # MCP server architecture
```

## Cloned Repositories

All in `~/isabl/`:

| Repo | Source | Content |
|------|--------|---------|
| isabl_cli | papaemmelab | CLI and Python SDK |
| isabl_web | local | Vue.js frontend |
| isabl_api | papaemmelab (private) | Django REST API |
| isabl_apps | papaemmelab | 63 production apps |
| shahlab_apps | shahcompbio | 111 research apps |
| notebooks | local | 31 example notebooks |

## Quick Commands

```bash
# Install user skills
./scripts/install-skills.sh

# Start local API
cd ~/isabl/isabl_api && docker compose up -d

# Test CLI
export ISABL_API_URL="http://localhost:8000/api/v1/"
python3 -c "import isabl_cli as ii; print(list(ii.get_experiments()))"
```
