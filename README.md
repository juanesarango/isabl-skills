# Isabl AI Integration

> AI agent integration for the Isabl genomics platform

## What is this?

Tools and documentation for teaching AI coding assistants (Claude Code, Cursor, GitHub Copilot) to work effectively with [Isabl](https://docs.isabl.io).

## Components

| Component | Portability | Purpose |
|-----------|-------------|---------|
| **MCP Server** | All MCP clients | Direct tool access to Isabl API (10 tools) |
| **Skills** | Claude Code only | Guided workflows for complex tasks (8 skills) |
| **API Docs** | All AI tools | Data model and schema reference |

## Quick Start

### Install Skills (Claude Code)

```bash
./scripts/install-skills.sh
```

Then in Claude Code:
- `/isabl-write-app` - Create a new Isabl application
- `/isabl-debug-analysis` - Debug a failed analysis
- `/isabl-query-data` - Query data from Isabl
- `/isabl-project-report` - Generate project status reports
- `/isabl-merge-results` - Aggregate results from multiple analyses
- `/isabl-submit-data` - Submit new sequencing data
- `/isabl-monitor-analyses` - Track analysis status and find issues
- `/isabl-run-pipeline` - Run multiple apps as a pipeline

### MCP Server (Coming Soon)

See `mcp-server/DESIGN.md` for architecture.

## Repository Structure

```
├── skills/              # Claude Code skills
├── scripts/             # Install script
├── mcp-server/          # MCP server (in development)
└── docs/
    ├── repos/           # Analysis of Isabl repositories
    └── local-testing.md # Run local API for testing
```

## Related

- [Isabl Documentation](https://docs.isabl.io)
- [isabl_cli](https://github.com/papaemmelab/isabl_cli) - CLI and Python SDK
- [MCP Specification](https://modelcontextprotocol.io)

## License

MIT
