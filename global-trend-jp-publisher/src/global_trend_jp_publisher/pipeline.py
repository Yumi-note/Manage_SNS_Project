from __future__ import annotations

from global_trend_jp_publisher.config import Settings
from global_trend_jp_publisher.connectors.newsapi import fetch_newsapi_items
from global_trend_jp_publisher.connectors.rss import fetch_rss_items
from global_trend_jp_publisher.formatters.post_formatters import format_for_redbook, format_for_x
from global_trend_jp_publisher.models import DraftPost, TrendItem
from global_trend_jp_publisher.processors.categorize import determine_category
from global_trend_jp_publisher.processors.insights import build_japan_takeaways, build_x_japan_hook
from global_trend_jp_publisher.processors.language import detect_language
from global_trend_jp_publisher.processors.localize import rewrite_to_japanese, summarize_for_japanese_audience
from global_trend_jp_publisher.quality.checks import validate_draft


def collect_items(settings: Settings) -> list[TrendItem]:
    items = list(fetch_rss_items(settings.feed_list(), settings.max_items_per_source))
    items.extend(fetch_newsapi_items(settings.newsapi_key, settings.max_items_per_source))
    return [x for x in items if x.url]


def build_drafts(items: list[TrendItem], category_filter: str = "all") -> list[DraftPost]:
    drafts: list[DraftPost] = []
    for item in items:
        item.category = determine_category(item.source_name, item.title, item.snippet, item.url)
        if category_filter != "all" and item.category != category_filter:
            continue
        item.language = detect_language(f"{item.title} {item.snippet}")
        summarized = summarize_for_japanese_audience(item.title, item.snippet)
        summary_ja = rewrite_to_japanese(summarized)
        title_ja = rewrite_to_japanese(item.title)
        takeaways_ja = build_japan_takeaways(item.category, title_ja, summary_ja)
        x_hook_ja = build_x_japan_hook(item.category, title_ja, summary_ja)

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
        )
        validate_draft(draft)
        drafts.append(draft)
    return drafts
