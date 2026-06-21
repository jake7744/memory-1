from __future__ import annotations

import unittest

from saju_datetime_tool import current_datetime


class DateTimeToolTest(unittest.TestCase):
    def test_current_datetime_shape(self) -> None:
        result = current_datetime("Asia/Seoul")
        self.assertEqual(result["timezone"], "Asia/Seoul")
        self.assertRegex(result["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(result["time_hm"], r"^\d{2}:\d{2}$")


if __name__ == "__main__":
    unittest.main()

