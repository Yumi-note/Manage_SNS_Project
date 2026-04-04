"""Generate archive pages for browsing past digests."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path


@dataclass(slots=True)
class ArticleEntry:
    title_ja: str
    title_original: str
    summary_ja: str
    source_name: str
    source_url: str
    subcategory: str


@dataclass(slots=True)
class DigestEntry:
    date_str: str
    time_str: str
    rel_path: str
    articles: list[ArticleEntry]

    @property
    def article_count(self) -> int:
        return len(self.articles)

    @property
    def category_counts(self) -> Counter:
        return Counter(article.subcategory for article in self.articles)

    @property
    def display_time(self) -> str:
        try:
            return datetime.strptime(self.time_str, "%H%M%S").strftime("%H:%M")
        except ValueError:
            return self.time_str


_DISPLAY_ONLY_SENTENCES = [
    "背景として、この話題はプロダクト機能・ユーザー体験・運用面のいずれに影響するかで評価が分かれます。",
    "注目すべき点は、公開された情報の範囲で何が確定情報で、何が今後の運用や追加発表に依存するかを切り分けることです。",
    "日本での実務観点では、導入コスト、既存ワークフローとの整合性、ユーザーへの説明負荷を合わせて確認するのが有効です。",
    "本要約は元記事の記載範囲に基づく整理であり、数値や仕様は最新の公式情報で最終確認してください。",
    "このトピックは継続的なアップデートが想定されるため、一次情報の更新有無を追跡すると解像度が上がります。",
]


def generate_archive_index(news_dir: str = "data/news") -> Path:
    """Generate a home page and per-day archive pages for all digests."""
    news_path = Path(news_dir)
    if not news_path.exists():
        raise FileNotFoundError(f"News directory not found: {news_path}")

    digests_by_date = _scan_digests(news_path)
    if not digests_by_date:
        raise ValueError("No digests found in news directory")

    for date_str, digests in digests_by_date.items():
        day_index = news_path / date_str / "index.html"
        day_index.write_text(_generate_day_html(date_str, digests), encoding="utf-8")

    archive_path = news_path / "index.html"
    archive_path.write_text(_generate_home_html(digests_by_date), encoding="utf-8")
    return archive_path


def _scan_digests(news_path: Path) -> dict[str, list[DigestEntry]]:
    digests_by_date: dict[str, list[DigestEntry]] = defaultdict(list)
    for date_dir in sorted(news_path.iterdir()):
        if not date_dir.is_dir():
            continue

        try:
            datetime.strptime(date_dir.name, "%Y-%m-%d")
        except ValueError:
            continue

        for time_dir in sorted(date_dir.iterdir()):
            if not time_dir.is_dir() or not (time_dir / "index.html").exists():
                continue
            digests_by_date[date_dir.name].append(
                DigestEntry(
                    date_str=date_dir.name,
                    time_str=time_dir.name,
                    rel_path=f"{date_dir.name}/{time_dir.name}/index.html",
                    articles=_load_articles(time_dir),
                )
            )
        digests_by_date[date_dir.name].sort(key=lambda item: item.time_str, reverse=True)

    return {key: value for key, value in digests_by_date.items() if value}


def _load_articles(time_dir: Path) -> list[ArticleEntry]:
    payload_path = time_dir / "tech_news_digest.json"
    if not payload_path.exists():
        return []

    raw_items = json.loads(payload_path.read_text(encoding="utf-8"))
    return [
        ArticleEntry(
            title_ja=item.get("title_ja", "(no title)"),
            title_original=item.get("title_original", ""),
            summary_ja=_sanitize_display_summary(item.get("summary_ja", "")),
            source_name=item.get("source_name", "Unknown source"),
            source_url=item.get("source_url", "#"),
            subcategory=item.get("subcategory") or "Other",
        )
        for item in raw_items
    ]


def _sanitize_display_summary(summary: str) -> str:
    cleaned = summary
    for sentence in _DISPLAY_ONLY_SENTENCES:
        cleaned = cleaned.replace(sentence, "")
    return cleaned.replace("  ", " ").strip()


def _generate_home_html(digests_by_date: dict[str, list[DigestEntry]]) -> str:
    cards_html = []
    for date_str in sorted(digests_by_date.keys(), reverse=True):
        digests = digests_by_date[date_str]
        article_total = sum(digest.article_count for digest in digests)
        latest_time = digests[0].display_time if digests else "--:--"
        category_counts = Counter()
        for digest in digests:
            category_counts.update(digest.category_counts)

        badges = "".join(
            f'<span class="badge">{escape(category)} {count}</span>'
            for category, count in category_counts.most_common(5)
        )
        cards_html.append(
            f"""<a class="date-card" href="{date_str}/index.html">
                <div class="date-card-topline">
                    <span class="date-pill">{escape(date_str)}</span>
                    <span class="latest-time">最新 {escape(latest_time)}</span>
                </div>
                <h2>{escape(date_str)} の記事一覧</h2>
                <p>{article_total}件の記事 / {len(digests)}回の収集結果をまとめて閲覧できます。</p>
                <div class="badge-row">{badges}</div>
            </a>"""
        )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>海外テックニュース HOME</title>
    <style>
{_archive_css()}
    </style>
</head>
<body>
    <main class="shell">
        <header class="hero">
            <p class="eyebrow">Archive Home</p>
            <h1>海外テックニュース HOME</h1>
            <p class="lede">日付ごとに記事をまとめて表示します。各日付ページでは、その日に収集した記事をカテゴリ別に一覧できます。</p>
        </header>
        <section class="card-grid">
            {''.join(cards_html)}
        </section>
    </main>
</body>
</html>
"""
    return html


def _generate_day_html(date_str: str, digests: list[DigestEntry]) -> str:
    grouped_articles: dict[str, list[tuple[str, ArticleEntry, str]]] = defaultdict(list)
    for digest in digests:
        for article in digest.articles:
            grouped_articles[article.subcategory].append((digest.display_time, article, digest.rel_path.split('/', 1)[1]))

    category_sections = []
    for category in sorted(grouped_articles.keys()):
        article_cards = []
        for display_time, article, rel_path in grouped_articles[category]:
            excerpt = escape(article.summary_ja[:220] + ("..." if len(article.summary_ja) > 220 else ""))
            article_cards.append(
                f"""<article class="article-row">
                    <div class="article-meta">
                        <span class="time-pill">{escape(display_time)}</span>
                        <span class="source-name">{escape(article.source_name)}</span>
                    </div>
                    <h3>{escape(article.title_ja)}</h3>
                    <p class="original-title">原題: {escape(article.title_original)}</p>
                    <p class="excerpt">{excerpt}</p>
                    <div class="actions">
                        <a href="{escape(rel_path)}">この回のダッシュボード</a>
                        <a href="{escape(article.source_url)}" target="_blank" rel="noopener noreferrer">元記事</a>
                    </div>
                </article>"""
            )
        category_sections.append(
            f"""<section class="category-section">
                <div class="section-header">
                    <h2>{escape(category)}</h2>
                    <span>{len(grouped_articles[category])}件</span>
                </div>
                <div class="article-stack">{''.join(article_cards)}</div>
            </section>"""
        )

    digest_links = "".join(
        f'<a class="run-link" href="{digest.time_str}/index.html">{escape(digest.display_time)} の収集結果 ({digest.article_count}件)</a>'
        for digest in digests
    )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(date_str)} の海外テックニュース</title>
    <style>
{_archive_css()}
    </style>
</head>
<body>
    <main class="shell">
        <header class="hero">
            <div class="hero-nav">
                <a class="back-link" href="../index.html">HOMEへ戻る</a>
            </div>
            <p class="eyebrow">Daily Archive</p>
            <h1>{escape(date_str)} の記事一覧</h1>
            <p class="lede">同日に複数回収集した記事を1ページに集約しています。カテゴリごとに見たい話題を追えます。</p>
            <div class="run-links">{digest_links}</div>
        </header>
        <section class="category-layout">
            {''.join(category_sections)}
        </section>
    </main>
</body>
</html>
"""


def _archive_css() -> str:
    return """        :root {
            color-scheme: dark;
            --panel: rgba(14, 23, 39, 0.95);
            --line: rgba(145, 167, 201, 0.22);
            --text: #eef4ff;
            --muted: #a9bdd8;
            --accent-soft: #7dd3fc;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Hiragino Sans", "Noto Sans JP", sans-serif;
            background:
                radial-gradient(circle at top left, rgba(52, 211, 153, 0.18), transparent 22%),
                radial-gradient(circle at top right, rgba(125, 211, 252, 0.2), transparent 24%),
                linear-gradient(180deg, #07101c, #0a1120);
            color: var(--text);
        }

        .shell {
            max-width: 1160px;
            margin: 0 auto;
            padding: 24px;
        }

        .hero {
            padding: 28px;
            border-radius: 28px;
            border: 1px solid var(--line);
            background: linear-gradient(145deg, rgba(14, 22, 38, 0.97), rgba(9, 15, 29, 0.95));
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2rem, 3vw, 3rem);
        }

        .eyebrow {
            margin: 0 0 10px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
            color: var(--accent-soft);
        }

        .lede,
        .date-card p,
        .original-title,
        .excerpt {
            color: var(--muted);
            line-height: 1.8;
        }

        .card-grid,
        .category-layout,
        .article-stack {
            display: grid;
            gap: 18px;
            margin-top: 24px;
        }

        .date-card,
        .category-section,
        .article-row {
            border-radius: 24px;
            border: 1px solid var(--line);
            background: var(--panel);
        }

        .date-card {
            display: block;
            padding: 22px;
            color: inherit;
            text-decoration: none;
        }

        .date-card-topline,
        .section-header,
        .article-meta,
        .actions,
        .run-links,
        .hero-nav {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }

        .date-pill,
        .latest-time,
        .badge,
        .time-pill,
        .source-name,
        .back-link,
        .run-link,
        .actions a {
            display: inline-flex;
            align-items: center;
            min-height: 36px;
            padding: 0 12px;
            border-radius: 999px;
            border: 1px solid var(--line);
            text-decoration: none;
        }

        .date-pill,
        .time-pill {
            background: rgba(52, 211, 153, 0.15);
            color: #baf7df;
        }

        .latest-time,
        .source-name,
        .badge,
        .back-link,
        .run-link,
        .actions a {
            color: var(--muted);
            background: rgba(255, 255, 255, 0.04);
        }

        .badge-row,
        .run-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 14px;
        }

        .category-section,
        .article-row {
            padding: 20px;
        }

        .section-header {
            justify-content: space-between;
            margin-bottom: 14px;
        }

        .section-header h2,
        .article-row h3,
        .date-card h2 {
            margin: 0;
        }

        .actions {
            margin-top: 12px;
        }

        @media (max-width: 720px) {
            .shell {
                padding: 14px;
            }

            .hero,
            .date-card,
            .category-section,
            .article-row {
                padding: 18px;
                border-radius: 20px;
            }
        }
"""
