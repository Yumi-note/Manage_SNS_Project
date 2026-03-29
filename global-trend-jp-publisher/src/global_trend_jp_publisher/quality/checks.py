from __future__ import annotations

from global_trend_jp_publisher.models import DraftPost


class QualityError(Exception):
    pass


def validate_draft(draft: DraftPost) -> None:
    if not draft.source_url:
        raise QualityError("source_url is required")
    if "出典:" not in draft.x_post:
        raise QualityError("x_post must contain attribution")
    if len(draft.x_post) > 280:
        raise QualityError("x_post must be <= 280 chars")
    if len(draft.summary_ja.strip()) < 20:
        raise QualityError("summary is too short")
