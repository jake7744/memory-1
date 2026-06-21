from __future__ import annotations

import argparse
import json
import sys

from saju_sipsung_rules import analyze_sipsung


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze ten-god relationships for Saju ganji.")
    parser.add_argument("--day-stem", required=True, help="Day stem, one of 甲乙丙丁戊己庚辛壬癸.")
    parser.add_argument("--target", required=True, help="Target heavenly stem or earthly branch.")
    parser.add_argument("--polarity-mode", choices=["standard", "cheyong"], default="cheyong")
    parser.add_argument("--branch-mode", choices=["surface", "hidden_main", "hidden_all"], default="hidden_all")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = analyze_sipsung(
            day_stem=args.day_stem,
            target_character=args.target,
            polarity_mode=args.polarity_mode,
            branch_mode=args.branch_mode,
        )
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

