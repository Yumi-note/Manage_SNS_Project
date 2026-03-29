from __future__ import annotations

from typing import Iterable

import requests

from global_trend_jp_publisher.models import TrendItem
from global_trend_jp_publisher.processors.categorize import determine_category


def fetch_newsapi_items(api_key: str, limit: int) -> Iterable[TrendItem]:
    if not api_key:
        return []

    url = "https://newsapi.org/v2/top-headlines"
    params = {"language": "en", "category": "business", "pageSize": limit, "apiKey": api_key}
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []

    items: list[TrendItem] = []
    for article in payload.get("articles", []):
        title = article.get("title", "(no title)")
        snippet = article.get("description", "")
        items.append(
            TrendItem(
                source_name=article.get("source", {}).get("name", "NewsAPI"),
                category=determine_category(
                    article.get("source", {}).get("name", "NewsAPI"),
                    title,
                    snippet,
                    article.get("url", ""),
                ),
                title=title,
                url=article.get("url", ""),
                snippet=snippet,
            )
        )
    return items
