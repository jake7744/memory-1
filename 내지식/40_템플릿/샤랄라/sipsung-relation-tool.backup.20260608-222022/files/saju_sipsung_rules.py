from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


PolarityMode = Literal["standard", "cheyong"]
BranchMode = Literal["surface", "hidden_main", "hidden_all"]


@dataclass(frozen=True)
class GanjiInfo:
    character: str
    element: str
    polarity: str
    kind: Literal["stem", "branch"]
    label: str


@dataclass(frozen=True)
class HiddenStem:
    stem: str
    role: Literal["main", "middle", "residual"]
    weight: int


class SipsungCalculator:
    """Deterministic ten-god calculator for a chosen Myeongli rule profile."""

    STEMS: dict[str, dict[str, str]] = {
        "甲": {"element": "목", "polarity": "+", "label": "갑목"},
        "乙": {"element": "목", "polarity": "-", "label": "을목"},
        "丙": {"element": "화", "polarity": "+", "label": "병화"},
        "丁": {"element": "화", "polarity": "-", "label": "정화"},
        "戊": {"element": "토", "polarity": "+", "label": "무토"},
        "己": {"element": "토", "polarity": "-", "label": "기토"},
        "庚": {"element": "금", "polarity": "+", "label": "경금"},
        "辛": {"element": "금", "polarity": "-", "label": "신금"},
        "壬": {"element": "수", "polarity": "+", "label": "임수"},
        "癸": {"element": "수", "polarity": "-", "label": "계수"},
    }

    BRANCH_ELEMENTS: dict[str, dict[str, str]] = {
        "子": {"element": "수", "label": "자수"},
        "丑": {"element": "토", "label": "축토"},
        "寅": {"element": "목", "label": "인목"},
        "卯": {"element": "목", "label": "묘목"},
        "辰": {"element": "토", "label": "진토"},
        "巳": {"element": "화", "label": "사화"},
        "午": {"element": "화", "label": "오화"},
        "未": {"element": "토", "label": "미토"},
        "申": {"element": "금", "label": "신금"},
        "酉": {"element": "금", "label": "유금"},
        "戌": {"element": "토", "label": "술토"},
        "亥": {"element": "수", "label": "해수"},
    }

    STANDARD_BRANCH_POLARITY: dict[str, str] = {
        "子": "+",
        "丑": "-",
        "寅": "+",
        "卯": "-",
        "辰": "+",
        "巳": "-",
        "午": "+",
        "未": "-",
        "申": "+",
        "酉": "-",
        "戌": "+",
        "亥": "-",
    }

    CHEYONG_BRANCH_POLARITY: dict[str, str] = {
        **STANDARD_BRANCH_POLARITY,
        "子": "-",
        "巳": "+",
        "午": "-",
        "亥": "+",
    }

    HIDDEN_STEMS: dict[str, tuple[HiddenStem, ...]] = {
        "子": (HiddenStem("癸", "main", 100),),
        "丑": (HiddenStem("己", "main", 60), HiddenStem("癸", "middle", 30), HiddenStem("辛", "residual", 10)),
        "寅": (HiddenStem("甲", "main", 60), HiddenStem("丙", "middle", 30), HiddenStem("戊", "residual", 10)),
        "卯": (HiddenStem("乙", "main", 100),),
        "辰": (HiddenStem("戊", "main", 60), HiddenStem("乙", "middle", 30), HiddenStem("癸", "residual", 10)),
        "巳": (HiddenStem("丙", "main", 60), HiddenStem("庚", "middle", 30), HiddenStem("戊", "residual", 10)),
        "午": (HiddenStem("丁", "main", 70), HiddenStem("己", "middle", 30)),
        "未": (HiddenStem("己", "main", 60), HiddenStem("丁", "middle", 30), HiddenStem("乙", "residual", 10)),
        "申": (HiddenStem("庚", "main", 60), HiddenStem("壬", "middle", 30), HiddenStem("戊", "residual", 10)),
        "酉": (HiddenStem("辛", "main", 100),),
        "戌": (HiddenStem("戊", "main", 60), HiddenStem("辛", "middle", 30), HiddenStem("丁", "residual", 10)),
        "亥": (HiddenStem("壬", "main", 70), HiddenStem("甲", "middle", 30)),
    }

    GENERATES: dict[str, str] = {"목": "화", "화": "토", "토": "금", "금": "수", "수": "목"}
    CONTROLS: dict[str, str] = {"목": "토", "토": "수", "수": "화", "화": "금", "금": "목"}

    SIPSUNG_ENGLISH: dict[str, str] = {
        "비견": "friend",
        "겁재": "rob wealth",
        "식신": "eating god",
        "상관": "hurting officer",
        "편재": "indirect wealth",
        "정재": "direct wealth",
        "편관": "seven killings",
        "정관": "direct officer",
        "편인": "indirect resource",
        "정인": "direct resource",
    }

    @classmethod
    def validate_day_stem(cls, day_stem: str) -> str:
        normalized = cls._normalize_one(day_stem, "day_stem")
        if normalized not in cls.STEMS:
            raise ValueError(f"day_stem must be one of 10 heavenly stems: {', '.join(cls.STEMS)}")
        return normalized

    @classmethod
    def validate_target(cls, target_character: str) -> str:
        normalized = cls._normalize_one(target_character, "target_character")
        if normalized not in cls.STEMS and normalized not in cls.BRANCH_ELEMENTS:
            supported = ", ".join([*cls.STEMS.keys(), *cls.BRANCH_ELEMENTS.keys()])
            raise ValueError(f"target_character must be a heavenly stem or earthly branch: {supported}")
        return normalized

    @staticmethod
    def _normalize_one(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")
        normalized = value.strip()
        if len(normalized) != 1:
            raise ValueError(f"{field_name} must be exactly one ganji character")
        return normalized

    @classmethod
    def get_info(cls, character: str, polarity_mode: PolarityMode = "cheyong") -> GanjiInfo:
        normalized = cls.validate_target(character)
        if normalized in cls.STEMS:
            data = cls.STEMS[normalized]
            return GanjiInfo(normalized, data["element"], data["polarity"], "stem", data["label"])

        if polarity_mode not in ("standard", "cheyong"):
            raise ValueError("polarity_mode must be 'standard' or 'cheyong'")

        data = cls.BRANCH_ELEMENTS[normalized]
        polarity_map = cls.CHEYONG_BRANCH_POLARITY if polarity_mode == "cheyong" else cls.STANDARD_BRANCH_POLARITY
        return GanjiInfo(normalized, data["element"], polarity_map[normalized], "branch", data["label"])

    @classmethod
    def calculate_pair(cls, day_stem: str, target_character: str, polarity_mode: PolarityMode = "cheyong") -> dict[str, Any]:
        day = cls.get_info(cls.validate_day_stem(day_stem), polarity_mode)
        target = cls.get_info(target_character, polarity_mode)
        return cls._build_pair_result(day, target, polarity_mode)

    @classmethod
    def analyze(
        cls,
        day_stem: str,
        target_character: str,
        polarity_mode: PolarityMode = "cheyong",
        branch_mode: BranchMode = "hidden_all",
    ) -> dict[str, Any]:
        if branch_mode not in ("surface", "hidden_main", "hidden_all"):
            raise ValueError("branch_mode must be 'surface', 'hidden_main', or 'hidden_all'")

        day = cls.get_info(cls.validate_day_stem(day_stem), polarity_mode)
        target = cls.get_info(target_character, polarity_mode)
        surface = cls._build_pair_result(day, target, polarity_mode)

        result: dict[str, Any] = {
            "rule_profile": {
                "polarity_mode": polarity_mode,
                "branch_mode": branch_mode,
                "branch_polarity_note": cls._polarity_note(polarity_mode),
            },
            "day_stem": cls._serialize_info(day),
            "target": cls._serialize_info(target),
            "surface": surface,
            "primary_sipsung": surface["sipsung"],
            "relationship_direction": surface["relationship_direction"],
            "hidden_stems": [],
            "interpretation_guardrails": [
                "Do not infer ten-god relationships without this calculation result.",
                "For branches, distinguish surface qi from hidden-stem ten gods.",
                "Mention the selected polarity mode when branch polarity affects the result.",
            ],
        }

        if target.kind == "branch":
            hidden = cls._analyze_hidden_stems(day, target.character, polarity_mode)
            if branch_mode == "hidden_main":
                hidden = hidden[:1]
            result["hidden_stems"] = hidden
            if branch_mode in ("hidden_main", "hidden_all") and hidden:
                result["primary_sipsung"] = hidden[0]["sipsung"]
                result["primary_basis"] = "hidden_main_stem"
            else:
                result["primary_basis"] = "branch_surface"
        else:
            result["primary_basis"] = "stem"

        return result

    @classmethod
    def _analyze_hidden_stems(cls, day: GanjiInfo, branch: str, polarity_mode: PolarityMode) -> list[dict[str, Any]]:
        hidden_results = []
        for hidden in cls.HIDDEN_STEMS[branch]:
            hidden_info = cls.get_info(hidden.stem, polarity_mode)
            pair = cls._build_pair_result(day, hidden_info, polarity_mode)
            hidden_results.append(
                {
                    "stem": hidden.stem,
                    "label": hidden_info.label,
                    "role": hidden.role,
                    "weight": hidden.weight,
                    "element": hidden_info.element,
                    "polarity": hidden_info.polarity,
                    "sipsung": pair["sipsung"],
                    "relationship_direction": pair["relationship_direction"],
                    "relationship_type": pair["relationship_type"],
                }
            )
        return hidden_results

    @classmethod
    def _build_pair_result(cls, day: GanjiInfo, target: GanjiInfo, polarity_mode: PolarityMode) -> dict[str, Any]:
        same_polarity = day.polarity == target.polarity
        sipsung, relationship_direction, relationship_type = cls._calculate_sipsung(
            day.element, day.polarity, target.element, target.polarity
        )
        return {
            "day": cls._serialize_info(day),
            "target": cls._serialize_info(target),
            "same_polarity": same_polarity,
            "relationship_type": relationship_type,
            "relationship_direction": relationship_direction,
            "sipsung": sipsung,
            "sipsung_en": cls.SIPSUNG_ENGLISH[sipsung],
            "polarity_mode": polarity_mode,
        }

    @classmethod
    def _calculate_sipsung(cls, day_element: str, day_polarity: str, target_element: str, target_polarity: str) -> tuple[str, str, str]:
        same_polarity = day_polarity == target_polarity

        if day_element == target_element:
            return ("비견" if same_polarity else "겁재", "same_element", "동기")
        if cls.GENERATES[day_element] == target_element:
            return ("식신" if same_polarity else "상관", "day_generates_target", "상생")
        if cls.CONTROLS[day_element] == target_element:
            return ("편재" if same_polarity else "정재", "day_controls_target", "상극")
        if cls.CONTROLS[target_element] == day_element:
            return ("편관" if same_polarity else "정관", "target_controls_day", "상극")
        if cls.GENERATES[target_element] == day_element:
            return ("편인" if same_polarity else "정인", "target_generates_day", "상생")

        raise RuntimeError("Unreachable five-element relationship")

    @staticmethod
    def _serialize_info(info: GanjiInfo) -> dict[str, str]:
        return {
            "character": info.character,
            "label": info.label,
            "kind": info.kind,
            "element": info.element,
            "polarity": info.polarity,
        }

    @staticmethod
    def _polarity_note(polarity_mode: PolarityMode) -> str:
        if polarity_mode == "cheyong":
            return "Uses the source text profile: 巳/亥 are treated as yang, 子/午 as yin."
        return "Uses the common alternating branch polarity profile."


def analyze_sipsung(
    day_stem: str,
    target_character: str,
    polarity_mode: PolarityMode = "cheyong",
    branch_mode: BranchMode = "hidden_all",
) -> dict[str, Any]:
    return SipsungCalculator.analyze(day_stem, target_character, polarity_mode, branch_mode)

