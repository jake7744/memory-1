from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from saju_feedback_analyzer import summarize_correlations
from saju_feedback_store import DEFAULT_FEEDBACK_DIR, correlations_jsonl_path, ensure_feedback_dirs, read_jsonl


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def week_bounds_for(value: str | date) -> tuple[date, date]:
    target = parse_date(value) if isinstance(value, str) else value
    start = target - timedelta(days=target.weekday())
    end = start + timedelta(days=6)
    return start, end


def weekly_report_path(week_start: date, feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR) -> Path:
    base = ensure_feedback_dirs(feedback_dir)
    reports_dir = base / "reports" / "weekly"
    reports_dir.mkdir(parents=True, exist_ok=True)
    iso = week_start.isocalendar()
    return reports_dir / f"{iso.year}-W{iso.week:02d}.md"


def filter_correlations_for_week(correlations: list[dict[str, Any]], week_start: date, week_end: date) -> list[dict[str, Any]]:
    selected = []
    for item in correlations:
        item_date = item.get("date")
        if not item_date:
            continue
        parsed = parse_date(item_date)
        if week_start <= parsed <= week_end:
            selected.append(item)
    return selected


def format_relation_names(names: list[str]) -> str:
    if not names:
        return "기록된 형충파해합 없음"
    return ", ".join(names)


def format_vector(item: dict[str, Any]) -> str:
    angle = item.get("vector_angle")
    element = item.get("vector_element")
    if angle is None:
        return "총 벡터 방향 없음"
    element_text = element.get("element", "") if isinstance(element, dict) else ""
    return f"{angle}° {element_text}".strip()


def render_weekly_report(correlations: list[dict[str, Any]], week_start: date, week_end: date) -> str:
    summary = summarize_correlations(correlations)
    lines = [
        f"# 주간 사주 피드백 연결 리포트 - {week_start.isoformat()} ~ {week_end.isoformat()}",
        "",
        "이 리포트는 계산된 운의 구조가 실제 사건, 정정, 지연 반응, 물상 대체와 어떻게 연결됐는지 보기 위한 기록입니다.",
        "",
        "## 이번 주 연결 기록",
        "",
    ]

    if not summary["connection_reviews"]:
        lines.append("_이번 주에 저장된 실제 사건 연결 기록이 없습니다._")
    else:
        for item in summary["connection_reviews"]:
            actions = ", ".join(item.get("recommended_actions", [])) or "기록된 우회 행동 없음"
            lines.extend(
                [
                    f"### {item['date']} {item.get('time_text') or '시간 미상'} [{item.get('hour_pillar')}]",
                    "",
                    f"- 사건 성격: {item.get('event_type')} / 감정: {item.get('emotion')}",
                    f"- 시운 십성: {item.get('hour_sipsung')}",
                    f"- 십이운성/십이신살: {item.get('twelve_stage')} / {item.get('twelve_spirit')}",
                    f"- 형충파해합 연결: {format_relation_names(item.get('relation_names', []))}",
                    f"- 벡터 방향: {format_vector(item)}",
                    f"- 우회 행동 후보: {actions}",
                    f"- 연결 해석: {item.get('connection_note', '')}",
                    "",
                ]
            )

    lines.extend(["## 정정과 지연 반응", ""])
    if not summary["correction_reviews"]:
        lines.append("_이번 주에 저장된 정정 피드백이 없습니다._")
    else:
        for item in summary["correction_reviews"]:
            lines.extend(
                [
                    f"- {item['date']} {item.get('time_text') or '시간 미상'} [{item.get('hour_pillar')}]: {item.get('connection_note', '')}",
                ]
            )

    lines.extend(
        [
            "",
            "## 다음 분석에 반영할 읽기 방식",
            "",
            "- 실제 사건 원문을 계산 결과에 억지로 맞추지 않습니다.",
            "- 물리 사건 시점과 감정 재활성화 시점을 분리해서 읽습니다.",
            "- 파해법은 실제로 행동으로 전환됐는지와 함께 기록합니다.",
            "- 같은 계산 구조라도 몸, 관계, 일, 집안일 중 어느 영역으로 발현됐는지 우선 확인합니다.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_weekly_report(
    week_of: str,
    feedback_dir: str | Path = DEFAULT_FEEDBACK_DIR,
) -> dict[str, Any]:
    week_start, week_end = week_bounds_for(week_of)
    rows = read_jsonl(correlations_jsonl_path(feedback_dir))
    selected = filter_correlations_for_week(rows, week_start, week_end)
    path = weekly_report_path(week_start, feedback_dir)
    path.write_text(render_weekly_report(selected, week_start, week_end), encoding="utf-8")
    return {
        "status": "success",
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "correlations_used": len(selected),
        "weekly_report": str(path),
    }
