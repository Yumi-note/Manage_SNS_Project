from global_trend_jp_publisher.processors.localize import expand_summary, summarize_for_japanese_audience


def test_summarize_keeps_reasonable_length_for_long_input() -> None:
    long_snippet = "。".join(["これは詳細な説明文です" * 8 for _ in range(50)])
    result = summarize_for_japanese_audience("タイトル", long_snippet)
    assert len(result) <= 1203
    assert len(result) > 280


def test_summarize_short_input_unchanged() -> None:
    snippet = "短い説明です。"
    result = summarize_for_japanese_audience("タイトル", snippet)
    assert "タイトル。短い説明です。" in result


def test_expand_summary_reaches_readable_web_length_for_short_input() -> None:
    result = expand_summary("短いタイトル", "これは短い説明です。")
    assert 500 <= len(result) <= 1000
