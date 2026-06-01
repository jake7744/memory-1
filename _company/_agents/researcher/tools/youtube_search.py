#!/usr/bin/env python3
"""Researcher YouTube search collector.

Uses the shared YouTube Data API key from:
  _agents/youtube/tools/youtube_account.json

Per-tool options live in youtube_search.json next to this script.
It prints a markdown-ready research brief and writes youtube_search_report.md.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
CONFIG_PATH = os.path.join(HERE, "youtube_search.json")
REPORT_PATH = os.path.join(HERE, "youtube_search_report.md")
YOUTUBE_ACCOUNT_PATH = os.path.abspath(
    os.path.join(HERE, "..", "..", "youtube", "tools", "youtube_account.json")
)
YOUTUBE_OAUTH_PATH = os.path.abspath(
    os.path.join(HERE, "..", "..", "youtube", "oauth.local.json")
)


def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def raw_json_value(path, key):
    try:
        import re
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        m = re.search(r'"' + re.escape(key) + r'"\s*:\s*"([^"]*)"', text)
        return m.group(1).strip() if m else ""
    except Exception:
        return ""


def get_config():
    cfg = load_json(CONFIG_PATH, {})
    acct = load_json(YOUTUBE_ACCOUNT_PATH, {})
    api_key = (
        cfg.get("YOUTUBE_API_KEY")
        or acct.get("YOUTUBE_API_KEY")
        or raw_json_value(YOUTUBE_ACCOUNT_PATH, "YOUTUBE_API_KEY")
        or ""
    ).strip()
    keywords = cfg.get("TARGET_KEYWORDS") or []
    if isinstance(keywords, str):
        keywords = [x.strip() for x in keywords.split(",") if x.strip()]
    max_results = int(cfg.get("MAX_RESULTS") or 5)
    published_days = int(cfg.get("PUBLISHED_DAYS") or 90)
    order = cfg.get("ORDER") or "relevance"
    return api_key, keywords, max_results, published_days, order


def build_youtube_client(api_key):
    from googleapiclient.discovery import build

    if api_key:
        return build("youtube", "v3", developerKey=api_key)

    oauth = load_json(YOUTUBE_OAUTH_PATH, {})
    refresh_token = (oauth.get("refresh_token") or raw_json_value(YOUTUBE_OAUTH_PATH, "refresh_token") or "").strip()
    client_id = (
        oauth.get("client_id")
        or raw_json_value(YOUTUBE_ACCOUNT_PATH, "YOUTUBE_OAUTH_CLIENT_ID")
        or ""
    ).strip()
    client_secret = (
        oauth.get("client_secret")
        or raw_json_value(YOUTUBE_ACCOUNT_PATH, "YOUTUBE_OAUTH_CLIENT_SECRET")
        or ""
    ).strip()
    if not refresh_token or not client_id or not client_secret:
        print("ERROR: YOUTUBE_API_KEY is missing and OAuth refresh token/client is incomplete.")
        print("Set YOUTUBE_API_KEY or reconnect YouTube OAuth in Connect AI.")
        sys.exit(1)

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def main():
    api_key, keywords, max_results, published_days, order = get_config()
    if not keywords:
        print("ERROR: TARGET_KEYWORDS is empty. Add search keywords to youtube_search.json.")
        sys.exit(1)

    try:
        import googleapiclient.discovery  # noqa: F401
    except ImportError:
        print("ERROR: google-api-python-client is not installed. Run: pip install google-api-python-client")
        sys.exit(1)

    youtube = build_youtube_client(api_key)
    published_after = (
        datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=published_days)
    ).isoformat("T").replace("+00:00", "Z")

    lines = [
        "# Researcher YouTube Search Report",
        "",
        f"- Keywords: {', '.join(keywords)}",
        f"- Published after: {published_after}",
        f"- Order: {order}",
        "",
    ]

    for keyword in keywords:
        lines.append(f"## Keyword: {keyword}")
        try:
            search = youtube.search().list(
                part="snippet",
                q=keyword,
                type="video",
                maxResults=max_results,
                order=order,
                publishedAfter=published_after,
            ).execute()
        except Exception as e:
            lines.append(f"- Search failed: {e}")
            lines.append("")
            continue

        video_ids = [
            item.get("id", {}).get("videoId")
            for item in search.get("items", [])
            if item.get("id", {}).get("videoId")
        ]
        stats_by_id = {}
        if video_ids:
            try:
                stats = youtube.videos().list(
                    part="statistics,contentDetails",
                    id=",".join(video_ids),
                ).execute()
                stats_by_id = {item["id"]: item for item in stats.get("items", [])}
            except Exception:
                stats_by_id = {}

        for idx, item in enumerate(search.get("items", []), 1):
            video_id = item.get("id", {}).get("videoId", "")
            snip = item.get("snippet", {})
            stat = stats_by_id.get(video_id, {}).get("statistics", {})
            title = snip.get("title", "").replace("\n", " ").strip()
            channel = snip.get("channelTitle", "").strip()
            published = snip.get("publishedAt", "")
            desc = snip.get("description", "").replace("\n", " ").strip()[:260]
            url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
            lines.extend([
                f"{idx}. {title}",
                f"   - Channel: {channel}",
                f"   - Published: {published}",
                f"   - Views: {stat.get('viewCount', 'n/a')}, Likes: {stat.get('likeCount', 'n/a')}, Comments: {stat.get('commentCount', 'n/a')}",
                f"   - URL: {url}",
                f"   - Description: {desc}",
            ])
        lines.append("")

    report = "\n".join(lines).strip() + "\n"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
