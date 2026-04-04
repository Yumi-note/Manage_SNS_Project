from global_trend_jp_publisher.storage.archive_index import generate_archive_index


def test_generate_archive_index_creates_home_and_daily_pages(tmp_path) -> None:
    news_dir = tmp_path / "news"
    digest_dir = news_dir / "2026-04-03" / "120000"
    digest_dir.mkdir(parents=True)
    (digest_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    (digest_dir / "tech_news_digest.json").write_text(
        """
[
  {
    "title_ja": "日本語タイトル",
    "title_original": "Original Title",
    "summary_ja": "本文の日本語訳です。",
    "source_name": "TechCrunch",
    "source_url": "https://example.com/article",
    "subcategory": "AI/ML"
  }
]
""".strip(),
        encoding="utf-8",
    )

    archive_path = generate_archive_index(str(news_dir))

    home_html = archive_path.read_text(encoding="utf-8")
    day_html = (news_dir / "2026-04-03" / "index.html").read_text(encoding="utf-8")

    assert "2026-04-03/index.html" in home_html
    assert "2026-04-03 の記事一覧" in day_html
    assert "日本語タイトル" in day_html
    assert "AI/ML" in day_html