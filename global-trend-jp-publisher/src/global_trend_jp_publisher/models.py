from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TrendItem:
    source_name: str
    category: str
    title: str
    url: str
    snippet: str
    language: str = "unknown"


@dataclass(slots=True)
class DraftPost:
    title_ja: str
    summary_ja: str
    x_post: str
    redbook_post: str
    takeaways_ja: list[str]
    source_url: str
    source_name: str
    category: str
    needs_fact_check: bool
