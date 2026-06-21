from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
from typing import Any

from saju_sipsung_rules import SipsungCalculator, analyze_sipsung


STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
SIXTY_PILLARS = [STEMS[i % 10] + BRANCHES[i % 12] for i in range(60)]

HOUR_BRANCHES = list(BRANCHES)
HOUR_STARTS = [
    time(23, 30),
    time(1, 30),
    time(3, 30),
    time(5, 30),
    time(7, 30),
    time(9, 30),
    time(11, 30),
    time(13, 30),
    time(15, 30),
    time(17, 30),
    time(19, 30),
    time(21, 30),
]

HOUR_STEM_START_BY_DAY_STEM = {
    "甲": "甲",
    "己": "甲",
    "乙": "丙",
    "庚": "丙",
    "丙": "戊",
    "辛": "戊",
    "丁": "庚",
    "壬": "庚",
    "戊": "壬",
    "癸": "壬",
}


@dataclass(frozen=True)
class Pillar:
    stem: str
    branch: str

    @classmethod
    def parse(cls, value: str, field_name: str = "pillar") -> "Pillar":
        normalized = value.strip()
        if len(normalized) != 2:
            raise ValueError(f"{field_name} must contain exactly two ganji characters")
        stem, branch = normalized[0], normalized[1]
        SipsungCalculator.validate_day_stem(stem)
        if branch not in SipsungCalculator.BRANCH_ELEMENTS:
            raise ValueError(f"{field_name} branch must be one of {''.join(SipsungCalculator.BRANCH_ELEMENTS)}")
        return cls(stem, branch)

    def text(self) -> str:
        return self.stem + self.branch


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value)


def pillar_from_anchor(target_date: date, anchor_date: date, anchor_pillar: str) -> Pillar:
    anchor = Pillar.parse(anchor_pillar, "anchor_pillar")
    try:
        anchor_index = SIXTY_PILLARS.index(anchor.text())
    except ValueError as exc:
        raise ValueError(f"Invalid sexagenary anchor pillar: {anchor_pillar}") from exc

    delta_days = (target_date - anchor_date).days
    return Pillar.parse(SIXTY_PILLARS[(anchor_index + delta_days) % 60], "day_pillar")


def calculate_day_pillar(target_date: date, config: dict[str, Any]) -> Pillar:
    anchor = config.get("day_pillar_anchor", {})
    anchor_date = parse_iso_date(anchor.get("date", "2026-06-07"))
    anchor_pillar = anchor.get("pillar", "壬子")
    return pillar_from_anchor(target_date, anchor_date, anchor_pillar)


def calculate_hour_pillar(day_stem: str, branch_index: int) -> Pillar:
    start_stem = HOUR_STEM_START_BY_DAY_STEM[day_stem]
    stem_index = STEMS.index(start_stem)
    return Pillar(STEMS[(stem_index + branch_index) % 10], HOUR_BRANCHES[branch_index])


def build_hour_slots(target_date: date, day_stem: str) -> list[dict[str, Any]]:
    slots = []
    for index, branch in enumerate(HOUR_BRANCHES):
        start_t = HOUR_STARTS[index]
        end_t = HOUR_STARTS[(index + 1) % 12]
        start_date = target_date
        end_date = target_date + timedelta(days=1) if index == 0 else target_date

        if index == 0:
            range_label = f"{start_t.strftime('%H:%M')}~{end_t.strftime('%H:%M')}(+1)"
        else:
            range_label = f"{start_t.strftime('%H:%M')}~{end_t.strftime('%H:%M')}"

        pillar = calculate_hour_pillar(day_stem, index)
        slots.append(
            {
                "branch": branch,
                "pillar": pillar.text(),
                "stem": pillar.stem,
                "start": datetime.combine(start_date, start_t).isoformat(timespec="minutes"),
                "end": datetime.combine(end_date, end_t).isoformat(timespec="minutes"),
                "range_label": range_label,
            }
        )
    return slots


def annotate_pillar(day_master: str, pillar: Pillar, polarity_mode: str, branch_mode: str) -> dict[str, Any]:
    return {
        "pillar": pillar.text(),
        "stem": analyze_sipsung(day_master, pillar.stem, polarity_mode=polarity_mode, branch_mode=branch_mode),
        "branch": analyze_sipsung(day_master, pillar.branch, polarity_mode=polarity_mode, branch_mode=branch_mode),
    }


def analyze_daily_luck(config: dict[str, Any], target_date: str | date) -> dict[str, Any]:
    if isinstance(target_date, str):
        target = parse_iso_date(target_date)
    else:
        target = target_date

    polarity_mode = config.get("polarity_mode", "cheyong")
    branch_mode = config.get("branch_mode", "hidden_all")
    natal = config["natal"]
    luck = config["luck"]
    natal_day = Pillar.parse(natal["day"], "natal.day")
    day_master = natal_day.stem

    day_pillar = calculate_day_pillar(target, config)
    hour_slots = build_hour_slots(target, day_pillar.stem)

    fixed_layers = {
        "natal": {key: Pillar.parse(value, f"natal.{key}").text() for key, value in natal.items()},
        "luck": {key: Pillar.parse(value, f"luck.{key}").text() for key, value in luck.items()},
    }

    analyzed_fixed_layers = {
        "natal": {
            key: annotate_pillar(day_master, Pillar.parse(value, f"natal.{key}"), polarity_mode, branch_mode)
            for key, value in natal.items()
        },
        "luck": {
            key: annotate_pillar(day_master, Pillar.parse(value, f"luck.{key}"), polarity_mode, branch_mode)
            for key, value in luck.items()
        },
    }

    analyzed_hours = []
    for slot in hour_slots:
        pillar = Pillar.parse(slot["pillar"], "hour.pillar")
        analyzed_hours.append(
            {
                **slot,
                "analysis": annotate_pillar(day_master, pillar, polarity_mode, branch_mode),
            }
        )

    return {
        "status": "success",
        "profile_name": config.get("profile_name", ""),
        "timezone": config.get("timezone", "Asia/Seoul"),
        "target_date": target.isoformat(),
        "rule_profile": {
            "polarity_mode": polarity_mode,
            "branch_mode": branch_mode,
            "hour_boundary": config.get("hour_boundary", "23:30"),
            "day_pillar_anchor": config.get("day_pillar_anchor", {}),
        },
        "day_master": day_master,
        "fixed_layers": fixed_layers,
        "fixed_layers_analysis": analyzed_fixed_layers,
        "calculated": {
            "day_pillar": day_pillar.text(),
            "day_analysis": annotate_pillar(day_master, day_pillar, polarity_mode, branch_mode),
            "hour_pillars": analyzed_hours,
        },
        "report_guardrails": [
            "Use fixed natal, daewoon, year luck, and month luck from config.",
            "Calculate only day luck and hour luck from target_date unless the user updates fixed layers.",
            "For hourly reports, use the 23:30 two-hour boundary profile unless config says otherwise.",
        ],
    }
