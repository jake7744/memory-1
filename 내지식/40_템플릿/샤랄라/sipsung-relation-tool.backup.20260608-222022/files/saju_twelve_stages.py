from __future__ import annotations

from typing import Any

from saju_sipsung_rules import SipsungCalculator


STAGE_ORDER = ("장생", "목욕", "관대", "건록", "제왕", "쇠", "병", "사", "묘", "절", "태", "양")

STAGE_DESCRIPTIONS = {
    "장생": "새 기운이 태어나고 가능성이 열리는 자리",
    "목욕": "감각, 노출, 정화, 변동성이 강해지는 자리",
    "관대": "형태를 갖추고 사회적 외형을 정비하는 자리",
    "건록": "자기 힘과 기반이 안정적으로 서는 자리",
    "제왕": "기운이 가장 왕성하고 주도성이 강해지는 자리",
    "쇠": "정점 이후 힘을 조절하고 내려놓기 시작하는 자리",
    "병": "기운이 약해져 관리와 보완이 필요한 자리",
    "사": "기운이 멈추고 전환을 준비하는 자리",
    "묘": "기운이 저장되고 안으로 압축되는 자리",
    "절": "기존 흐름이 끊기고 새 판을 기다리는 자리",
    "태": "새 가능성이 안에서 잉태되는 자리",
    "양": "기운이 보호받으며 다음 출현을 준비하는 자리",
}

TWELVE_STAGE_TABLE: dict[str, dict[str, str]] = {
    "甲": {
        "亥": "장생",
        "子": "목욕",
        "丑": "관대",
        "寅": "건록",
        "卯": "제왕",
        "辰": "쇠",
        "巳": "병",
        "午": "사",
        "未": "묘",
        "申": "절",
        "酉": "태",
        "戌": "양",
    },
    "乙": {
        "午": "장생",
        "巳": "목욕",
        "辰": "관대",
        "卯": "건록",
        "寅": "제왕",
        "丑": "쇠",
        "子": "병",
        "亥": "사",
        "戌": "묘",
        "酉": "절",
        "申": "태",
        "未": "양",
    },
    "丙": {
        "寅": "장생",
        "卯": "목욕",
        "辰": "관대",
        "巳": "건록",
        "午": "제왕",
        "未": "쇠",
        "申": "병",
        "酉": "사",
        "戌": "묘",
        "亥": "절",
        "子": "태",
        "丑": "양",
    },
    "丁": {
        "酉": "장생",
        "申": "목욕",
        "未": "관대",
        "午": "건록",
        "巳": "제왕",
        "辰": "쇠",
        "卯": "병",
        "寅": "사",
        "丑": "묘",
        "子": "절",
        "亥": "태",
        "戌": "양",
    },
    "戊": {
        "寅": "장생",
        "卯": "목욕",
        "辰": "관대",
        "巳": "건록",
        "午": "제왕",
        "未": "쇠",
        "申": "병",
        "酉": "사",
        "戌": "묘",
        "亥": "절",
        "子": "태",
        "丑": "양",
    },
    "己": {
        "酉": "장생",
        "申": "목욕",
        "未": "관대",
        "午": "건록",
        "巳": "제왕",
        "辰": "쇠",
        "卯": "병",
        "寅": "사",
        "丑": "묘",
        "子": "절",
        "亥": "태",
        "戌": "양",
    },
    "庚": {
        "巳": "장생",
        "午": "목욕",
        "未": "관대",
        "申": "건록",
        "酉": "제왕",
        "戌": "쇠",
        "亥": "병",
        "子": "사",
        "丑": "묘",
        "寅": "절",
        "卯": "태",
        "辰": "양",
    },
    "辛": {
        "子": "장생",
        "亥": "목욕",
        "戌": "관대",
        "酉": "건록",
        "申": "제왕",
        "未": "쇠",
        "午": "병",
        "巳": "사",
        "辰": "묘",
        "卯": "절",
        "寅": "태",
        "丑": "양",
    },
    "壬": {
        "申": "장생",
        "酉": "목욕",
        "戌": "관대",
        "亥": "건록",
        "子": "제왕",
        "丑": "쇠",
        "寅": "병",
        "卯": "사",
        "辰": "묘",
        "巳": "절",
        "午": "태",
        "未": "양",
    },
    "癸": {
        "卯": "장생",
        "寅": "목욕",
        "丑": "관대",
        "子": "건록",
        "亥": "제왕",
        "戌": "쇠",
        "酉": "병",
        "申": "사",
        "未": "묘",
        "午": "절",
        "巳": "태",
        "辰": "양",
    },
}


def analyze_twelve_stage(day_stem: str, target_branch: str) -> dict[str, Any]:
    stem = SipsungCalculator.validate_day_stem(day_stem)
    branch = target_branch.strip()
    if branch not in SipsungCalculator.BRANCH_ELEMENTS:
        supported = ", ".join(SipsungCalculator.BRANCH_ELEMENTS)
        raise ValueError(f"target_branch must be one of earthly branches: {supported}")

    stage = TWELVE_STAGE_TABLE[stem][branch]
    return {
        "day_stem": stem,
        "target_branch": branch,
        "twelve_stage": stage,
        "stage_index": STAGE_ORDER.index(stage) + 1,
        "description": STAGE_DESCRIPTIONS[stage],
    }


def analyze_twelve_stages_for_branches(day_stem: str, branches: list[str]) -> list[dict[str, Any]]:
    return [analyze_twelve_stage(day_stem, branch) for branch in branches]

