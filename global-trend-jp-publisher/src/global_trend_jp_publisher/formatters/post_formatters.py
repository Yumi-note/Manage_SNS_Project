from __future__ import annotations


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
