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

画像テキスト抽出（OCR）は `rapidocr-onnxruntime` を優先利用します。
環境によってはフォールバックとしてOS側の `tesseract` コマンドも使用できます。

- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get update && sudo apt-get install -y tesseract-ocr`

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
- `gtjp run-from-url <URL>` : 単一URLから下書きを生成
- `gtjp run-from-url <URL> --category tech|finance` : 単一URLをカテゴリ指定で生成
- `gtjp run-from-redbook-url-list <URLファイル>` : Redbook用のURL一覧から一括生成
- `gtjp list-sources` : 現在の入力ソースを表示

### Redbook URL list format

- UTF-8テキストで1行1URL
- `#` で始まる行と空行は無視

例:

```text
# redbook or article urls
https://techcrunch.com/2026/03/28/stanford-study-outlines-dangers-of-asking-ai-chatbots-for-personal-advice/
https://www.theverge.com/entertainment/903056/suno-ai-music-v5-5-model
```

実行例:

```bash
gtjp run-from-redbook-url-list data/inputs/redbook_urls.txt
```

出力先には通常の `posts.md` などに加え、Redbook投稿だけをまとめた `redbook_posts_only.md` も生成されます。
さらに、X投稿原文だけをまとめた `x_posts_only.md` も生成されます。

## GitHub Actions for Redbook Tech -> X

- ワークフロー: `.github/workflows/redbook_tech_x_drafts.yml`
- 実行時刻: 毎日 01:00 / 03:00 JST
- 入力URL一覧: `data/inputs/redbook_urls.txt`
- 主な出力: `x_posts_only.md`（X投稿原文）

## Classification logic

- ソース名、URL、タイトル、要約内キーワードを組み合わせてテック / 金融を判定
- X では文字数制限内で、日本向けの一言を優先的に残す
- 画像中心ページで本文抽出が弱い場合は、画像OCRの結果を要約元に使う
