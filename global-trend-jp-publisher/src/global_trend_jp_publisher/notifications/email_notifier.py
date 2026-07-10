"""Email alert for articles flagged as important to a security engineer."""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from global_trend_jp_publisher.models import DraftPost


def build_security_alert_subject(drafts: list[DraftPost]) -> str:
    return f"[セキュリティ重要] テックニュース digest ({len(drafts)}件)"


def build_security_alert_body(drafts: list[DraftPost]) -> str:
    lines = [
        f"セキュリティエンジニアにとって重要と判定された記事が {len(drafts)} 件あります。",
        "",
    ]
    for draft in drafts:
        lines.extend(
            [
                f"■ {draft.title_ja}",
                f"  原題: {draft.title_original}",
                f"  判定理由: {draft.security_reason or '(理由なし)'}",
                f"  要約: {draft.summary_ja}",
                f"  URL: {draft.source_url}",
                "",
            ]
        )
    return "\n".join(lines)


def send_security_alert_email(
    drafts: list[DraftPost],
    *,
    to_email: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
) -> None:
    """Send a plaintext email listing security-relevant articles.

    No-ops when ``drafts`` is empty. Raises on any SMTP failure so callers
    can decide how to surface it (this pipeline logs and continues rather
    than failing the whole digest run).
    """
    if not drafts:
        return

    message = MIMEMultipart()
    message["Subject"] = build_security_alert_subject(drafts)
    message["From"] = smtp_user
    message["To"] = to_email
    message.attach(MIMEText(build_security_alert_body(drafts), "plain", "utf-8"))

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [to_email], message.as_string())
