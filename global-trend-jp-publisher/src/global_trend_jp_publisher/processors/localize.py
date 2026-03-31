from __future__ import annotations

import re

from deep_translator import GoogleTranslator


def summarize_for_japanese_audience(title: str, snippet: str) -> str:
    base = f"{title}。{snippet}".strip()
    base = " ".join(base.split())

    # Keep more context for long image-heavy posts; X output is truncated later in formatter.
    max_chars = 1200
    if len(base) <= max_chars:
        return base

    # Prefer sentence-aware truncation before hard cutoff.
    sentences = re.split(r"(?<=[。.!?！？])\s*", base)
    kept: list[str] = []
    total = 0
    for sentence in sentences:
        if not sentence:
            continue
        if total + len(sentence) > max_chars:
            break
        kept.append(sentence)
        total += len(sentence)
    if kept:
        return "".join(kept).strip() + "..."
    return base[:max_chars].rstrip() + "..."


def expand_summary(title: str, snippet: str) -> str:
    """Expand article summary to 500-1000 characters for better readability.

    Recommended for web display. Keeps sentence boundaries intact.

    Args:
        title: Article title
        snippet: Original snippet or summary

    Returns:
        Expanded summary (500-1000 chars if possible)
    """
    base = f"{title}。{snippet}".strip()
    base = " ".join(base.split())

    # Target: 500-1000 characters
    # Prefer sentence-aware expansion
    min_chars = 500
    target_chars = 800
    max_chars = 1000

    if len(base) >= min_chars:
        # Already long enough
        if len(base) <= max_chars:
            return base
        # Truncate at max
        sentences = re.split(r"(?<=[。.!?！？])\s*", base)
        kept: list[str] = []
        total = 0
        for sentence in sentences:
            if not sentence:
                continue
            if total + len(sentence) > max_chars:
                break
            kept.append(sentence)
            total += len(sentence)
        if kept:
            return "".join(kept).strip()
        return base[:max_chars].rstrip()
    # Too short: add structured context without introducing new factual claims.
    core = base[: target_chars - 80].strip()
    if not core:
        core = "記事本文の要約情報が短いため、主要ポイントのみを掲載しています。"

    sections = [
        core,
        "背景として、この話題はプロダクト機能・ユーザー体験・運用面のいずれに影響するかで評価が分かれます。",
        "注目すべき点は、公開された情報の範囲で何が確定情報で、何が今後の運用や追加発表に依存するかを切り分けることです。",
        "日本での実務観点では、導入コスト、既存ワークフローとの整合性、ユーザーへの説明負荷を合わせて確認するのが有効です。",
        "本要約は元記事の記載範囲に基づく整理であり、数値や仕様は最新の公式情報で最終確認してください。",
    ]

    expanded = " ".join(" ".join(s.split()) for s in sections if s).strip()

    if len(expanded) < min_chars:
        filler = " このトピックは継続的なアップデートが想定されるため、一次情報の更新有無を追跡すると解像度が上がります。"
        while len(expanded) < min_chars:
            expanded += filler

    if len(expanded) <= max_chars:
        return expanded

    sentences = re.split(r"(?<=[。.!?！？])\s*", expanded)
    kept: list[str] = []
    total = 0
    for sentence in sentences:
        if not sentence:
            continue
        if total + len(sentence) > max_chars:
            break
        kept.append(sentence)
        total += len(sentence)
    if kept:
        return "".join(kept).strip()
    return expanded[:max_chars].rstrip()


def rewrite_to_japanese(text: str) -> str:
    if not text:
        return ""
    try:
        return GoogleTranslator(source="auto", target="ja").translate(text)
    except Exception:
        # Fallback keeps workflow running when translator is rate-limited.
        return text
