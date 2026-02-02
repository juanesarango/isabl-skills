# Isabl MCP Server Design

> Production-quality MCP server for AI agent integration with Isabl

## Overview

This MCP server provides tools for AI agents to interact with the Isabl genomics platform. Unlike the experimental `isaibl` prototype, this implementation prioritizes:

- **Production readiness**: Proper error handling, logging, configuration
- **Modularity**: Pluggable components for LLM providers, vector stores
- **Security**: Optional authentication, configurable SSL
- **Testability**: Unit tests, integration tests, mocks

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MCP Server                              │
│                      (isabl_mcp/server.py)                      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ API Tools    │  │ RAG Tools    │  │ CLI Tools            │  │
│  │              │  │              │  │                      │  │
│  │ • query      │  │ • query_docs │  │ • generate_command   │  │
│  │ • get        │  │ • search     │  │ • explain_app        │  │
│  │ • create     │  │ • stats      │  │ • debug_analysis     │  │
│  │ • update     │  │              │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
└─────────┼─────────────────┼──────────────────────┼──────────────┘
          │                 │                      │
          ▼                 ▼                      ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
│ Isabl API       │ │ Knowledge Base  │ │ CLI Knowledge           │
│ Client          │ │ (RAG)           │ │                         │
│                 │ │                 │ │ • SDK patterns          │
│ • REST calls    │ │ • API docs      │ │ • App templates         │
│ • Auth handling │ │ • User guides   │ │ • Query examples        │
│ • Retry logic   │ │ • CLI docs      │ │                         │
└─────────────────┘ └─────────────────┘ └─────────────────────────┘
```

## Lessons from isaibl Prototype

| Issue in Prototype | Solution |
|-------------------|----------|
| Invalid model name (`gpt-5-mini`) | Validated model config with defaults |
| No database initialization | Auto-create empty DBs, ingestion pipeline |
| SSL verification disabled | Configurable SSL with sensible defaults |
| Broad exception handling | Typed exceptions, structured logging |
| Hardcoded configuration | Single config source with validation |
| No caching | Response caching with TTL |
| No retry logic | Exponential backoff for API calls |
| No document ingestion | CLI tool to index documentation |

## Tools

### Category 1: API Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `isabl_query` | Query experiments, analyses, samples | `endpoint`, `filters`, `fields`, `limit` |
| `isabl_get` | Get single instance by ID | `endpoint`, `id`, `fields` |
| `isabl_create` | Create new instance | `endpoint`, `data` |
| `isabl_update` | Update existing instance | `endpoint`, `id`, `data` |
| `isabl_count` | Count matching records | `endpoint`, `filters` |

### Category 2: RAG/Documentation Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `query_documentation` | Ask questions about Isabl | `question`, `source` (api/docs/cli/all) |
| `search_docs` | Keyword/semantic search | `query`, `doc_type`, `limit` |
| `get_knowledge_stats` | Database statistics | - |

### Category 3: CLI/SDK Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `generate_cli_command` | Generate isabl CLI command | `task_description`, `context` |
| `generate_sdk_code` | Generate Python SDK code | `task_description`, `context` |
| `explain_application` | Explain an AbstractApplication | `app_name` or `app_code` |
| `debug_analysis` | Help debug failed analysis | `analysis_id` or `error_message` |

### Category 4: Utility Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `list_applications` | List registered applications | `filters` |
| `get_analysis_logs` | Fetch analysis stdout/stderr | `analysis_id` |
| `validate_experiments` | Check if experiments are valid for an app | `app_name`, `experiment_ids` |

## Project Structure

```
mcp-server/
├── DESIGN.md                    # This file
├── README.md                    # Usage documentation
├── pyproject.toml               # Project config (PEP 621)
├── requirements.txt             # Pinned dependencies
├── requirements-dev.txt         # Dev dependencies
│
├── isabl_mcp/                   # Main package
│   ├── __init__.py
│   ├── server.py                # MCP server entry point
│   ├── config.py                # Configuration management
│   ├── exceptions.py            # Custom exceptions
│   │
│   ├── tools/                   # Tool implementations
│   │   ├── __init__.py
│   │   ├── base.py              # Base tool class
│   │   ├── api.py               # API tools
│   │   ├── rag.py               # RAG/documentation tools
│   │   ├── cli.py               # CLI/SDK generation tools
│   │   └── utils.py             # Utility tools
│   │
│   ├── clients/                 # External service clients
│   │   ├── __init__.py
│   │   ├── isabl_api.py         # Isabl REST API client
│   │   └── llm.py               # LLM provider abstraction
│   │
│   ├── rag/                     # RAG system
│   │   ├── __init__.py
│   │   ├── knowledge_base.py    # Vector store management
│   │   ├── retriever.py         # Document retrieval
│   │   ├── prompts.py           # Prompt templates
│   │   └── ingestion.py         # Document ingestion pipeline
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logging.py           # Structured logging
│       └── cache.py             # Response caching
│
├── scripts/                     # CLI scripts
│   ├── ingest_docs.py           # Index documentation
│   └── test_server.py           # Manual testing
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_api_tools.py
│   ├── test_rag_tools.py
│   ├── test_cli_tools.py
│   └── test_integration.py
│
└── data/                        # Knowledge base data
    ├── .gitkeep
    └── vectordb/                # Chroma persistence (gitignored)
```

## Configuration

Single source of truth via environment variables with validation:

```python
# isabl_mcp/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Isabl API
    isabl_api_url: str = "https://api.isabl.io/api/v1/"
    isabl_api_token: str  # Required, no default
    isabl_verify_ssl: bool = True
    isabl_timeout: int = 30
    isabl_max_retries: int = 3

    # LLM Provider
    llm_provider: str = "openai"  # openai, anthropic, local
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # RAG System
    embeddings_model: str = "text-embedding-3-small"
    vectordb_path: str = "./data/vectordb"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    similarity_threshold: float = 0.3

    # Server
    server_name: str = "isabl-mcp"
    server_version: str = "1.0.0"
    log_level: str = "INFO"
    cache_ttl: int = 300  # seconds

    class Config:
        env_file = ".env"
        env_prefix = "ISABL_MCP_"
```

## Error Handling

```python
# isabl_mcp/exceptions.py
class IsablMCPError(Exception):
    """Base exception for all MCP errors."""
    pass

class ConfigurationError(IsablMCPError):
    """Invalid configuration."""
    pass

class APIError(IsablMCPError):
    """Isabl API error."""
    def __init__(self, status_code: int, message: str, endpoint: str):
        self.status_code = status_code
        self.endpoint = endpoint
        super().__init__(f"API error {status_code} on {endpoint}: {message}")

class RAGError(IsablMCPError):
    """RAG system error."""
    pass

class ToolError(IsablMCPError):
    """Tool execution error."""
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {message}")
```

## API Client

```python
# isabl_mcp/clients/isabl_api.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class IsablAPIClient:
    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Token {token}"},
            verify=verify_ssl,
            timeout=30.0
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get(self, endpoint: str, **params) -> dict:
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    async def query(self, endpoint: str, filters: dict, fields: list = None, limit: int = 100):
        params = {**filters, "limit": limit}
        if fields:
            params["fields"] = ",".join(fields)
        return await self.get(endpoint, **params)
```

## RAG System

### Knowledge Base Sources

| Source | Content | Update Frequency |
|--------|---------|------------------|
| docs.isabl.io | User guides, tutorials | Weekly |
| isabl_cli docstrings | SDK documentation | On release |
| API OpenAPI spec | Endpoint documentation | On release |
| Example notebooks | Usage patterns | Monthly |

### Ingestion Pipeline

```python
# scripts/ingest_docs.py
async def ingest_documentation():
    """Index all documentation sources."""

    # 1. Fetch docs.isabl.io pages
    pages = await fetch_gitbook_pages("https://docs.isabl.io")

    # 2. Extract isabl_cli docstrings
    docstrings = extract_module_docs("isabl_cli")

    # 3. Parse OpenAPI spec (if available)
    api_docs = parse_openapi_spec("openapi.json")

    # 4. Chunk and embed
    chunks = chunk_documents(pages + docstrings + api_docs)

    # 5. Store in vector database
    vectordb.add_documents(chunks)
```

## Testing Strategy

### Unit Tests
- Mock Isabl API responses
- Mock LLM responses
- Test tool parameter validation
- Test error handling

### Integration Tests
- Test against real Isabl API (staging)
- Test RAG retrieval quality
- Test end-to-end tool execution

### Fixtures

```python
# tests/conftest.py
import pytest
from isabl_mcp.config import Settings

@pytest.fixture
def mock_settings():
    return Settings(
        isabl_api_url="http://localhost:8000/api/v1/",
        isabl_api_token="test-token",
        llm_provider="mock",
        vectordb_path=":memory:"
    )

@pytest.fixture
def mock_api_client(mock_settings):
    # Returns client with mocked responses
    pass
```

## Dependencies

```toml
# pyproject.toml
[project]
name = "isabl-mcp"
version = "1.0.0"
requires-python = ">=3.10"

dependencies = [
    # MCP
    "mcp>=1.0.0,<2.0.0",

    # HTTP
    "httpx>=0.27.0,<1.0.0",
    "tenacity>=8.0.0,<9.0.0",

    # LLM
    "openai>=1.0.0,<2.0.0",
    "anthropic>=0.30.0,<1.0.0",

    # RAG
    "chromadb>=0.5.0,<1.0.0",
    "langchain-core>=0.2.0,<1.0.0",
    "langchain-openai>=0.1.0,<1.0.0",

    # Config
    "pydantic-settings>=2.0.0,<3.0.0",
    "python-dotenv>=1.0.0,<2.0.0",

    # Utils
    "structlog>=24.0.0,<25.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
]
```

## Implementation Phases

### Phase 3a: Foundation (Week 1)
- [ ] Project setup (pyproject.toml, structure)
- [ ] Configuration system with Pydantic
- [ ] Isabl API client with retry logic
- [ ] Basic MCP server with 1 tool (isabl_query)
- [ ] Unit tests for API client

### Phase 3b: API Tools (Week 2)
- [ ] All API tools (query, get, create, update, count)
- [ ] Proper error handling and responses
- [ ] Integration tests with staging API

### Phase 3c: RAG System (Week 3)
- [ ] Knowledge base setup (Chroma)
- [ ] Document ingestion pipeline
- [ ] RAG tools (query_documentation, search_docs)
- [ ] Prompt engineering for Isabl domain

### Phase 3d: CLI Tools (Week 4)
- [ ] CLI command generation
- [ ] SDK code generation
- [ ] Debug analysis tool
- [ ] Application explanation tool

### Phase 3e: Polish (Week 5)
- [ ] Caching layer
- [ ] Logging and monitoring
- [ ] Documentation
- [ ] Cross-tool testing (Claude, Cursor, Zed)

## Usage

### Installation

```bash
cd mcp-server
pip install -e ".[dev]"
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Running

```bash
# Start MCP server
python -m isabl_mcp.server

# Index documentation
python scripts/ingest_docs.py

# Run tests
pytest
```

### Claude Code Integration

```json
// ~/.claude/settings.json or project .claude/settings.json
{
  "mcpServers": {
    "isabl": {
      "command": "python",
      "args": ["-m", "isabl_mcp.server"],
      "cwd": "/path/to/mcp-server",
      "env": {
        "ISABL_MCP_ISABL_API_TOKEN": "${ISABL_API_TOKEN}"
      }
    }
  }
}
```
