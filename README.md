# Manage_SNS_Project

海外トレンドを日本向けに再構成し、X と Redbook 向けの投稿下書きを生成する管理用リポジトリです。
X / Redbook 投稿のネタ文作成自動化ツールとして運用できる構成にしています。

## Main project

- 投稿生成プロジェクト: [global-trend-jp-publisher](global-trend-jp-publisher)

## GitHub Actions

- 日次実行ワークフローは `.github/workflows/daily_trend_posts.yml` にあります。
- 実行対象は `global-trend-jp-publisher` ディレクトリです。
