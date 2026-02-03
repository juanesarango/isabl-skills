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
```

Or create a `.env` file:

```
ISABL_API_URL=https://api.isabl.io/api/v1/
ISABL_API_TOKEN=your-token-here
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
| `search_apps` | Search installed apps by name or purpose |
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

### Testing with local API

1. Start the local Isabl API (using Podman):

```bash
cd ~/isabl/isabl_api && podman compose up -d
```

2. Get an API token from the database:

```bash
podman exec isabl_demo-postgres-1 psql -U postgres -d isabl_demo -c \
  "SELECT t.key, u.username FROM authtoken_token t JOIN auth_user u ON t.user_id = u.id;"
```

3. Test the MCP server tools:

```bash
export ISABL_API_URL="http://localhost:8000/api/v1"
export ISABL_API_TOKEN="your-token-here"
source .venv/bin/activate
python -c "
import asyncio
from isabl_mcp.server import create_server

async def test():
    mcp = create_server()
    tools = mcp._tool_manager._tools
    print('Tools:', list(tools.keys()))
    result = await tools['isabl_query'].fn(endpoint='projects', filters={}, limit=3)
    print('Projects count:', result.get('count'))

asyncio.run(test())
"
```
