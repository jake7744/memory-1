from __future__ import annotations

import argparse
import json
import sys

from saju_twelve_stages import analyze_twelve_stage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze the twelve life stage for a day stem and branch.")
    parser.add_argument("--day-stem", required=True, help="Day stem, one of 甲乙丙丁戊己庚辛壬癸.")
    parser.add_argument("--target-branch", required=True, help="Target earthly branch.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = analyze_twelve_stage(args.day_stem, args.target_branch)
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

