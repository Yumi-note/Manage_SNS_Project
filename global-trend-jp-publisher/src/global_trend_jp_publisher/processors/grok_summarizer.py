"""Article summarization via the Grok (xAI) chat completions API."""

from __future__ import annotations

import json
from dataclasses import dataclass

import requests

_API_URL = "https://api.x.ai/v1/chat/completions"
_DEFAULT_TIMEOUT = 30

_SYSTEM_PROMPT = (
    "You are a summarization assistant for a Japanese tech-news digest. "
    "Given an article title and body text, respond with ONLY a single JSON "
    "object (no markdown fences, no commentary) with these exact keys:\n"
    '  "summary_ja": a natural, standalone Japanese summary of the article, at most 400 characters.\n'
    '  "summary_en": a natural, standalone English summary of the article, at most 400 characters.\n'
    '  "security_important": true or false — whether a security engineer would find this '
    "article important (vulnerabilities, breaches, exploits, security tooling/policy with "
    "real operational impact). Routine product news is false.\n"
    '  "security_reason": one short Japanese sentence explaining the security_important verdict '
    '(empty string when false).'
)


class GrokSummarizerError(Exception):
    """Raised when Grok summarization is unavailable or returns an unusable response."""


@dataclass(slots=True)
class GrokSummary:
    summary_ja: str
    summary_en: str
    security_important: bool
    security_reason: str


def summarize_with_grok(
    title: str,
    body: str,
    api_key: str,
    model: str = "grok-4-fast",
    timeout: int = _DEFAULT_TIMEOUT,
) -> GrokSummary:
    """Summarize an article with Grok: ~400-char JA/EN summaries plus a
    security-relevance verdict. Raises ``GrokSummarizerError`` on any failure
    (missing key, network error, bad response) so callers can fall back to
    the rule-based summarizer.
    """
    if not api_key:
        raise GrokSummarizerError("XAI_API_KEY is not configured")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Title: {title}\n\nBody:\n{body}"},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
    }

    try:
        response = requests.post(
            _API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
    except Exception as exc:
        raise GrokSummarizerError(f"Grok summarization request failed: {exc}") from exc

    summary_ja = str(data.get("summary_ja") or "").strip()
    summary_en = str(data.get("summary_en") or "").strip()
    if not summary_ja or not summary_en:
        raise GrokSummarizerError("Grok response is missing summary_ja/summary_en")

    return GrokSummary(
        summary_ja=summary_ja[:400],
        summary_en=summary_en[:400],
        security_important=bool(data.get("security_important", False)),
        security_reason=str(data.get("security_reason") or "").strip(),
    )
