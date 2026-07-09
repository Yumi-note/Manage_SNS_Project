from global_trend_jp_publisher.models import TrendItem
from global_trend_jp_publisher.pipeline import select_top_items_interleaved


def _item(source: str, idx: int) -> TrendItem:
    return TrendItem(
        source_name=source,
        category="tech",
        title=f"{source} article {idx}",
        url=f"https://example.com/{source}/{idx}",
        snippet="snippet",
    )


def test_select_top_items_interleaved_caps_total() -> None:
    items = [_item("A", i) for i in range(5)] + [_item("B", i) for i in range(5)]
    selected = select_top_items_interleaved(items, 4)
    assert len(selected) == 4


def test_select_top_items_interleaved_mixes_sources() -> None:
    items = [_item("A", i) for i in range(5)] + [_item("B", i) for i in range(5)]
    selected = select_top_items_interleaved(items, 4)
    sources = {item.source_name for item in selected}
    assert sources == {"A", "B"}


def test_select_top_items_interleaved_no_cap_when_total_is_zero() -> None:
    items = [_item("A", i) for i in range(3)]
    assert select_top_items_interleaved(items, 0) == items


def test_select_top_items_interleaved_returns_all_when_under_total() -> None:
    items = [_item("A", i) for i in range(2)]
    assert select_top_items_interleaved(items, 10) == items
