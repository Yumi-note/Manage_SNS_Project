from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from global_trend_jp_publisher.models import TrendItem
from global_trend_jp_publisher.processors.categorize import determine_category
from global_trend_jp_publisher.processors.ocr import ocr_from_image_url


BOILERPLATE_KEYWORDS = {
    "icp",
    "营业执照",
    "営業許可",
    "互联网",
    "internet",
    "license",
    "hotline",
    "举报",
    "通報",
    "上海",
    "网安",
    "algorithm",
    "许可证",
}


def _is_boilerplate(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in BOILERPLATE_KEYWORDS)


def _filter_meaningful_paragraphs(paragraphs: list[str]) -> list[str]:
    cleaned: list[str] = []
    for p in paragraphs:
        value = " ".join(p.split())
        if len(value) < 40:
            continue
        if _is_boilerplate(value):
            continue
        cleaned.append(value)
    return cleaned


def _extract_image_candidates(soup: BeautifulSoup, base_url: str) -> list[str]:
    seen: set[str] = set()
    candidates: list[str] = []

    meta_selectors = [
        ("meta", {"property": "og:image"}),
        ("meta", {"name": "twitter:image"}),
    ]
    for tag_name, attrs in meta_selectors:
        tag = soup.find(tag_name, attrs=attrs)
        if tag and tag.get("content"):
            url = urljoin(base_url, tag["content"].strip())
            if url.startswith("http") and url not in seen:
                seen.add(url)
                candidates.append(url)

    for img in soup.find_all("img"):
        src = (img.get("src") or img.get("data-src") or "").strip()
        if not src:
            continue
        url = urljoin(base_url, src)
        lowered = url.lower()
        if any(token in lowered for token in ["avatar", "icon", "logo", "sprite", "emoji"]):
            continue
        if url.startswith("http") and url not in seen:
            seen.add(url)
            candidates.append(url)
        if len(candidates) >= 8:
            break
    return candidates


def _extract_embedded_image_urls(html: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    # Xiaohongshu note payload often contains image urls in urlDefault fields.
    raw_urls = re.findall(r'"urlDefault"\s*:\s*"([^"]+)"', html)
    for raw in raw_urls:
        decoded = _decode_json_string(raw).replace("\\/", "/")
        decoded = decoded.strip()
        if decoded.startswith("http://"):
            decoded = "https://" + decoded[len("http://") :]
        if not decoded.startswith("http"):
            continue
        lowered = decoded.lower()
        if any(token in lowered for token in ["avatar", "icon", "logo", "emoji", "sprite"]):
            continue
        if decoded in seen:
            continue
        seen.add(decoded)
        urls.append(decoded)
    return urls


def _snippet_needs_ocr(snippet: str) -> bool:
    if not snippet or len(snippet.strip()) < 80:
        return True
    if _is_boilerplate(snippet):
        return True
    return False


def _decode_json_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except Exception:
        return value


def _clean_extracted_text(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"#([^#]{1,80})\[.*?\]#", "", cleaned)
    cleaned = re.sub(r"#[\w\u4e00-\u9fff\u3040-\u30ff-]{1,80}", "", cleaned)
    cleaned = re.sub(r"##+", " ", cleaned)
    cleaned = re.sub(r"\s+#\s*$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _extract_script_text_candidates(html: str) -> list[str]:
    key_pattern = r'(?:desc|content|noteDesc|noteContent|description|shareInfo)'
    regex = re.compile(rf'"{key_pattern}"\s*:\s*"((?:\\.|[^"\\]){{20,}})"')

    candidates: list[str] = []
    for match in regex.finditer(html):
        decoded = _clean_extracted_text(_decode_json_string(match.group(1)))
        if len(decoded) < 20:
            continue
        if _is_boilerplate(decoded):
            continue
        # Exclude obvious URL-heavy blobs.
        if decoded.count("http") >= 2:
            continue
        candidates.append(decoded)

    # Prefer longer meaningful candidates first.
    candidates.sort(key=len, reverse=True)
    return candidates[:10]


def _normalize_for_dedupe(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def _combine_text_candidates(candidates: list[str], max_chars: int = 2400) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    total = 0
    for candidate in candidates:
        value = " ".join(candidate.split())
        key = _normalize_for_dedupe(value)
        if not value or key in seen:
            continue
        seen.add(key)
        if total + len(value) > max_chars:
            remaining = max(0, max_chars - total)
            if remaining > 80:
                parts.append(value[:remaining].rstrip() + "...")
            break
        parts.append(value)
        total += len(value)
        if len(parts) >= 4:
            break
    return "\n".join(parts)


def extract_article_text_from_html(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    title = "(no title)"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    # Prefer article/main containers; fallback to all paragraph text.
    containers = soup.select("article") or soup.select("main") or [soup]
    paragraphs: list[str] = []
    for container in containers:
        for p in container.find_all("p"):
            text = p.get_text(" ", strip=True)
            paragraphs.append(text)

    paragraphs = _filter_meaningful_paragraphs(paragraphs)

    if not paragraphs:
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            paragraphs.append(og_desc["content"].strip())

    snippet = " ".join(paragraphs[:4]).strip()
    if len(snippet) > 800:
        snippet = snippet[:800] + "..."
    return title, snippet


def fetch_url_item(url: str, timeout: int = 20) -> TrendItem:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 (compatible; GTJPBot/1.0)"},
    )
    response.raise_for_status()
    title, snippet = extract_article_text_from_html(response.text)

    script_candidates = _extract_script_text_candidates(response.text)
    hostname = urlparse(url).hostname or "custom-url"
    is_xiaohongshu = "xiaohongshu.com" in hostname

    if script_candidates and _snippet_needs_ocr(snippet):
        snippet = _combine_text_candidates(script_candidates, max_chars=2200)

    # For Xiaohongshu-like pages, merge HTML text + script-derived text for better continuity.
    if is_xiaohongshu and script_candidates and not _snippet_needs_ocr(snippet):
        merged = _combine_text_candidates([snippet, *script_candidates], max_chars=2200)
        if len(merged) > len(snippet):
            snippet = merged

    should_try_ocr = _snippet_needs_ocr(snippet) or is_xiaohongshu
    if should_try_ocr:
        soup = BeautifulSoup(response.text, "html.parser")
        image_candidates = _extract_embedded_image_urls(response.text) + _extract_image_candidates(soup, url)
        deduped: list[str] = []
        seen: set[str] = set()
        for image_url in image_candidates:
            if image_url in seen:
                continue
            seen.add(image_url)
            deduped.append(image_url)
        image_candidates = deduped[:12]
        ocr_chunks: list[str] = []
        for image_url in image_candidates:
            ocr_text = ocr_from_image_url(image_url, timeout=timeout)
            if len(ocr_text) >= 40:
                ocr_chunks.append(ocr_text)
            if len(ocr_chunks) >= 4:
                break
        if ocr_chunks:
            if snippet:
                snippet = _combine_text_candidates([snippet, *ocr_chunks], max_chars=2200)
            else:
                snippet = _combine_text_candidates(ocr_chunks, max_chars=2200)

    source_name = hostname.replace("www.", "")
    category = determine_category(source_name, title, snippet, url)
    return TrendItem(
        source_name=source_name,
        category=category,
        title=title,
        url=url,
        snippet=snippet,
    )
