from __future__ import annotations

import unittest

from saju_sipsung_rules import SipsungCalculator, analyze_sipsung


class SipsungCalculatorTest(unittest.TestCase):
    def test_stem_relationship(self) -> None:
        result = analyze_sipsung("丙", "庚")
        self.assertEqual(result["primary_sipsung"], "편재")
        self.assertEqual(result["relationship_direction"], "day_controls_target")

    def test_day_stem_rejects_branch(self) -> None:
        with self.assertRaises(ValueError):
            analyze_sipsung("寅", "丙")

    def test_cheyong_branch_surface(self) -> None:
        result = analyze_sipsung("丙", "子", polarity_mode="cheyong", branch_mode="surface")
        self.assertEqual(result["surface"]["sipsung"], "정관")

    def test_standard_branch_surface(self) -> None:
        result = analyze_sipsung("丙", "子", polarity_mode="standard", branch_mode="surface")
        self.assertEqual(result["surface"]["sipsung"], "편관")

    def test_hidden_all_for_in_branch(self) -> None:
        result = analyze_sipsung("丙", "寅", branch_mode="hidden_all")
        hidden = result["hidden_stems"]
        self.assertEqual(hidden[0]["stem"], "甲")
        self.assertEqual(hidden[0]["sipsung"], "편인")
        self.assertEqual(hidden[1]["stem"], "丙")
        self.assertEqual(hidden[1]["sipsung"], "비견")
        self.assertEqual(hidden[2]["stem"], "戊")
        self.assertEqual(hidden[2]["sipsung"], "식신")

    def test_pair_compatibility_method(self) -> None:
        result = SipsungCalculator.calculate_pair("丙", "寅")
        self.assertEqual(result["sipsung"], "편인")


if __name__ == "__main__":
    unittest.main()

