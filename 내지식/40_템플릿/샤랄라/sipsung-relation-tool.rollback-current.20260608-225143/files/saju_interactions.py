from __future__ import annotations

from itertools import combinations
from typing import Any

from saju_vector_model import enrich_branch_pair_relation


STEM_COMBINES = {
    frozenset(("甲", "己")): "甲己合",
    frozenset(("乙", "庚")): "乙庚合",
    frozenset(("丙", "辛")): "丙辛合",
    frozenset(("丁", "壬")): "丁壬合",
    frozenset(("戊", "癸")): "戊癸合",
}
STEM_CLASHES = {
    frozenset(("甲", "庚")): "甲庚沖",
    frozenset(("乙", "辛")): "乙辛沖",
    frozenset(("丙", "壬")): "丙壬沖",
    frozenset(("丁", "癸")): "丁癸沖",
}

BRANCH_SIX_COMBINES = {
    frozenset(("子", "丑")): "子丑合",
    frozenset(("寅", "亥")): "寅亥合",
    frozenset(("卯", "戌")): "卯戌合",
    frozenset(("辰", "酉")): "辰酉合",
    frozenset(("巳", "申")): "巳申合",
    frozenset(("午", "未")): "午未合",
}
BRANCH_CLASHES = {
    frozenset(("子", "午")): "子午沖",
    frozenset(("丑", "未")): "丑未沖",
    frozenset(("寅", "申")): "寅申沖",
    frozenset(("卯", "酉")): "卯酉沖",
    frozenset(("辰", "戌")): "辰戌沖",
    frozenset(("巳", "亥")): "巳亥沖",
}
BRANCH_HARMS = {
    frozenset(("子", "未")): "子未害",
    frozenset(("丑", "午")): "丑午害",
    frozenset(("寅", "巳")): "寅巳害",
    frozenset(("卯", "辰")): "卯辰害",
    frozenset(("申", "亥")): "申亥害",
    frozenset(("酉", "戌")): "酉戌害",
}
BRANCH_BREAKS = {
    frozenset(("子", "酉")): "子酉破",
    frozenset(("丑", "辰")): "丑辰破",
    frozenset(("寅", "亥")): "寅亥破",
    frozenset(("卯", "午")): "卯午破",
    frozenset(("巳", "申")): "巳申破",
    frozenset(("未", "戌")): "未戌破",
}
BRANCH_WONJIN = {
    frozenset(("子", "未")): "子未 원진",
    frozenset(("丑", "午")): "丑午 원진",
    frozenset(("寅", "酉")): "寅酉 원진",
    frozenset(("卯", "申")): "卯申 원진",
    frozenset(("辰", "亥")): "辰亥 원진",
    frozenset(("巳", "戌")): "巳戌 원진",
}
BRANCH_GWIMUN = {
    frozenset(("子", "酉")): "子酉 귀문",
    frozenset(("丑", "午")): "丑午 귀문",
    frozenset(("寅", "未")): "寅未 귀문",
    frozenset(("卯", "申")): "卯申 귀문",
    frozenset(("辰", "亥")): "辰亥 귀문",
    frozenset(("巳", "戌")): "巳戌 귀문",
}

BRANCH_PAIR_PUNISHMENTS = {
    frozenset(("子", "卯")): "子卯刑",
}
SELF_PUNISHMENTS = {"辰": "辰辰自刑", "午": "午午自刑", "酉": "酉酉自刑", "亥": "亥亥自刑"}

TRINES = {
    frozenset(("申", "子", "辰")): "申子辰三合 水局",
    frozenset(("亥", "卯", "未")): "亥卯未三合 木局",
    frozenset(("寅", "午", "戌")): "寅午戌三合 火局",
    frozenset(("巳", "酉", "丑")): "巳酉丑三合 金局",
}
DIRECTIONAL = {
    frozenset(("寅", "卯", "辰")): "寅卯辰方合 木方",
    frozenset(("巳", "午", "未")): "巳午未方合 火方",
    frozenset(("申", "酉", "戌")): "申酉戌方合 金方",
    frozenset(("亥", "子", "丑")): "亥子丑方合 水方",
}
THREE_PUNISHMENTS = {
    frozenset(("寅", "巳", "申")): "寅巳申三刑",
    frozenset(("丑", "戌", "未")): "丑戌未三刑",
}
HALF_COMBINES = {
    frozenset(("申", "子")): "申子半合 水",
    frozenset(("子", "辰")): "子辰半合 水",
    frozenset(("亥", "卯")): "亥卯半合 木",
    frozenset(("卯", "未")): "卯未半合 木",
    frozenset(("寅", "午")): "寅午半合 火",
    frozenset(("午", "戌")): "午戌半合 火",
    frozenset(("巳", "酉")): "巳酉半合 金",
    frozenset(("酉", "丑")): "酉丑半合 金",
    frozenset(("申", "辰")): "申辰拱合 水",
    frozenset(("亥", "未")): "亥未拱合 木",
    frozenset(("寅", "戌")): "寅戌拱合 火",
    frozenset(("巳", "丑")): "巳丑拱合 金",
}


def make_layered_pillars(fixed_layers: dict[str, dict[str, str]], day_pillar: str, hour_pillar: str | None = None) -> list[dict[str, str]]:
    layers = []
    for group_name, group in fixed_layers.items():
        for name, pillar in group.items():
            layers.append({"layer": f"{group_name}_{name}", "pillar": pillar, "stem": pillar[0], "branch": pillar[1]})
    layers.append({"layer": "day_luck", "pillar": day_pillar, "stem": day_pillar[0], "branch": day_pillar[1]})
    if hour_pillar:
        layers.append({"layer": "hour_luck", "pillar": hour_pillar, "stem": hour_pillar[0], "branch": hour_pillar[1]})
    return layers


def scan_interactions(layers: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "layers": layers,
        "stem_relations": _scan_stem_pairs(layers),
        "branch_pair_relations": _scan_branch_pairs(layers),
        "branch_triple_relations": _scan_branch_triples(layers),
    }


def _relation_record(kind: str, name: str, items: tuple[dict[str, str], ...]) -> dict[str, Any]:
    return {
        "kind": kind,
        "name": name,
        "layers": [item["layer"] for item in items],
        "pillars": [item["pillar"] for item in items],
        "stems": [item["stem"] for item in items],
        "branches": [item["branch"] for item in items],
    }


def _scan_stem_pairs(layers: list[dict[str, str]]) -> list[dict[str, Any]]:
    found = []
    for left, right in combinations(layers, 2):
        key = frozenset((left["stem"], right["stem"]))
        if key in STEM_COMBINES:
            found.append(_relation_record("천간합", STEM_COMBINES[key], (left, right)))
        if key in STEM_CLASHES:
            found.append(_relation_record("천간충", STEM_CLASHES[key], (left, right)))
    return found


def _scan_branch_pairs(layers: list[dict[str, str]]) -> list[dict[str, Any]]:
    found = []
    for left, right in combinations(layers, 2):
        pair = (left, right)
        key = frozenset((left["branch"], right["branch"]))
        if left["branch"] == right["branch"] and left["branch"] in SELF_PUNISHMENTS:
            found.append(_relation_record("자형", SELF_PUNISHMENTS[left["branch"]], pair))
        for kind, table in (
            ("육합", BRANCH_SIX_COMBINES),
            ("반합", HALF_COMBINES),
            ("충", BRANCH_CLASHES),
            ("형", BRANCH_PAIR_PUNISHMENTS),
            ("파", BRANCH_BREAKS),
            ("해", BRANCH_HARMS),
            ("원진", BRANCH_WONJIN),
            ("귀문", BRANCH_GWIMUN),
        ):
            if key in table:
                found.append(_relation_record(kind, table[key], pair))
    return [enrich_branch_pair_relation(item) for item in found]


def _scan_branch_triples(layers: list[dict[str, str]]) -> list[dict[str, Any]]:
    found = []
    for first, second, third in combinations(layers, 3):
        key = frozenset((first["branch"], second["branch"], third["branch"]))
        for kind, table in (("삼합", TRINES), ("방합", DIRECTIONAL), ("삼형", THREE_PUNISHMENTS)):
            if key in table:
                found.append(_relation_record(kind, table[key], (first, second, third)))
    return found
