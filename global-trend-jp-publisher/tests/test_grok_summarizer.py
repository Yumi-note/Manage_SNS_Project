import json

import pytest
import requests

from global_trend_jp_publisher.processors.grok_summarizer import (
    GrokSummarizerError,
    summarize_with_grok,
)


class _FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def _chat_payload(content: dict) -> dict:
    return {"choices": [{"message": {"content": json.dumps(content)}}]}


def test_summarize_with_grok_raises_without_api_key() -> None:
    with pytest.raises(GrokSummarizerError):
        summarize_with_grok("title", "body", api_key="")


def test_summarize_with_grok_parses_valid_response(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        assert headers["Authorization"] == "Bearer test-key"
        return _FakeResponse(
            _chat_payload(
                {
                    "summary_ja": "日本語要約です。",
                    "summary_en": "English summary.",
                    "security_important": True,
                    "security_reason": "脆弱性の報告があるため。",
                }
            )
        )

    monkeypatch.setattr("global_trend_jp_publisher.processors.grok_summarizer.requests.post", fake_post)

    result = summarize_with_grok("title", "body", api_key="test-key")

    assert result.summary_ja == "日本語要約です。"
    assert result.summary_en == "English summary."
    assert result.security_important is True
    assert result.security_reason == "脆弱性の報告があるため。"


def test_summarize_with_grok_truncates_overlong_summaries(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(
            _chat_payload(
                {
                    "summary_ja": "あ" * 500,
                    "summary_en": "a" * 500,
                    "security_important": False,
                    "security_reason": "",
                }
            )
        )

    monkeypatch.setattr("global_trend_jp_publisher.processors.grok_summarizer.requests.post", fake_post)

    result = summarize_with_grok("title", "body", api_key="test-key")

    assert len(result.summary_ja) == 400
    assert len(result.summary_en) == 400


def test_summarize_with_grok_raises_on_malformed_response(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse({"choices": [{"message": {"content": "not json"}}]})

    monkeypatch.setattr("global_trend_jp_publisher.processors.grok_summarizer.requests.post", fake_post)

    with pytest.raises(GrokSummarizerError):
        summarize_with_grok("title", "body", api_key="test-key")


def test_summarize_with_grok_raises_when_summaries_missing(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        return _FakeResponse(_chat_payload({"security_important": False, "security_reason": ""}))

    monkeypatch.setattr("global_trend_jp_publisher.processors.grok_summarizer.requests.post", fake_post)

    with pytest.raises(GrokSummarizerError):
        summarize_with_grok("title", "body", api_key="test-key")
