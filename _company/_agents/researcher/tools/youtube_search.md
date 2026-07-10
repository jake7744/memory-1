# YouTube Search Collector

Researcher가 YouTube Data API v3로 키워드 기반 영상을 검색하고, 제목/채널/조회수/좋아요/댓글 수/설명을 수집하는 도구입니다.

## Requirements
- Python 3
- `pip install google-api-python-client`
- YouTube API key in `_agents/youtube/tools/youtube_account.json`

## Config
Edit `youtube_search.json`.

- `TARGET_KEYWORDS`: search keywords
- `MAX_RESULTS`: videos per keyword
- `PUBLISHED_DAYS`: search window
- `ORDER`: `relevance`, `viewCount`, or `date`

## Run

```bash
python youtube_search.py
```

Output is printed and saved as `youtube_search_report.md`.
