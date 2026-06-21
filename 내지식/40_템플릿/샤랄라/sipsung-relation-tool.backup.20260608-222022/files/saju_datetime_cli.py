from __future__ import annotations

import argparse
import json
import sys

from saju_datetime_tool import DEFAULT_TIMEZONE, current_datetime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Return current local datetime for Saju tools.")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(json.dumps({"status": "success", "data": current_datetime(args.timezone)}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

