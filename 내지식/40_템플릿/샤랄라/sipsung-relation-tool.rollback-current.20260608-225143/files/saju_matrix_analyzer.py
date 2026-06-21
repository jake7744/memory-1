from __future__ import annotations

from typing import Any

from saju_daily_luck import Pillar, analyze_daily_luck, load_config
from saju_interactions import make_layered_pillars, scan_interactions
from saju_twelve_spirits import analyze_twelve_spirit
from saju_twelve_stages import analyze_twelve_stage
from saju_vector_model import summarize_branch_vectors


def analyze_matrix(config: dict[str, Any], target_date: str, hour_pillar: str | None = None) -> dict[str, Any]:
    daily = analyze_daily_luck(config, target_date)
    day_master = daily["day_master"]
    natal = config["natal"]
    basis_mode = config.get("twelve_spirits_basis", "year_branch")
    base_branch = Pillar.parse(natal["year" if basis_mode == "year_branch" else "day"]).branch

    day_pillar = Pillar.parse(daily["calculated"]["day_pillar"], "day_luck")
    selected_hour = hour_pillar
    if selected_hour:
        Pillar.parse(selected_hour, "hour_luck")

    layers = make_layered_pillars(daily["fixed_layers"], day_pillar.text(), selected_hour)
    interactions = scan_interactions(layers)
    vector_summary = summarize_branch_vectors([item["branch"] for item in layers])

    branches = [{"layer": item["layer"], "branch": item["branch"]} for item in layers]
    twelve_stages = [
        {"layer": item["layer"], **analyze_twelve_stage(day_master, item["branch"])}
        for item in layers
    ]
    twelve_spirits = [
        {"layer": item["layer"], **analyze_twelve_spirit(base_branch, item["branch"], basis_mode)}
        for item in layers
    ]

    hour_matrices = []
    if not selected_hour:
        for slot in daily["calculated"]["hour_pillars"]:
            hour_layers = make_layered_pillars(daily["fixed_layers"], day_pillar.text(), slot["pillar"])
            hour_matrices.append(
                {
                    "range_label": slot["range_label"],
                    "hour_pillar": slot["pillar"],
                    "interactions": scan_interactions(hour_layers),
                    "twelve_stage": analyze_twelve_stage(day_master, slot["branch"]),
                    "twelve_spirit": analyze_twelve_spirit(base_branch, slot["branch"], basis_mode),
                }
            )

    return {
        "status": "success",
        "daily_luck": daily,
        "matrix": {
            "layers": layers,
            "branches": branches,
            "twelve_stages": twelve_stages,
            "twelve_spirits": twelve_spirits,
            "interactions": interactions,
            "vector_summary": vector_summary,
            "hour_matrices": hour_matrices,
        },
        "report_guardrails": [
            "Use matrix.interactions as the source of truth for all detected stem and branch relations.",
            "Do not ask the user to request missing relations; scan_interactions is exhaustive for implemented tables.",
            "Mention that twelve spirits use the configured basis branch.",
        ],
    }


def analyze_matrix_from_config(config_path: str, target_date: str, hour_pillar: str | None = None) -> dict[str, Any]:
    return analyze_matrix(load_config(config_path), target_date, hour_pillar)
