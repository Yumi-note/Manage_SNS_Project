"""Generate interactive HTML dashboard for tech news digests."""

from __future__ import annotations

from datetime import datetime
from html import escape

from global_trend_jp_publisher.models import DraftPost
from global_trend_jp_publisher.processors.categorize_enhanced import get_category_color, get_category_emoji
from global_trend_jp_publisher.processors.company_extractor import get_company_profile


_DISPLAY_ONLY_SENTENCES = [
    "背景として、この話題はプロダクト機能・ユーザー体験・運用面のいずれに影響するかで評価が分かれます。",
    "注目すべき点は、公開された情報の範囲で何が確定情報で、何が今後の運用や追加発表に依存するかを切り分けることです。",
    "日本での実務観点では、導入コスト、既存ワークフローとの整合性、ユーザーへの説明負荷を合わせて確認するのが有効です。",
    "本要約は元記事の記載範囲に基づく整理であり、数値や仕様は最新の公式情報で最終確認してください。",
    "このトピックは継続的なアップデートが想定されるため、一次情報の更新有無を追跡すると解像度が上がります。",
]


def generate_dashboard_html(drafts: list[DraftPost], generated_at: datetime | None = None) -> str:
    """Generate a readable article dashboard with filters and navigation."""
    if generated_at is None:
        generated_at = datetime.now()

    date_str = generated_at.strftime("%Y年%-m月%-d日")
    time_str = generated_at.strftime("%H:%M")

    categories: dict[str, list[DraftPost]] = {}
    for draft in drafts:
        subcategory = draft.subcategory or "Other"
        categories.setdefault(subcategory, []).append(draft)

    category_buttons_html = [
        '<button class="category-btn active" data-category="all">すべて ({count})</button>'.format(count=len(drafts))
    ]
    for category in sorted(categories.keys()):
        color = get_category_color(category)
        emoji = get_category_emoji(category)
        category_buttons_html.append(
            f'<button class="category-btn" data-category="{escape(category)}" style="--accent:{color}">{emoji} {escape(category)} ({len(categories[category])})</button>'
        )
    category_buttons_str = "\n".join(category_buttons_html)

    articles_str = "\n".join(_generate_article_card(idx, draft) for idx, draft in enumerate(drafts, start=1))

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>海外テックニュース日本語まとめ</title>
    <style>
{_get_dark_theme_css()}
    </style>
</head>
<body>
    <div class="page-shell">
        <header class="hero">
            <div class="hero-nav">
                <a class="nav-link" href="../../index.html">HOME</a>
                <a class="nav-link" href="../index.html">この日の記事一覧</a>
            </div>
            <div class="hero-copy">
                <p class="eyebrow">Global Tech News Digest</p>
                <h1>海外テックニュース 日本語まとめ</h1>
                <p class="timestamp">{date_str} {time_str} JST に収集した記事を掲載しています。</p>
                <p class="description">各カードには本文寄りの日本語訳を掲載し、記事中で触れた企業は別ページの解説リンクとして分離しています。</p>
            </div>
        </header>

        <section class="control-panel">
            <div class="control-header">
                <div>
                    <h2>記事を探す</h2>
                    <p>カテゴリとキーワードで一覧を絞り込めます。</p>
                </div>
                <input type="text" id="search-input" placeholder="タイトル・本文・媒体名で検索">
            </div>
            <div class="category-buttons">
                {category_buttons_str}
            </div>
        </section>

        <main class="article-list" id="articles-container">
            {articles_str}
        </main>

        <footer class="footer">
            <p>本ページは公開記事をもとに自動生成しています。数値や仕様は必ず元記事で確認してください。</p>
            <p>JSON データは同じフォルダ内の tech_news_digest.json で参照できます。</p>
        </footer>
    </div>

    <script>
{_get_dashboard_javascript()}
    </script>
</body>
</html>
"""
    return html


def _generate_article_card(idx: int, draft: DraftPost) -> str:
    """Generate a single article card HTML."""
    category = draft.subcategory or "Other"
    emoji = get_category_emoji(category)
    color = get_category_color(category)
    paragraphs_html = _render_summary_paragraphs(draft.summary_ja)
    company_links_html = _render_company_links(draft.mentioned_companies)

    return f"""<article class="article-card" data-category="{escape(category)}" data-index="{idx}">
    <div class="card-topline">
        <span class="category-chip" style="background:{color}">{emoji} {escape(category)}</span>
        <span class="source-chip">{escape(draft.source_name)}</span>
    </div>

    <h2 class="article-title">{escape(draft.title_ja)}</h2>
    <p class="article-original-title">原題: <em>{escape(draft.title_original)}</em></p>

    <section class="article-section">
        <h3>記事の日本語訳</h3>
        <div class="article-summary">{paragraphs_html}</div>
    </section>

    {company_links_html}

    <div class="article-actions">
        <a href="{escape(draft.source_url)}" target="_blank" rel="noopener noreferrer" class="action-link primary">元記事を読む</a>
    </div>
</article>"""


def _render_summary_paragraphs(summary: str) -> str:
    cleaned_summary = _sanitize_display_summary(summary)
    paragraphs = [part.strip() for part in cleaned_summary.split("\n") if part.strip()]
    if not paragraphs:
        return '<p class="article-paragraph">本文を抽出できなかったため、元記事を参照してください。</p>'
    return "".join(f'<p class="article-paragraph">{escape(paragraph)}</p>' for paragraph in paragraphs)


def _sanitize_display_summary(summary: str) -> str:
    cleaned = summary
    for sentence in _DISPLAY_ONLY_SENTENCES:
        cleaned = cleaned.replace(sentence, "")
    cleaned = cleaned.replace("  ", " ").strip()
    return cleaned


def _render_company_links(companies: list[str]) -> str:
    if not companies:
        return ""

    links = []
    for company in sorted(companies):
        profile = get_company_profile(company)
        slug = profile.slug if profile else company.lower().replace(" ", "-")
        links.append(
            f'<a href="companies/{escape(slug)}.html" target="_blank" rel="noopener noreferrer" class="company-link">{escape(company)} の解説</a>'
        )

    return f"""<section class="article-section company-section">
        <h3>関連企業の別ページ解説</h3>
        <div class="company-links">{' '.join(links)}</div>
    </section>"""


def _get_dark_theme_css() -> str:
    """Return complete dashboard CSS."""
    return """        :root {
            color-scheme: dark;
            --bg: #0a0f1d;
            --panel: rgba(13, 20, 36, 0.92);
            --line: rgba(132, 152, 187, 0.25);
            --text: #eef3ff;
            --muted: #adc1dd;
            --accent: #7dd3fc;
            --accent-strong: #38bdf8;
            --shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: "Hiragino Sans", "Noto Sans JP", sans-serif;
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.22), transparent 26%),
                radial-gradient(circle at top left, rgba(16, 185, 129, 0.16), transparent 20%),
                linear-gradient(180deg, #07101f 0%, #0b1327 48%, #0a0f1d 100%);
            color: var(--text);
        }

        .page-shell {
            max-width: 1180px;
            margin: 0 auto;
            padding: 24px;
        }

        .hero {
            padding: 28px;
            border: 1px solid var(--line);
            border-radius: 28px;
            background: linear-gradient(145deg, rgba(18, 27, 48, 0.96), rgba(10, 17, 32, 0.96));
            box-shadow: var(--shadow);
        }

        .hero-nav {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 28px;
        }

        .nav-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 42px;
            padding: 0 16px;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text);
            text-decoration: none;
        }

        .eyebrow {
            margin: 0 0 10px;
            color: var(--accent);
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.78rem;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2rem, 3vw, 3.3rem);
            line-height: 1.1;
        }

        .timestamp,
        .description {
            color: var(--muted);
        }

        .control-panel {
            margin: 20px 0 28px;
            padding: 22px;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: var(--panel);
            backdrop-filter: blur(12px);
        }

        .control-header {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            align-items: end;
            flex-wrap: wrap;
        }

        .control-header h2 {
            margin: 0 0 6px;
        }

        .control-header p {
            margin: 0;
            color: var(--muted);
        }

        #search-input {
            width: min(100%, 360px);
            min-height: 46px;
            padding: 0 14px;
            border-radius: 14px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text);
        }

        .category-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 16px;
        }

        .category-btn {
            min-height: 42px;
            padding: 0 14px;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.04);
            color: var(--text);
            cursor: pointer;
        }

        .category-btn.active {
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: #06111f;
            border-color: transparent;
            font-weight: 700;
        }

        .article-list {
            display: grid;
            gap: 18px;
        }

        .article-card {
            padding: 24px;
            border-radius: 24px;
            border: 1px solid var(--line);
            background: linear-gradient(180deg, rgba(12, 18, 34, 0.96), rgba(14, 22, 39, 0.9));
            box-shadow: var(--shadow);
        }

        .card-topline {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }

        .category-chip,
        .source-chip {
            display: inline-flex;
            align-items: center;
            min-height: 34px;
            padding: 0 12px;
            border-radius: 999px;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .source-chip {
            background: rgba(255, 255, 255, 0.08);
            color: var(--muted);
        }

        .article-title {
            margin: 0 0 10px;
            font-size: clamp(1.45rem, 2vw, 2rem);
            line-height: 1.35;
        }

        .article-original-title {
            margin: 0 0 18px;
            color: var(--muted);
        }

        .article-section {
            margin-top: 18px;
            padding-top: 18px;
            border-top: 1px solid var(--line);
        }

        .article-section h3 {
            margin: 0 0 12px;
            font-size: 1rem;
            color: var(--accent);
        }

        .article-paragraph {
            margin: 0 0 14px;
            color: #dce7f8;
            line-height: 1.9;
            font-size: 1rem;
        }

        .company-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .company-link,
        .action-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 42px;
            padding: 0 14px;
            border-radius: 14px;
            text-decoration: none;
            border: 1px solid rgba(125, 211, 252, 0.3);
        }

        .company-link {
            color: var(--accent);
            background: rgba(56, 189, 248, 0.08);
        }

        .article-actions {
            margin-top: 22px;
        }

        .footer {
            padding: 28px 8px 40px;
            color: var(--muted);
            text-align: center;
        }

        .footer p {
            margin: 6px 0;
        }

        .action-link.primary {
            color: #06111f;
            font-weight: 700;
            background: linear-gradient(135deg, #7dd3fc, #22d3ee);
            border-color: transparent;
        }

        @media (max-width: 720px) {
            .page-shell {
                padding: 14px;
            }

            .hero,
            .control-panel,
            .article-card {
                padding: 18px;
                border-radius: 20px;
            }

            .control-header {
                align-items: stretch;
            }

            #search-input {
                width: 100%;
            }
        }
"""


def _get_dashboard_javascript() -> str:
    """Return JavaScript for interactivity."""
    return """
        const categoryButtons = document.querySelectorAll('.category-btn');
        const articleCards = document.querySelectorAll('.article-card');
        const searchInput = document.getElementById('search-input');

        let activeCategory = 'all';

        function applyFilters() {
            const query = searchInput.value.trim().toLowerCase();
            articleCards.forEach(card => {
                const matchesCategory = activeCategory === 'all' || card.dataset.category === activeCategory;
                const searchableText = card.innerText.toLowerCase();
                const matchesQuery = !query || searchableText.includes(query);
                card.style.display = matchesCategory && matchesQuery ? '' : 'none';
            });
        }

        categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                categoryButtons.forEach(item => item.classList.remove('active'));
                button.classList.add('active');
                activeCategory = button.dataset.category;
                applyFilters();
            });
        });

        searchInput.addEventListener('input', applyFilters);
    """
