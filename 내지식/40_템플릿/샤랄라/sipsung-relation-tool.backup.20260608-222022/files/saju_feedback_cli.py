from __future__ import annotations

import argparse
import json
import sys

from saju_feedback_analyzer import summarize_correlations
from saju_feedback_store import (
    correlations_jsonl_path,
    initialize_daily_log,
    read_jsonl,
    store_event,
)
from saju_feedback_report import generate_weekly_report
from saju_datetime_tool import DEFAULT_TIMEZONE, current_datetime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Store and analyze Saju daily/hourly feedback.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init-day")
    init.add_argument("--config", required=True)
    init.add_argument("--date", required=True)
    init.add_argument("--feedback-dir", default=None)

    event = subparsers.add_parser("add-event")
    event.add_argument("--config", required=True)
    event.add_argument("--date", default=None)
    event.add_argument("--event-text", required=True)
    event.add_argument("--time-text", default=None)
    event.add_argument("--hour-pillar", default=None)
    event.add_argument("--event-type", default="other")
    event.add_argument("--emotion", default="neutral")
    event.add_argument("--agent-note", default="")
    event.add_argument("--feedback-dir", default=None)

    summary = subparsers.add_parser("summary")
    summary.add_argument("--feedback-dir", default=None)

    weekly = subparsers.add_parser("weekly-report")
    weekly.add_argument("--week-of", required=True, help="Any date in the target week, YYYY-MM-DD.")
    weekly.add_argument("--feedback-dir", default=None)

    now = subparsers.add_parser("now")
    now.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        feedback_dir = args.feedback_dir if getattr(args, "feedback_dir", None) else None
        if args.command == "init-day":
            result = initialize_daily_log(args.config, args.date, feedback_dir or _default_feedback_dir())
        elif args.command == "add-event":
            result = store_event(
                config_path=args.config,
                date=args.date,
                event_text=args.event_text,
                time_text=args.time_text,
                hour_pillar=args.hour_pillar,
                event_type=args.event_type,
                emotion=args.emotion,
                agent_note=args.agent_note,
                feedback_dir=feedback_dir or _default_feedback_dir(),
            )
        elif args.command == "summary":
            rows = read_jsonl(correlations_jsonl_path(feedback_dir or _default_feedback_dir()))
            result = {"status": "success", "summary": summarize_correlations(rows)}
        elif args.command == "weekly-report":
            result = generate_weekly_report(args.week_of, feedback_dir or _default_feedback_dir())
        elif args.command == "now":
            result = {"status": "success", "data": current_datetime(args.timezone)}
        else:
            raise ValueError(f"Unknown command: {args.command}")

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


def _default_feedback_dir() -> str:
    from saju_feedback_store import DEFAULT_FEEDBACK_DIR

    return str(DEFAULT_FEEDBACK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
