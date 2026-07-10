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
    title_original: str = ""
    subcategory: str = ""  # Enhanced: AI/ML, Security, Startups, Hardware, etc.
    mentioned_companies: list[str] = None  # New: company names in article
    summary_en: str = ""  # ~400-char English summary, alongside summary_ja
    security_alert: bool = False  # True when a security engineer would find this important
    security_reason: str = ""  # Short justification for security_alert

    def __post_init__(self):
        if self.mentioned_companies is None:
            self.mentioned_companies = []
