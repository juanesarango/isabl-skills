# Contributing to Isabl Skills

Thanks for your interest in contributing!

## Quick Start

```bash
# Clone the repo
git clone https://github.com/juanesarango/isabl-skills.git
cd isabl-skills

# Install MCP server for development
cd mcp-server
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Adding a New Skill

1. Create `skills/isabl-your-skill.md`
2. Follow the structure of existing skills (YAML frontmatter + workflow steps)
3. Update `skills/README.md` with your skill
4. Update `scripts/install.sh` to include your skill
5. Submit a PR

### Skill Template

```markdown
---
name: isabl-your-skill
description: Brief description of what this skill does
tools: Read, Bash
---

# Your Skill Title

You are helping the user [goal].

## Checklist

1. [ ] Step one
2. [ ] Step two

## Step 1: Title

[Instructions...]
```

## Adding an MCP Tool

1. Add your tool function to the appropriate file in `mcp-server/isabl_mcp/tools/`
2. Register the tool in `server.py`
3. Add tests in `mcp-server/tests/`
4. Update `mcp-server/README.md`
5. Submit a PR

## Code Style

- Python: Follow PEP 8, use type hints
- Use `ruff` for linting
- Use `uv` for dependency management

## Testing

```bash
cd mcp-server
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_api.py  # Specific file
```

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit PR with clear description

## Questions?

Open an issue on GitHub.
