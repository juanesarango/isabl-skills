"""CLI for the Isabl knowledge tree pipeline."""

from pathlib import Path

import click

from isabl_knowledge.config import load_config


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
@click.pass_context
def extract(ctx):
    """Extract content from all configured sources."""
    cfg = ctx.obj["config"]
    click.echo(f"Extracting from {len(cfg.sources)} sources...")
    for source in cfg.sources:
        click.echo(f"  - {source.name} ({source.type})")
    click.echo("Extract not yet implemented.")


@cli.command()
@click.pass_context
def summarize(ctx):
    """Generate LLM summaries for extracted documents."""
    click.echo("Summarize not yet implemented.")


@cli.command()
@click.pass_context
def tree(ctx):
    """Build the knowledge tree from summaries."""
    click.echo("Tree building not yet implemented.")


@cli.command()
@click.pass_context
def publish(ctx):
    """Render and publish the knowledge tree."""
    click.echo("Publish not yet implemented.")


@cli.command()
@click.pass_context
def build(ctx):
    """Run the full pipeline: extract -> summarize -> tree -> publish."""
    ctx.invoke(extract)
    ctx.invoke(summarize)
    ctx.invoke(tree)
    ctx.invoke(publish)


@cli.command()
@click.pass_context
def serve(ctx):
    """Start the knowledge MCP server."""
    click.echo("MCP server not yet implemented.")
