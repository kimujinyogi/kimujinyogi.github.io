#!/usr/bin/env python3
"""
ITニュースランキング生成スクリプト
RSS フィードから最新記事を収集し、Hugo 用 Markdown を生成する。
"""

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser

JST = timezone(timedelta(hours=9))

RSS_SOURCES = [
    {
        "url": "https://b.hatena.ne.jp/hotentry/it.rss",
        "name": "はてブ",
    },
    {
        "url": "https://zenn.dev/feed",
        "name": "Zenn",
    },
    {
        "url": "https://qiita.com/popular-items/feed",
        "name": "Qiita",
    },
]

CONTENT_NEWS_DIR = Path(__file__).parent.parent / "campcar" / "content" / "news"
TOP_N = 20


def fetch_entries(source: dict, since: datetime) -> list[dict]:
    """1つのRSSソースからエントリを取得する。"""
    feed = feedparser.parse(source["url"])
    entries = []
    for entry in feed.entries:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

        if published and published < since:
            continue

        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        entries.append(
            {
                "title": title,
                "url": link,
                "source": source["name"],
                "published": published,
            }
        )
    return entries


def collect_all_entries(hours: int = 24) -> list[dict]:
    """全RSSソースからエントリを収集し、重複排除して返す。"""
    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    seen_urls: set[str] = set()
    all_entries: list[dict] = []

    for source in RSS_SOURCES:
        try:
            entries = fetch_entries(source, since)
            for entry in entries:
                url = entry["url"]
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_entries.append(entry)
        except Exception as e:
            print(f"[WARNING] {source['name']} の取得に失敗: {e}")

    return all_entries


def build_ranking_md(entries: list[dict], title: str, date_str: str) -> str:
    """ランキング Markdown 文字列を組み立てる。"""
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {date_str}",
        'type: "news"',
        "draft: false",
        "---",
        "",
        f"## 今日のITニュース TOP{len(entries)}",
        "",
    ]
    for i, entry in enumerate(entries, 1):
        safe_title = entry["title"].replace('"', """)
        lines.append(f'{i}. [{safe_title}]({entry["url"]}) - {entry["source"]}')

    lines.append("")
    return "\n".join(lines)


def build_weekly_md(entries: list[dict], title: str, date_str: str) -> str:
    """週間まとめ Markdown 文字列を組み立てる。"""
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {date_str}",
        'type: "news"',
        "draft: false",
        "---",
        "",
        f"## 今週のITニュース TOP{len(entries)}",
        "",
    ]
    for i, entry in enumerate(entries, 1):
        safe_title = entry["title"].replace('"', """)
        lines.append(f'{i}. [{safe_title}]({entry["url"]}) - {entry["source"]}')

    lines.append("")
    return "\n".join(lines)


def write_daily(now: datetime) -> None:
    """今日のランキングページを生成する。"""
    date_label = now.strftime("%Y-%m-%d")
    date_iso = now.strftime("%Y-%m-%dT04:00:00+09:00")

    entries = collect_all_entries(hours=24)
    entries = entries[:TOP_N]

    if not entries:
        print("[INFO] 今日のエントリが0件のため、daily ページをスキップします。")
        return

    title = f"{date_label} ITニュースランキング"
    content = build_ranking_md(entries, title, date_iso)

    out_dir = CONTENT_NEWS_DIR / date_label
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[INFO] 書き込み完了: {out_path} ({len(entries)}件)")


def write_weekly(now: datetime) -> None:
    """週間まとめページを生成する（土曜日のみ呼ぶ想定）。"""
    entries = collect_all_entries(hours=24 * 7)
    entries = entries[:TOP_N]

    if not entries:
        print("[INFO] 週間エントリが0件のため、weekly ページをスキップします。")
        return

    # 週の開始日（7日前の日曜日）
    week_start = now - timedelta(days=6)
    week_label = week_start.strftime("%Y-%m-%d")
    date_iso = now.strftime("%Y-%m-%dT04:00:00+09:00")
    title = f"週間ITニュースランキング ({week_label} 〜 {now.strftime('%Y-%m-%d')})"

    content = build_weekly_md(entries, title, date_iso)

    out_dir = CONTENT_NEWS_DIR / f"weekly-{week_label}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[INFO] 週間まとめ書き込み完了: {out_path} ({len(entries)}件)")


def main() -> None:
    now = datetime.now(tz=JST)
    print(f"[INFO] 実行日時 (JST): {now.isoformat()}")

    write_daily(now)

    # 土曜日 (weekday==5) は週間まとめも生成
    if now.weekday() == 5:
        write_weekly(now)


if __name__ == "__main__":
    main()
