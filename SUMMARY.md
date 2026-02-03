# What We Built and Why

## The Problem

Isabl is a genomics platform with private repositories. AI coding assistants (Claude, Cursor, Copilot) don't know how to:
- Query the Isabl API
- Write Isabl applications (pipelines)
- Debug failed analyses
- Use the isabl_cli SDK

## The Solution

Three layers of AI integration, from most portable to most powerful:

### 1. AGENTS.md Files (All AI Tools)

**What**: Markdown files placed in each repository that describe patterns and conventions.

**Why**: Every major AI tool reads these files automatically:
- Claude Code reads `CLAUDE.md`
- Cursor reads `.cursorrules`
- Copilot reads `.github/copilot-instructions.md`

We create one canonical `AGENTS.md` and symlink it to tool-specific names.

**Files created**:
- `templates/isabl_cli.md` - SDK usage, query patterns, application framework
- `templates/isabl_web.md` - Vue.js patterns, API integration
- `templates/register_apps.md` - App deployment patterns

### 2. Skills (Claude Code Only)

**What**: Guided workflows with checklists for complex multi-step tasks.

**Why**: Some tasks are too complex for just context. Writing an Isabl application requires:
- Defining metadata
- Implementing validation
- Setting up dependencies
- Writing the command
- Registering the app

A skill walks through each step systematically.

**Skills created**:
- `isabl-write-app` - Create new Isabl applications
- `isabl-debug-analysis` - Debug failed analyses
- `isabl-query-data` - Query data with the SDK

### 3. MCP Server (All MCP Clients)

**What**: A server that exposes tools AI can call directly.

**Why**: Context files tell AI *about* Isabl, but MCP tools let AI *interact* with Isabl:
- Query experiments directly
- Search documentation
- Generate CLI commands
- Debug analyses by reading logs

**Status**: Designed (`mcp-server/DESIGN.md`), not yet implemented.

## What Was Completed

| Phase | Deliverable |
|-------|-------------|
| Repo Analysis | `docs/repos/*.md` - Understanding of each Isabl repo |
| AGENTS.md | `templates/*.md` - Context files for 3 repos |
| Skills | `skills/*.md` - 3 guided workflows |
| Install Scripts | `scripts/*.sh` - Deploy and install automation |
| Local Testing | `docs/local-testing.md` - Docker setup for API |
| MCP Design | `mcp-server/DESIGN.md` - Architecture for production server |

## What's Next

1. **Implement MCP Server** - The most powerful integration point
2. **Test with Users** - Validate skills and context files work in practice
3. **Cross-Tool Testing** - Verify Cursor and other tools work with AGENTS.md

## Quick Reference

```bash
# Install skills (Claude Code)
./scripts/install-skills.sh

# Deploy context files to repos
./scripts/deploy-agents-md.sh

# Start local API for testing
cd ~/isabl/isabl_api && docker compose up -d

# Test CLI connection
export ISABL_API_URL="http://localhost:8000/api/v1/"
python3 -c "import isabl_cli as ii; print(list(ii.get_experiments()))"
```
