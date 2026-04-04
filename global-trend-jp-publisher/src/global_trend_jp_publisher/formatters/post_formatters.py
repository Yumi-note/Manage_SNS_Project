from __future__ import annotations

from datetime import datetime


def category_label(category: str) -> str:
    if category == "finance":
        return "金融"
    return "テック"


def format_for_x(
    title_ja: str,
    summary_ja: str,
    source_url: str,
    japan_hook_ja: str = "",
    max_len: int = 280,
) -> str:
    body_parts = [title_ja, summary_ja]
    if japan_hook_ja:
        body_parts.append(japan_hook_ja)
    post = "\n".join(body_parts) + f"\n出典: {source_url}"
    if len(post) <= max_len:
        return post
    reserve = len(f"\n出典: {source_url}")

    if japan_hook_ja:
        without_summary = f"{title_ja}\n{japan_hook_ja}\n出典: {source_url}"
        if len(without_summary) <= max_len:
            return without_summary

    allowed = max(30, max_len - reserve - 3)
    compact = (title_ja + " " + summary_ja)[:allowed].rstrip() + "..."
    trimmed = f"{compact}\n出典: {source_url}"
    if len(trimmed) <= max_len:
        return trimmed

    allowed_title = max(10, max_len - reserve - 3)
    short_title = title_ja[:allowed_title].rstrip() + "..."
    return f"{short_title}\n出典: {source_url}"


def format_for_redbook(
    title_ja: str,
    summary_ja: str,
    source_url: str,
    category: str,
    takeaways_ja: list[str],
) -> str:
    takeaway_lines = "\n".join(f"- {line}" for line in takeaways_ja)
    return (
        f"【{category_label(category)}トレンド要約】\n"
        f"{title_ja}\n\n"
        f"{summary_ja}\n\n"
        "日本向けの示唆:\n"
        f"{takeaway_lines}\n\n"
        f"出典: {source_url}\n"
        "※ 数値や事実は投稿前に確認してください。"
    )


# ── Tech News Digest formatter ─────────────────────────────────────────────


_SOURCE_ICON: dict[str, str] = {
    "techcrunch": "TechCrunch",
    "the verge": "The Verge",
    "verge": "The Verge",
    "wired": "Wired",
    "ars technica": "Ars Technica",
    "mit technology review": "MIT Tech Review",
    "mit tech": "MIT Tech Review",
    "venturebeat": "VentureBeat",
    "engadget": "Engadget",
}


def _normalize_source(source_name: str) -> str:
    key = source_name.lower()
    for k, v in _SOURCE_ICON.items():
        if k in key:
            return v
    return source_name


def format_tech_news_item(
    idx: int,
    title_ja: str,
    title_original: str,
    summary_ja: str,
    source_url: str,
    source_name: str,
    mentioned_companies: list[str],
) -> str:
    """Return a single article block for the digest."""
    source_label = _normalize_source(source_name)
    company_lines = "\n".join(
        f"- [{company}](companies/{company.lower().replace(' ', '-')}.html)"
        for company in mentioned_companies
    )
    company_block = (
        "#### 🏢 企業解説リンク\n\n"
        f"{company_lines}\n\n"
        if company_lines
        else ""
    )
    return (
        f"## 記事 {idx}  ｜  {source_label}\n\n"
        f"### {title_ja}\n\n"
        f"> 原題: *{title_original}*\n\n"
        "#### 📝 記事の日本語訳\n\n"
        f"{summary_ja}\n\n"
        f"{company_block}"
        f"🔗 [元記事を読む]({source_url})\n\n"
        "---\n"
    )


def format_tech_news_digest(
    items: list[dict],
    generated_at: datetime | None = None,
) -> str:
    """Return the full digest Markdown document.

    Each element of *items* must have keys:
        idx, title_ja, title_original, summary_ja,
        source_url, source_name, mentioned_companies
    """
    if generated_at is None:
        generated_at = datetime.now()

    date_str = generated_at.strftime("%Y年%-m月%-d日")
    time_str = generated_at.strftime("%H:%M")

    lines: list[str] = [
        "# 🌐 海外テックニュース 日本語まとめ",
        "",
        f"**生成日時:** {date_str}  {time_str} JST",
        "",
        "> 世界の有力テックメディア（TechCrunch・The Verge・Wired・Ars Technica・MIT Tech Review・VentureBeat・Engadget）から"
        "注目記事を自動収集し、日本の読者向けに翻訳・要約しました。",
        "",
        "---",
        "",
    ]

    # Table of contents
    lines.append("## 目次\n")
    for item in items:
        lines.append(f"{item['idx']}. [{item['title_ja']}](#{_toc_anchor(item['idx'], item['title_ja'])})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Article blocks
    for item in items:
        lines.append(
            format_tech_news_item(
                idx=item["idx"],
                title_ja=item["title_ja"],
                title_original=item["title_original"],
                summary_ja=item["summary_ja"],
                source_url=item["source_url"],
                source_name=item["source_name"],
                mentioned_companies=item.get("mentioned_companies", []),
            )
        )

    lines.append("")
    lines.append(
        "> ⚠️ 本まとめは自動生成です。数値・固有名詞などの事実は元記事でご確認ください。"
    )
    return "\n".join(lines)


def _toc_anchor(idx: int, title: str) -> str:
    """Generate a GitHub-style Markdown anchor for the ToC entry."""
    import re
    slug = re.sub(r"[^\w\u3000-\u9fff\u30a0-\u30ff\u3040-\u309f\-]", "", title.lower().replace(" ", "-"))
    return f"記事-{idx}--{slug}"

