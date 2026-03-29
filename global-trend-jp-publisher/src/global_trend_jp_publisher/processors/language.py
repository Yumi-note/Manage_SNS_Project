from __future__ import annotations

from langdetect import detect


def detect_language(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return "unknown"
    try:
        return detect(cleaned)
    except Exception:
        return "unknown"
