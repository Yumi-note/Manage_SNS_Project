from __future__ import annotations

from deep_translator import GoogleTranslator


def summarize_for_japanese_audience(title: str, snippet: str) -> str:
    base = f"{title}。{snippet}".strip()
    if len(base) > 280:
        base = base[:280] + "..."
    return base


def rewrite_to_japanese(text: str) -> str:
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="ja").translate(text)
    except Exception:
        # Fallback keeps workflow running when translator is rate-limited.
        return text
