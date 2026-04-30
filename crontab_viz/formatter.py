"""Human-readable formatting of crontab expressions."""

from typing import List
from crontab_viz.parser import CronExpression

_MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

_DAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]


def _ordinal(n: int) -> str:
    """Return ordinal string for a number (1 -> '1st', etc.)."""
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 if n % 100 not in (11, 12, 13) else 0, "th")
    return f"{n}{suffix}"


def _describe_field(values: List[int], unit: str, names: List[str] = None) -> str:
    """Describe a parsed crontab field in plain English."""
    full_range = {
        "minute": list(range(60)),
        "hour": list(range(24)),
        "day": list(range(1, 32)),
        "month": list(range(1, 13)),
        "weekday": list(range(7)),
    }
    all_vals = full_range.get(unit, [])
    if sorted(values) == sorted(all_vals):
        return f"every {unit}"

    if names:
        labeled = [names[v] for v in sorted(values) if 0 <= v < len(names)]
    else:
        labeled = [_ordinal(v) if unit in ("day",) else str(v) for v in sorted(values)]

    if len(labeled) == 1:
        return labeled[0]
    return ", ".join(labeled[:-1]) + f" and {labeled[-1]}"


def describe(expr: CronExpression) -> str:
    """Return a human-readable description of a CronExpression."""
    parts = []

    minute_desc = _describe_field(expr.minutes, "minute")
    hour_desc = _describe_field(expr.hours, "hour")

    if minute_desc == "every minute" and hour_desc == "every hour":
        time_part = "every minute"
    elif minute_desc == "every minute":
        time_part = f"every minute during hour(s) {_describe_field(expr.hours, 'hour')}"
    else:
        minutes_str = ", ".join(str(m) for m in sorted(expr.minutes))
        hours_str = ", ".join(str(h) for h in sorted(expr.hours))
        time_part = f"at minute {minutes_str} past hour {hours_str}"

    parts.append(time_part)

    dom_desc = _describe_field(expr.days, "day")
    dow_desc = _describe_field(expr.weekdays, "weekday", _DAY_NAMES)
    month_desc = _describe_field(expr.months, "month", _MONTH_NAMES)

    if dom_desc != "every day":
        parts.append(f"on the {dom_desc} of the month")
    if dow_desc != "every weekday":
        parts.append(f"on {dow_desc}")
    if month_desc != "every month":
        parts.append(f"in {month_desc}")

    return ", ".join(parts)
