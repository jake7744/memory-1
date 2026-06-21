from __future__ import annotations

import unittest

from saju_vector_model import angle_delta, circular_mean, classify_vector_relation, summarize_branch_vectors


class VectorModelTest(unittest.TestCase):
    def test_clash_is_reset(self) -> None:
        result = classify_vector_relation("子", "午")
        self.assertEqual(result["delta"], 180)
        self.assertEqual(result["vector_relation"], "reset_clash")
        self.assertEqual(result["resultant_expression"], "0")

    def test_chuk_sul_punishment_vector(self) -> None:
        result = classify_vector_relation("丑", "戌")
        self.assertEqual(result["delta"], 90)
        self.assertEqual(result["vector_relation"], "tuning_pressure")
        self.assertEqual(result["resultant_angle"], 105.0)
        self.assertEqual(result["resultant_element"]["element"], "수")
        self.assertIn("코딩", result["recommended_actions"])

    def test_circular_mean_wraparound(self) -> None:
        self.assertAlmostEqual(circular_mean(330, 30), 0.0, places=6)

    def test_angle_delta_wraparound(self) -> None:
        self.assertEqual(angle_delta(330, 30), 60)

    def test_rejects_non_branch(self) -> None:
        with self.assertRaises(ValueError):
            classify_vector_relation("甲", "子")

    def test_multi_branch_summary_for_four_o_three_chuk(self) -> None:
        result = summarize_branch_vectors({"午": 4, "丑": 3})
        self.assertAlmostEqual(result["resultant_angle"], 316.935687, places=6)
        self.assertEqual(result["resultant_element"]["element"], "화/토")
        self.assertEqual(result["resultant_element"]["branches"], ["巳", "辰"])
        self.assertEqual(result["nearest_branch"]["branch"], "辰")
        self.assertIn("구조화", result["recommended_actions"])


if __name__ == "__main__":
    unittest.main()
