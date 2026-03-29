from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict

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
