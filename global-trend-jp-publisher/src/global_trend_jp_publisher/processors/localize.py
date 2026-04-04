from __future__ import annotations

import re

from deep_translator import GoogleTranslator


_TRANSLATION_CHUNK_LIMIT = 3000


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split()).strip()


def _truncate_sentences(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    sentences = re.split(r"(?<=[。.!?！？])\s*", text)
    kept: list[str] = []
    total = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if total + len(sentence) > max_chars:
            break
        kept.append(sentence)
        total += len(sentence)

    if kept:
        return " ".join(kept).strip()
    return text[:max_chars].rstrip() + "..."


def _split_for_translation(text: str, max_chars: int = _TRANSLATION_CHUNK_LIMIT) -> list[str]:
    normalized = text.replace("\r\n", "\n")
    paragraphs = [part.strip() for part in re.split(r"\n+", normalized) if part.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            sentences = re.split(r"(?<=[。.!?！？])\s+", paragraph)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if current and len(current) + len(sentence) + 1 > max_chars:
                    chunks.append(current)
                    current = sentence
                elif not current and len(sentence) > max_chars:
                    chunks.append(sentence[:max_chars].rstrip())
                else:
                    current = f"{current} {sentence}".strip()
            continue

        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip() if current else paragraph

    if current:
        chunks.append(current)
    return chunks


def summarize_for_japanese_audience(title: str, snippet: str) -> str:
    base = f"{title}。{snippet}".strip()
    base = _normalize_whitespace(base)

    # Keep more context for long image-heavy posts; X output is truncated later in formatter.
    max_chars = 1200
    if len(base) <= max_chars:
        return base

    # Prefer sentence-aware truncation before hard cutoff.
    truncated = _truncate_sentences(base, max_chars)
    if truncated != base:
        return truncated.rstrip() + "..."
    return truncated


def expand_summary(title: str, snippet: str) -> str:
    """Prepare a readable Japanese excerpt from translated article text."""
    cleaned_paragraphs = [_normalize_whitespace(part) for part in re.split(r"\n+", snippet) if part.strip()]
    if not cleaned_paragraphs:
        return _normalize_whitespace(title)

    excerpt = "\n\n".join(cleaned_paragraphs)
    normalized_title = _normalize_whitespace(title)
    if len(excerpt) < 20 and normalized_title and normalized_title not in excerpt:
        excerpt = f"{normalized_title}。{excerpt}".strip()

    max_chars = 2200
    if len(excerpt) <= max_chars:
        return excerpt

    paragraphs: list[str] = []
    total = 0
    for paragraph in cleaned_paragraphs:
        candidate = _truncate_sentences(paragraph, max_chars=max_chars)
        separator = 2 if paragraphs else 0
        if total + len(candidate) + separator > max_chars:
            break
        paragraphs.append(candidate)
        total += len(candidate) + separator

    if paragraphs:
        return "\n\n".join(paragraphs)
    return _truncate_sentences(excerpt, max_chars=max_chars)


def rewrite_to_japanese(text: str) -> str:
    if not text:
        return ""
    try:
        chunks = _split_for_translation(text)
        if not chunks:
            return ""
        translator = GoogleTranslator(source="auto", target="ja")
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n\n".join(part.strip() for part in translated_chunks if part and part.strip())
    except Exception:
        # Fallback keeps workflow running when translator is rate-limited.
        return text
