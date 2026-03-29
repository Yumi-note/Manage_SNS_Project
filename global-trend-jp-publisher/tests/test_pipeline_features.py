from global_trend_jp_publisher.models import TrendItem
from global_trend_jp_publisher.pipeline import build_drafts
from global_trend_jp_publisher.processors.categorize import determine_category


def test_determine_category_from_source_name() -> None:
    assert determine_category("The Verge", "new device", "AI features", "https://example.com/gadgets/1") == "tech"
    assert determine_category("WSJ.com: Markets", "stocks lower", "gold declines", "https://example.com/markets/1") == "finance"


def test_determine_category_uses_url_and_weighted_terms() -> None:
    assert determine_category(
        "Example Source",
        "Developers get new AI API tools",
        "software teams can automate workflows",
        "https://example.com/tech/api-tools",
    ) == "tech"
    assert determine_category(
        "Example Source",
        "Treasury yield rises as stock market falls",
        "earnings and fed concerns pressure investors",
        "https://example.com/business/markets-update",
    ) == "finance"


def test_build_drafts_applies_category_filter_and_takeaways() -> None:
    items = [
        TrendItem(
            source_name="The Verge",
            category="tech",
            title="AI app update",
            url="https://example.com/tech",
            snippet="A new AI model improves work automation.",
        ),
        TrendItem(
            source_name="WSJ.com: Markets",
            category="finance",
            title="Gold and stocks move lower",
            url="https://example.com/finance",
            snippet="Markets fell after rate concerns.",
        ),
    ]

    drafts = build_drafts(items, category_filter="finance")

    assert len(drafts) == 1
    assert drafts[0].category == "finance"
    assert len(drafts[0].takeaways_ja) == 2
    assert "日本向けの示唆:" in drafts[0].redbook_post