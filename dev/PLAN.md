# Isabl Skills - Development Plan

> Teaching AI agents to work with the Isabl genomics platform

## Goal

Enable AI coding assistants (Claude Code, Cursor, Copilot) to effectively work with Isabl by providing:

1. **Skills** - Guided workflows for complex tasks (Claude Code)
2. **MCP Tools** - Building blocks for data access (all MCP clients)

## Progress

| Phase | Status | What |
|-------|--------|------|
| 1. Repo Analysis | ✓ Complete | Analyzed isabl_api, isabl_cli, isabl_web, isabl_apps, shahlab_apps |
| 2. Skills | ✓ Complete | 8 skills for common workflows |
| 3. MCP Design | ✓ Complete | 8 tools designed based on usage patterns |
| 4. MCP Implementation | ✓ Complete | All 8 tools implemented and tested |
| 5. Local Testing | ✓ Complete | Tested with local API via Podman |
| 6. Repo Structure | ✓ Complete | Clean separation of user/dev files |
| 7. Distribution | ✓ Complete | One-liner curl install for skills |
| 8. Quality & CI | **In Progress** | Tests, linting, GitHub Actions |

## Current State

### Repository Structure
```
isabl-skills/
├── README.md            # User entry point
├── LICENSE              # MIT
├── CLAUDE.md            # Project context for Claude
├── .gitignore
├── .env.example
├── skills/              # 8 Claude Code skills
│   ├── README.md
│   └── isabl-*.md
├── mcp-server/          # 8 MCP tools
│   ├── README.md
│   └── isabl_mcp/
├── scripts/
│   └── install.sh       # curl installer
└── dev/                 # Development notes
    ├── PLAN.md          # This file
    ├── SUMMARY.md
    ├── local-testing.md
    └── reference/       # Isabl repo analysis
```

### MCP Tools (8)

| Category | Tool | Purpose |
|----------|------|---------|
| Data | `isabl_query` | Query any endpoint with filters |
| Data | `isabl_get_tree` | Get individual → samples → experiments hierarchy |
| Data | `isabl_get_results` | Get result files from analysis |
| Data | `isabl_get_logs` | Get execution logs |
| Apps | `get_apps` | Search apps and get details |
| Apps | `get_app_template` | Get boilerplate for new app |
| Aggregation | `merge_results` | Combine results from multiple analyses |
| Aggregation | `project_summary` | Get project statistics |

### Skills (8)

| Skill | Purpose |
|-------|---------|
| `isabl-query-data` | Query patterns and filter syntax |
| `isabl-write-app` | Create new applications |
| `isabl-debug-analysis` | Debug failed analyses |
| `isabl-project-report` | Generate project reports |
| `isabl-merge-results` | Aggregate results |
| `isabl-submit-data` | Submit new data |
| `isabl-monitor-analyses` | Track analysis status |
| `isabl-run-pipeline` | Run multiple apps |

---

## Phase 8: Quality & CI (Current)

### TODO - High Priority

- [x] **Add CONTRIBUTING.md** - Contributor guidelines
- [x] **Fix skill code bugs**
  - `isabl-run-pipeline.md` line 348: added `experiments` parameter
  - `isabl-merge-results.md` line 224: split into proper Python + bash
- [x] **Create GitHub Actions CI**
  - Test MCP server on Python 3.10, 3.11, 3.12, 3.13
  - Lint with ruff
  - Install script syntax check

### TODO - Medium Priority

- [ ] **Expand MCP server tests** - Currently minimal coverage
- [ ] **Standardize skill structure** - Consistent template across all skills

### TODO - Low Priority

- [ ] **Add CHANGELOG.md** - Version history
- [ ] **Publish to PyPI** - `pip install isabl-mcp`
- [ ] **Submit to Context7** - docs.isabl.io for AI search

---

## Quick Commands

```bash
# Install skills
curl -fsSL https://raw.githubusercontent.com/juanesarango/isabl-skills/main/scripts/install.sh | bash

# Start local API (Podman)
cd ~/isabl/isabl_api && podman compose up -d

# Test MCP server
cd mcp-server && uv venv && source .venv/bin/activate
uv pip install -e . && pytest
```

## Links

- **Repo**: https://github.com/juanesarango/isabl-skills
- **Isabl Docs**: https://docs.isabl.io
- **Isabl Paper**: https://link.springer.com/article/10.1186/s12859-020-03879-7
