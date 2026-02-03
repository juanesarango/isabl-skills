# 🤖 🧬 isabl skills

> Claude Code skills and MCP for the Isabl genomics platform

## What is this?

Skills and tools for teaching AI coding assistants to work effectively with [Isabl](https://docs.isabl.io), a platform for the management, analysis, and visualization of genomic data ([paper](https://link.springer.com/article/10.1186/s12859-020-03879-7)).

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/juanesarango/isabl-skills/main/scripts/install.sh | bash
```

## Skills

After installing, use these in Claude Code:

| Skill | Purpose |
|-------|---------|
| `/isabl-write-app` | Create a new Isabl application |
| `/isabl-debug-analysis` | Debug a failed analysis |
| `/isabl-query-data` | Query data from Isabl API |
| `/isabl-project-report` | Generate project status reports |
| `/isabl-merge-results` | Aggregate results across analyses |
| `/isabl-submit-data` | Submit new sequencing data |
| `/isabl-monitor-analyses` | Track analysis status and find issues |
| `/isabl-run-pipeline` | Run multiple apps as a pipeline |

## Components

| Component | Portability | Purpose |
|-----------|-------------|---------|
| **Skills** | Claude Code | Guided workflows for complex tasks (8 skills) |
| **MCP Server** | All MCP clients | Direct tool access to Isabl API (9 tools) |
| **API Docs** | All AI tools | Data model and schema reference |

## MCP Server

See [mcp-server/README.md](mcp-server/README.md) for installation and usage.

## Repository Structure

```
├── skills/              # Claude Code skills (8)
├── scripts/             # Install scripts
├── mcp-server/          # MCP server for Isabl API
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
