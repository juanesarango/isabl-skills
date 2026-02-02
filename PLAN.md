# Isabl AI Integration Plan

> Teaching AI agents to work with the Isabl genomics platform

## Overview

This repository documents the strategy and implementation for integrating AI coding assistants with the Isabl platform. The approach prioritizes **vendor-neutral solutions** that work across multiple AI tools.

## Repository Inventory

### Core Platform

| Repository | Source | Status | Purpose |
|------------|--------|--------|---------|
| **isabl_cli** | `papaemmelab/isabl_cli` | Cloned | CLI and Python SDK |
| **isabl_web** | Local | Available | Vue.js frontend |
| **isabl_api** | - | Not cloned | Django REST API (referenced in docs) |

### Application Framework

| Repository | Source | Status | Purpose |
|------------|--------|--------|---------|
| **register_apps** | `papaemmelab/register_apps` | Cloned | Versioned app registration |
| **cookiecutter-toil** | `papaemmelab/cookiecutter-toil` | Cloned | Pipeline template |
| **toil_container** | `papaemmelab/toil_container` | Cloned | Toil + Docker/Singularity |

### Experimental/Reference

| Repository | Source | Status | Purpose |
|------------|--------|--------|---------|
| **isaibl** | `juanesarango/isaibl` | Prototype | RAG + MCP server (experimental, not production) |

### Examples

| Repository | Source | Status | Purpose |
|------------|--------|--------|---------|
| **analyses-notebooks** | `juanesarango/analyses-notebooks` | Cloned | Jupyter notebooks |

See [docs/repos/](docs/repos/) for detailed analysis of each repository.

## Integration Strategy

### Portability-First Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                     Portable Layer (MCP)                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Extend isaibl MCP Server                                 │  │
│  │  • Existing: RAG for API docs, API calling                │  │
│  │  • Add: CLI command generation, analysis debugging        │  │
│  │  • Works with: Claude, Cursor, Zed, Sourcegraph, etc.    │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Context Files (Per-Repo)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  AGENTS.md (canonical) → symlinked to:                    │  │
│  │  • CLAUDE.md (Claude Code)                                │  │
│  │  • .cursorrules (Cursor)                                  │  │
│  │  • .github/copilot-instructions.md (GitHub Copilot)       │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                  Tool-Specific Extensions                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Claude Code Skills (optional, Claude-only)               │  │
│  │  • Guided workflows for complex tasks                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Cross-Tool Context File Mapping

| Tool | File | Status |
|------|------|--------|
| Canonical | `AGENTS.md` | Source of truth |
| Claude Code | `CLAUDE.md` | Symlink → AGENTS.md |
| Cursor | `.cursorrules` | Symlink → AGENTS.md |
| GitHub Copilot | `.github/copilot-instructions.md` | Symlink → AGENTS.md |
| Windsurf | `.windsurfrules` | Symlink → AGENTS.md |

## Implementation Phases

### Phase 1: Repository Analysis
- [x] Clone all Isabl repositories
- [x] Document what each repository does
- [x] Identify key patterns, conventions, and APIs

**Completed**: 2026-02-02. See [docs/repos/](docs/repos/).

### Phase 2: Context Files (AGENTS.md)
- [ ] Create AGENTS.md for isabl_cli (SDK usage, query patterns)
- [ ] Create AGENTS.md for isabl_web (Vue patterns, API integration)
- [ ] Create AGENTS.md for register_apps (deployment patterns)
- [ ] Set up symlinks for tool-specific files
- [ ] Test with Claude Code, Cursor

### Phase 3: MCP Server (Production Implementation)
- [ ] Design MCP server architecture (learning from isaibl prototype)
- [ ] Implement core tools: API query, CLI generation, debugging
- [ ] Build RAG system with pluggable backends
- [ ] Add isabl_cli and docs.isabl.io to knowledge base
- [ ] Test across multiple AI tools (Claude, Cursor, Zed)

### Phase 4: Skills (Claude-Specific, Optional)
- [ ] isabl:write-app - Guided application development
- [ ] isabl:debug-analysis - Systematic troubleshooting
- [ ] isabl:query-data - Data retrieval workflows

## Directory Structure

```
~/isabl/
├── isabl-ai-integration/      # This repo
│   ├── PLAN.md                # This file
│   ├── README.md              # Public-facing documentation
│   ├── docs/
│   │   ├── repos/             # Analysis of each repository
│   │   │   ├── README.md      # Inventory
│   │   │   ├── isabl_cli.md
│   │   │   ├── isabl_web.md
│   │   │   ├── register_apps.md
│   │   │   └── isaibl.md
│   │   └── presentation/      # Slides and materials
│   ├── templates/             # AGENTS.md templates
│   ├── mcp-server/            # MCP enhancements (or extend isaibl)
│   └── skills/                # Claude-specific skills
│
├── isabl_cli/                 # papaemmelab/isabl_cli
├── isabl_web/                 # Frontend
├── register_apps/             # papaemmelab/register_apps
├── cookiecutter-toil/         # Pipeline template
├── toil_container/            # Base container
├── isaibl/                    # Existing LLM integration
└── analyses-notebooks/        # Example notebooks
```

## Key Insights from Analysis

### isabl_cli
- Core SDK: `import isabl_cli as ii`
- Query pattern: `ii.get_experiments(projects=102, sample__category="TUMOR")`
- Application framework: Inherit from `AbstractApplication`
- Batch systems: SLURM, LSF, SGE, local

### isabl_web
- Vue.js 2 + Vuetify 2.6 + Vuex
- Token auth in localStorage
- Configuration via `window.$isabl`
- 49 components, panel-based layout

### isaibl (experimental prototype)
- Proof-of-concept for RAG + MCP approach
- Demonstrates dual vector stores pattern
- **Reference implementation, not production code**
- Ideas to learn from for proper implementation

### register_apps
- Deployment tool for versioned containers
- Creates wrapper scripts in `/work/isabl/bin`
- Integrates with virtualenvwrapper

## Next Steps

1. **Create AGENTS.md templates** for isabl_cli and isabl_web
2. **Extend isaibl** with isabl_cli knowledge base
3. **Add MCP tools** for common CLI operations
4. **Test cross-tool** with Claude Code and Cursor

## Resources

- [Isabl Documentation](https://docs.isabl.io)
- [MCP Specification](https://modelcontextprotocol.io)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)

## Timeline

| Date | Milestone |
|------|-----------|
| 2026-02-02 | Project initialized, repos analyzed |
| TBD | Phase 2 complete - AGENTS.md files created |
| TBD | Phase 3 complete - MCP server enhanced |
| TBD | Phase 4 complete - Skills implemented |
