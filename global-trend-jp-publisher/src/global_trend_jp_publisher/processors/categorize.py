from __future__ import annotations

import re

TECH_KEYWORDS = {
    "ai",
    "software",
    "app",
    "startup",
    "chip",
    "semiconductor",
    "cloud",
    "robot",
    "device",
    "smartphone",
    "social",
    "openai",
    "nvidia",
    "google",
    "meta",
    "microsoft",
}

FINANCE_KEYWORDS = {
    "stock",
    "stocks",
    "market",
    "markets",
    "invest",
    "investor",
    "earnings",
    "gold",
    "silver",
    "bond",
    "fed",
    "rate",
    "inflation",
    "etf",
    "oil",
    "dollar",
    "yen",
}

TECH_SOURCES = {"the verge", "techcrunch", "wired", "the information"}
FINANCE_SOURCES = {"wsj.com: markets", "bloomberg", "financial times", "marketwatch"}

TECH_STRONG_PATTERNS = {
    "artificial intelligence",
    "chatbot",
    "developer",
    "software",
    "app store",
    "smartphone",
    "headset",
    "chipmaker",
    "semiconductor",
    "open source",
}

FINANCE_STRONG_PATTERNS = {
    "stock market",
    "share price",
    "interest rate",
    "treasury yield",
    "federal reserve",
    "etf",
    "commodity",
    "gold price",
    "oil price",
    "earnings report",
}


def _normalize_text(*parts: str) -> str:
    text = " ".join(parts).lower()
    return re.sub(r"\s+", " ", text)


def _keyword_score(text: str, keywords: set[str], weight: int) -> int:
    return sum(weight for keyword in keywords if keyword in text)


def determine_category(source_name: str, title: str, snippet: str, url: str = "") -> str:
    source_lower = source_name.lower()
    title_lower = _normalize_text(title)
    snippet_lower = _normalize_text(snippet)
    url_lower = url.lower()
    text = _normalize_text(source_name, title, snippet, url)

    if any(name in source_lower for name in TECH_SOURCES):
        return "tech"
    if any(name in source_lower for name in FINANCE_SOURCES):
        return "finance"

    tech_score = 0
    finance_score = 0

    tech_score += _keyword_score(title_lower, TECH_KEYWORDS, 3)
    finance_score += _keyword_score(title_lower, FINANCE_KEYWORDS, 3)
    tech_score += _keyword_score(snippet_lower, TECH_KEYWORDS, 1)
    finance_score += _keyword_score(snippet_lower, FINANCE_KEYWORDS, 1)
    tech_score += _keyword_score(text, TECH_STRONG_PATTERNS, 4)
    finance_score += _keyword_score(text, FINANCE_STRONG_PATTERNS, 4)

    if any(token in url_lower for token in ["/gadgets/", "/tech/", "/ai/", "/apps/", "/entertainment/"]):
        tech_score += 3
    if any(token in url_lower for token in ["/markets/", "/business/", "/finance/"]):
        finance_score += 3

    if any(token in text for token in ["nasdaq", "s&p 500", "dow jones", "earnings", "yield", "fx"]):
        finance_score += 4
    if any(token in text for token in ["gpu", "model", "api", "ios", "android", "developer tool"]):
        tech_score += 4

    if finance_score > tech_score:
        return "finance"
    return "tech"