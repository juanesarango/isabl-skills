# isaibl Analysis

> RAG + MCP Server for LLM-based Isabl Interaction

**Repository**: `juanesarango/isaibl`
**Language**: Python
**Key Tech**: ChromaDB, LangChain, OpenAI, MCP Protocol
**Status**: Experimental prototype (not production code)

## Purpose

isaibl is an **experimental prototype** exploring LLM-based tools for Isabl. It serves as a proof-of-concept and reference for what a production implementation could look like. Key ideas to learn from:

- RAG system for querying API and user documentation
- MCP server exposing tools to AI agents
- Natural language interface for API calls
- Rich terminal chat interface

## Architecture

```
app/
├── rag.py           # MultiVectorRAGSystem - dual knowledge bases
├── mcp_server.py    # MCP server with 6 tools
├── agent.py         # IsablRAGAgent - high-level interface
├── chat.py          # Rich terminal chat
├── cli.py           # CLI entry point
├── prompts.py       # Prompt templates
└── few_shots.py     # Example API commands
```

## RAG System

### Dual Vector Stores

| Database | Purpose |
|----------|---------|
| `./db/isabl_api` | API operations and schemas |
| `./db/isabl_docs` | User guides and documentation |

### Configuration

```python
RAGConfig(
    chunk_size=1000,
    chunk_overlap=200,
    llm_model="gpt-5-mini",
    embeddings_model="text-embedding-3-small",
    temperature=0.05,
    top_k=5
)
```

## MCP Server Tools

| Tool | Purpose |
|------|---------|
| `call_isabl_api` | Make HTTP calls to Isabl API |
| `query_isabl_api` | Query API documentation |
| `query_isabl_docs` | Query user documentation |
| `query_combined` | Query both databases |
| `search_documents` | Targeted document search |
| `get_database_stats` | Database statistics |

### Server Configuration

```json
{
  "mcpServers": {
    "isabl_rag_api": {
      "command": "python3",
      "args": ["-m", "app.mcp_server"],
      "env": {
        "OPENAI_API_KEY": "...",
        "ISABL_API_URL": "...",
        "ISABL_API_TOKEN": "..."
      }
    }
  }
}
```

## Agent Capabilities

- **Query Routing**: Automatically selects best tool based on question
- **API Calling**: Constructs and executes HTTP requests with auth
- **Multi-step Reasoning**: Up to 10 steps per query
- **Tool Selection**: Uses descriptions to choose approach

## CLI Commands

```bash
python -m app chat     # Interactive chat
python -m app test     # Run tests
python -m app server   # Start MCP server
python -m app agent    # Run agent query
python -m app stats    # Database stats
python -m app tools    # List available tools
```

## Prompt Templates

| Template | Purpose |
|----------|---------|
| default | Standard Q&A |
| detailed | Comprehensive answers |
| concise | Brief responses |
| technical | Technical depth |
| summarize | Summary generation |
| questions | Generate questions |

## Ideas to Learn From

1. **Multi-vector RAG pattern**: Separate knowledge bases for different content types
2. **MCP tool definitions**: Well-structured JSON schemas
3. **Query routing**: Keyword-based fallback to LLM reasoning
4. **Dual knowledge bases**: API schema vs user documentation
5. **Configuration management**: `.env` pattern with dataclasses

## What to Build Differently in Production

The experimental nature revealed areas for improvement:

| Prototype Approach | Production Approach |
|-------------------|---------------------|
| Single-file modules | Proper package structure with separation |
| OpenAI-only embeddings | Pluggable embedding providers |
| ChromaDB local files | Configurable vector store backends |
| Hardcoded prompts | Template system with versioning |
| Basic error handling | Structured error types with recovery |
| No caching | RAG result caching layer |
| Single agent | Multi-agent coordination |

## Key Concepts for AI Agents

1. **RAG-first**: Documentation queries before API calls
2. **Dual knowledge bases**: API schema vs user guides
3. **MCP protocol**: Standard tool interface
4. **Token authentication**: Bearer token for API calls
5. **Async architecture**: All operations are async/await
