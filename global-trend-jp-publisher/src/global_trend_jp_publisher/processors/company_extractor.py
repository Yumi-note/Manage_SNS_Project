"""Company extractor and profile generator for tech articles.

Identifies tech companies mentioned in articles and generates company profile pages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CompanyProfile:
    """Company information."""

    name: str
    slug: str  # URL-safe identifier
    description: str  # What they do
    founded: str | None = None
    headquarters: str | None = None
    products: list[str] = None
    key_facts: list[str] = None

    def __post_init__(self):
        if self.products is None:
            self.products = []
        if self.key_facts is None:
            self.key_facts = []


# Comprehensive tech company database
TECH_COMPANIES: dict[str, CompanyProfile] = {
    "Google": CompanyProfile(
        name="Google",
        slug="google",
        description="検索エンジンと広告プラットフォームで知られるアメリカ合衆国のテクノロジー企業。"
        "Android、Gmail、YouTubeなど多くのウェブサービスを提供しており、世界中の個人と企業に欠かせない存在です。",
        founded="1998年",
        headquarters="カリフォルニア州マウンテンビュー",
        products=["検索エンジン", "Gmail", "Google Chrome", "Android", "YouTube", "Google Cloud", "Gmail アドレス変更機能"],
        key_facts=[
            "世界中で月間30億人以上がGoogleを使用",
            "検索市場でのシェアは90%以上",
            "2023年のAI技術への投資を大幅に増加",
            "プライバシー規制への対応が重要なテーマ",
        ],
    ),
    "Airbnb": CompanyProfile(
        name="Airbnb",
        slug="airbnb",
        description="民泊プラットフォームの大手企業。個人の部屋や住居を短期間で借りたい旅行者と、"
        "貸したい家主をマッチングするサービスを提供しています。世界220以上の国・地域で利用可能です。",
        founded="2008年",
        headquarters="カリフォルニア州サンフランシスコ",
        products=["民泊仲介サービス", "Airbnb Experiences", "Airbnb Adventures", "専用車送迎サービス"],
        key_facts=[
            "世界中で800万以上のリスティング",
            "累計4億人以上のゲストが利用",
            "COVID-19後、旅行需要の回復に伴い成長中",
            "地方創生と観光促進に貢献",
        ],
    ),
    "TechCrunch": CompanyProfile(
        name="TechCrunch",
        slug="techcrunch",
        description="テクノロジーとスタートアップニュースの大手メディア。"
        "ベンチャー企業の資金調達情報、新製品発表、業界インサイトを報道する情報源として、投資家や起業家に広く読まれています。",
        founded="2005年",
        headquarters="サンフランシスコ",
        products=["ニュースサイト", "Crunchbase（企業データベース）", "Disrupt イベント"],
        key_facts=[
            "月間1000万人以上の訪問者",
            "スタートアップ業界の第一報メディア",
            "Crunchbaseは400万社以上のデータを保有",
        ],
    ),
    "The Verge": CompanyProfile(
        name="The Verge",
        slug="the-verge",
        description="テクノロジー、サイエンス、アート、カルチャーをカバーするメディア。"
        "ガジェットレビュー、スマートフォン、ドローン、家電製品など、消費者向けテクノロジーの深掘り記事で知られています。",
        founded="2011年",
        headquarters="ニューヨーク",
        products=["ニュース・レビューサイト", "ポッドキャスト", "動画コンテンツ"],
        key_facts=[
            "テックニュースの信頼できるソース",
            "詳細で中立的なレビュー評で定評がある",
            "消費者向けテクノロジーのトレンド発信源",
        ],
    ),
    "Apple": CompanyProfile(
        name="Apple",
        slug="apple",
        description="iPhoneやMacで知られるアメリカのテクノロジー企業。ハード、ソフト、サービスを統合した"
        "エコシステムで、全世界のユーザーから高い顧客満足度を得ています。デザインと革新を重視する企業文化が特徴。",
        founded="1976年",
        headquarters="カリフォルニア州クパチーノ",
        products=["iPhone", "Mac", "iPad", "Apple Watch", "Apple TV", "AirPods"],
        key_facts=[
            "世界で最も価値のある公開企業の一つ",
            "AppStoreは100万以上のアプリをホスト",
            "プライバシー保護を強く推進",
            "55周年を2026年に迎える",
        ],
    ),
    "Amazon": CompanyProfile(
        name="Amazon",
        slug="amazon",
        description="オンライン小売とクラウドコンピューティングの大手企業。"
        "Amazonショッピング、AWS（クラウドサービス）、Prime Video、Alexaなど多角的に事業を展開しています。",
        founded="1994年",
        headquarters="ワシントン州シアトル",
        products=["Amazonショッピング", "AWS", "Prime Video", "Alexa", "Kindle"],
        key_facts=[
            "世界最大のクラウドサービスプロバイダー",
            "日本を含む世界中で迅速配送を実現",
            "新しい技術投資に積極的",
        ],
    ),
    "Meta": CompanyProfile(
        name="Meta",
        slug="meta",
        description="Facebook、Instagram、WhatsAppなどのソーシャルメディアプラットフォームを運営する企業。"
        "メタバース開発にも注力しており、テクノロジーと社会の関係を形作る大きな力を持っています。",
        founded="2004年（旧Facebook）",
        headquarters="カリフォルニア州メンロパーク",
        products=["Facebook", "Instagram", "WhatsApp", "Meta Quest", "Threads"],
        key_facts=[
            "世界で30億人以上が利用",
            "メタバースへの投資を積極化",
            "データプライバシーに関する規制圧力が高い",
        ],
    ),
    "Microsoft": CompanyProfile(
        name="Microsoft",
        slug="microsoft",
        description="Windows、Office、Azure、ChatGPT連携など、エンタープライズとコンシューマー向けソフトウェアの大手。"
        "クラウドコンピューティング、AI分野への投資を強化しており、業界の方向性を大きく影響します。",
        founded="1975年",
        headquarters="ワシントン州レドモンド",
        products=["Windows", "Office 365", "Azure", "Teams", "GitHub", "Copilot"],
        key_facts=[
            "Azure はクラウド市場で急速に成長",
            "OpenAI への投資で AI リーダーシップを強化",
            "企業向けソフトウェアで圧倒的シェア",
        ],
    ),
    "NVIDIA": CompanyProfile(
        name="NVIDIA",
        slug="nvidia",
        description="GPU（グラフィックス処理ユニット）と AI チップの技術で知られるアメリカの企業。"
        "AI モデル学習、ゲーミング、データセンターインフラの中核技術を提供しており、AI ブームの最大の受益者の一つです。",
        founded="1993年",
        headquarters="カリフォルニア州サンタクララ",
        products=["GPU チップ", "CUDA 技術", "AI ハードウェア"],
        key_facts=[
            "AI 学習には NVIDIA チップがほぼ必須",
            "ビットコイン採掘需要での収益経験",
            "最新 100 シリーズ AI チップは高需要",
        ],
    ),
    "SpaceX": CompanyProfile(
        name="SpaceX",
        slug="spacex",
        description="民間ロケット開発・衛星通信企業。Starlink という衛星インターネットサービスを提供しており、"
        "世界中の誰もが高速インターネットにアクセスできることを目指しています。",
        founded="2002年",
        headquarters="テキサス州ボーカ・チカ",
        products=["Starlink 衛星インターネット", "Falcon ロケット", "Dragon 宇宙船"],
        key_facts=[
            "Starlink は世界 170 以上の国で利用可能",
            "ロケット再利用技術で低コスト化を実現",
            "火星探査プロジェクトを進行中",
        ],
    ),
    "OpenAI": CompanyProfile(
        name="OpenAI",
        slug="openai",
        description="ChatGPT や GPT-4 などの大規模言語モデル（LLM）を開発する企業。"
        "AI の安全性と透明性を重視しながら、様々な分野での AI 応用を推進しています。",
        founded="2015年",
        headquarters="カリフォルニア州サンフランシスコ",
        products=["ChatGPT", "GPT-4", "API", "DALL-E"],
        key_facts=[
            "ChatGPT は最速で 1 億ユーザーを獲得",
            "Microsoft と戦略的パートナーシップ",
            "生成 AI 業界の技術リーダー",
        ],
    ),
    "Softr": CompanyProfile(
        name="Softr",
        slug="softr",
        description="ノーコード・ローコード プラットフォーム。非技術者でも ビジネスアプリを簡単に構築できるよう支援する企業。"
        "Airtable などのデータベースと連携し、プロトタイピングから本番運用まで対応します。",
        founded="2019年",
        headquarters="ドイツ・ベルリン",
        products=["ノーコードプラットフォーム", "AI ネイティブアプリビルダー"],
        key_facts=[
            "500 以上の企業が利用",
            "API First アーキテクチャ",
            "AI による自動コード生成機能を搭載",
        ],
    ),
    "Proton": CompanyProfile(
        name="Proton",
        slug="proton",
        description="プライバシー重視の通信・ストレージサービスプロバイダー。"
        "ProtonMail（暗号化メール）、Proton VPN、Proton Drive など複数のサービスで、"
        "ユーザーのプライバシーを高度に保護します。",
        founded="2014年",
        headquarters="スイス・ジュネーブ",
        products=["ProtonMail", "Proton VPN", "Proton Drive", "Proton Meet"],
        key_facts=[
            "エンドツーエンド暗号化で完全保護",
            "スイスの厳しいプライバシー法の下で運営",
            "200 万以上のユーザー",
        ],
    ),
}


def extract_companies_from_text(text: str) -> list[str]:
    """Extract company names mentioned in the given text.

    Args:
        text: Article title, summary, or full content

    Returns:
        List of company names found (no duplicates)
    """
    if not text:
        return []

    text_lower = text.lower()
    found = set()

    for company_name in TECH_COMPANIES.keys():
        # Case-insensitive search with word boundaries
        pattern = r"\b" + re.escape(company_name.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.add(company_name)

    return sorted(list(found))


def get_company_profile(company_name: str) -> CompanyProfile | None:
    """Get profile for a company by name.

    Returns None if not found in database.
    """
    return TECH_COMPANIES.get(company_name)


def get_all_companies() -> list[CompanyProfile]:
    """Get all company profiles."""
    return list(TECH_COMPANIES.values())
