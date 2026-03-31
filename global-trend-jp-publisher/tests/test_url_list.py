from pathlib import Path

from global_trend_jp_publisher.processors.url_list import load_urls_from_file


def test_load_urls_from_file_skips_comments_and_deduplicates(tmp_path: Path) -> None:
    target = tmp_path / "urls.txt"
    target.write_text(
        "\n".join(
            [
                "# comment",
                "",
                "https://example.com/a",
                "https://example.com/a",
                "http://example.com/b",
                "not-a-url",
            ]
        ),
        encoding="utf-8",
    )

    urls = load_urls_from_file(str(target))
    assert urls == ["https://example.com/a", "http://example.com/b"]
