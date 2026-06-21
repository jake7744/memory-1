from __future__ import annotations

from typing import Any, Literal

from saju_sipsung_rules import SipsungCalculator


SpiritBasis = Literal["year_branch", "day_branch"]

SPIRIT_ORDER = ("겁살", "재살", "천살", "지살", "연살", "월살", "망신살", "장성살", "반안살", "역마살", "육해살", "화개살")

GROUP_BY_BRANCH = {
    "申": "申子辰",
    "子": "申子辰",
    "辰": "申子辰",
    "寅": "寅午戌",
    "午": "寅午戌",
    "戌": "寅午戌",
    "巳": "巳酉丑",
    "酉": "巳酉丑",
    "丑": "巳酉丑",
    "亥": "亥卯未",
    "卯": "亥卯未",
    "未": "亥卯未",
}

TWELVE_SPIRIT_TABLE = {
    "申子辰": {
        "巳": "겁살",
        "午": "재살",
        "未": "천살",
        "申": "지살",
        "酉": "연살",
        "戌": "월살",
        "亥": "망신살",
        "子": "장성살",
        "丑": "반안살",
        "寅": "역마살",
        "卯": "육해살",
        "辰": "화개살",
    },
    "寅午戌": {
        "亥": "겁살",
        "子": "재살",
        "丑": "천살",
        "寅": "지살",
        "卯": "연살",
        "辰": "월살",
        "巳": "망신살",
        "午": "장성살",
        "未": "반안살",
        "申": "역마살",
        "酉": "육해살",
        "戌": "화개살",
    },
    "巳酉丑": {
        "寅": "겁살",
        "卯": "재살",
        "辰": "천살",
        "巳": "지살",
        "午": "연살",
        "未": "월살",
        "申": "망신살",
        "酉": "장성살",
        "戌": "반안살",
        "亥": "역마살",
        "子": "육해살",
        "丑": "화개살",
    },
    "亥卯未": {
        "申": "겁살",
        "酉": "재살",
        "戌": "천살",
        "亥": "지살",
        "子": "연살",
        "丑": "월살",
        "寅": "망신살",
        "卯": "장성살",
        "辰": "반안살",
        "巳": "역마살",
        "午": "육해살",
        "未": "화개살",
    },
}

SPIRIT_DESCRIPTIONS = {
    "겁살": "갑작스러운 절단, 손실, 강제 방향 전환",
    "재살": "압박, 통제, 사고 대응, 날카로운 긴장",
    "천살": "외부 환경의 큰 압력과 하늘 변수",
    "지살": "이동, 현장성, 바깥 활동",
    "연살": "도화, 주목, 매력, 감각적 노출",
    "월살": "정체, 어둠, 불명확성, 감정 침잠",
    "망신살": "노출, 체면 손상, 드러나는 사건",
    "장성살": "주도권, 중심성, 강한 추진",
    "반안살": "안정, 지위, 올라타는 발판",
    "역마살": "이동, 전환, 유통, 속도",
    "육해살": "미세한 방해, 직감, 숨은 문제 감지",
    "화개살": "저장, 몰입, 예술성, 고독한 정리",
}


def validate_branch(branch: str, field_name: str = "branch") -> str:
    normalized = branch.strip()
    if normalized not in SipsungCalculator.BRANCH_ELEMENTS:
        supported = ", ".join(SipsungCalculator.BRANCH_ELEMENTS)
        raise ValueError(f"{field_name} must be one of earthly branches: {supported}")
    return normalized


def analyze_twelve_spirit(base_branch: str, target_branch: str, basis: SpiritBasis = "year_branch") -> dict[str, Any]:
    base = validate_branch(base_branch, "base_branch")
    target = validate_branch(target_branch, "target_branch")
    group = GROUP_BY_BRANCH[base]
    spirit = TWELVE_SPIRIT_TABLE[group][target]
    return {
        "basis": basis,
        "base_branch": base,
        "target_branch": target,
        "trine_group": group,
        "twelve_spirit": spirit,
        "spirit_index": SPIRIT_ORDER.index(spirit) + 1,
        "description": SPIRIT_DESCRIPTIONS[spirit],
    }


def analyze_twelve_spirits_for_branches(
    base_branch: str,
    branches: list[str],
    basis: SpiritBasis = "year_branch",
) -> list[dict[str, Any]]:
    return [analyze_twelve_spirit(base_branch, branch, basis) for branch in branches]

