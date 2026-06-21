from __future__ import annotations

import unittest

from saju_matrix_analyzer import analyze_matrix
from saju_twelve_spirits import analyze_twelve_spirit


CONFIG = {
    "profile_name": "test",
    "timezone": "Asia/Seoul",
    "polarity_mode": "cheyong",
    "branch_mode": "hidden_all",
    "hour_boundary": "23:30",
    "day_pillar_anchor": {"date": "2026-06-07", "pillar": "壬子"},
    "twelve_spirits_basis": "year_branch",
    "natal": {"year": "癸丑", "month": "戊辰", "day": "辛酉", "hour": "甲午"},
    "luck": {"daewoon": "壬戌", "year": "丙午", "month": "甲午"},
}


class MatrixAnalyzerTest(unittest.TestCase):
    def test_twelve_spirit_source_pattern(self) -> None:
        result = analyze_twelve_spirit("丑", "子")
        self.assertEqual(result["twelve_spirit"], "육해살")

    def test_matrix_finds_day_relations_without_followup(self) -> None:
        result = analyze_matrix(CONFIG, "2026-06-07")
        pair_names = {item["name"] for item in result["matrix"]["interactions"]["branch_pair_relations"]}
        self.assertIn("子午沖", pair_names)
        self.assertIn("子丑合", pair_names)
        self.assertIn("子辰半合 水", pair_names)

    def test_matrix_finds_hour_relations(self) -> None:
        result = analyze_matrix(CONFIG, "2026-06-07", "庚申")
        stem_names = {item["name"] for item in result["matrix"]["interactions"]["stem_relations"]}
        triple_names = {item["name"] for item in result["matrix"]["interactions"]["branch_triple_relations"]}
        pair_names = {item["name"] for item in result["matrix"]["interactions"]["branch_pair_relations"]}
        self.assertIn("甲庚沖", stem_names)
        self.assertIn("申酉戌方合 金方", triple_names)
        self.assertIn("申辰拱合 水", pair_names)

    def test_hour_matrices_are_generated_when_no_hour_selected(self) -> None:
        result = analyze_matrix(CONFIG, "2026-06-07")
        self.assertEqual(len(result["matrix"]["hour_matrices"]), 12)

    def test_matrix_includes_vector_summary(self) -> None:
        result = analyze_matrix(CONFIG, "2026-06-08", "戊午")
        summary = result["matrix"]["vector_summary"]
        self.assertEqual(summary["branch_counts"]["午"], 4)
        self.assertEqual(summary["branch_counts"]["丑"], 2)
        self.assertIn("recommended_actions", summary)


if __name__ == "__main__":
    unittest.main()
