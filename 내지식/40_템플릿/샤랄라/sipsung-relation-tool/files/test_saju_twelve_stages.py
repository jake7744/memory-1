from __future__ import annotations

import unittest

from saju_twelve_stages import analyze_twelve_stage, analyze_twelve_stages_for_branches


class TwelveStagesTest(unittest.TestCase):
    def test_source_example_sin_to_ja_is_jangsaeng(self) -> None:
        result = analyze_twelve_stage("辛", "子")
        self.assertEqual(result["twelve_stage"], "장생")
        self.assertEqual(result["stage_index"], 1)

    def test_imja_itself_branch_for_im_day_is_jewang(self) -> None:
        result = analyze_twelve_stage("壬", "子")
        self.assertEqual(result["twelve_stage"], "제왕")

    def test_parallel_branch_list(self) -> None:
        result = analyze_twelve_stages_for_branches("辛", ["子", "午", "酉"])
        self.assertEqual([item["twelve_stage"] for item in result], ["장생", "병", "건록"])

    def test_rejects_non_branch_target(self) -> None:
        with self.assertRaises(ValueError):
            analyze_twelve_stage("辛", "壬")

    def test_rejects_branch_as_day_stem(self) -> None:
        with self.assertRaises(ValueError):
            analyze_twelve_stage("子", "子")


if __name__ == "__main__":
    unittest.main()

