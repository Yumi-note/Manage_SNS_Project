import pytest

from global_trend_jp_publisher.models import DraftPost
from global_trend_jp_publisher.quality.checks import QualityError, validate_draft


def test_validate_draft_ok() -> None:
    draft = DraftPost(
        title_ja="タイトル",
        summary_ja="これは十分な長さを持つ日本語要約のサンプルです。",
        x_post="タイトル\nこれは要約です\n出典: https://example.com",
        redbook_post="long form",
        takeaways_ja=["示唆1", "示唆2"],
        source_url="https://example.com",
        source_name="source",
        category="tech",
        needs_fact_check=True,
    )
    validate_draft(draft)


def test_validate_draft_raises_without_source() -> None:
    draft = DraftPost(
        title_ja="タイトル",
        summary_ja="これは十分な長さを持つ日本語要約のサンプルです。",
        x_post="タイトル\nこれは要約です\n出典: ",
        redbook_post="long form",
        takeaways_ja=["示唆1", "示唆2"],
        source_url="",
        source_name="source",
        category="tech",
        needs_fact_check=True,
    )
    with pytest.raises(QualityError):
        validate_draft(draft)
