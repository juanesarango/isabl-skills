# What We Built and Why

## The Problem

Isabl is a genomics platform with private repositories. AI coding assistants (Claude, Cursor, Copilot) don't know how to:
- Query the Isabl API (experiments, analyses, projects)
- Write Isabl applications (174 apps across 2 repos)
- Debug failed analyses (read logs, understand errors)
- Merge results from multiple analyses
- Find the right app for a task

## Target Users

| User | Needs |
|------|-------|
| **Bioinformaticians** | Write new apps, debug pipelines, understand existing apps |
| **Analysts/Scientists** | Query data, merge results, generate reports, track jobs |

## The Solution: Hybrid Approach

Two layers that work together:

### Layer 1: MCP Tools (Building Blocks)

Works in **all AI clients** (Claude, Cursor, Copilot, Zed).

| Category | Tools | Purpose |
|----------|-------|---------|
| **Data Access** | `isabl_query`, `isabl_get_tree`, `isabl_get_results`, `isabl_get_logs` | Query API, get hierarchies, fetch files |
| **Applications** | `search_apps`, `explain_app`, `get_app_template` | Find, understand, and create apps |
| **Aggregation** | `merge_results`, `project_summary` | Combine results, get stats |
| **Documentation** | `search_docs` | RAG search across docs |

### Layer 2: Skills (Guided Workflows)

Works in **Claude Code only**. For complex multi-step tasks.

| Skill | Purpose |
|-------|---------|
| `isabl-write-app` | 9-step guide to create an AbstractApplication |
| `isabl-debug-analysis` | 8-step systematic debugging workflow |
| `isabl-query-data` | Query patterns and filter syntax reference |

### Why This Architecture?

```
┌─────────────────────────────────────────────────────────┐
│                    Skills (Claude Code)                  │
│  "Debug this analysis" → walks through 8 steps          │
│  "Write an app" → walks through 9 steps                 │
└────────────────────────┬────────────────────────────────┘
                         │ uses
┌────────────────────────▼────────────────────────────────┐
│                    MCP Tools (All Clients)               │
│  "Get logs for analysis 123" → returns log content      │
│  "Query experiments where project=102" → returns data   │
└─────────────────────────────────────────────────────────┘
```

- **MCP tools** = stateless, single operations, portable
- **Skills** = stateful, multi-step workflows, Claude-only

## Resources Analyzed

| Resource | Content | Insights |
|----------|---------|----------|
| **isabl_apps** | 63 production apps | Patterns: TARGETS, PAIRS, dependencies |
| **shahlab_apps** | 111 research apps | WGS, scDNA, scRNA, ONT, spatial |
| **notebooks** | 31 Jupyter notebooks | Common workflows: query, merge, visualize |
| **docs.isabl.io** | Official documentation | API, CLI, data model |

### What Users Actually Do (from notebooks)

1. **Query & fetch** - Find experiments/analyses with filters
2. **Merge results** - Combine outputs from multiple analyses
3. **Track status** - Monitor failed/pending analyses
4. **Restart jobs** - Re-run with different parameters
5. **Access files** - Navigate storage_url for VCFs, TSVs
6. **Build commands** - Generate CLI commands
7. **Visualize** - HPC benchmarks, project footprints

## Files Created

```
isabl-ai-integration/
├── PLAN.md              # Progress and architecture
├── SUMMARY.md           # This file
├── README.md            # Quick start for users
├── skills/              # User skills (installed globally)
│   ├── isabl-write-app.md
│   ├── isabl-debug-analysis.md
│   └── isabl-query-data.md
├── .claude/skills/      # Dev skills (project-local)
├── templates/           # AGENTS.md for each repo
├── scripts/
│   ├── install-skills.sh
│   └── deploy-agents-md.sh
├── docs/
│   ├── repos/           # Repository analyses
│   └── local-testing.md
└── mcp-server/
    └── DESIGN.md        # MCP server architecture
```

## What's Next

1. **Implement MCP Server** - Build the 10 tools
2. **Add more skills** - merge-results, find-app, project-report
3. **Test cross-tool** - Verify with Claude, Cursor, Copilot

## Quick Reference

```bash
# Install skills (Claude Code)
./scripts/install-skills.sh

# Deploy AGENTS.md to repos
./scripts/deploy-agents-md.sh

# Start local API
cd ~/isabl/isabl_api && docker compose up -d

# Test CLI
export ISABL_API_URL="http://localhost:8000/api/v1/"
python3 -c "import isabl_cli as ii; print(list(ii.get_experiments()))"
```
