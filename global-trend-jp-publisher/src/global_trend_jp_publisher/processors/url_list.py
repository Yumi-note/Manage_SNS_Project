from __future__ import annotations

from pathlib import Path


def load_urls_from_file(file_path: str) -> list[str]:
    path = Path(file_path)
    raw = path.read_text(encoding="utf-8")

    urls: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        if value.startswith("http://") or value.startswith("https://"):
            if value not in seen:
                urls.append(value)
                seen.add(value)
    return urls
