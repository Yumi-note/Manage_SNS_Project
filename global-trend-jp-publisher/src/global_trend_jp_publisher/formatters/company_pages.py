"""Generate company profile HTML pages."""

from __future__ import annotations

from pathlib import Path

from global_trend_jp_publisher.processors.company_extractor import CompanyProfile


def generate_company_page_html(company: CompanyProfile) -> str:
    """Generate an HTML page for a company profile with dark theme."""
    products_html = "\n".join(f"<li>{p}</li>" for p in (company.products or []))
    facts_html = "\n".join(f"<li>{f}</li>" for f in (company.key_facts or []))

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company.name} - 企業プロフィール</title>
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
            line-height: 1.8;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%);
            padding: 3rem 2rem;
            border-radius: 0.8rem;
            margin-bottom: 2rem;
            border-left: 4px solid #4fd1c5;
        }}

        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: #fff;
        }}

        .tagline {{
            font-size: 1.1rem;
            color: #cbd5e0;
            margin-top: 1rem;
        }}

        .basic-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
            padding: 1.5rem;
            background-color: #1a1a1a;
            border: 1px solid #444;
            border-radius: 0.6rem;
        }}

        .info-block {{
            border-left: 3px solid #0ea5e9;
            padding-left: 1rem;
        }}

        .info-label {{
            font-size: 0.85rem;
            color: #a0aec0;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }}

        .info-value {{
            font-size: 1rem;
            color: #fff;
        }}

        section {{
            margin: 2.5rem 0;
            padding: 1.5rem;
            background-color: #1a1a1a;
            border: 1px solid #444;
            border-radius: 0.6rem;
        }}

        section h2 {{
            font-size: 1.5rem;
            color: #4fd1c5;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        section p {{
            line-height: 1.8;
            color: #cbd5e0;
            margin-bottom: 1rem;
        }}

        section ul {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        section li {{
            padding: 0.7rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: #cbd5e0;
        }}

        section li::before {{
            content: "→";
            position: absolute;
            left: 0;
            color: #f97316;
            font-weight: bold;
        }}

        .back-link {{
            display: inline-block;
            margin-top: 2rem;
            padding: 0.7rem 1.5rem;
            background-color: #2d3748;
            color: #4fd1c5;
            text-decoration: none;
            border-radius: 0.4rem;
            border: 1px solid #4fd1c5;
            transition: all 0.2s ease;
        }}

        .back-link:hover {{
            background-color: #4fd1c5;
            color: #0f0f0f;
        }}

        footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #444;
            text-align: center;
            color: #a0aec0;
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8rem;
            }}

            .container {{
                padding: 1rem;
            }}

            section {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏢 {company.name}</h1>
            <div class="tagline">{company.description}</div>
        </header>

        <div class="basic-info">
            <div class="info-block">
                <div class="info-label">創業年</div>
                <div class="info-value">{company.founded or "不明"}</div>
            </div>
            <div class="info-block">
                <div class="info-label">本社所在地</div>
                <div class="info-value">{company.headquarters or "不明"}</div>
            </div>
        </div>

        <section>
            <h2>📱 主な製品・サービス</h2>
            <ul>
                {products_html}
            </ul>
        </section>

        <section>
            <h2>💡 主要な知識</h2>
            <ul>
                {facts_html}
            </ul>
        </section>

        <footer>
            <p>⚠️ このページはニュース記事から自動生成されたもので、最新情報は公式サイトでご確認ください</p>
            <a href="javascript:history.back()" class="back-link">← 記事に戻る</a>
        </footer>
    </div>
</body>
</html>
"""
    return html


def write_company_profiles(output_dir: str) -> dict[str, Path]:
    """Generate company profile pages for all companies with articles.

    Args:
        output_dir: Directory to write company profiles to

    Returns:
        Dict mapping company slug to file path
    """
    from global_trend_jp_publisher.processors.company_extractor import get_all_companies

    out_path = Path(output_dir)
    companies_dir = out_path / "companies"
    companies_dir.mkdir(parents=True, exist_ok=True)

    written_files = {}
    for company in get_all_companies():
        html = generate_company_page_html(company)
        file_path = companies_dir / f"{company.slug}.html"
        file_path.write_text(html, encoding="utf-8")
        written_files[company.slug] = file_path

    return written_files
