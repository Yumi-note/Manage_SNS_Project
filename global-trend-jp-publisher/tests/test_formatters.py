from datetime import datetime

from global_trend_jp_publisher.formatters.dashboard import generate_dashboard_html
from global_trend_jp_publisher.formatters.post_formatters import format_for_redbook, format_for_x, format_tech_news_digest
from global_trend_jp_publisher.models import DraftPost


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


def test_dashboard_uses_article_translation_and_company_links() -> None:
    html = generate_dashboard_html(
        [
            DraftPost(
                title_ja="新機能の発表",
                summary_ja="本文の日本語訳です。\n\n追加の説明です。",
                x_post="",
                redbook_post="",
                takeaways_ja=["示唆1"],
                source_url="https://example.com/article",
                source_name="The Verge",
                category="tech",
                needs_fact_check=True,
                title_original="New feature launches",
                subcategory="AI/ML",
                mentioned_companies=["Google"],
            )
        ],
        generated_at=datetime(2026, 4, 4, 10, 0, 0),
    )
    assert "記事の日本語訳" in html
    assert "日本への示唆" not in html
    assert "Google の解説" in html
    assert "../../index.html" in html


def test_markdown_digest_omits_takeaway_section_and_lists_company_links() -> None:
    digest = format_tech_news_digest(
        [
            {
                "idx": 1,
                "title_ja": "日本語タイトル",
                "title_original": "Original Title",
                "summary_ja": "本文の日本語訳。",
                "source_url": "https://example.com/article",
                "source_name": "TechCrunch",
                "mentioned_companies": ["Google"],
            }
        ],
        generated_at=datetime(2026, 4, 4, 10, 0, 0),
    )
    assert "#### 🎯 日本への示唆" not in digest
    assert "#### 🏢 企業解説リンク" in digest
    assert "companies/google.html" in digest
