"""CLI for the Isabl knowledge tree pipeline."""

import json
from pathlib import Path

import click

from isabl_knowledge.config import load_config
from isabl_knowledge.llm import get_default_model


@click.group()
@click.option(
    "--config", "-c",
    default="knowledge.yaml",
    type=click.Path(exists=True, path_type=Path),
    help="Path to knowledge.yaml config file.",
)
@click.pass_context
def cli(ctx, config: Path):
    """Isabl Knowledge Tree - extract, organize, and serve platform knowledge."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


@cli.command()
@click.option("--output-dir", "-o", default="data", type=click.Path(path_type=Path))
@click.pass_context
def extract(ctx, output_dir: Path):
    """Extract content from all configured sources."""
    cfg = ctx.obj["config"]
    output_dir.mkdir(parents=True, exist_ok=True)

    all_docs = []
    for source in cfg.sources:
        click.echo(f"Extracting: {source.name} ({source.type})...")
        try:
            from isabl_knowledge.extractors.registry import get_extractor
            extractor = get_extractor(source)
            docs = extractor.extract()
            all_docs.extend(docs)
            click.echo(f"  -> {len(docs)} documents")
        except Exception as e:
            click.echo(f"  -> Skipped: {e}")

    out_file = output_dir / "documents.json"
    out_file.write_text(json.dumps([d.model_dump() for d in all_docs], indent=2))
    click.echo(f"\nTotal: {len(all_docs)} documents saved to {out_file}")


@cli.command()
@click.option("--data-dir", "-d", default="data", type=click.Path(path_type=Path))
@click.option("--model", "-m", default=None)
@click.pass_context
def summarize(ctx, data_dir: Path, model: str):
    """Generate LLM summaries for extracted documents."""
    from isabl_knowledge.models import Document
    from isabl_knowledge.summarizer import summarize_documents

    docs_file = data_dir / "documents.json"
    if not docs_file.exists():
        click.echo(f"No documents found at {docs_file}. Run 'extract' first.")
        return

    raw = json.loads(docs_file.read_text())
    docs = [Document(**d) for d in raw]
    pending = sum(1 for d in docs if not d.summary)
    effective_model = model or get_default_model()
    click.echo(f"Summarizing {pending}/{len(docs)} documents with {effective_model}...")

    summarize_documents(docs, model=model, output_path=docs_file)
    click.echo(f"Summaries saved to {docs_file}")


@cli.command()
@click.option("--data-dir", "-d", default="data", type=click.Path(path_type=Path))
@click.option("--output-dir", "-o", default="output", type=click.Path(path_type=Path))
@click.option("--model", "-m", default=None)
@click.pass_context
def tree(ctx, data_dir: Path, output_dir: Path, model: str):
    """Build the knowledge tree from summaries."""
    from isabl_knowledge.models import Document
    from isabl_knowledge.tree_builder import build_tree

    docs_file = data_dir / "documents.json"
    if not docs_file.exists():
        click.echo(f"No documents found at {docs_file}. Run 'extract' and 'summarize' first.")
        return

    raw = json.loads(docs_file.read_text())
    docs = [Document(**d) for d in raw]
    effective_model = model or get_default_model()
    click.echo(f"Building tree from {len(docs)} documents with {effective_model}...")

    tree_node = build_tree(docs, model=model)

    output_dir.mkdir(parents=True, exist_ok=True)
    tree_file = output_dir / "tree.json"
    tree_file.write_text(json.dumps(tree_node.model_dump(), indent=2))
    click.echo(f"Tree saved to {tree_file}")


@cli.command()
@click.option("--data-dir", "-d", default="data", type=click.Path(path_type=Path))
@click.option("--output-dir", "-o", default="output", type=click.Path(path_type=Path))
@click.pass_context
def publish(ctx, data_dir: Path, output_dir: Path):
    """Render and publish the knowledge tree."""
    from isabl_knowledge.models import Document, TreeNode
    from isabl_knowledge.renderers.github_repo import render_tree_to_repo
    from isabl_knowledge.renderers.html_tree import render_tree_to_html
    from isabl_knowledge.renderers.mermaid import render_tree_to_mermaid

    tree_file = output_dir / "tree.json"
    docs_file = data_dir / "documents.json"

    if not tree_file.exists():
        click.echo(f"No tree found at {tree_file}. Run 'tree' first.")
        return
    if not docs_file.exists():
        click.echo(f"No documents found at {docs_file}. Run 'extract' first.")
        return

    tree_data = json.loads(tree_file.read_text())
    tree_node = TreeNode(**tree_data)

    raw_docs = json.loads(docs_file.read_text())
    docs = {d["doc_id"]: Document(**d) for d in raw_docs}

    site_dir = output_dir / "site"
    click.echo(f"Rendering tree to {site_dir}...")
    render_tree_to_repo(tree_node, docs, site_dir)

    # Generate mermaid visualization
    mermaid_md = output_dir / "TREE.md"
    mermaid_md.write_text(f"# Isabl Knowledge Tree\n\n{render_tree_to_mermaid(tree_node)}\n")
    click.echo(f"Mermaid tree saved to {mermaid_md}")

    # Generate interactive HTML tree
    html_file = output_dir / "tree.html"
    html_file.write_text(render_tree_to_html(tree_node, docs))
    click.echo(f"Interactive tree saved to {html_file}")

    click.echo(f"Site rendered to {site_dir}")


@cli.command()
@click.option("--data-dir", "-d", default="data", type=click.Path(path_type=Path))
@click.option("--output-dir", "-o", default="output", type=click.Path(path_type=Path))
@click.option("--model", "-m", default=None)
@click.pass_context
def build(ctx, data_dir: Path, output_dir: Path, model: str):
    """Run the full pipeline: extract -> summarize -> tree -> publish."""
    ctx.invoke(extract, output_dir=data_dir)
    ctx.invoke(summarize, data_dir=data_dir, model=model)
    ctx.invoke(tree, data_dir=data_dir, output_dir=output_dir, model=model)
    ctx.invoke(publish, data_dir=data_dir, output_dir=output_dir)


@cli.command(name="eval")
@click.option("--data-dir", "-d", default="data", type=click.Path(path_type=Path))
@click.option("--output-dir", "-o", default="output", type=click.Path(path_type=Path))
@click.option("--questions", "-q", default=None, type=click.Path(path_type=Path),
              help="Path to eval_questions.json. If not provided, generates questions.")
@click.option("--count", "-n", default=20, help="Number of questions to generate.")
@click.option("--model", "-m", default=None)
@click.pass_context
def eval_cmd(ctx, data_dir: Path, output_dir: Path, questions: Path | None, count: int, model: str):
    """Evaluate knowledge tree retrieval and answer quality."""
    import asyncio
    from isabl_knowledge.eval import (
        EvalQuestion, evaluate, generate_questions, print_report,
    )
    from isabl_knowledge.models import Document, TreeNode

    tree_file = output_dir / "tree.json"
    docs_file = data_dir / "documents.json"

    if not tree_file.exists():
        click.echo(f"No tree found at {tree_file}. Run 'build' first.")
        return
    if not docs_file.exists():
        click.echo(f"No documents found at {docs_file}. Run 'build' first.")
        return

    tree_data = json.loads(tree_file.read_text())
    tree_node = TreeNode(**tree_data)
    raw_docs = json.loads(docs_file.read_text())
    docs_list = [Document(**d) for d in raw_docs]
    docs_dict = {d.doc_id: d for d in docs_list}

    effective_model = model or get_default_model()

    # Load or generate questions
    if questions and questions.exists():
        click.echo(f"Loading questions from {questions}...")
        q_data = json.loads(questions.read_text())
        eval_questions = [EvalQuestion(**q) for q in q_data]
    else:
        click.echo(f"Generating {count} test questions with {effective_model}...")
        eval_questions = asyncio.run(
            generate_questions(docs_list, count=count, model=model)
        )
        # Save generated questions for reuse
        q_file = output_dir / "eval_questions.json"
        q_file.write_text(json.dumps(
            [{"question": q.question, "expected_doc_ids": q.expected_doc_ids,
              "expected_answer": q.expected_answer, "category": q.category}
             for q in eval_questions],
            indent=2,
        ))
        click.echo(f"Questions saved to {q_file}")

    click.echo(f"\nEvaluating {len(eval_questions)} questions...")

    def on_progress(i, total, question):
        click.echo(f"  [{i}/{total}] {question[:70]}...")

    results = asyncio.run(
        evaluate(eval_questions, tree_node, docs_dict, model=model, on_progress=on_progress)
    )

    # Print and save report
    report = print_report(results)
    report_file = output_dir / "eval_report.md"
    report_file.write_text(report)
    click.echo(f"\nReport saved to {report_file}")

    # Save raw results
    results_file = output_dir / "eval_results.json"
    results_file.write_text(json.dumps(
        [{"question": r.question, "category": r.category,
          "retrieval_recall": r.retrieval_recall,
          "correctness_score": r.correctness_score,
          "retrieved_doc_ids": r.retrieved_doc_ids,
          "expected_doc_ids": r.expected_doc_ids,
          "generated_answer": r.generated_answer,
          "expected_answer": r.expected_answer,
          "judge_reasoning": r.judge_reasoning}
         for r in results],
        indent=2,
    ))

    # Print summary
    total = len(results)
    avg_recall = sum(r.retrieval_recall for r in results) / total if total else 0
    avg_correctness = sum(r.correctness_score for r in results) / total if total else 0
    click.echo(f"\n{'='*50}")
    click.echo(f"  Retrieval Recall: {avg_recall:.0%}")
    click.echo(f"  Answer Correctness: {avg_correctness:.2f}/1.0")
    click.echo(f"  Questions: {total}")
    click.echo(f"{'='*50}")


@cli.command()
@click.option("--output-dir", "-o", default="output", type=click.Path(path_type=Path))
@click.option("--data-dir", "-d", default="data", type=click.Path(path_type=Path))
@click.pass_context
def serve(ctx, output_dir: Path, data_dir: Path):
    """Start the knowledge MCP server."""
    from isabl_knowledge.mcp_server import create_knowledge_server

    tree_file = output_dir / "tree.json"
    docs_file = data_dir / "documents.json"

    if not tree_file.exists():
        click.echo(f"No tree found at {tree_file}. Run 'build' first.")
        return
    if not docs_file.exists():
        click.echo(f"No documents found at {docs_file}. Run 'build' first.")
        return

    server = create_knowledge_server(
        tree_path=tree_file,
        docs_path=docs_file,
    )
    click.echo("Starting Isabl Knowledge MCP server...")
    server.run()
