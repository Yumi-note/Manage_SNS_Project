from __future__ import annotations

from typing import Iterable

import feedparser

from global_trend_jp_publisher.models import TrendItem
from global_trend_jp_publisher.processors.categorize import determine_category


def fetch_rss_items(feed_urls: list[str], limit: int) -> Iterable[TrendItem]:
    for url in feed_urls:
        parsed = feedparser.parse(url)
        source_name = parsed.feed.get("title", url)
        for entry in parsed.entries[:limit]:
            summary = entry.get("summary", "")
            if len(summary) > 500:
                summary = summary[:500] + "..."
            title = entry.get("title", "(no title)")
            yield TrendItem(
                source_name=source_name,
                category=determine_category(source_name, title, summary, entry.get("link", "")),
                title=title,
                url=entry.get("link", ""),
                snippet=summary,
            )
