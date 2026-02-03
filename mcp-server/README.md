# Isabl MCP Server

MCP server providing AI agents access to the Isabl genomics platform.

## Requirements

- Python 3.10 or higher (required by the MCP SDK)

## Installation

```bash
cd mcp-server
pip install -e .
```

Or with uv:

```bash
cd mcp-server
uv pip install -e .
```

## Configuration

Set environment variables:

```bash
export ISABL_API_URL="https://api.isabl.io/api/v1/"
export ISABL_API_TOKEN="your-token-here"

# Optional: for app search functionality
export ISABL_APPS_PATH="/path/to/isabl_apps"
export ISABL_SHAHLAB_APPS_PATH="/path/to/shahlab_apps"
```

Or create a `.env` file:

```
ISABL_API_URL=https://api.isabl.io/api/v1/
ISABL_API_TOKEN=your-token-here
ISABL_APPS_PATH=/path/to/isabl_apps
ISABL_SHAHLAB_APPS_PATH=/path/to/shahlab_apps
```

## Usage

### Run directly

```bash
python -m isabl_mcp.server
```

### Claude Code Integration

Add to your Claude Code MCP settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "isabl": {
      "command": "python",
      "args": ["-m", "isabl_mcp.server"],
      "env": {
        "ISABL_API_URL": "https://api.isabl.io/api/v1/",
        "ISABL_API_TOKEN": "${ISABL_TOKEN}"
      }
    }
  }
}
```

### Cursor Integration

Add to your Cursor settings:

```json
{
  "mcp": {
    "servers": {
      "isabl": {
        "command": "python",
        "args": ["-m", "isabl_mcp.server"]
      }
    }
  }
}
```

## Tools

### Data Access (4)

| Tool | Description |
|------|-------------|
| `isabl_query` | Query any API endpoint with filters |
| `isabl_get_tree` | Get individual → samples → experiments hierarchy |
| `isabl_get_results` | Get result files from an analysis |
| `isabl_get_logs` | Get execution logs (stdout, stderr, script) |

### Applications (3)

| Tool | Description |
|------|-------------|
| `search_apps` | Search 174 apps by name or purpose |
| `explain_app` | Get detailed app explanation |
| `get_app_template` | Get boilerplate code for new app |

### Aggregation (2)

| Tool | Description |
|------|-------------|
| `merge_results` | Combine results from multiple analyses |
| `project_summary` | Get project statistics |

## Examples

### Query failed analyses

```
isabl_query("analyses", {"projects": 102, "status": "FAILED"})
```

### Get analysis logs for debugging

```
isabl_get_logs(12345, log_type="stderr", tail_lines=50)
```

### Search for fusion detection apps

```
search_apps("fusion")
```

### Get project overview

```
project_summary(102)
```

## Development

### Run tests

```bash
pytest tests/
```

### Local development with hot reload

```bash
python -m isabl_mcp.server
```
