import email

from global_trend_jp_publisher.models import DraftPost
from global_trend_jp_publisher.notifications.email_notifier import (
    build_security_alert_body,
    build_security_alert_subject,
    send_security_alert_email,
)


def _security_draft() -> DraftPost:
    return DraftPost(
        title_ja="重大な脆弱性が発見される",
        summary_ja="要約です。",
        x_post="",
        redbook_post="",
        takeaways_ja=[],
        source_url="https://example.com/cve",
        source_name="TechCrunch",
        category="tech",
        needs_fact_check=True,
        title_original="Critical vulnerability found",
        security_alert=True,
        security_reason="リモートコード実行が可能なため。",
    )


def test_build_security_alert_subject_includes_count() -> None:
    subject = build_security_alert_subject([_security_draft(), _security_draft()])
    assert "2件" in subject


def test_build_security_alert_body_includes_article_details() -> None:
    body = build_security_alert_body([_security_draft()])
    assert "重大な脆弱性が発見される" in body
    assert "リモートコード実行が可能なため。" in body
    assert "https://example.com/cve" in body


def test_send_security_alert_email_noop_when_no_drafts(monkeypatch) -> None:
    def fail(*args, **kwargs):
        raise AssertionError("SMTP should not be used when there are no drafts")

    monkeypatch.setattr("global_trend_jp_publisher.notifications.email_notifier.smtplib.SMTP_SSL", fail)

    send_security_alert_email(
        [],
        to_email="to@example.com",
        smtp_host="smtp.gmail.com",
        smtp_port=465,
        smtp_user="user@example.com",
        smtp_password="pw",
    )


def test_send_security_alert_email_sends_via_smtp(monkeypatch) -> None:
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port):
            sent["host"] = host
            sent["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def login(self, user, password):
            sent["login"] = (user, password)

        def sendmail(self, from_addr, to_addrs, message):
            sent["from"] = from_addr
            sent["to"] = to_addrs
            sent["message"] = message

    monkeypatch.setattr("global_trend_jp_publisher.notifications.email_notifier.smtplib.SMTP_SSL", FakeSMTP)

    send_security_alert_email(
        [_security_draft()],
        to_email="to@example.com",
        smtp_host="smtp.gmail.com",
        smtp_port=465,
        smtp_user="user@example.com",
        smtp_password="pw",
    )

    assert sent["host"] == "smtp.gmail.com"
    assert sent["port"] == 465
    assert sent["login"] == ("user@example.com", "pw")
    assert sent["from"] == "user@example.com"
    assert sent["to"] == ["to@example.com"]

    parsed = email.message_from_string(sent["message"])
    body_part = parsed.get_payload()[0]
    assert "重大な脆弱性が発見される" in body_part.get_payload(decode=True).decode("utf-8")
