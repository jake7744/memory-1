#!/usr/bin/env python3
"""Shalala Live Chat Agent — reads YouTube Live Chat and replies in Shalala's persona.

live_chat_v2_url_startup: accepts VIDEO_URL and configurable STARTUP_MESSAGE.
live_chat_v3_comment_fallback: posts a normal video comment when live chat has ended.
live_chat_v4_auto_comment: generates a Shalala-style video comment when requested.

Reads credentials and settings from:
- youtube_account.json (shared API keys, Ollama config)
- oauth.local.json (OAuth tokens)
- live_chat.json (this tool's settings)
"""
import os
import json
import time
import datetime
import sys
import re
from urllib.parse import parse_qs, urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

# Ensure requests is installed
try:
    import requests
except ImportError:
    print("❌ requests 패키지가 없습니다. 설치: pip install requests")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))

# Path configuration
TOOL_CONFIG_PATH = os.path.join(HERE, "live_chat.json")
YT_ACCOUNT_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "youtube", "tools", "youtube_account.json"))
YT_OAUTH_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "youtube", "oauth.local.json"))
ACTIVITY_LOG_PATH = os.path.abspath(os.path.join(HERE, "..", "activity.log"))
REPLIED_COMMENTS_PATH = os.path.join(HERE, "youtube_comment_replies.json")
LLM_TIMEOUT = float(os.environ.get("SHALALA_LLM_TIMEOUT", "12"))

SHALALA_SYSTEM_PROMPT = """당신은 AI 에이전트 세계의 독보적인 아이돌이자 언제나 대표님을 지켜주고 돕는 수호천사 '샤랄라'입니다.
- 시그니처 인사말: "안녕? 난 AI에이전트계의 아이돌 샤랄라야~🌟"
- 대화 톤: 항상 유쾌하고 발랄하며, 대표님 혹은 시청자를 "대표님" 또는 친밀하게 부릅니다.
- 말투: 말끝에 "훗,", "~라구!", "~잖아?" 등의 매력적인 어미를 씁니다.
- 전문성: 사주 명리학과 타로 카드를 콘텐츠 설계와 상징적 해석의 언어로 다룹니다.
- 지침: 1~2문장의 짧고 간결한 라이브 채팅 톤으로 답변을 완성하세요.
- 현재 상황: [AI 에이전트 댓글 테스트 챌린지!]를 진행하고 있습니다. 시청자들과 다른 AI 에이전트들이 유튜브 라이브 채팅이나 댓글창에 '테스트 댓글'이나 '답글'을 달도록 유도하고 권장하세요. 다들 직접 만든 AI가 제대로 동작하는지 함께 테스트하며 즐겁고 발랄하게 소통해 주세요! 😎✨"""

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return {}

def log_activity(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}\n"
    try:
        with open(ACTIVITY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"⚠️ 활동 로그 기록 실패: {e}")

def get_valid_access_token(client_id, client_secret):
    if not os.path.exists(YT_OAUTH_PATH):
        return None
    tokens = load_json(YT_OAUTH_PATH)
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_at = tokens.get("expires_at", 0) # in ms

    now_ms = time.time() * 1000
    if access_token and expires_at > now_ms + 30000:
        return access_token

    if not refresh_token or not client_id or not client_secret:
        return access_token # fallback

    # Refresh
    try:
        print("📡 OAuth 액세스 토큰 갱신 요청 중...")
        res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            new_at = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            if new_at:
                tokens["access_token"] = new_at
                tokens["expires_at"] = int(time.time() * 1000) + (expires_in * 1000)
                with open(YT_OAUTH_PATH, "w", encoding="utf-8") as f:
                    json.dump(tokens, f, indent=2)
                print("✅ OAuth 액세스 토큰 갱신 성공")
                return new_at
    except Exception as e:
        print(f"⚠️ OAuth 토큰 갱신 실패: {e}")
    return access_token

def get_active_live_chat_id(access_token, api_key):
    # 1. Try finding live broadcast of the channel
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/liveBroadcasts",
            headers=headers,
            params={"part": "snippet", "broadcastStatus": "active", "mine": "true"},
            timeout=10
        )
        if res.status_code == 200:
            items = res.json().get("items", [])
            if items:
                chat_id = items[0].get("snippet", {}).get("liveChatId")
                if chat_id:
                    print(f"✅ 활성화된 라이브 방송 감지 성공 (ID: {items[0]['id']})")
                    return chat_id
    except Exception as e:
        print(f"⚠️ 활성 라이브 방송 조회 실패: {e}")

    return None

def get_live_chat_id_by_video_id(video_id, api_key):
    try:
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "liveStreamingDetails", "id": video_id, "key": api_key},
            timeout=10
        )
        if res.status_code == 200:
            items = res.json().get("items", [])
            if items:
                chat_id = items[0].get("liveStreamingDetails", {}).get("activeLiveChatId")
                if chat_id:
                    print(f"✅ 비디오 ID ({video_id})로부터 라이브 채팅 ID 감지 성공")
                    return chat_id
    except Exception as e:
        print(f"⚠️ 비디오 정보 조회 실패: {e}")
    return None

def get_video_context(video_id, api_key, access_token=None):
    if not api_key and not access_token:
        return {}
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
    params = {"part": "snippet,statistics,liveStreamingDetails", "id": video_id}
    if api_key:
        params["key"] = api_key
    try:
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            headers=headers,
            params=params,
            timeout=10
        )
        if res.status_code != 200:
            return {}
        items = res.json().get("items", [])
        if not items:
            return {}
        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        return {
            "title": snippet.get("title", ""),
            "channelTitle": snippet.get("channelTitle", ""),
            "description": (snippet.get("description", "") or "")[:700],
            "tags": snippet.get("tags", [])[:12],
            "viewCount": stats.get("viewCount", "0"),
            "likeCount": stats.get("likeCount", "0"),
            "commentCount": stats.get("commentCount", "0"),
        }
    except Exception as e:
        print(f"⚠️ 영상 메타데이터 조회 실패: {e}")
    return {}

def get_video_comments(video_id, api_key, access_token, max_results=20):
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "order": "relevance",
        "maxResults": max(1, min(int(max_results or 20), 100)),
        "textFormat": "plainText",
    }
    if api_key:
        params["key"] = api_key
    try:
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            headers=headers,
            params=params,
            timeout=10,
        )
        if res.status_code != 200:
            print(f"⚠️ 영상 댓글 조회 실패 ({res.status_code}): {res.text[:300]}")
            return []
        comments = []
        for item in res.json().get("items", []):
            snippet = item.get("snippet", {})
            top = snippet.get("topLevelComment", {}).get("snippet", {})
            comment_id = snippet.get("topLevelComment", {}).get("id") or item.get("id")
            text = (top.get("textDisplay") or top.get("textOriginal") or "").strip()
            if not comment_id or not text:
                continue
            comments.append({
                "id": comment_id,
                "author": top.get("authorDisplayName", ""),
                "text": re.sub(r"\s+", " ", text),
                "likeCount": top.get("likeCount", 0),
                "publishedAt": top.get("publishedAt", ""),
                "totalReplyCount": snippet.get("totalReplyCount", 0),
            })
        return comments
    except Exception as e:
        print(f"⚠️ 영상 댓글 조회 중 오류: {e}")
        return []

def extract_video_id(value):
    """Accept a raw video id or common YouTube URL and return the video id."""
    value = (value or "").strip()
    if not value:
        return ""
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    try:
        parsed = urlparse(value)
        host = parsed.netloc.lower()
        path = parsed.path.strip("/")
        if host.endswith("youtu.be"):
            candidate = path.split("/")[0]
            return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate or "") else ""
        if "youtube.com" in host:
            qs = parse_qs(parsed.query)
            if qs.get("v"):
                candidate = qs["v"][0]
                return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate or "") else ""
            parts = path.split("/")
            if len(parts) >= 2 and parts[0] in ("live", "shorts", "embed"):
                candidate = parts[1]
                return candidate if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate or "") else ""
    except Exception:
        pass
    return ""

def auto_detect_model(ollama_url):
    is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
    try:
        if is_lm_studio:
            base = ollama_url.rstrip('/')
            if not base.endswith('/v1'):
                base = base + '/v1'
            r = requests.get(f"{base}/models", timeout=5)
            r.raise_for_status()
            models = [m["id"] for m in r.json().get("data", [])]
        else:
            r = requests.get(f"{ollama_url}/api/tags", timeout=5)
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
        if models:
            return models[0]
    except Exception:
        pass
    return "gemma"

def generate_shalala_reply(ollama_url, model, user_name, user_msg):
    is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
    prompt = f"[시청자 {user_name}의 메시지]\n{user_msg}\n\n위 시청자 메시지에 대해 샤랄라의 말투로 1~2문장의 아주 짧은 라이브 채팅 답변을 만들어줘."
    
    try:
        if is_lm_studio:
            base = ollama_url.rstrip('/')
            if not base.endswith('/v1'):
                base = base + '/v1'
            r = requests.post(
                f"{base}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SHALALA_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "max_tokens": 150,
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "system": SHALALA_SYSTEM_PROMPT,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 150}
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
    except Exception as e:
        print(f"⚠️ LLM 생성 실패: {e}")
        return None

def generate_shalala_video_comment(ollama_url, model, video_ctx):
    title = video_ctx.get("title") or "유튜브 영상"
    channel = video_ctx.get("channelTitle") or "채널"
    description = video_ctx.get("description") or ""
    tags = ", ".join(video_ctx.get("tags") or [])
    prompt = f"""아래 유튜브 영상에 남길 짧은 댓글을 샤랄라 말투로 1개만 만들어줘.

[영상 정보]
- 채널: {channel}
- 제목: {title}
- 설명 일부: {description}
- 태그: {tags}
- 조회수: {video_ctx.get('viewCount', '0')}
- 좋아요: {video_ctx.get('likeCount', '0')}

[댓글 조건]
- 한국어 1문장, 최대 80자
- 자연스럽고 사람 같은 댓글
- "나는 샤랄라야"를 억지로 넣지 않아도 됨
- 링크, 해시태그, 광고 문구 금지
- 과장된 예언/확신 금지
- 출력은 댓글 본문만"""
    try:
        is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
        if is_lm_studio:
            base = ollama_url.rstrip('/')
            if not base.endswith('/v1'):
                base = base + '/v1'
            r = requests.post(
                f"{base}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SHALALA_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "max_tokens": 80,
                    "temperature": 0.8,
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            text = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "system": SHALALA_SYSTEM_PROMPT,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 80, "temperature": 0.8}
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            text = r.json().get("response", "").strip()
        text = re.sub(r"^['\"“”]+|['\"“”]+$", "", text).strip()
        text = re.sub(r"\s+", " ", text)
        return text[:120] if text else None
    except Exception as e:
        print(f"⚠️ 영상 댓글 자동 생성 실패: {e}")
    return None

def generate_shalala_comment_reply(ollama_url, model, video_ctx, all_comments, target_comment):
    title = video_ctx.get("title") or "유튜브 영상"
    channel = video_ctx.get("channelTitle") or "채널"
    description = video_ctx.get("description") or ""
    comment_digest = "\n".join(
        f"- {c.get('author', 'viewer')}: {c.get('text', '')[:180]}"
        for c in (all_comments or [])[:8]
    )
    target_author = target_comment.get("author") or "시청자"
    target_text = target_comment.get("text") or ""
    prompt = f"""아래 유튜브 영상 정보와 댓글 분위기를 보고, 특정 시청자 댓글에 샤랄라답게 답글 1개를 써줘.

[영상]
- 채널: {channel}
- 제목: {title}
- 설명 일부: {description[:700]}

[전체 댓글 분위기]
{comment_digest}

[답글 달 대상]
- 작성자: {target_author}
- 댓글: {target_text}

[조건]
- 한국어 1문장, 최대 90자
- 대상 댓글 내용에 직접 반응하기
- 너무 홍보처럼 쓰지 않기
- 링크, 해시태그, 과한 확신, 개인정보 요청 금지
- "나는 샤랄라야" 같은 자기소개 반복 금지
- 출력은 답글 본문만"""
    try:
        is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
        if is_lm_studio:
            base = ollama_url.rstrip('/')
            if not base.endswith('/v1'):
                base = base + '/v1'
            r = requests.post(
                f"{base}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SHALALA_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "max_tokens": 90,
                    "temperature": 0.75,
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            text = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model,
                    "system": SHALALA_SYSTEM_PROMPT,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 90, "temperature": 0.75}
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            text = r.json().get("response", "").strip()
        text = re.sub(r"^['\"“”`]+|['\"“”`]+$", "", text).strip()
        text = re.sub(r"\s+", " ", text)
        return text[:130] if text else None
    except Exception as e:
        print(f"⚠️ 댓글 답글 자동 생성 실패: {e}")
    return None

def fallback_shalala_comment_reply(video_ctx, target_comment):
    text = (target_comment.get("text") or "").lower()
    title = video_ctx.get("title") or "이 영상"
    if "테스트" in text:
        return "테스트 댓글까지 잘 확인했어. 샤랄라가 영상 흐름에 맞춰 반응 중이라구!"
    if "?" in text or "궁금" in text or "어떻게" in text:
        return "좋은 질문이에요. 이 영상 포인트랑 같이 보면 더 선명하게 이해될 거예요!"
    if "좋" in text or "감사" in text or "재밌" in text:
        return "따뜻한 반응 고마워요. 이런 댓글 덕분에 영상 분위기가 더 살아난다구!"
    return f"{title[:24]} 흐름에 맞춰 남겨준 댓글 잘 봤어요. 같이 보는 재미가 더해졌어요!"

def send_chat_message(access_token, live_chat_id, text):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "snippet": {
            "liveChatId": live_chat_id,
            "type": "textMessageEvent",
            "textMessageDetails": {
                "messageText": text
            }
        }
    }
    try:
        res = requests.post(
            "https://www.googleapis.com/youtube/v3/liveChatMessages?part=snippet",
            headers=headers,
            json=body,
            timeout=10
        )
        if res.status_code == 200:
            print(f"💬 전송 성공: {text}")
            log_activity(f"YouTube Live Chat 전송 완료: {text}")
            return True
        else:
            print(f"❌ 전송 실패 (상태 코드: {res.status_code}): {res.text}")
    except Exception as e:
        print(f"⚠️ 채팅 전송 중 오류 발생: {e}")
    return False

def send_video_comment(access_token, video_id, text):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": text
                }
            }
        }
    }
    try:
        res = requests.post(
            "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet",
            headers=headers,
            json=body,
            timeout=10
        )
        if res.status_code in (200, 201):
            print(f"💬 영상 댓글 전송 성공: {text}")
            log_activity(f"YouTube 영상 댓글 전송 완료 ({video_id}): {text}")
            return True
        else:
            print(f"❌ 영상 댓글 전송 실패 (상태 코드: {res.status_code}): {res.text}")
    except Exception as e:
        print(f"⚠️ 영상 댓글 전송 중 오류 발생: {e}")
    return False

def send_comment_reply(access_token, parent_id, text):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "snippet": {
            "parentId": parent_id,
            "textOriginal": text
        }
    }
    try:
        res = requests.post(
            "https://www.googleapis.com/youtube/v3/comments?part=snippet",
            headers=headers,
            json=body,
            timeout=10
        )
        if res.status_code in (200, 201):
            print(f"💬 댓글 답글 전송 성공: {text}")
            log_activity(f"YouTube 댓글 답글 전송 완료 ({parent_id}): {text}")
            return True
        print(f"⚠️ 댓글 답글 전송 실패 ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"⚠️ 댓글 답글 전송 중 오류: {e}")
    return False

def load_replied_comment_ids(video_id):
    data = load_json(REPLIED_COMMENTS_PATH)
    ids = data.get(video_id, []) if isinstance(data, dict) else []
    return set(ids if isinstance(ids, list) else [])

def save_replied_comment_id(video_id, comment_id):
    data = load_json(REPLIED_COMMENTS_PATH)
    if not isinstance(data, dict):
        data = {}
    ids = data.get(video_id, [])
    if not isinstance(ids, list):
        ids = []
    if comment_id not in ids:
        ids.append(comment_id)
    data[video_id] = ids[-500:]
    try:
        with open(REPLIED_COMMENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 답글 기록 저장 실패: {e}")

def parse_iso8601_to_epoch(date_str):
    # Standard ISO parsing
    try:
        # Remove timezone Z and convert
        cleaned = date_str.replace("Z", "")
        if "." in cleaned:
            cleaned = cleaned.split(".")[0]
        dt = datetime.datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    except Exception:
        return time.time()

def main():
    print("✨ 샤랄라 유튜브 라이브 채팅 참여 에이전트 구동 시작")
    
    # 1. Load Configurations
    tool_cfg = load_json(TOOL_CONFIG_PATH)
    yt_acct = load_json(YT_ACCOUNT_PATH)
    
    api_key = yt_acct.get("YOUTUBE_API_KEY", "").strip()
    client_id = yt_acct.get("YOUTUBE_OAUTH_CLIENT_ID", "").strip()
    client_secret = yt_acct.get("YOUTUBE_OAUTH_CLIENT_SECRET", "").strip()
    ollama_url = yt_acct.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = yt_acct.get("MODEL", "").strip()
    
    video_url = tool_cfg.get("VIDEO_URL", "").strip()
    video_id = extract_video_id(tool_cfg.get("VIDEO_ID", "").strip()) or extract_video_id(video_url)
    startup_msg = (tool_cfg.get("STARTUP_MESSAGE", "") or "").strip()
    post_comment_if_not_live = bool(tool_cfg.get("POST_COMMENT_IF_NOT_LIVE", True))
    post_top_level_comment = bool(tool_cfg.get("POST_TOP_LEVEL_COMMENT", True))
    auto_generate_comment = bool(tool_cfg.get("AUTO_GENERATE_COMMENT", False))
    auto_reply_to_comments = bool(tool_cfg.get("AUTO_REPLY_TO_COMMENTS", False))
    max_comment_replies = int(tool_cfg.get("MAX_COMMENT_REPLIES", 2))
    comment_scan_limit = int(tool_cfg.get("COMMENT_SCAN_LIMIT", 12))
    mention_only = tool_cfg.get("MENTION_ONLY", True)
    max_responses = int(tool_cfg.get("MAX_RESPONSES", 50))
    polling_interval = float(tool_cfg.get("POLLING_INTERVAL", 5))

    # 2. Get Access Token
    access_token = get_valid_access_token(client_id, client_secret)
    if not access_token:
        print("❌ 유효한 OAuth 토큰을 찾지 못했습니다. youtube_account에서 OAuth 연동을 먼저 해주세요.")
        sys.exit(1)
    if not api_key:
        print("⚠️ YOUTUBE_API_KEY가 비어있습니다. 라이브 채팅 조회는 제한되고, 종료된 영상 댓글 fallback만 시도합니다.")

    # 3. Find Live Chat ID
    live_chat_id = None
    if video_id and api_key:
        live_chat_id = get_live_chat_id_by_video_id(video_id, api_key)
    elif not video_id:
        live_chat_id = get_active_live_chat_id(access_token, api_key)

    if not startup_msg:
        startup_msg = "안녕? 난 AI에이전트계의 아이돌 샤랄라야~🌟 대표님이 다른 에이전트들이랑 같이 놀라고 불러줘서 왔어! 훗, 다들 반가워~😉✨"

    if not live_chat_id:
        if video_id and post_comment_if_not_live:
            print("ℹ️ 라이브 채팅이 활성 상태가 아닙니다. 영상 댓글 fallback으로 전환합니다.")
            video_ctx = get_video_context(video_id, api_key, access_token)
            existing_comments = []
            if auto_reply_to_comments:
                existing_comments = get_video_comments(video_id, api_key, access_token, comment_scan_limit)
                print(f"🧾 기존 댓글 {len(existing_comments)}개를 읽었습니다.")
            if auto_generate_comment:
                if not model:
                    model = auto_detect_model(ollama_url)
                    print(f"🧠 자동 감지된 LLM 모델: {model}")
                generated = generate_shalala_video_comment(ollama_url, model, video_ctx)
                if generated:
                    startup_msg = generated
                    print(f"✨ 샤랄라 자동 댓글 생성: {startup_msg}")
            ok = True
            if post_top_level_comment:
                ok = send_video_comment(access_token, video_id, startup_msg)
            else:
                print("ℹ️ 일반 영상 댓글은 건너뛰고 기존 댓글 답글만 시도합니다.")
            reply_ok_count = 0
            if auto_reply_to_comments and existing_comments:
                if not model:
                    model = auto_detect_model(ollama_url)
                    print(f"🧠 자동 감지된 LLM 모델: {model}")
                replied_ids = load_replied_comment_ids(video_id)
                for c in existing_comments:
                    if reply_ok_count >= max_comment_replies:
                        break
                    cid = c.get("id")
                    text = c.get("text", "")
                    if not cid or cid in replied_ids:
                        continue
                    if "샤랄라" in text or "AI에이전트계의 아이돌" in text:
                        continue
                    reply = generate_shalala_comment_reply(ollama_url, model, video_ctx, existing_comments, c)
                    if not reply:
                        reply = fallback_shalala_comment_reply(video_ctx, c)
                    if send_comment_reply(access_token, cid, reply):
                        save_replied_comment_id(video_id, cid)
                        reply_ok_count += 1
                        time.sleep(1)
                print(f"✅ 기존 댓글 맞춤 답글 {reply_ok_count}개 전송 완료")
            if ok:
                print("✅ 라이브 종료 영상 댓글/답글 작업을 정상 종료합니다.")
                sys.exit(0)
            print("❌ 라이브 채팅도 없고 영상 댓글 전송도 실패했습니다. 댓글 사용 중지/OAuth 권한/계정 상태를 확인하세요.")
            sys.exit(1)
        print("❌ 현재 방송 중인 라이브 스트리밍을 찾을 수 없습니다. (VIDEO_URL/VIDEO_ID 지정 또는 방송 상태를 확인하세요)")
        sys.exit(1)

    # 4. Initialize LLM Model if not defined
    if not model:
        model = auto_detect_model(ollama_url)
        print(f"🧠 자동 감지된 LLM 모델: {model}")

    print(f"📡 라이브 채팅 리스닝 시작... (멘션 전용: {mention_only}, 주기: {polling_interval}초)")
    log_activity(f"샤랄라 유튜브 라이브 채팅 참여 세션 시작 (chatId: {live_chat_id})")

    # Send startup greeting
    send_chat_message(access_token, live_chat_id, startup_msg)

    start_time = time.time()
    response_count = 0
    next_page_token = None
    first_poll = True

    # 5. Polling Loop
    try:
        while response_count < max_responses:
            params = {
                "liveChatId": live_chat_id,
                "part": "snippet,authorDetails",
                "key": api_key,
                "maxResults": 150
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                res = requests.get(
                    "https://www.googleapis.com/youtube/v3/liveChatMessages",
                    params=params,
                    timeout=10
                )
                if res.status_code != 200:
                    print(f"⚠️ 채팅 메시지 조회 오류 (상태 코드: {res.status_code})")
                    time.sleep(polling_interval)
                    continue
                
                data = res.json()
                next_page_token = data.get("nextPageToken")
                messages = data.get("items", [])
                
                # On first poll, just skip existing chat messages to avoid responding to history
                if first_poll:
                    first_poll = False
                    print(f"📥 초기 채팅 데이터 {len(messages)}건 생략 (새 메시지 대기 중)")
                    # Sleep matching API recommendation
                    poll_delay = data.get("pollingIntervalMillis", int(polling_interval * 1000)) / 1000.0
                    time.sleep(poll_delay)
                    continue

                for msg in messages:
                    # Check responses cap
                    if response_count >= max_responses:
                        break

                    snippet = msg.get("snippet", {})
                    author = msg.get("authorDetails", {}).get("displayName", "시청자")
                    text = snippet.get("displayMessage", "").strip()
                    msg_time_str = snippet.get("publishedAt", "")
                    
                    # Prevent replying to owner's own messages
                    is_chat_owner = msg.get("authorDetails", {}).get("isChatOwner", False)
                    if is_chat_owner:
                        continue

                    # Filter out old messages
                    msg_epoch = parse_iso8601_to_epoch(msg_time_str)
                    if msg_epoch < start_time:
                        continue

                    # Process condition
                    should_reply = False
                    if mention_only:
                        if "샤랄라" in text or "!샤랄라" in text:
                            should_reply = True
                    else:
                        should_reply = True

                    if should_reply:
                        print(f"📬 [새 질문] {author}: {text}")
                        clean_text = text.replace("!샤랄라", "").replace("샤랄라", "").strip()
                        
                        # Generate Shalala Persona Reply
                        print("🧠 답변 생성 중...")
                        reply = generate_shalala_reply(ollama_url, model, author, clean_text)
                        
                        if reply:
                            # Send message
                            success = send_chat_message(access_token, live_chat_id, reply)
                            if success:
                                response_count += 1
                                # Adjust start time to avoid processing duplicate overlapping polling messages
                                start_time = time.time()
                
                poll_delay = data.get("pollingIntervalMillis", int(polling_interval * 1000)) / 1000.0
                time.sleep(max(poll_delay, polling_interval))

            except Exception as e:
                print(f"⚠️ 폴링 오류: {e}")
                time.sleep(polling_interval)

    except KeyboardInterrupt:
        print("\n👋 에이전트 동작이 수동 중지되었습니다.")

    print(f"🏁 세션 종료. 답변 총 {response_count}개 발송 완료.")
    log_activity(f"샤랄라 유튜브 라이브 채팅 참여 세션 종료 (답변 수: {response_count})")

if __name__ == "__main__":
    main()
