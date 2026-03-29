from global_trend_jp_publisher.formatters.post_formatters import format_for_redbook, format_for_x


def test_x_post_respects_limit() -> None:
    long_summary = "a" * 1000
    post = format_for_x("title", long_summary, "https://example.com", "日本視点: 仕事での使い道を足すと良い")
    assert len(post) <= 280
    assert "出典:" in post


def test_x_post_prefers_hook_when_it_fits() -> None:
    post = format_for_x(
        "短いタイトル",
        "これはかなり長い本文です。" * 20,
        "https://example.com",
        "日本視点: 国内比較を一言入れると伝わりやすい。",
    )
    assert "日本視点:" in post
    assert len(post) <= 280


def test_redbook_post_includes_takeaways() -> None:
    post = format_for_redbook(
        "タイトル",
        "これは要約です。",
        "https://example.com",
        "tech",
        ["示唆1", "示唆2"],
    )
    assert "【テックトレンド要約】" in post
    assert "- 示唆1" in post
    assert "- 示唆2" in post
