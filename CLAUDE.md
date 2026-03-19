# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Hugo ベースの個人ブログサイト（[kimujinyogi.github.io](https://kimujinyogi.github.io/)）。
テーマは `zzo`（Git サブモジュール）。コンテンツは日本語で、キャンピングカー旅行・日常生活・書籍レビューが主なカテゴリ。

## ブランチ構成

- `campcar` — ソースブランチ（このブランチに push するとCIが動く）
- `master` — CircleCI が自動生成した公開用 HTML が入るブランチ（直接編集しない）

## ビルドコマンド

Hugo がインストールされていることが前提。

```bash
# 開発サーバー起動（campcar/ ディレクトリ内で実行）
cd campcar && hugo server

# 本番ビルド
cd campcar && HUGO_ENV=production hugo -v

# 新しい記事を作成
cd campcar && hugo new posts/<記事ディレクトリ名>/index.md
```

CircleCI は `campcar` ブランチへの push をトリガーに自動デプロイ（`.circleci/config.yml` 参照）。

## ディレクトリ構造

```
campcar/               # Hugo プロジェクトのルート
├── config/_default/   # Hugo 設定ファイル群
├── content/
│   └── posts/         # ブログ記事（各記事がサブディレクトリ）
├── assets/css/
│   └── custom.css     # テーマへのカスタムCSSオーバーライド
├── layouts/partials/  # テーマのpartialオーバーライド
├── static/            # 画像などの静的ファイル
└── themes/zzo/        # Git サブモジュール（テーマ）
books/                 # campcar 外に置いてある書籍メモ（サイトには含まれない）
```

## 記事の書き方

各記事は `campcar/content/posts/<記事名>/index.md` という構造。Front matter の例：

```yaml
---
title: "タイトル"
date: 2026-01-01
categories: ["カテゴリ"]
tags: ["タグ1", "タグ2"]
---
```

画像は `campcar/static/<記事名>/` に置き、`/記事名/画像名.jpg` で参照する。

中央揃えの画像は `custom.css` で定義された `imagecenter` クラスを使う：

```html
<img src="/path/to/image.jpg" class="imagecenter">
```

## テーマのカスタマイズ

`themes/zzo/` は Git サブモジュールなので直接編集しない。オーバーライドは：
- CSS: `campcar/assets/css/custom.css`
- テンプレート: `campcar/layouts/` 以下に同じパスで配置
