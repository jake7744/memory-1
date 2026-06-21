from __future__ import annotations

import argparse
import json
import sys

from saju_daily_luck import analyze_daily_luck, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze daily and hourly luck from a preconfigured Saju profile.")
    parser.add_argument("--config", required=True, help="Path to saju_luck_config.json.")
    parser.add_argument("--date", required=True, help="Target local date in YYYY-MM-DD format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        result = analyze_daily_luck(config, args.date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

