# Isabl Knowledge Tree

Extract, organize, and serve structured knowledge from the Isabl genomics platform as a navigable tree — for humans and LLMs.

## What It Does

```
Sources (code, docs, APIs)
    → Extract documents
    → Summarize with LLM
    → Organize into a hierarchical tree
    → Serve via MCP / HTML / Markdown
```

The pipeline turns scattered documentation, Python docstrings, Django models, and API specs into a single knowledge tree that an LLM can navigate to find answers.

## Quickstart

```bash
# Install
cd knowledge
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Configure LLM access (pick one)
export OPENAI_API_KEY=sk-...                          # Direct OpenAI
export LLM_BASE_URL=https://gateway.example.com/v1    # Or any OpenAI-compatible API
export LLM_API_KEY=your-key
export LLM_MODEL=gpt-4.1-mini                         # Optional, this is the default

# Run the full pipeline
isabl-knowledge build
```

This will:
1. Clone repos and crawl docs to extract documents
2. Generate LLM summaries for each document
3. Build a hierarchical knowledge tree
4. Render HTML, Mermaid, and markdown outputs

## CLI Commands

| Command | Description |
|---------|-------------|
| `isabl-knowledge extract` | Extract documents from all configured sources |
| `isabl-knowledge summarize` | Generate LLM summaries (skips already-summarized docs) |
| `isabl-knowledge tree` | Build the knowledge tree from summaries |
| `isabl-knowledge publish` | Render tree to HTML, Mermaid, and site directory |
| `isabl-knowledge build` | Run the full pipeline (extract → summarize → tree → publish) |
| `isabl-knowledge eval` | Evaluate retrieval quality with generated test questions |
| `isabl-knowledge serve` | Start the MCP server for LLM access |

Common options: `-d/--data-dir` (default: `data/`), `-o/--output-dir` (default: `output/`), `-m/--model`.

### Running Individual Steps

```bash
# Extract only (useful when adding new sources)
isabl-knowledge extract -o data

# Re-summarize without re-extracting
isabl-knowledge summarize -d data

# Rebuild tree without re-extracting or re-summarizing
isabl-knowledge tree -d data -o output

# Evaluate the tree's retrieval quality
isabl-knowledge eval -d data -o output
isabl-knowledge eval -q output/eval_questions.json    # Reuse saved questions
```

## Configuration

Edit `knowledge.yaml` to define sources:

```yaml
name: isabl-knowledge

sources:
  # Python docstrings and class signatures
  - name: isabl_cli
    type: github_python
    repo: papaemmelab/isabl_cli

  # Gitbook documentation site
  - name: docs
    type: gitbook
    url: https://docs.isabl.io

  # Django models, serializers, views, URLs
  - name: isabl_api
    type: django_api
    repo: papaemmelab/isabl_api

  # OpenAPI / Swagger spec
  - name: api_spec
    type: openapi
    url: data/swagger.json

tree:
  max_depth: 4
  max_nodes: 100
```

### Source Types

| Type | Extracts | Config |
|------|----------|--------|
| `github_python` | Docstrings, function signatures, class definitions | `repo` (GitHub `org/repo`) |
| `gitbook` | Documentation pages via Jina Reader | `url` (site root) |
| `django_api` | Models, serializers, views, URL routing | `repo`, optional `extract: ["branch:name"]` |
| `openapi` | Endpoints, schemas, parameters | `url` (path to JSON spec) |

## Project Structure

```
knowledge/
├── knowledge.yaml          # Pipeline configuration
├── data/
│   └── documents.json      # Extracted + summarized documents
├── output/
│   ├── tree.json            # Knowledge tree structure
│   ├── tree.html            # Interactive D3.js visualization
│   ├── TREE.md              # Mermaid mindmap
│   ├── eval_report.md       # Evaluation results
│   └── site/                # Rendered markdown site
└── src/isabl_knowledge/
    ├── cli.py               # Click CLI
    ├── config.py             # YAML config models
    ├── models.py             # Document and TreeNode models
    ├── llm.py                # LLM client setup and utilities
    ├── summarizer.py         # Async batch summarization
    ├── tree_builder.py       # Tree construction + leaf splitting
    ├── eval.py               # RAG evaluation harness
    ├── mcp_server.py         # MCP server (get_tree, get_node, get_document)
    ├── extractors/           # Source-specific extractors
    │   ├── base.py
    │   ├── github_python.py
    │   ├── gitbook.py
    │   ├── django_api.py
    │   ├── openapi.py
    │   └── registry.py
    └── renderers/            # Output format renderers
        ├── github_repo.py
        ├── html_tree.py
        └── mermaid.py
```

## MCP Server

The knowledge tree can be served as an MCP server for Claude or other LLM tools:

```bash
isabl-knowledge serve -d data -o output
```

This exposes three tools:
- **`get_tree`** — Returns the top-level tree with node summaries
- **`get_node(node_id)`** — Drill into a branch, see children or linked documents
- **`get_document(doc_id)`** — Get full document content

## Evaluation

The eval harness tests whether the knowledge tree provides enough signal for an LLM to find and answer questions correctly:

```bash
# Generate questions and evaluate
isabl-knowledge eval -n 20

# Reuse previously generated questions
isabl-knowledge eval -q output/eval_questions.json
```

It measures:
- **Retrieval recall** — Did the LLM navigate to the right leaf nodes?
- **Answer correctness** — Was the generated answer correct vs. expected? (scored 0.0–1.0)

Results are saved to `output/eval_report.md`.

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run specific test
pytest tests/test_tree_builder.py -v
```

## Adding a New Extractor

1. Create `src/isabl_knowledge/extractors/my_source.py`
2. Subclass `BaseExtractor` and implement `extract() -> list[Document]`
3. Register it in `extractors/registry.py`
4. Add a source entry in `knowledge.yaml`

```python
from isabl_knowledge.extractors.base import BaseExtractor
from isabl_knowledge.models import Document

class MyExtractor(BaseExtractor):
    def extract(self) -> list[Document]:
        # Return a list of Document objects
        return [
            Document(
                doc_id="my-source/page-1",
                source_type="my_source",
                source_url="https://...",
                content="...",
            )
        ]
```
