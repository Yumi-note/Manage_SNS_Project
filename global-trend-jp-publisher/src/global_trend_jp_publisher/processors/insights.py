from __future__ import annotations


def build_japan_takeaways(category: str, title_ja: str, summary_ja: str) -> list[str]:
    text = f"{title_ja} {summary_ja}"

    if category == "finance":
        bullets = [
            "日本株、為替、金利のどこに波及する話かを切り分けると、国内読者に伝わりやすくなります。",
            "数字が出ている話題は、その数値が一次情報でも確認できるかを見てから投稿すると安全です。",
        ]
        if any(keyword in text for keyword in ["金", "ゴールド", "gold", "silver", "原油"]):
            bullets[1] = "コモディティ関連は為替やインフレ見通しと合わせて見ると、日本の家計や投資判断に結びつけやすいです。"
        return bullets

    bullets = [
        "日本企業や個人がすぐ試せる使い方があるかを一言足すと、海外ニュースが自分ごと化しやすくなります。",
        "国内の類似サービスや競合企業と比べて何が新しいのかを補足すると、読者の理解が深まります。",
    ]
    if any(keyword in text.lower() for keyword in ["ai", "生成", "chatbot", "model"]):
        bullets[1] = "AI系の話題は、業務効率化・制作・学習のどこに効くかを日本語で具体化すると保存されやすくなります。"
    return bullets


def build_x_japan_hook(category: str, title_ja: str, summary_ja: str) -> str:
    text = f"{title_ja} {summary_ja}"

    if category == "finance":
        if any(keyword in text for keyword in ["金", "ゴールド", "silver", "原油", "コモディティ"]):
            return "日本視点: 為替とインフレの文脈で見ると実生活へのつながりが見えやすい。"
        if any(keyword in text for keyword in ["AI", "ai", "半導体", "NVIDIA", "エヌビディア"]):
            return "日本視点: 日本株では半導体・電機への連想が起きやすいテーマです。"
        return "日本視点: 日本株・為替・金利のどこに効く話か一言添えると伝わりやすい。"

    if any(keyword in text.lower() for keyword in ["ai", "生成", "chatbot", "model"]):
        return "日本視点: 仕事や学習でどう使えるかまで落とすと保存されやすい話題です。"
    if any(keyword in text.lower() for keyword in ["sale", "deal", "price", "discount", "headset", "device"]):
        return "日本視点: 国内で代替できる製品や価格差まで触れると反応を取りやすいです。"
    return "日本視点: 日本での使い道や国内サービス比較を一言入れると刺さりやすいです。"