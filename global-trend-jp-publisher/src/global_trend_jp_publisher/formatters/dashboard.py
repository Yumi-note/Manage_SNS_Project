"""Generate interactive HTML dashboard for tech news with dark theme and filtering."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from global_trend_jp_publisher.models import DraftPost
from global_trend_jp_publisher.processors.categorize_enhanced import get_category_emoji, get_category_color


def generate_dashboard_html(drafts: list[DraftPost], generated_at: datetime | None = None) -> str:
    """Generate a complete interactive HTML dashboard for the tech news digest."""
    if generated_at is None:
        generated_at = datetime.now()

    date_str = generated_at.strftime("%Y年%-m月%-d日")
    time_str = generated_at.strftime("%H:%M")

    # Build category summary
    categories = {}
    for draft in drafts:
        sub = draft.subcategory or "Other"
        if sub not in categories:
            categories[sub] = []
        categories[sub].append(draft)

    # Generate category filter buttons HTML
    category_buttons_html = []
    for cat in sorted(categories.keys()):
        posts = categories[cat]
        color = get_category_color(cat)
        emoji = get_category_emoji(cat)
        count = len(posts)
        category_buttons_html.append(
            f'<button class="category-btn" data-category="{cat}" '
            f'style="border-left-color: {color}">'
            f'{emoji} {cat} ({count})</button>'
        )
    category_buttons_str = "\n".join(category_buttons_html)

    # Generate article cards
    article_cards_html = []
    for idx, draft in enumerate(drafts, start=1):
        article_cards_html.append(_generate_article_card(idx, draft))
    articles_str = "\n".join(article_cards_html)

    css = _get_dark_theme_css()
    js = _get_dashboard_javascript()

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 海外テックニュース日本語まとめ</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <h1>🌐 海外テックニュース 日本語まとめ</h1>
                <p class="timestamp">生成日時: <strong>{date_str}</strong> {time_str} JST</p>
                <p class="description">世界の有力テックメディア（TechCrunch・The Verge・Wired・Ars Technica・MIT Tech Review・VentureBeat・Engadget）から注目記事を自動収集し、日本の読者向けに翻訳・要約しました。</p>
            </div>
        </header>

        <!-- Filter Section -->
        <section class="filter-section">
            <div class="filter-controls">
                <h2>🔍 カテゴリで絞り込み</h2>
                <div class="category-buttons">
                    <button class="category-btn active" data-category="all">📊 すべて ({len(drafts)})</button>
                    {category_buttons_str}
                </div>
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="キーワード検索...">
                </div>
            </div>
        </section>

        <!-- Articles Grid -->
        <main class="articles-section">
            <div id="articles-container" class="articles-grid">
                {articles_str}
            </div>
        </main>

        <!-- Footer -->
        <footer class="footer">
            <p>⚠️ 本まとめは自動生成です。数値・固有名詞などの事実は元記事でご確認ください。</p>
            <p class="api-note">🔌 API へのアクセスには <code>tech_news_digest.json</code> をご参照ください。</p>
        </footer>
    </div>

    <script>
{js}
    </script>
</body>
</html>
"""
    return html


def _generate_article_card(idx: int, draft: DraftPost) -> str:
    """Generate a single article card HTML."""
    emoji = get_category_emoji(draft.subcategory or "Other")
    color = get_category_color(draft.subcategory or "Other")
    category = draft.subcategory or "Other"

    # Build takeaways list items
    takeaways_items = "\n".join(f"            <li>{takeaway}</li>" for takeaway in draft.takeaways_ja)

    # Build company links if any
    company_links_html = ""
    if draft.mentioned_companies:
        company_links = []
        for company in sorted(draft.mentioned_companies):
            company_slug = company.lower().replace(" ", "-")
            company_links.append(
                f'<a href="companies/{company_slug}.html" target="_blank" class="company-link">{company}</a>'
            )
        company_links_html = f"""
        <div class="companies-section">
            <h4>🏢 関連企業</h4>
            <div class="company-links">
                {" ".join(company_links)}
            </div>
        </div>
"""

    card_html = f"""<article class="article-card" data-category="{category}" data-index="{idx}">
    <div class="article-header">
        <div class="category-badge" style="background-color: {color}">
            {emoji} {category}
        </div>
        <div class="source-badge">{draft.source_name}</div>
    </div>

    <h3 class="article-title">{draft.title_ja}</h3>

    <p class="article-original-title">原題: <em>{draft.title_original}</em></p>

    <div class="article-body">
        <h4>📝 要約</h4>
        <p class="article-summary">{draft.summary_ja}</p>

        <h4>🎯 日本への示唆</h4>
        <ul class="takeaways">
{takeaways_items}
        </ul>
{company_links_html}
        <a href="{draft.source_url}" target="_blank" rel="noopener noreferrer" class="source-link">
            🔗 元記事を読む
        </a>
    </div>
</article>
"""
    return card_html


def _get_dark_theme_css() -> str:
    """Return complete dark theme CSS."""
    return """        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', "Hiragino Kaku Gothic ProN", sans-serif;
            background-color: #0f0f0f;
            color: #e5e7eb;
            line-height: 1.6;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%);
            color: #fff;
            padding: 3rem 2rem;
            border-bottom: 1px solid #444;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }

        .header p {
            margin: 0.5rem 0;
            font-size: 1rem;
            opacity: 0.9;
        }

        .timestamp {
            color: #4fd1c5;
            font-weight: 500;
        }

        .description {
            margin-top: 1rem;
            color: #cbd5e0;
            max-width: 800px;
            line-height: 1.7;
        }

        /* Filter Section */
        .filter-section {
            background-color: #1a1a1a;
            border-bottom: 1px solid #444;
            padding: 2rem;
        }

        .filter-controls {
            max-width: 1200px;
            margin: 0 auto;
        }

        .filter-section h2 {
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: #fff;
        }

        .category-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-bottom: 1.5rem;
        }

        .category-btn {
            background-color: #2d3748;
            border: 2px solid #444;
            border-left: 4px solid;
            border-left-color: #718096;
            color: #e5e7eb;
            padding: 0.6rem 1.2rem;
            border-radius: 0.4rem;
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .category-btn:hover {
            background-color: #4a5568;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        .category-btn.active {
            background-color: #4fd1c5;
            border-left-color: #0ea5e9;
            color: #0f0f0f;
            font-weight: 600;
        }

        .search-box {
            margin-top: 1rem;
        }

        .search-box input {
            width: 100%;
            max-width: 500px;
            background-color: #2d3748;
            border: 1px solid #444;
            border-radius: 0.4rem;
            color: #e5e7eb;
            padding: 0.8rem 1rem;
            font-size: 1rem;
        }

        .search-box input::placeholder {
            color: #718096;
        }

        .search-box input:focus {
            outline: none;
            border-color: #4fd1c5;
            box-shadow: 0 0 0 3px rgba(79, 209, 197, 0.1);
        }

        /* Articles Section */
        .articles-section {
            padding: 3rem 2rem;
        }

        .articles-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 2rem;
        }

        /* Article Card */
        .article-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
            border: 1px solid #444;
            border-radius: 0.6rem;
            padding: 1.5rem;
            transition: all 0.3s ease;
            overflow: hidden;
            position: relative;
        }

        .article-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            border-color: #666;
        }

        .article-header {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            align-items: center;
        }

        .category-badge {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 0.3rem;
            font-size: 0.85rem;
            font-weight: 600;
            color: #fff;
        }

        .source-badge {
            background-color: #4a5568;
            color: #cbd5e0;
            padding: 0.3rem 0.7rem;
            border-radius: 0.3rem;
            font-size: 0.8rem;
            margin-left: auto;
        }

        .article-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }

        .article-original-title {
            color: #a0aec0;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            font-style: italic;
        }

        .article-body {
            color: #d1d5db;
        }

        .article-body h4 {
            color: #4fd1c5;
            font-size: 1rem;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .article-body h4:first-of-type {
            margin-top: 0;
        }

        .article-summary {
            line-height: 1.7;
            margin-bottom: 1rem;
            color: #cbd5e0;
        }

        .takeaways {
            list-style: none;
            margin: 0.5rem 0;
        }

        .takeaways li {
            padding: 0.4rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: #cbd5e0;
        }

        .takeaways li::before {
            content: "→";
            position: absolute;
            left: 0;
            color: #f97316;
        }

        .source-link {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background-color: #0ea5e9;
            color: #fff;
            text-decoration: none;
            border-radius: 0.3rem;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }

        .source-link:hover {
            background-color: #0284c7;
            transform: translateX(3px);
        }

        /* Footer */
        .footer {
            background-color: #1a1a1a;
            border-top: 1px solid #444;
            padding: 2rem;
            text-align: center;
            color: #a0aec0;
            font-size: 0.95rem;
        }

        .footer p {
            margin: 0.5rem 0;
        }

        .footer code {
            background-color: #2d3748;
            padding: 0.2rem 0.5rem;
            border-radius: 0.2rem;
            color: #4fd1c5;
            font-family: 'Courier New', monospace;
        }

        .api-note {
            margin-top: 1rem;
            font-size: 0.85rem;
            opacity: 0.8;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }

            .articles-grid {
                grid-template-columns: 1fr;
            }

            .category-buttons {
                flex-direction: column;
            }

            .category-btn {
                width: 100%;
                text-align: left;
            }

            .article-header {
                flex-wrap: wrap;
            }

            .source-badge {
                margin-left: 0;
                margin-top: 0.5rem;
            }

            .filter-section {
                padding: 1.5rem;
            }

            .header {
                padding: 2rem 1rem;
            }

            .articles-section {
                padding: 1.5rem;
            }
        }

        /* Companies Section */
        .companies-section {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #444;
        }

        .companies-section-title {
            font-size: 0.9rem;
            color: #4fd1c5;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .company-links {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .company-link {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            background-color: #2d3748;
            border: 1px solid #4fd1c5;
            border-radius: 0.3rem;
            color: #4fd1c5;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }

        .company-link:hover {
            background-color: #4fd1c5;
            color: #0f0f0f;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(79, 209, 197, 0.2);
        }

        @media (prefers-color-scheme: dark) {
            body {
                background-color: #0f0f0f;
                color: #e5e7eb;
            }
        }
"""


def _get_dashboard_javascript() -> str:
    """Return JavaScript for interactivity."""
    return """
        const categoryButtons = document.querySelectorAll('.category-btn');
        const articleCards = document.querySelectorAll('.article-card');
        const searchInput = document.getElementById('search-input');

        // Category filtering
        categoryButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                categoryButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const selectedCategory = btn.dataset.category;
                filterArticles(selectedCategory);
            });
        });

        function filterArticles(category) {
            articleCards.forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.style.display = '';
                    card.style.animation = 'fadeIn 0.3s ease';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        // Search functionality
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            articleCards.forEach(card => {
                const title = card.querySelector('.article-title').textContent.toLowerCase();
                const summary = card.querySelector('.article-summary').textContent.toLowerCase();
                const source = card.querySelector('.source-badge').textContent.toLowerCase();

                if (title.includes(query) || summary.includes(query) || source.includes(query)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });

        // Add fade-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);

        // Set initial active button
        document.querySelector('[data-category="all"]').classList.add('active');
    """
