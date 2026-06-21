from __future__ import annotations

from datetime import datetime, timedelta, timezone as datetime_timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_TIMEZONE = "Asia/Seoul"
FALLBACK_TIMEZONES = {
    "Asia/Seoul": datetime_timezone(timedelta(hours=9), name="KST"),
}


def resolve_timezone(timezone: str = DEFAULT_TIMEZONE):
    try:
        return ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        if timezone in FALLBACK_TIMEZONES:
            return FALLBACK_TIMEZONES[timezone]
        raise


def current_datetime(timezone: str = DEFAULT_TIMEZONE) -> dict[str, Any]:
    tz = resolve_timezone(timezone)
    now = datetime.now(tz)
    return {
        "timezone": timezone,
        "iso": now.isoformat(timespec="seconds"),
        "date": now.date().isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "time_hm": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
    }
