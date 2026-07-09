from __future__ import annotations

from global_trend_jp_publisher.config import Settings
from global_trend_jp_publisher.connectors.newsapi import fetch_newsapi_items
from global_trend_jp_publisher.connectors.rss import fetch_rss_items
from global_trend_jp_publisher.formatters.post_formatters import format_for_redbook, format_for_x
from global_trend_jp_publisher.models import DraftPost, TrendItem
from global_trend_jp_publisher.processors.categorize import determine_category
from global_trend_jp_publisher.processors.categorize_enhanced import categorize_article_enhanced
from global_trend_jp_publisher.processors.company_extractor import extract_companies_from_text
from global_trend_jp_publisher.processors.insights import build_japan_takeaways, build_x_japan_hook
from global_trend_jp_publisher.processors.language import detect_language
from global_trend_jp_publisher.processors.localize import (
    rewrite_to_japanese,
    expand_summary,
)
from global_trend_jp_publisher.processors.text_cleaner import (
    clean_html_entities,
    dedupe_repeated_text,
    strip_html_tags,
)
from global_trend_jp_publisher.quality.checks import validate_draft


def collect_items(settings: Settings) -> list[TrendItem]:
    items = list(fetch_rss_items(settings.feed_list(), settings.max_items_per_source))
    items.extend(fetch_newsapi_items(settings.newsapi_key, settings.max_items_per_source))
    return [x for x in items if x.url]


def select_top_items_interleaved(items: list[TrendItem], total: int) -> list[TrendItem]:
    """Cap the item list to ``total`` while keeping a mix of sources.

    Items normally arrive grouped by source (all of feed A, then all of feed
    B, ...). Naively slicing the first N would return articles from a single
    source only. This round-robins across sources instead, so a 5-article
    digest still touches multiple outlets.
    """
    if total <= 0 or len(items) <= total:
        return items

    by_source: dict[str, list[TrendItem]] = {}
    order: list[str] = []
    for item in items:
        if item.source_name not in by_source:
            by_source[item.source_name] = []
            order.append(item.source_name)
        by_source[item.source_name].append(item)

    selected: list[TrendItem] = []
    while len(selected) < total:
        progressed = False
        for source in order:
            if len(selected) >= total:
                break
            bucket = by_source[source]
            if bucket:
                selected.append(bucket.pop(0))
                progressed = True
        if not progressed:
            break
    return selected


def build_drafts(items: list[TrendItem], category_filter: str = "all") -> list[DraftPost]:
    drafts: list[DraftPost] = []
    for item in items:
        item.category = determine_category(item.source_name, item.title, item.snippet, item.url)
        if category_filter != "all" and item.category != category_filter:
            continue
        item.language = detect_language(f"{item.title} {item.snippet}")

        # Clean HTML tags/entities from snippet and drop repeated boilerplate
        # sentences before translation (safety net in case a connector ever
        # hands us raw markup or duplicated text).
        cleaned_snippet = strip_html_tags(item.snippet)
        cleaned_snippet = clean_html_entities(cleaned_snippet)
        cleaned_snippet = dedupe_repeated_text(cleaned_snippet)

        title_ja = rewrite_to_japanese(item.title)
        summary_seed_ja = rewrite_to_japanese(cleaned_snippet)
        # Expand after translation so the final Japanese text reaches the target length.
        summary_ja = expand_summary(title_ja, summary_seed_ja)
        summary_ja = clean_html_entities(summary_ja)
        takeaways_ja = build_japan_takeaways(item.category, title_ja, summary_ja)
        x_hook_ja = build_x_japan_hook(item.category, title_ja, summary_ja)

        # Enhanced: Determine subcategory for better filtering
        subcategory = categorize_article_enhanced(item.title, item.snippet, item.source_name)

        # Extract mentioned companies from title and snippet
        mentioned_companies = extract_companies_from_text(f"{item.title} {item.snippet}")

        draft = DraftPost(
            title_ja=title_ja,
            summary_ja=summary_ja,
            x_post=format_for_x(title_ja, summary_ja, item.url, x_hook_ja),
            redbook_post=format_for_redbook(title_ja, summary_ja, item.url, item.category, takeaways_ja),
            takeaways_ja=takeaways_ja,
            source_url=item.url,
            source_name=item.source_name,
            category=item.category,
            needs_fact_check=True,
            title_original=item.title,
            subcategory=subcategory,
            mentioned_companies=mentioned_companies,
        )
        validate_draft(draft)
        drafts.append(draft)
    return drafts
