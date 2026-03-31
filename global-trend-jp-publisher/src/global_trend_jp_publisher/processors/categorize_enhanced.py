"""Enhanced categorization for tech news articles.

Maps articles to 9 subcategories within the tech domain:
- AI/ML: artificial intelligence, machine learning, LLMs, neural networks
- Security: cybersecurity, privacy, encryption, data protection
- Startups: venture funding, new companies, Series A/B/C
- Hardware: devices, gadgets, chips, IoT, robotics
- Enterprise: B2B, cloud, productivity tools, infrastructure
- Policy: regulations, antitrust, government tech policy
- Media: content, streaming, creator economy
- Mobile: smartphones, apps, wearables
- Other: everything else
"""

from __future__ import annotations


CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "AI/ML": [
        "ai",
        "artificial intelligence",
        "machine learning",
        "llm",
        "large language model",
        "gpt",
        "chatgpt",
        "claude",
        "gemini",
        "neural",
        "deep learning",
        "transformer",
        "generative",
        "model",
        "生成",
        "ai",
        "機械学習",
    ],
    "Security": [
        "security",
        "cybersecurity",
        "privacy",
        "encryption",
        "breach",
        "vulnerability",
        "zero-day",
        "malware",
        "ransomware",
        "データ保護",
        "セキュリティ",
        "プライバシー",
    ],
    "Startups": [
        "startup",
        "venture",
        "funding",
        "series a",
        "series b",
        "series c",
        "ipo",
        "spac",
        "seed",
        "angel",
        "founder",
        "raised",
        "投資",
        "資金調達",
    ],
    "Hardware": [
        "device",
        "gadget",
        "chip",
        "semiconductor",
        "gpu",
        "cpu",
        "hardware",
        "robot",
        "drone",
        "iot",
        "wearable",
        "smartwatch",
        "headphone",
        "display",
        "ハードウェア",
        "ガジェット",
    ],
    "Enterprise": [
        "enterprise",
        "b2b",
        "business",
        "saas",
        "cloud",
        "aws",
        "azure",
        "gcp",
        "infrastructure",
        "database",
        "docker",
        "kubernetes",
        "productivity",
        "エンタープライズ",
    ],
    "Policy": [
        "regulation",
        "antitrust",
        "policy",
        "government",
        "law",
        "bill",
        "congress",
        "gdpr",
        "cookie",
        "privacy law",
        "規制",
        "政策",
    ],
    "Media": [
        "content",
        "streaming",
        "spotify",
        "netflix",
        "youtube",
        "tiktok",
        "creator",
        "podcast",
        "music",
        "video",
        "メディア",
        "配信",
    ],
    "Mobile": [
        "mobile",
        "smartphone",
        "iphone",
        "android",
        "app",
        "ios",
        "tablet",
        "ipad",
        "wearable",
        "smartwatch",
        "モバイル",
        "アプリ",
    ],
}


def categorize_article_enhanced(title: str, summary: str, source_name: str) -> str:
    """Categorize an article into one of 9 tech subcategories.

    Args:
        title: Article title (English or Japanese)
        summary: Article summary/snippet
        source_name: Source publication name

    Returns:
        One of: "AI/ML", "Security", "Startups", "Hardware", "Enterprise",
                "Policy", "Media", "Mobile", "Other"
    """
    text = f"{title} {summary}".lower()

    # Count keyword matches per category
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text)

    # Find the highest-scoring category
    if not scores or max(scores.values()) == 0:
        return "Other"

    best_category = max(scores, key=scores.get)
    return best_category


def get_category_emoji(category: str) -> str:
    """Return an emoji for the given category."""
    emojis = {
        "AI/ML": "🤖",
        "Security": "🔒",
        "Startups": "🚀",
        "Hardware": "⚙️",
        "Enterprise": "🏢",
        "Policy": "⚖️",
        "Media": "🎬",
        "Mobile": "📱",
        "Other": "📰",
    }
    return emojis.get(category, "📌")


def get_category_color(category: str) -> str:
    """Return a hex color for the given category (for UI)."""
    colors = {
        "AI/ML": "#10b981",  # emerald
        "Security": "#f97316",  # orange
        "Startups": "#8b5cf6",  # violet
        "Hardware": "#06b6d4",  # cyan
        "Enterprise": "#3b82f6",  # blue
        "Policy": "#ec4899",  # pink
        "Media": "#f59e0b",  # amber
        "Mobile": "#6366f1",  # indigo
        "Other": "#6b7280",  # gray
    }
    return colors.get(category, "#9ca3af")
