# Isabl AI Integration

> Vendor-neutral AI agent integration for the Isabl genomics platform

## What is this?

This repository provides tools and documentation for teaching AI coding assistants (Claude Code, Cursor, GitHub Copilot, etc.) to work effectively with the [Isabl](https://docs.isabl.io) bioinformatics platform.

## Approach

We prioritize **portability** across AI tools:

1. **MCP Server** (Most Portable) - Model Context Protocol works with Claude, Cursor, Zed, Sourcegraph
2. **AGENTS.md** (Canonical Context) - Symlinked to tool-specific files (CLAUDE.md, .cursorrules, etc.)
3. **Skills** (Claude-Specific) - Optional guided workflows for complex tasks

## Quick Start

### For Claude Code Users

1. Configure the MCP server in your Claude Code settings
2. The AGENTS.md files in each Isabl repo provide context automatically

### For Cursor Users

The `.cursorrules` symlinks point to the same AGENTS.md content.

### For Other AI Tools

Check if your tool supports MCP. If so, use the isabl-mcp server.

## Repository Structure

```
├── PLAN.md              # Implementation plan and progress
├── docs/
│   ├── repos/           # Analysis of each Isabl repository
│   └── presentation/    # Slides for presenting this work
├── templates/           # AGENTS.md templates for each repo
├── mcp-server/          # MCP server enhancements
└── skills/              # Claude Code skills (optional)
```

## Current Status

- **Phase 1**: Repository analysis (complete)
- **Phase 2**: AGENTS.md creation (in progress)
- **Phase 3**: MCP server enhancement (planned)
- **Phase 4**: Skills development (planned)

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [isabl_cli](https://github.com/papaemmelab/isabl_cli) | CLI and Python SDK |
| [isaibl](https://github.com/juanesarango/isaibl) | Existing RAG + MCP server |
| [docs.isabl.io](https://docs.isabl.io) | Platform documentation |

## License

MIT
