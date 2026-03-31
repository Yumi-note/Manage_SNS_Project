from global_trend_jp_publisher.connectors.url_article import (
    _combine_text_candidates,
    _extract_embedded_image_urls,
    _extract_script_text_candidates,
    _is_boilerplate,
    _snippet_needs_ocr,
)


def test_boilerplate_detection_for_xiaohongshu_footer_text() -> None:
    text = "上海ICP番号13030189 営業許可 インターネット文化事業ライセンス"
    assert _is_boilerplate(text)


def test_snippet_needs_ocr_for_short_or_boilerplate() -> None:
    assert _snippet_needs_ocr("短い文章")
    assert _snippet_needs_ocr("上海ICP番号13030189 営業許可")
    assert not _snippet_needs_ocr(
        "これは記事本文として十分な長さを持つ説明テキストで、具体的な内容が含まれています。"
        "日本向けに変換する価値がある情報で、背景、課題、実務上の示唆まで丁寧に述べています。"
    )


def test_extract_script_text_candidates_picks_meaningful_text() -> None:
    html = (
        '{"desc":"上海ICP番号13030189 営業許可"}'
        '{"noteDesc":"AI时代，普通人该把精力放哪里？这篇内容从学习路径和执行策略给出建议。"}'
    )
    candidates = _extract_script_text_candidates(html)
    assert candidates
    assert "AI时代" in candidates[0]


def test_combine_text_candidates_deduplicates_and_limits() -> None:
    combined = _combine_text_candidates(
        [
            "Alpha content paragraph.",
            "Alpha content paragraph.",
            "Beta content paragraph with more details.",
            "Gamma content paragraph with extra details.",
        ],
        max_chars=90,
    )
    assert combined.count("Alpha content paragraph") == 1
    assert "Beta content paragraph" in combined


def test_extract_embedded_image_urls_from_url_default() -> None:
    html = (
        '{"urlDefault":"http:\\u002F\\u002Fexample.com\\u002Fimg1.jpg"}'
        '{"urlDefault":"http:\\u002F\\u002Fexample.com\\u002Fimg2.jpg"}'
    )
    urls = _extract_embedded_image_urls(html)
    assert urls == [
        "https://example.com/img1.jpg",
        "https://example.com/img2.jpg",
    ]
