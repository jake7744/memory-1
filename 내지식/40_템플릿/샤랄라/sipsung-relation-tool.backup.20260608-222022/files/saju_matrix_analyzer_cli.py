from __future__ import annotations

import argparse
import json
import sys

from saju_matrix_analyzer import analyze_matrix_from_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Saju daily matrix with twelve stages, spirits, and interactions.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--hour-pillar", default=None, help="Optional selected hour pillar such as 庚申.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = analyze_matrix_from_config(args.config, args.date, args.hour_pillar)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

