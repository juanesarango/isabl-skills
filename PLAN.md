# Isabl AI Integration Plan

> Teaching AI agents to work with the Isabl genomics platform

## Goal

Enable AI coding assistants (Claude, Cursor, Copilot) to effectively work with Isabl by providing:

1. **Context files** (AGENTS.md) - Tell AI about Isabl patterns and conventions
2. **Skills** (Claude-only) - Guided workflows for complex tasks
3. **MCP Server** - Direct tool access to query API, search docs, generate code

## Progress

| Phase | Status | What |
|-------|--------|------|
| 1. Repo Analysis | ✓ Complete | Documented isabl_cli, isabl_web, register_apps patterns |
| 2. AGENTS.md | ✓ Complete | Created templates, deploy script |
| 3. Skills | ✓ Complete | 3 skills: write-app, debug-analysis, query-data |
| 4. Local Testing | ✓ Complete | Docker setup, isabl-cli configured |
| 5. MCP Server | **Next** | See `mcp-server/DESIGN.md` |

## Repository Structure

```
isabl-ai-integration/
├── PLAN.md                    # This file
├── README.md                  # User-facing docs
├── docs/
│   ├── repos/                 # Analysis of each Isabl repo
│   └── local-testing.md       # How to run local API
├── templates/                 # AGENTS.md for each repo
│   ├── isabl_cli.md
│   ├── isabl_web.md
│   └── register_apps.md
├── skills/                    # Claude Code skills
│   ├── isabl-write-app.md
│   ├── isabl-debug-analysis.md
│   └── isabl-query-data.md
├── scripts/
│   ├── install-skills.sh      # Install skills to ~/.claude/skills/
│   └── deploy-agents-md.sh    # Deploy AGENTS.md to repos
└── mcp-server/
    └── DESIGN.md              # MCP server architecture
```

## Cloned Repositories

All in `~/isabl/`:

| Repo | Source | Purpose |
|------|--------|---------|
| isabl_cli | papaemmelab | CLI and Python SDK |
| isabl_web | local | Vue.js frontend |
| isabl_api | papaemmelab (private) | Django REST API |
| register_apps | papaemmelab | App deployment |
| isaibl | juanesarango | Experimental RAG prototype (reference only) |

## Key Patterns

### isabl_cli SDK

```python
import isabl_cli as ii

# Query
experiments = ii.get_experiments(projects=102, sample__category="TUMOR")

# Single instance
exp = ii.Experiment("SAMPLE_001")
analysis = ii.Analysis(12345)

# Applications inherit from AbstractApplication
class MyApp(AbstractApplication):
    NAME = "my_app"
    VERSION = "1.0.0"
```

### Query Filters

| Operator | Example |
|----------|---------|
| `__contains` | `name__contains="tumor"` |
| `__in` | `status__in=["SUCCEEDED","FAILED"]` |
| `__gt/__lt` | `created__gt="2024-01-01"` |
| `!` prefix | `status!="FAILED"` |

## Next Steps

1. **Implement MCP Server** - Follow `mcp-server/DESIGN.md`
   - Start with API tools (query, get, create)
   - Add RAG for documentation
   - Add CLI/SDK code generation

2. **Test Cross-Tool** - Verify with Claude Code and Cursor

## Quick Commands

```bash
# Install skills
./scripts/install-skills.sh

# Deploy AGENTS.md to repos
./scripts/deploy-agents-md.sh

# Start local API (Docker)
cd ~/isabl/isabl_api && docker compose up -d

# Test CLI with local API
export ISABL_API_URL="http://localhost:8000/api/v1/"
python3 -c "import isabl_cli as ii; print(list(ii.get_experiments()))"
```
