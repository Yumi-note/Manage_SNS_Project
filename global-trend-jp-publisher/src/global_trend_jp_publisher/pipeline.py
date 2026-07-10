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
from global_trend_jp_publisher.processors.grok_summarizer import GrokSummarizerError, GrokSummary, summarize_with_grok
from global_trend_jp_publisher.processors.localize import condense_summary, rewrite_to_japanese
from global_trend_jp_publisher.processors.text_cleaner import (
    clean_html_entities,
    dedupe_repeated_text,
    strip_html_tags,
    truncate_summary,
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


def build_drafts(
    items: list[TrendItem],
    category_filter: str = "all",
    settings: Settings | None = None,
) -> list[DraftPost]:
    settings = settings or Settings()
    drafts: list[DraftPost] = []
    for item in items:
        item.category = determine_category(item.source_name, item.title, item.snippet, item.url)
        if category_filter != "all" and item.category != category_filter:
            continue
        item.language = detect_language(f"{item.title} {item.snippet}")

        # Clean HTML tags/entities from snippet and drop repeated boilerplate
        # sentences before translation/summarization (safety net in case a
        # connector ever hands us raw markup or duplicated text).
        cleaned_snippet = strip_html_tags(item.snippet)
        cleaned_snippet = clean_html_entities(cleaned_snippet)
        cleaned_snippet = dedupe_repeated_text(cleaned_snippet)

        title_ja = rewrite_to_japanese(item.title)

        # Enhanced: Determine subcategory for better filtering; also doubles
        # as a coarse security-relevance fallback when Grok is unavailable.
        subcategory = categorize_article_enhanced(item.title, item.snippet, item.source_name)

        grok_result: GrokSummary | None = None
        if settings.xai_api_key:
            try:
                grok_result = summarize_with_grok(
                    item.title, cleaned_snippet, settings.xai_api_key, settings.grok_model
                )
            except GrokSummarizerError:
                grok_result = None

        if grok_result is not None:
            summary_ja = grok_result.summary_ja
            summary_en = grok_result.summary_en
            security_alert = grok_result.security_important
            security_reason = grok_result.security_reason
        else:
            summary_seed_ja = rewrite_to_japanese(cleaned_snippet)
            # Condense to a ~400-char summary in both languages instead of
            # dumping the full translated body. condense_summary backfills
            # with the title when the body alone is too thin to stand on its own.
            summary_ja = truncate_summary(
                clean_html_entities(condense_summary(title_ja, summary_seed_ja)), max_chars=400
            )
            summary_en = truncate_summary(condense_summary(item.title, cleaned_snippet), max_chars=400)
            security_alert = subcategory == "Security"
            security_reason = (
                "キーワードベースの分類でセキュリティ関連と判定されました（Grok未設定のためフォールバック）"
                if security_alert
                else ""
            )

        takeaways_ja = build_japan_takeaways(item.category, title_ja, summary_ja)
        x_hook_ja = build_x_japan_hook(item.category, title_ja, summary_ja)

        # Extract mentioned companies from title and snippet
        mentioned_companies = extract_companies_from_text(f"{item.title} {item.snippet}")

        draft = DraftPost(
            title_ja=title_ja,
            summary_ja=summary_ja,
            summary_en=summary_en,
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
            security_alert=security_alert,
            security_reason=security_reason,
        )
        validate_draft(draft)
        drafts.append(draft)
    return drafts
