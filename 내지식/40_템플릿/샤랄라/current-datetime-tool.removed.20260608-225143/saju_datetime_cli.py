from __future__ import annotations

import argparse
import json
import sys

from saju_datetime_tool import DEFAULT_TIMEZONE, current_datetime


def main() -> int:
    parser = argparse.ArgumentParser(description="Return current local datetime for Connect AI.")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    args = parser.parse_args()

    try:
        print(json.dumps({"status": "success", "data": current_datetime(args.timezone)}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
