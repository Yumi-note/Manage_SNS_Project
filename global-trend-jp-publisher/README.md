# global-trend-jp-publisher

海外トレンド（テック/金融）を収集し、日本向けに再構成した投稿ドラフトを生成する Python プロジェクトです。最終投稿は人間が確認して X / Redbook に手動投稿する運用を前提としています。

## What it does

- RSS や API ソースから記事候補を収集
- テック / 金融に自動分類してカテゴリ別に出力
- 英語/中国語などを検出し、日本語向けに要約・再構成
- X 向け短文と Redbook 向け長文のドラフトを同時生成
- X 向けには日本向けの一言補足を自動挿入
- Redbook 向けに日本向けの示唆を自動追記
- 引用元 URL、注意事項、ファクトチェックフラグを付与
- 日次出力を Markdown / JSON で保存

## Safety and policy

- 記事本文の丸ごと翻訳・転載はしない
- 要約と独自表現で再構成する
- 元記事リンクを明示する
- 数値・主張は公開前に必ず人間確認する

## Quick start

1. Python 3.11 を用意
2. 環境変数テンプレートをコピー

```bash
cp .env.example .env
```

3. 依存をインストール

```bash
pip install -r requirements.txt
```

4. 日次ドラフト生成

```bash
gtjp run-daily
```

## Output

- 日次フォルダ: `data/drafts/YYYY-MM-DD/HHMMSS/`
- `drafts.json`: 構造化データ
- `posts.md`: 投稿候補（X / Redbook）
- `tech_posts.md` / `finance_posts.md`: カテゴリ別投稿候補
- `tech_drafts.json` / `finance_drafts.json`: カテゴリ別構造化データ

## Commands

- `gtjp run-daily` : 収集からドラフト出力まで実行
- `gtjp run-daily --category tech` : テックだけ出力
- `gtjp run-daily --category finance` : 金融だけ出力
- `gtjp list-sources` : 現在の入力ソースを表示

## Classification logic

- ソース名、URL、タイトル、要約内キーワードを組み合わせてテック / 金融を判定
- X では文字数制限内で、日本向けの一言を優先的に残す
