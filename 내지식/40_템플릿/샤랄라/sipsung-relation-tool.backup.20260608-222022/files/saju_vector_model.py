from __future__ import annotations

import math
from typing import Any

from saju_sipsung_rules import SipsungCalculator


BRANCH_ANGLES = {
    "卯": 0,
    "寅": 30,
    "丑": 60,
    "子": 90,
    "亥": 120,
    "戌": 150,
    "酉": 180,
    "申": 210,
    "未": 240,
    "午": 270,
    "巳": 300,
    "辰": 330,
}

ANGLE_BRANCHES = {angle: branch for branch, angle in BRANCH_ANGLES.items()}
SORTED_ANGLES = sorted(ANGLE_BRANCHES)

ELEMENT_ACTIONS = {
    "목": ["기획 확장", "아이디어 발아", "관계 열기", "새 방향 설정"],
    "화": ["표현", "발표", "가시화", "짧고 분명한 실행"],
    "토": ["정리", "마감", "압축", "경계 설정", "구조화"],
    "금": ["절단", "판단", "삭제", "디버깅", "정밀화"],
    "수": ["기록", "언어화", "데이터화", "코딩", "흐름 분석"],
}


def validate_branch(branch: str, field_name: str = "branch") -> str:
    normalized = branch.strip()
    if normalized not in BRANCH_ANGLES:
        supported = ", ".join(BRANCH_ANGLES)
        raise ValueError(f"{field_name} must be one of earthly branches: {supported}")
    return normalized


def angle_delta(angle_a: float, angle_b: float) -> float:
    diff = abs(angle_a - angle_b) % 360
    return min(diff, 360 - diff)


def circular_mean(angle_a: float, angle_b: float) -> float:
    x = math.cos(math.radians(angle_a)) + math.cos(math.radians(angle_b))
    y = math.sin(math.radians(angle_a)) + math.sin(math.radians(angle_b))
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        raise ValueError("Circular mean is undefined for exactly opposite angles")
    return normalize_angle(math.degrees(math.atan2(y, x)))


def normalize_angle(angle: float) -> float:
    normalized = round(angle % 360, 10)
    if normalized == 360:
        return 0.0
    if normalized.is_integer():
        return float(int(normalized))
    return normalized


def equal_force_resultant(delta_degrees: float, force: float = 1.0) -> float:
    radians = math.radians(delta_degrees)
    value = math.sqrt(force * force + force * force + 2 * force * force * math.cos(radians))
    return 0.0 if abs(value) < 1e-12 else value


def branch_angle(branch: str) -> int:
    return BRANCH_ANGLES[validate_branch(branch)]


def angle_element(angle: float) -> dict[str, Any]:
    normalized = normalize_angle(angle)
    if normalized in ANGLE_BRANCHES:
        branch = ANGLE_BRANCHES[int(normalized)]
        info = SipsungCalculator.get_info(branch)
        return {
            "angle": normalized,
            "element": info.element,
            "basis": "exact_branch",
            "branches": [branch],
            "label": info.label,
        }

    lower = max((item for item in SORTED_ANGLES if item < normalized), default=SORTED_ANGLES[-1])
    upper_candidates = [item for item in SORTED_ANGLES if item > normalized]
    upper = upper_candidates[0] if upper_candidates else SORTED_ANGLES[0]
    lower_branch = ANGLE_BRANCHES[lower]
    upper_branch = ANGLE_BRANCHES[upper]
    lower_element = SipsungCalculator.get_info(lower_branch).element
    upper_element = SipsungCalculator.get_info(upper_branch).element
    element = lower_element if lower_element == upper_element else f"{lower_element}/{upper_element}"
    return {
        "angle": normalized,
        "element": element,
        "basis": "between_branches",
        "branches": [lower_branch, upper_branch],
        "label": f"{lower_branch}-{upper_branch} 사이",
    }


def action_recommendations(element: str) -> list[str]:
    if "/" in element:
        actions: list[str] = []
        for part in element.split("/"):
            actions.extend(ELEMENT_ACTIONS.get(part, []))
        return actions
    return ELEMENT_ACTIONS.get(element, [])


def nearest_branch_angle(angle: float) -> dict[str, Any]:
    normalized = normalize_angle(angle)
    distances = [
        (angle_delta(normalized, branch_angle_value), branch, branch_angle_value)
        for branch, branch_angle_value in BRANCH_ANGLES.items()
    ]
    distance, branch, branch_angle_value = min(distances, key=lambda item: item[0])
    info = SipsungCalculator.get_info(branch)
    return {
        "branch": branch,
        "angle": branch_angle_value,
        "distance": distance,
        "element": info.element,
        "label": info.label,
    }


def summarize_branch_vectors(branch_counts: dict[str, int] | list[str], force: float = 1.0) -> dict[str, Any]:
    if isinstance(branch_counts, list):
        counts: dict[str, int] = {}
        for branch in branch_counts:
            normalized = validate_branch(branch)
            counts[normalized] = counts.get(normalized, 0) + 1
    else:
        counts = {validate_branch(branch): int(count) for branch, count in branch_counts.items() if int(count) > 0}

    if not counts:
        raise ValueError("branch_counts must include at least one earthly branch")

    components = []
    x_total = 0.0
    y_total = 0.0
    total_force = 0.0
    for branch, count in sorted(counts.items(), key=lambda item: BRANCH_ANGLES[item[0]]):
        angle = BRANCH_ANGLES[branch]
        magnitude = count * force
        x = magnitude * math.cos(math.radians(angle))
        y = magnitude * math.sin(math.radians(angle))
        x_total += x
        y_total += y
        total_force += magnitude
        info = SipsungCalculator.get_info(branch)
        components.append(
            {
                "branch": branch,
                "count": count,
                "angle": angle,
                "element": info.element,
                "magnitude": magnitude,
                "x": round(x, 10),
                "y": round(y, 10),
            }
        )

    resultant_magnitude = math.hypot(x_total, y_total)
    if resultant_magnitude < 1e-12:
        resultant_angle = None
        element_info = None
        nearest = None
        actions = ["기존 흐름 멈춤", "판 다시 잡기", "작은 새 행동 선택"]
        meaning = "전체 지지 벡터가 거의 상쇄되어 리셋 압력이 큽니다."
    else:
        resultant_angle = normalize_angle(math.degrees(math.atan2(y_total, x_total)))
        element_info = angle_element(resultant_angle)
        nearest = nearest_branch_angle(resultant_angle)
        actions = action_recommendations(element_info["element"])
        meaning = "중복 지지의 총합이 만드는 우세 방향입니다."

    return {
        "branch_counts": counts,
        "components": components,
        "x_total": round(x_total, 10),
        "y_total": round(y_total, 10),
        "total_input_magnitude": total_force,
        "resultant_magnitude": round(resultant_magnitude, 10),
        "resultant_angle": resultant_angle,
        "resultant_element": element_info,
        "nearest_branch": nearest,
        "recommended_actions": actions,
        "meaning": meaning,
        "guardrails": [
            "This is a weighted vector summary of repeated branches, not a classical proof.",
            "Use it to derive action direction after classical relations are scanned.",
            "Do not replace interaction tables with vector summary; use both together.",
        ],
    }


def classify_vector_relation(branch_a: str, branch_b: str, force: float = 1.0) -> dict[str, Any]:
    left = validate_branch(branch_a, "branch_a")
    right = validate_branch(branch_b, "branch_b")
    angle_a = BRANCH_ANGLES[left]
    angle_b = BRANCH_ANGLES[right]
    delta = angle_delta(angle_a, angle_b)
    resultant = equal_force_resultant(delta, force)

    result: dict[str, Any] = {
        "branches": [left, right],
        "angles": [angle_a, angle_b],
        "delta": delta,
        "resultant_magnitude": resultant,
        "guardrails": [
            "Do not present this as physical proof.",
            "Use it as a symbolic and computational direction model.",
            "Do not say a clash creates a perfect vacuum or guarantees an outcome.",
        ],
    }

    if delta == 180:
        result.update(
            {
                "vector_relation": "reset_clash",
                "relation_label": "충",
                "resultant_expression": "0",
                "meaning": "기존 방향성 상쇄 / 리셋",
                "action_rule": "비워진 방향성에 새 행동 벡터를 작게 주입합니다.",
                "resultant_angle": None,
                "resultant_element": None,
                "recommended_actions": ["기존 흐름 멈춤", "판 다시 잡기", "작은 새 행동 선택"],
            }
        )
    elif delta == 90:
        mean_angle = circular_mean(angle_a, angle_b)
        element_info = angle_element(mean_angle)
        result.update(
            {
                "vector_relation": "tuning_pressure",
                "relation_label": "형_pressure",
                "resultant_expression": "sqrt(2)F",
                "meaning": "구조적 마찰 / 튜닝 압력",
                "action_rule": "평균 방향의 오행 기능으로 압력을 전환합니다.",
                "resultant_angle": mean_angle,
                "resultant_element": element_info,
                "recommended_actions": action_recommendations(element_info["element"]),
            }
        )
    elif delta == 0:
        element_info = angle_element(angle_a)
        result.update(
            {
                "vector_relation": "amplification",
                "relation_label": "동방향",
                "resultant_expression": "2F",
                "meaning": "동일 방향 증폭 / 과잉 가능성",
                "action_rule": "증폭된 오행을 과열시키지 말고 사용량을 조절합니다.",
                "resultant_angle": angle_a,
                "resultant_element": element_info,
                "recommended_actions": action_recommendations(element_info["element"]),
            }
        )
    elif delta == 60:
        mean_angle = circular_mean(angle_a, angle_b)
        element_info = angle_element(mean_angle)
        result.update(
            {
                "vector_relation": "cooperative_flow",
                "relation_label": "60도 협력",
                "resultant_expression": "sqrt(3)F",
                "meaning": "부드러운 강화 / 연결 가능성",
                "action_rule": "흐름을 막지 말고 작은 실행으로 연결합니다.",
                "resultant_angle": mean_angle,
                "resultant_element": element_info,
                "recommended_actions": action_recommendations(element_info["element"]),
            }
        )
    elif delta == 120:
        mean_angle = circular_mean(angle_a, angle_b)
        element_info = angle_element(mean_angle)
        result.update(
            {
                "vector_relation": "balanced_tension",
                "relation_label": "120도 긴장 균형",
                "resultant_expression": "F",
                "meaning": "방향 차이를 가진 유지 / 긴장 속 균형",
                "action_rule": "둘 중 한 방향을 억누르지 말고 중간 기능으로 조율합니다.",
                "resultant_angle": mean_angle,
                "resultant_element": element_info,
                "recommended_actions": action_recommendations(element_info["element"]),
            }
        )
    else:
        mean_angle = circular_mean(angle_a, angle_b)
        element_info = angle_element(mean_angle)
        result.update(
            {
                "vector_relation": "other_angle",
                "relation_label": "기타 각도",
                "resultant_expression": "computed",
                "meaning": "충·형 핵심 압력은 아니지만 방향성 차이가 있습니다.",
                "action_rule": "다른 명리 관계와 함께 보조 정보로만 사용합니다.",
                "resultant_angle": mean_angle,
                "resultant_element": element_info,
                "recommended_actions": action_recommendations(element_info["element"]),
            }
        )

    return result


def enrich_branch_pair_relation(relation: dict[str, Any]) -> dict[str, Any]:
    branches = relation.get("branches", [])
    if len(branches) != 2:
        return relation
    return {**relation, "vector": classify_vector_relation(branches[0], branches[1])}
