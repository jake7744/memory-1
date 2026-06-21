from __future__ import annotations

from typing import Any


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

    if event["event_type"] == "correction":
        summary = "정정 피드백입니다. 물리 사건 시점과 감정 재활성화 시점을 분리해 이후 분석에 반영합니다."
    else:
        summary = " / ".join(highlights)

    return {
        "correlation_id": event["event_id"],
        "created_at": event["created_at"],
        "date": event["date"],
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
    for item in correlations:
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
        "connection_reviews": connection_reviews,
        "correction_reviews": correction_reviews,
        "report_instruction": (
            "Explain how each calculated structure manifested as an actual event, correction, "
            "delayed reaction, or practical workaround."
        ),
    }
