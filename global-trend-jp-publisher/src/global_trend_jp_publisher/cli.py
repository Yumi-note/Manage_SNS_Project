from __future__ import annotations

import typer

from global_trend_jp_publisher.config import Settings
from global_trend_jp_publisher.pipeline import build_drafts, collect_items
from global_trend_jp_publisher.storage.writer import write_outputs

app = typer.Typer(help="Generate Japanese-ready trend post drafts for X and Redbook")


@app.command("list-sources")
def list_sources() -> None:
    settings = Settings()
    typer.echo("Configured RSS feeds:")
    for idx, feed in enumerate(settings.feed_list(), start=1):
        typer.echo(f"  {idx}. {feed}")
    if settings.newsapi_key:
        typer.echo("NewsAPI: enabled")
    else:
        typer.echo("NewsAPI: disabled (set NEWSAPI_KEY in .env)")


@app.command("run-daily")
def run_daily(category: str = typer.Option("all", "--category", help="all, tech, finance")) -> None:
    settings = Settings()
    if category not in {"all", "tech", "finance"}:
        typer.echo("category must be one of: all, tech, finance")
        raise typer.Exit(code=2)
    items = collect_items(settings)
    if not items:
        typer.echo("No trend items found. Check RSS_FEEDS / API settings.")
        raise typer.Exit(code=1)

    drafts = build_drafts(items, category_filter=category)
    if not drafts:
        typer.echo(f"No drafts produced for category: {category}")
        raise typer.Exit(code=1)
    out_dir = write_outputs(settings.output_dir, drafts)
    typer.echo(f"Generated {len(drafts)} drafts at: {out_dir}")


if __name__ == "__main__":
    app()
