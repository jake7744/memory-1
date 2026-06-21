from __future__ import annotations

import argparse
import json
import sys

from saju_vector_model import classify_vector_relation
from saju_vector_model import summarize_branch_vectors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze branch vector relation.")
    parser.add_argument("--branch-a", required=True)
    parser.add_argument("--branch-b", required=True)
    parser.add_argument("--summary", default=None, help="Optional comma separated branch counts, e.g. 午:4,丑:3.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.summary:
            counts = {}
            for item in args.summary.split(","):
                branch, count = item.split(":", 1)
                counts[branch.strip()] = int(count.strip())
            result = summarize_branch_vectors(counts)
        else:
            result = classify_vector_relation(args.branch_a, args.branch_b)
        print(json.dumps({"status": "success", "data": result}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
