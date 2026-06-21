from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from saju_matrix_analyzer import analyze_matrix, load_config


DEFAULT_FEEDBACK_DIR = Path(r"C:\Users\coldp\Documents\ConnectAI\자료\사주_피드백")
EVENT_TYPES = {"work", "relationship", "body", "emotion", "housework", "money", "correction", "other"}
EMOTIONS = {"anger", "fatigue", "relief", "focus", "anxiety", "neutral", "stress", "sadness", "joy"}


def ensure_feedback_dirs(feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR) -> Path:
    base = Path(feedback_dir)
    (base / "daily").mkdir(parents=True, exist_ok=True)
    return base


def daily_markdown_path(date: str, feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR) -> Path:
    return ensure_feedback_dirs(feedback_dir) / "daily" / f"{date}.md"


def events_jsonl_path(feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR) -> Path:
    return ensure_feedback_dirs(feedback_dir) / "events.jsonl"


def correlations_jsonl_path(feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR) -> Path:
    return ensure_feedback_dirs(feedback_dir) / "correlations.jsonl"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalize_event_type(value: str | None) -> str:
    normalized = (value or "other").strip().lower()
    return normalized if normalized in EVENT_TYPES else "other"


def normalize_emotion(value: str | None) -> str:
    normalized = (value or "neutral").strip().lower()
    return normalized if normalized in EMOTIONS else "neutral"


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items = []
    with path.open("r", encoding="utf-8-sig") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                items.append(json.loads(stripped))
    return items


def find_hour_slot(matrix_result: dict[str, Any], time_text: str | None = None, hour_pillar: str | None = None) -> dict[str, Any]:
    hours = matrix_result["daily_luck"]["calculated"]["hour_pillars"]
    if hour_pillar:
        for slot in hours:
            if slot["pillar"] == hour_pillar:
                return slot
        raise ValueError(f"hour_pillar not found for date: {hour_pillar}")

    if not time_text:
        raise ValueError("time_text or hour_pillar is required to match an hour luck slot")

    parsed_time = datetime.strptime(time_text.strip(), "%H:%M").time()
    parsed_minutes = parsed_time.hour * 60 + parsed_time.minute
    for slot in hours:
        start_time = datetime.fromisoformat(slot["start"]).time()
        end_time = datetime.fromisoformat(slot["end"]).time()
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        if start_minutes <= end_minutes:
            if start_minutes <= parsed_minutes < end_minutes:
                return slot
        else:
            if parsed_minutes >= start_minutes or parsed_minutes < end_minutes:
                return slot
    raise ValueError(f"time_text did not match an hour luck slot: {time_text}")


def compact_interactions(interactions: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    def compact(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "kind": item["kind"],
                "name": item["name"],
                "layers": item["layers"],
                "pillars": item["pillars"],
                "branches": item.get("branches", []),
                "vector": item.get("vector"),
            }
            for item in items
        ]

    return {
        "stem_relations": compact(interactions.get("stem_relations", [])),
        "branch_pair_relations": compact(interactions.get("branch_pair_relations", [])),
        "branch_triple_relations": compact(interactions.get("branch_triple_relations", [])),
    }


def build_linked_matrix(matrix_result: dict[str, Any], hour_slot: dict[str, Any]) -> dict[str, Any]:
    hour_matrices = matrix_result["matrix"].get("hour_matrices", [])
    hour_matrix = next((item for item in hour_matrices if item["hour_pillar"] == hour_slot["pillar"]), None)
    if hour_matrix is None:
        selected = analyze_matrix(
            _config_from_daily_result(matrix_result),
            matrix_result["daily_luck"]["target_date"],
            hour_slot["pillar"],
        )
        matrix = selected["matrix"]
        interactions = matrix["interactions"]
        twelve_stage = next(
            item for item in matrix["twelve_stages"] if item["layer"] == "hour_luck"
        )
        twelve_spirit = next(
            item for item in matrix["twelve_spirits"] if item["layer"] == "hour_luck"
        )
        vector_summary = matrix["vector_summary"]
    else:
        interactions = hour_matrix["interactions"]
        twelve_stage = hour_matrix["twelve_stage"]
        twelve_spirit = hour_matrix["twelve_spirit"]
        vector_summary = matrix_result["matrix"]["vector_summary"]

    return {
        "date": matrix_result["daily_luck"]["target_date"],
        "day_pillar": matrix_result["daily_luck"]["calculated"]["day_pillar"],
        "hour_pillar": hour_slot["pillar"],
        "hour_range": hour_slot["range_label"],
        "hour_sipsung": {
            "stem": hour_slot["analysis"]["stem"]["primary_sipsung"],
            "branch": hour_slot["analysis"]["branch"]["primary_sipsung"],
        },
        "interactions": compact_interactions(interactions),
        "twelve_stage": twelve_stage,
        "twelve_spirit": twelve_spirit,
        "vector_summary": vector_summary,
    }


def _config_from_daily_result(matrix_result: dict[str, Any]) -> dict[str, Any]:
    daily = matrix_result["daily_luck"]
    return {
        "profile_name": daily.get("profile_name", ""),
        "timezone": daily.get("timezone", "Asia/Seoul"),
        "polarity_mode": daily["rule_profile"].get("polarity_mode", "cheyong"),
        "branch_mode": daily["rule_profile"].get("branch_mode", "hidden_all"),
        "hour_boundary": daily["rule_profile"].get("hour_boundary", "23:30"),
        "day_pillar_anchor": daily["rule_profile"].get("day_pillar_anchor", {}),
        "natal": daily["fixed_layers"]["natal"],
        "luck": daily["fixed_layers"]["luck"],
    }


def create_daily_markdown(matrix_result: dict[str, Any], feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR) -> Path:
    date = matrix_result["daily_luck"]["target_date"]
    path = daily_markdown_path(date, feedback_dir)
    if path.exists():
        return path

    daily = matrix_result["daily_luck"]
    lines = [
        f"# 사주 피드백 로그 - {date}",
        "",
        "## 오늘의 일진/시운 요약",
        "",
        f"- 일간: {daily['day_master']}",
        f"- 일운: {daily['calculated']['day_pillar']}",
        f"- 원국: {daily['fixed_layers']['natal']}",
        f"- 운: {daily['fixed_layers']['luck']}",
        "",
        "## 시간대별 예측 핵심",
        "",
    ]
    for slot in daily["calculated"]["hour_pillars"]:
        stem_sipsung = slot["analysis"]["stem"]["primary_sipsung"]
        branch_sipsung = slot["analysis"]["branch"]["primary_sipsung"]
        lines.append(f"- {slot['range_label']} [{slot['pillar']}]: {stem_sipsung} / {branch_sipsung}")

    lines.extend(
        [
            "",
            "## 실제 사건 로그",
            "",
            "_아직 기록된 실제 사건이 없습니다._",
            "",
            "## 예측과 실제의 연결",
            "",
            "_피드백이 추가되면 여기에 연관 분석이 누적됩니다._",
            "",
            "## 정정된 해석",
            "",
            "_정정 피드백이 있으면 여기에 따로 기록합니다._",
            "",
            "## 다음 분석에 반영할 패턴",
            "",
            "_계산 구조와 실제 사건의 연결 방식이 확인되면 여기에 요약합니다._",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def append_event_to_markdown(path: Path, event: dict[str, Any], correlation: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    if "_아직 기록된 실제 사건이 없습니다._" in text:
        text = text.replace("_아직 기록된 실제 사건이 없습니다._\n", "")
    if "_피드백이 추가되면 여기에 연관 분석이 누적됩니다._" in text:
        text = text.replace("_피드백이 추가되면 여기에 연관 분석이 누적됩니다._\n", "")
    if event["event_type"] == "correction" and "_정정 피드백이 있으면 여기에 따로 기록합니다._" in text:
        text = text.replace("_정정 피드백이 있으면 여기에 따로 기록합니다._\n", "")

    event_block = (
        f"- {event['time_text'] or '시간 미상'} [{event['hour_pillar']} / {event['hour_range']}] "
        f"{event['event_text']} "
        f"(type={event['event_type']}, emotion={event['emotion']})\n"
    )
    link_block = (
        f"- event_id={event['event_id']}: {correlation['summary']}\n"
    )
    text = text.replace("## 예측과 실제의 연결\n\n", f"## 예측과 실제의 연결\n\n{link_block}", 1)
    text = text.replace("## 실제 사건 로그\n\n", f"## 실제 사건 로그\n\n{event_block}", 1)
    if event["event_type"] == "correction":
        correction = f"- {event['time_text'] or '시간 미상'}: {event['event_text']}\n"
        text = text.replace("## 정정된 해석\n\n", f"## 정정된 해석\n\n{correction}", 1)
    path.write_text(text, encoding="utf-8")


def initialize_daily_log(
    config_path: str | Path,
    date: str,
    feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR,
) -> dict[str, Any]:
    matrix = analyze_matrix(load_config(str(config_path)), date)
    path = create_daily_markdown(matrix, feedback_dir)
    return {"status": "success", "date": date, "daily_markdown": str(path), "matrix": matrix}


def store_event(
    config_path: str | Path,
    date: str,
    event_text: str,
    time_text: str | None = None,
    hour_pillar: str | None = None,
    event_type: str | None = None,
    emotion: str | None = None,
    agent_note: str | None = None,
    feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR,
) -> dict[str, Any]:
    matrix = analyze_matrix(load_config(str(config_path)), date)
    daily_path = create_daily_markdown(matrix, feedback_dir)
    hour_slot = find_hour_slot(matrix, time_text=time_text, hour_pillar=hour_pillar)
    linked_matrix = build_linked_matrix(matrix, hour_slot)

    event = {
        "event_id": str(uuid4()),
        "created_at": now_iso(),
        "date": date,
        "time_text": time_text,
        "hour_pillar": hour_slot["pillar"],
        "hour_range": hour_slot["range_label"],
        "event_text": event_text,
        "event_type": normalize_event_type(event_type),
        "emotion": normalize_emotion(emotion),
        "linked_matrix": linked_matrix,
        "agent_note": agent_note or "",
    }

    from saju_feedback_analyzer import analyze_event_correlation

    correlation = analyze_event_correlation(event)
    append_jsonl(events_jsonl_path(feedback_dir), event)
    append_jsonl(correlations_jsonl_path(feedback_dir), correlation)
    append_event_to_markdown(daily_path, event, correlation)
    return {
        "status": "success",
        "event": event,
        "correlation": correlation,
        "daily_markdown": str(daily_path),
    }
