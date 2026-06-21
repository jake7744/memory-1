from __future__ import annotations

import unittest

from saju_daily_luck import calculate_day_pillar, calculate_hour_pillar, analyze_daily_luck


CONFIG = {
    "profile_name": "test",
    "timezone": "Asia/Seoul",
    "polarity_mode": "cheyong",
    "branch_mode": "hidden_all",
    "hour_boundary": "23:30",
    "day_pillar_anchor": {"date": "2026-06-07", "pillar": "壬子"},
    "natal": {"year": "癸丑", "month": "戊辰", "day": "辛酉", "hour": "甲午"},
    "luck": {"daewoon": "壬戌", "year": "丙午", "month": "甲午"},
}


class SajuDailyLuckTest(unittest.TestCase):
    def test_known_anchor_day(self) -> None:
        self.assertEqual(calculate_day_pillar(__import__("datetime").date(2026, 6, 7), CONFIG).text(), "壬子")

    def test_next_day_from_anchor(self) -> None:
        self.assertEqual(calculate_day_pillar(__import__("datetime").date(2026, 6, 8), CONFIG).text(), "癸丑")

    def test_hour_pillar_for_imja_day(self) -> None:
        self.assertEqual(calculate_hour_pillar("壬", 3).text(), "癸卯")
        self.assertEqual(calculate_hour_pillar("壬", 4).text(), "甲辰")
        self.assertEqual(calculate_hour_pillar("壬", 8).text(), "戊申")

    def test_daily_luck_shape(self) -> None:
        result = analyze_daily_luck(CONFIG, "2026-06-07")
        self.assertEqual(result["calculated"]["day_pillar"], "壬子")
        self.assertEqual(result["calculated"]["hour_pillars"][3]["pillar"], "癸卯")
        self.assertEqual(result["calculated"]["hour_pillars"][4]["range_label"], "07:30~09:30")
        self.assertEqual(result["calculated"]["hour_pillars"][11]["end"], "2026-06-07T23:30")


if __name__ == "__main__":
    unittest.main()
