from __future__ import annotations

from typing import Any


# 하루 전체 피드백 식별 태그. 프론트(app.js)에서 event_text 앞에 자동으로 붙인다.
DAY_SCOPE_TAG = "[하루 전체]"


def is_day_scope_event(event_text: str | None) -> bool:
    """event_text가 '하루 전체' 태그로 시작하면 시진과 무관한 일 단위 피드백으로 본다."""
    return bool(event_text) and event_text.strip().startswith(DAY_SCOPE_TAG)


def relation_names(linked_matrix: dict[str, Any]) -> list[str]:
    interactions = linked_matrix["interactions"]
    names = []
    for key in ("stem_relations", "branch_pair_relations", "branch_triple_relations"):
        names.extend(item["name"] for item in interactions.get(key, []))
    return names


def relation_kinds(linked_matrix: dict[str, Any]) -> list[str]:
    interactions = linked_matrix["interactions"]
    kinds = []
    for key in ("stem_relations", "branch_pair_relations", "branch_triple_relations"):
        for item in interactions.get(key, []):
            kind = item["kind"]
            if kind not in kinds:
                kinds.append(kind)
    return kinds


def selected_vector_actions(linked_matrix: dict[str, Any]) -> list[str]:
    summary = linked_matrix.get("vector_summary", {})
    return list(summary.get("recommended_actions", []))[:6]


def analyze_event_correlation(event: dict[str, Any]) -> dict[str, Any]:
    linked = event["linked_matrix"]
    names = relation_names(linked)
    kinds = relation_kinds(linked)
    hour_sipsung = linked["hour_sipsung"]
    stage = linked["twelve_stage"]["twelve_stage"]
    spirit = linked["twelve_spirit"]["twelve_spirit"]
    vector = linked.get("vector_summary", {})
    actions = selected_vector_actions(linked)

    highlights = []
    if names:
        highlights.append(f"형충파해합/신살 반응: {', '.join(names[:8])}")
    highlights.append(f"시운 십성: 천간 {hour_sipsung['stem']} / 지지 {hour_sipsung['branch']}")
    highlights.append(f"십이운성/십이신살: {stage} / {spirit}")
    if vector.get("resultant_angle") is not None:
        highlights.append(f"총 벡터 방향: {vector['resultant_angle']}° {vector.get('resultant_element', {}).get('element', '')}")
    if actions:
        highlights.append(f"우회 행동: {', '.join(actions)}")

    day_scope = is_day_scope_event(event.get("event_text"))

    if event["event_type"] == "correction":
        summary = "정정 피드백입니다. 물리 사건 시점과 감정 재활성화 시점을 분리해 이후 분석에 반영합니다."
    elif day_scope:
        summary = "하루 전체 피드백입니다. 특정 시진과 연결하지 않고 그날(일진) 단위로만 기록합니다."
    else:
        summary = " / ".join(highlights)

    return {
        "correlation_id": event["event_id"],
        "created_at": event["created_at"],
        "date": event["date"],
        "day_pillar": linked.get("day_pillar"),
        "day_scope": day_scope,
        "time_text": event["time_text"],
        "hour_pillar": event["hour_pillar"],
        "event_type": event["event_type"],
        "emotion": event["emotion"],
        "relation_kinds": kinds,
        "relation_names": names,
        "hour_sipsung": hour_sipsung,
        "twelve_stage": stage,
        "twelve_spirit": spirit,
        "vector_angle": vector.get("resultant_angle"),
        "vector_element": vector.get("resultant_element"),
        "recommended_actions": actions,
        "summary": summary,
    }


def summarize_correlations(correlations: list[dict[str, Any]]) -> dict[str, Any]:
    connection_reviews = []
    correction_reviews = []
    day_scope_reviews = []
    for item in correlations:
        # 하루 전체 피드백은 임의의 시진에 묶여 저장되므로, 시진 단위 통계
        # (connection_reviews / correction_reviews)에서 제외하고 일(日) 단위로만 모은다.
        if item.get("day_scope"):
            day_scope_reviews.append(
                {
                    "date": item.get("date"),
                    "day_pillar": item.get("day_pillar"),
                    "event_type": item.get("event_type"),
                    "emotion": item.get("emotion"),
                    "relation_names": item.get("relation_names", []),
                    "day_note": item.get("summary", ""),
                }
            )
            continue

        review = {
            "date": item.get("date"),
            "time_text": item.get("time_text"),
            "hour_pillar": item.get("hour_pillar"),
            "event_type": item.get("event_type"),
            "emotion": item.get("emotion"),
            "hour_sipsung": item.get("hour_sipsung"),
            "twelve_stage": item.get("twelve_stage"),
            "twelve_spirit": item.get("twelve_spirit"),
            "relation_names": item.get("relation_names", []),
            "vector_angle": item.get("vector_angle"),
            "vector_element": item.get("vector_element"),
            "recommended_actions": item.get("recommended_actions", []),
            "connection_note": item.get("summary", ""),
        }
        if item.get("event_type") == "correction":
            correction_reviews.append(review)
        else:
            connection_reviews.append(review)

    return {
        "total_events_reviewed": len(correlations),
        "hour_linked_events": len(connection_reviews) + len(correction_reviews),
        "connection_reviews": connection_reviews,
        "correction_reviews": correction_reviews,
        "day_scope_reviews": day_scope_reviews,
        "report_instruction": (
            "Do not rank by frequency. Explain how each calculated structure manifested "
            "as an actual event, correction, delayed reaction, or practical workaround. "
            "day_scope_reviews are whole-day notes not tied to any hour pillar; analyze them "
            "only at the daily (day pillar) level and exclude them from hour-pillar (시진) statistics."
        ),
    }
