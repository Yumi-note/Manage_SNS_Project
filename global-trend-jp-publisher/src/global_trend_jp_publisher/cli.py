from __future__ import annotations

import typer

from global_trend_jp_publisher.config import Settings
from global_trend_jp_publisher.connectors.url_article import fetch_url_item
from global_trend_jp_publisher.models import TrendItem
from global_trend_jp_publisher.pipeline import build_drafts, collect_items
from global_trend_jp_publisher.processors.url_list import load_urls_from_file
from global_trend_jp_publisher.storage.writer import (
    write_outputs,
    write_redbook_only_output,
    write_tech_news_output,
    write_x_only_output,
)
from global_trend_jp_publisher.storage.archive_index import generate_archive_index

app = typer.Typer(help="Generate Japanese-ready trend post drafts for X and Redbook")


def _enrich_items_with_article_text(items: list[TrendItem]) -> list[TrendItem]:
    """Replace short RSS summaries with article-body excerpts when available."""
    enriched: list[TrendItem] = []
    for item in items:
        if not item.url:
            enriched.append(item)
            continue
        try:
            detailed_item = fetch_url_item(item.url)
        except Exception:
            enriched.append(item)
            continue

        enriched.append(
            TrendItem(
                source_name=item.source_name,
                category=item.category,
                title=detailed_item.title if detailed_item.title and detailed_item.title != "(no title)" else item.title,
                url=item.url,
                snippet=detailed_item.snippet or item.snippet,
                language=item.language,
            )
        )

    return enriched


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


@app.command("run-from-url")
def run_from_url(
    url: str = typer.Argument(..., help="Article URL to convert into Japanese drafts"),
    category: str = typer.Option("all", "--category", help="all, tech, finance"),
) -> None:
    settings = Settings()
    if category not in {"all", "tech", "finance"}:
        typer.echo("category must be one of: all, tech, finance")
        raise typer.Exit(code=2)

    try:
        item = fetch_url_item(url)
    except Exception as exc:
        typer.echo(f"Failed to fetch URL: {exc}")
        raise typer.Exit(code=1)

    drafts = build_drafts([item], category_filter=category)
    if not drafts:
        typer.echo(f"No drafts produced for category: {category}")
        raise typer.Exit(code=1)

    out_dir = write_outputs(settings.output_dir, drafts)
    typer.echo(f"Generated {len(drafts)} draft from URL at: {out_dir}")


@app.command("run-from-redbook-url-list")
def run_from_redbook_url_list(
    url_file: str = typer.Argument(..., help="Path to text file containing one Redbook/article URL per line"),
    category: str = typer.Option("all", "--category", help="all, tech, finance"),
) -> None:
    settings = Settings()
    if category not in {"all", "tech", "finance"}:
        typer.echo("category must be one of: all, tech, finance")
        raise typer.Exit(code=2)

    try:
        urls = load_urls_from_file(url_file)
    except Exception as exc:
        typer.echo(f"Failed to read URL file: {exc}")
        raise typer.Exit(code=1)

    if not urls:
        typer.echo("No valid URLs found in url_file")
        raise typer.Exit(code=1)

    items = []
    errors: list[str] = []
    for url in urls:
        try:
            items.append(fetch_url_item(url))
        except Exception as exc:
            errors.append(f"{url} -> {exc}")

    if not items:
        typer.echo("All URL fetches failed")
        for err in errors:
            typer.echo(f"- {err}")
        raise typer.Exit(code=1)

    drafts = build_drafts(items, category_filter=category)
    if not drafts:
        typer.echo(f"No drafts produced for category: {category}")
        raise typer.Exit(code=1)

    out_dir = write_outputs(settings.output_dir, drafts)
    redbook_only_path = write_redbook_only_output(out_dir, drafts)
    x_only_path = write_x_only_output(out_dir, drafts)

    typer.echo(f"Generated {len(drafts)} drafts from {len(items)} URLs at: {out_dir}")
    typer.echo(f"Redbook-only output: {redbook_only_path}")
    typer.echo(f"X-only output: {x_only_path}")
    if errors:
        typer.echo(f"Skipped {len(errors)} URLs due to fetch errors")
        for err in errors:
            typer.echo(f"- {err}")


# Default path to the bundled tech-site RSS feed list
_DEFAULT_TECH_SITES_FILE = "data/inputs/tech_sites.txt"


@app.command("run-tech-news")
def run_tech_news(
    sites_file: str = typer.Option(
        _DEFAULT_TECH_SITES_FILE,
        "--sites-file",
        help="Path to text file with one RSS feed URL per line",
    ),
    max_items: int = typer.Option(5, "--max-items", help="Max articles per source"),
    news_dir: str = typer.Option("data/news", "--news-dir", help="Output directory for digest"),
) -> None:
    """Fetch articles from influential overseas tech sites and write a Japanese digest."""
    from global_trend_jp_publisher.processors.url_list import load_urls_from_file
    from global_trend_jp_publisher.connectors.rss import fetch_rss_items

    try:
        feeds = load_urls_from_file(sites_file)
    except Exception as exc:
        typer.echo(f"Failed to read sites file '{sites_file}': {exc}")
        raise typer.Exit(code=1)

    if not feeds:
        typer.echo(f"No RSS feed URLs found in '{sites_file}'")
        raise typer.Exit(code=1)

    items = list(fetch_rss_items(feeds, limit=max_items))
    if not items:
        typer.echo("No articles fetched. Check RSS feed URLs.")
        raise typer.Exit(code=1)

    items = _enrich_items_with_article_text(items)

    drafts = build_drafts(items, category_filter="tech")
    if not drafts:
        typer.echo("No tech drafts produced from fetched articles.")
        raise typer.Exit(code=1)

    out_dir = write_tech_news_output(news_dir, drafts)
    typer.echo(f"Generated tech news digest ({len(drafts)} articles) at: {out_dir}")
    typer.echo(f"  -> {out_dir / 'index.html'}")

    # Generate/update archive index
    try:
        archive_path = generate_archive_index(news_dir)
        typer.echo(f"✅ Updated archive index: {archive_path}")
    except Exception as e:
        typer.echo(f"⚠️  Archive index update failed: {e}", err=True)


@app.command("generate-archive-index")
def generate_archive_index_cmd(news_dir: str = typer.Option("data/news", "--news-dir", help="News directory")) -> None:
    """Generate or update the archive index for all digests."""
    try:
        archive_path = generate_archive_index(news_dir)
        typer.echo(f"✅ Archive index generated: {archive_path}")
        typer.echo(f"Open in browser: file://{archive_path.absolute()}")
    except Exception as exc:
        typer.echo(f"❌ Failed to generate archive index: {exc}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
