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
