"""Generate archive index pages for browsing past digests."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from collections import defaultdict


def generate_archive_index(news_dir: str = "data/news") -> Path:
    """Generate an index.html that lists all past digests by date/time.

    Scans data/news/{YYYY-MM-DD}/{HHMMSS}/ structure and creates
    a browsable archive for all existing digests.

    Returns:
        Path to the generated archive index
    """
    news_path = Path(news_dir)
    if not news_path.exists():
        raise FileNotFoundError(f"News directory not found: {news_path}")

    # Collect all digest directories
    digests_by_date = defaultdict(list)
    for date_dir in sorted(news_path.iterdir()):
        if not date_dir.is_dir():
            continue
        date_str = date_dir.name
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        for time_dir in sorted(date_dir.iterdir()):
            if not time_dir.is_dir():
                continue
            time_str = time_dir.name
            index_html = time_dir / "index.html"
            if index_html.exists():
                digests_by_date[date_str].append((time_str, time_dir))

    if not digests_by_date:
        raise ValueError("No digests found in news directory")

    # Generate HTML
    html = _generate_archive_html(digests_by_date, news_path)

    # Write to news directory root
    archive_path = news_path / "index.html"
    archive_path.write_text(html, encoding="utf-8")
    return archive_path


def _generate_archive_html(digests_by_date: dict[str, list[tuple[str, Path]]], news_path: Path) -> str:
    """Generate archive index HTML."""
    rows_html = []
    for date_str in sorted(digests_by_date.keys(), reverse=True):
        digests = digests_by_date[date_str]
        for time_str, time_path in sorted(digests, reverse=True):
            # Parse date/time
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H%M%S")
                display_time = dt.strftime("%H:%M:%S")
            except ValueError:
                display_time = time_str

            # Relative path for link
            rel_path = f"{date_str}/{time_str}/index.html"

            rows_html.append(
                f'<tr>'
                f'<td class="date">{date_str}</td>'
                f'<td class="time">{display_time}</td>'
                f'<td class="link"><a href="{rel_path}">📰 ダッシュボードを開く →</a></td>'
                f'</tr>'
            )

    rows_str = "\n".join(rows_html)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 海外テックニュース まとめ - アーカイブ</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', "Hiragino Kaku Gothic ProN", sans-serif;
            background-color: #0f0f0f;
            color: #e5e7eb;
            line-height: 1.6;
            padding: 2rem;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%);
            color: #fff;
            padding: 2rem;
            border-radius: 0.8rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #4fd1c5;
        }}

        header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}

        header p {{
            color: #cbd5e0;
            margin: 0.5rem 0;
        }}

        .archive-section {{
            background-color: #1a1a1a;
            border: 1px solid #444;
            border-radius: 0.8rem;
            overflow: hidden;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        thead {{
            background-color: #2d3748;
            border-bottom: 2px solid #4fd1c5;
        }}

        th {{
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #4fd1c5;
        }}

        tbody tr {{
            border-bottom: 1px solid #444;
            transition: background-color 0.2s ease;
        }}

        tbody tr:hover {{
            background-color: #252525;
        }}

        td {{
            padding: 1rem;
        }}

        td.date {{
            font-weight: 600;
            color: #fff;
            width: 130px;
        }}

        td.time {{
            color: #a0aec0;
            font-family: monospace;
            width: 100px;
        }}

        td.link a {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #0ea5e9;
            color: #fff;
            text-decoration: none;
            border-radius: 0.3rem;
            transition: all 0.2s ease;
            font-size: 0.95rem;
        }}

        td.link a:hover {{
            background-color: #0284c7;
            transform: translateX(3px);
        }}

        footer {{
            margin-top: 2rem;
            text-align: center;
            color: #a0aec0;
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}

            header h1 {{
                font-size: 1.5rem;
            }}

            table {{
                font-size: 0.9rem;
            }}

            td {{
                padding: 0.75rem;
            }}

            th {{
                padding: 0.75rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 海外テックニュース日本語まとめ</h1>
            <p>📚 アーカイブ - 過去のダッシュボード一覧</p>
            <p style="margin-top: 0.5rem; font-size: 0.9rem;">⏰ 2時間ごとに自動更新されています</p>
        </header>

        <section class="archive-section">
            <table>
                <thead>
                    <tr>
                        <th>📅 日付</th>
                        <th>⏰ 時刻 (JST)</th>
                        <th>📖 ダッシュボード</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_str}
                </tbody>
            </table>
        </section>

        <footer>
            <p>💡 各ダッシュボードはカテゴリフィルタと検索機能付きです</p>
            <p>🔌 JSON ファイルは各フォルダ内の <code>tech_news_digest.json</code> を参照してください</p>
        </footer>
    </div>
</body>
</html>
"""
    return html
