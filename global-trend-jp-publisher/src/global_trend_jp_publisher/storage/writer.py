from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from global_trend_jp_publisher.formatters.post_formatters import format_tech_news_digest
from global_trend_jp_publisher.formatters.dashboard import generate_dashboard_html
from global_trend_jp_publisher.formatters.company_pages import write_company_profiles
from global_trend_jp_publisher.models import DraftPost


def write_outputs(output_dir: str, drafts: list[DraftPost]) -> Path:
    now = datetime.now()
    out = Path(output_dir) / now.strftime("%Y-%m-%d") / now.strftime("%H%M%S")
    out.mkdir(parents=True, exist_ok=True)

    with (out / "drafts.json").open("w", encoding="utf-8") as f:
        json.dump([asdict(x) for x in drafts], f, ensure_ascii=False, indent=2)

    lines: list[str] = ["# Daily Draft Posts", ""]
    grouped: dict[str, list[DraftPost]] = defaultdict(list)
    for draft in drafts:
        grouped[draft.category].append(draft)

    for category in ["tech", "finance"]:
        category_drafts = grouped.get(category, [])
        if not category_drafts:
            continue
        lines.extend([f"# {category.title()} Posts", ""])
        category_lines: list[str] = [f"# {category.title()} Draft Posts", ""]
        for idx, draft in enumerate(category_drafts, start=1):
            block = [
                f"## Item {idx}: {draft.title_ja}",
                "",
                "### X Draft",
                draft.x_post,
                "",
                "### Redbook Draft",
                draft.redbook_post,
                "",
            ]
            lines.extend(block)
            category_lines.extend(block)
        (out / f"{category}_posts.md").write_text("\n".join(category_lines), encoding="utf-8")

        with (out / f"{category}_drafts.json").open("w", encoding="utf-8") as f:
            json.dump([asdict(x) for x in category_drafts], f, ensure_ascii=False, indent=2)

    (out / "posts.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def write_redbook_only_output(out_dir: Path, drafts: list[DraftPost]) -> Path:
    lines: list[str] = ["# Redbook Drafts Only", ""]
    for idx, draft in enumerate(drafts, start=1):
        lines.extend(
            [
                f"## Item {idx}: {draft.title_ja}",
                "",
                draft.redbook_post,
                "",
            ]
        )
    target = out_dir / "redbook_posts_only.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def write_x_only_output(out_dir: Path, drafts: list[DraftPost]) -> Path:
    lines: list[str] = ["# X Drafts Only", ""]
    for idx, draft in enumerate(drafts, start=1):
        lines.extend(
            [
                f"## Item {idx}: {draft.title_ja}",
                "",
                draft.x_post,
                "",
            ]
        )
    target = out_dir / "x_posts_only.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def write_tech_news_output(output_dir: str, drafts: list[DraftPost]) -> Path:
    """Write a clean, readable Japanese tech news digest to data/news/{date}/{time}/.
    
    Outputs:
    - tech_news_digest.html: Interactive dashboard with dark theme
    - tech_news_digest.md: Markdown version
    - tech_news_digest.json: Structured API data
    """
    now = datetime.now()
    out = Path(output_dir) / now.strftime("%Y-%m-%d") / now.strftime("%H%M%S")
    out.mkdir(parents=True, exist_ok=True)

    # Generate HTML dashboard
    dashboard_html = generate_dashboard_html(drafts, generated_at=now)
    (out / "index.html").write_text(dashboard_html, encoding="utf-8")

    items = [
        {
            "idx": i,
            "title_ja": d.title_ja,
            "title_original": d.title_original or d.source_name,
            "summary_ja": d.summary_ja,
            "source_url": d.source_url,
            "source_name": d.source_name,
            "takeaways_ja": d.takeaways_ja,
            "subcategory": d.subcategory or "Other",
        }
        for i, d in enumerate(drafts, start=1)
    ]

    # Generate Markdown version
    digest_md = format_tech_news_digest(items, generated_at=now)
    (out / "tech_news_digest.md").write_text(digest_md, encoding="utf-8")

    # Generate JSON API output
    with (out / "tech_news_digest.json").open("w", encoding="utf-8") as f:
        json.dump([asdict(d) for d in drafts], f, ensure_ascii=False, indent=2)

    # Generate company profile pages
    write_company_profiles(out)

    return out
