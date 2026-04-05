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

IOS_SOURCES = [
    {"url": "https://developer.apple.com/news/rss/news.rss", "name": "Apple Dev"},
    {"url": "https://www.hackingwithswift.com/articles/rss",  "name": "HackingWithSwift"},
    {"url": "https://www.swiftbysundell.com/feed.rss",        "name": "SwiftBySundell"},
    {"url": "https://9to5mac.com/feed/",                      "name": "9to5Mac"},
]

# Vision Pro専用ソース（一般Appleニュースも含むため、必ずキーワードフィルタをかけて使う）
VISIONPRO_SOURCES = [
    {"url": "https://feeds.macrumors.com/MacRumors-All", "name": "MacRumors"},
    {"url": "https://9to5mac.com/feed/",                 "name": "9to5Mac"},
]

IOS_KEYWORDS = ["iOS", "Swift", "SwiftUI", "Xcode", "App Store", "iPhone", "UIKit"]
VISIONPRO_KEYWORDS = ["Vision Pro", "visionOS", "spatial computing", "RealityKit", "ARKit", "ビジョンプロ"]

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


def collect_ios_entries(hours: int = 24) -> list[dict]:
    """iOS専用RSSソースからエントリを収集し、重複排除して返す。"""
    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    seen_urls: set[str] = set()
    all_entries: list[dict] = []

    for source in IOS_SOURCES:
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


def collect_visionpro_entries(hours: int = 48) -> list[dict]:
    """Vision Pro専用RSSソースからVision Proキーワードでフィルタして収集する。

    デフォルト48時間で取得することで、Vision Pro記事の少ない日でも取りこぼしを減らす。
    """
    since = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    seen_urls: set[str] = set()
    all_entries: list[dict] = []

    for source in VISIONPRO_SOURCES:
        try:
            entries = fetch_entries(source, since)
            for entry in entries:
                url = entry["url"]
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_entries.append(entry)
        except Exception as e:
            print(f"[WARNING] {source['name']} の取得に失敗: {e}")

    return filter_by_keywords(all_entries, VISIONPRO_KEYWORDS)


def filter_by_keywords(entries: list[dict], keywords: list[str]) -> list[dict]:
    """タイトルにキーワードを含むエントリを返す（大文字小文字を区別しない）。"""
    lower_keywords = [kw.lower() for kw in keywords]
    result = []
    for entry in entries:
        title_lower = entry["title"].lower()
        if any(kw in title_lower for kw in lower_keywords):
            result.append(entry)
    return result


def deduplicate(entries: list[dict]) -> list[dict]:
    """URLで重複を排除する。先に出現したエントリを優先する。"""
    seen_urls: set[str] = set()
    result = []
    for entry in entries:
        if entry["url"] not in seen_urls:
            seen_urls.add(entry["url"])
            result.append(entry)
    return result


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
        safe_title = entry["title"].replace('"', '\u201d')
        lines.append(f'{i}. [{safe_title}]({entry["url"]}) - {entry["source"]}')

    lines.append("")
    return "\n".join(lines)


def build_daily_md(
    general: list[dict],
    ios_entries: list[dict],
    vp_entries: list[dict],
    title: str,
    date_str: str,
) -> str:
    """3セクション（IT全般・iOS・Vision Pro）を含む日次 Markdown を組み立てる。"""
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {date_str}",
        'type: "news"',
        "draft: false",
        "---",
        "",
        f"## 今日のITニュース TOP{len(general)}",
        "",
    ]
    for i, entry in enumerate(general, 1):
        safe_title = entry["title"].replace('"', '\u201d')
        lines.append(f'{i}. [{safe_title}]({entry["url"]}) - {entry["source"]}')

    if ios_entries:
        lines += ["", "## iOSニュース", ""]
        for i, entry in enumerate(ios_entries, 1):
            safe_title = entry["title"].replace('"', '\u201d')
            lines.append(f'{i}. [{safe_title}]({entry["url"]}) - {entry["source"]}')

    if vp_entries:
        lines += ["", "## Vision Pro ニュース", ""]
        for i, entry in enumerate(vp_entries, 1):
            safe_title = entry["title"].replace('"', '\u201d')
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
        safe_title = entry["title"].replace('"', '\u201d')
        lines.append(f'{i}. [{safe_title}]({entry["url"]}) - {entry["source"]}')

    lines.append("")
    return "\n".join(lines)


def write_daily(now: datetime) -> None:
    """今日のランキングページを生成する。"""
    date_label = now.strftime("%Y-%m-%d")
    date_iso = now.strftime("%Y-%m-%dT04:00:00+09:00")

    # 1. IT全般エントリ
    general = collect_all_entries(hours=24)[:TOP_N]

    if not general:
        print("[INFO] 今日のエントリが0件のため、daily ページをスキップします。")
        return

    # 2. iOSエントリ = iOS専用RSS ＋ 全ソースのキーワードフィルタ
    ios_from_sources = collect_ios_entries(hours=24)
    ios_from_keywords = filter_by_keywords(collect_all_entries(hours=24), IOS_KEYWORDS)
    ios_entries = deduplicate(ios_from_sources + ios_from_keywords)[:15]

    # 3. Vision Proエントリ = Vision Pro専用ソース（48h）＋ 一般ソースのキーワードフィルタ
    # VISIONPRO_SOURCESからVision Proキーワードでフィルタ済みの記事を取得し、
    # さらに一般ソースにもVision Pro記事があれば追加する
    vp_from_sources = collect_visionpro_entries(hours=48)
    vp_from_general = filter_by_keywords(general, VISIONPRO_KEYWORDS)
    vp_entries = deduplicate(vp_from_sources + vp_from_general)[:10]

    title = f"{date_label} ITニュースランキング"
    content = build_daily_md(general, ios_entries, vp_entries, title, date_iso)

    out_dir = CONTENT_NEWS_DIR / date_label
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[INFO] 書き込み完了: {out_path} (IT全般:{len(general)}件, iOS:{len(ios_entries)}件, VisionPro:{len(vp_entries)}件)")


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
