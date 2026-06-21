from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from saju_feedback_store import initialize_daily_log, read_jsonl, store_event
from saju_feedback_report import generate_weekly_report


CONFIG_PATH = "saju_luck_config.example.json"


class FeedbackStoreTest(unittest.TestCase):
    def test_init_day_creates_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = initialize_daily_log(CONFIG_PATH, "2026-06-07", temp_dir)
            path = Path(result["daily_markdown"])
            self.assertTrue(path.exists())
            text = path.read_text(encoding="utf-8")
            self.assertIn("오늘의 일진/시운 요약", text)

    def test_add_event_by_time_matches_hour_slot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = store_event(
                CONFIG_PATH,
                "2026-06-07",
                "일하다가 갑자기 스트레스를 크게 느낌",
                time_text="15:40",
                event_type="emotion",
                emotion="stress",
                feedback_dir=temp_dir,
            )
            self.assertEqual(result["event"]["hour_range"], "15:30~17:30")
            self.assertEqual(result["event"]["hour_pillar"], "戊申")
            events = read_jsonl(Path(temp_dir) / "events.jsonl")
            self.assertEqual(len(events), 1)
            self.assertIn("linked_matrix", events[0])

    def test_add_event_defaults_to_current_datetime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = store_event(
                CONFIG_PATH,
                None,
                "방금 집중이 흐트러짐",
                event_type="emotion",
                emotion="anxiety",
                feedback_dir=temp_dir,
            )
            self.assertRegex(result["event"]["date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertRegex(result["event"]["time_text"], r"^\d{2}:\d{2}$")
            self.assertIn("created_at_timezone", result["event"])

    def test_add_event_by_hour_pillar(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = store_event(
                CONFIG_PATH,
                "2026-06-07",
                "경신시에 집중해서 코딩함",
                hour_pillar="戊申",
                event_type="work",
                emotion="focus",
                feedback_dir=temp_dir,
            )
            self.assertEqual(result["event"]["hour_pillar"], "戊申")

    def test_correction_is_stored_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = store_event(
                CONFIG_PATH,
                "2026-06-07",
                "아까 일이 아니라 지금 다시 생각나서 화가 남",
                time_text="15:40",
                event_type="correction",
                emotion="anger",
                feedback_dir=temp_dir,
            )
            self.assertEqual(result["event"]["event_type"], "correction")
            self.assertIn("정정 피드백", result["correlation"]["summary"])

    def test_add_event_generates_weekly_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = store_event(
                CONFIG_PATH,
                "2026-06-07",
                "일하다가 갑자기 스트레스를 크게 느낌",
                time_text="15:40",
                event_type="emotion",
                emotion="stress",
                feedback_dir=temp_dir,
            )
            report = Path(result["weekly_report"])
            self.assertTrue(report.exists())
            text = report.read_text(encoding="utf-8")
            self.assertIn("주간 사주 피드백 연결 리포트", text)
            self.assertIn("형충파해합 연결", text)

    def test_manual_weekly_report_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_event(
                CONFIG_PATH,
                "2026-06-07",
                "경신시에 집중해서 코딩함",
                hour_pillar="戊申",
                event_type="work",
                emotion="focus",
                feedback_dir=temp_dir,
            )
            result = generate_weekly_report("2026-06-07", temp_dir)
            self.assertEqual(result["correlations_used"], 1)
            self.assertTrue(Path(result["weekly_report"]).exists())


if __name__ == "__main__":
    unittest.main()
