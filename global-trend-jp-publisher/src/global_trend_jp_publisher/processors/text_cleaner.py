"""HTML entity and text cleaning utilities."""

from __future__ import annotations

import html
import re


def clean_html_entities(text: str) -> str:
    """Convert HTML entities to readable characters.

    Example:
        &#8230; -> …
        &quot; -> "
        &amp; -> &
    """
    if not text:
        return text
    try:
        return html.unescape(text)
    except Exception:
        return text


def clean_whitespace(text: str) -> str:
    """Normalize whitespace: collapse multiple spaces, trim."""
    if not text:
        return text
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)
    # Remove trailing ellipsis if already clean
    return text.strip()


def strip_html_tags(text: str) -> str:
    """Remove HTML tags, leaving plain text content.

    Example:
        "<p>Hello <b>world</b></p>" -> "Hello world"
    """
    if not text:
        return text
    return clean_whitespace(re.sub(r"<[^>]+>", " ", text))


def dedupe_repeated_text(text: str) -> str:
    """Drop sentences that repeat an earlier one, keeping first occurrence order.

    Some sources (RSS blurbs, scraped snippets) repeat the same sentence
    back-to-back or interleave a duplicated boilerplate line.
    """
    if not text:
        return text
    sentences = re.split(r"(?<=[。.!?！？])\s*", text)
    seen: set[str] = set()
    kept: list[str] = []
    for sentence in sentences:
        if not sentence:
            continue
        key = re.sub(r"\s+", "", sentence.lower())
        if key in seen:
            continue
        seen.add(key)
        kept.append(sentence)
    return " ".join(kept).strip()


def strip_source_suffix(title: str, site_name: str) -> str:
    """Strip a trailing "| Site Name" style suffix from a page title.

    Example:
        strip_source_suffix("Headline | TechCrunch", "TechCrunch") -> "Headline"
    """
    if not title or not site_name:
        return title
    pattern = rf"\s*[\|\-–—:]\s*{re.escape(site_name)}\s*$"
    stripped = re.sub(pattern, "", title, flags=re.IGNORECASE).strip()
    return stripped or title


def truncate_summary(text: str, max_chars: int = 300) -> str:
    """Truncate summary to max_chars, preferring sentence boundaries."""
    if not text or len(text) <= max_chars:
        return text

    # Try sentence-aware truncation
    sentences = re.split(r"(?<=[。.!?！？])\s*", text)
    kept: list[str] = []
    total = 0
    for sent in sentences:
        if not sent:
            continue
        if total + len(sent) > max_chars:
            break
        kept.append(sent)
        total += len(sent)

    if kept:
        result = "".join(kept).strip()
        if result and not result.endswith(("。", ".", "!", "?")):
            result += "…"
        return result

    return text[:max_chars].rstrip() + "…"
